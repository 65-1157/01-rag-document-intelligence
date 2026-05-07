"""
Vector store utilities for agro_rag.

This module stores document chunks in ChromaDB and retrieves relevant chunks
for Retrieval-Augmented Generation.

Expected input:
- data/processed/document_chunks.parquet

Expected output:
- persistent ChromaDB collection under chroma_db/
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

from agro_rag.rag.embeddings import DEFAULT_EMBEDDING_MODEL, load_embedding_model


DEFAULT_COLLECTION_NAME = "agro_environmental_documents"


def get_chroma_client(
    persist_directory: str | Path = "chroma_db",
) -> chromadb.PersistentClient:
    """
    Create a persistent ChromaDB client.

    Parameters
    ----------
    persist_directory : str or Path
        Directory where ChromaDB files will be stored.

    Returns
    -------
    chromadb.PersistentClient
        Persistent ChromaDB client.
    """
    persist_directory = Path(persist_directory)
    persist_directory.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=str(persist_directory))


def get_or_create_collection(
    client: chromadb.PersistentClient,
    collection_name: str = DEFAULT_COLLECTION_NAME,
):
    """
    Get or create a ChromaDB collection.

    Parameters
    ----------
    client : chromadb.PersistentClient
        ChromaDB client.

    collection_name : str
        Collection name.

    Returns
    -------
    chromadb.Collection
        ChromaDB collection.
    """
    return client.get_or_create_collection(name=collection_name)


def prepare_metadata_value(value: Any) -> str | int | float | bool | None:
    """
    Prepare one metadata value for ChromaDB.

    ChromaDB metadata values must be simple scalar types.

    Parameters
    ----------
    value : Any
        Raw metadata value.

    Returns
    -------
    str, int, float, bool or None
        Chroma-compatible metadata value.
    """
    if pd.isna(value):
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    return str(value)


def dataframe_to_chroma_records(
    chunks_df: pd.DataFrame,
    text_column: str = "chunk_text",
    id_column: str = "chunk_id",
    metadata_columns: list[str] | None = None,
) -> tuple[list[str], list[str], list[dict]]:
    """
    Convert a chunks DataFrame into ChromaDB records.

    Parameters
    ----------
    chunks_df : pandas.DataFrame
        Chunk-level DataFrame.

    text_column : str
        Column containing chunk text.

    id_column : str
        Column containing unique chunk IDs.

    metadata_columns : list of str, optional
        Metadata columns to store with each chunk.

    Returns
    -------
    tuple
        ids, documents, metadatas
    """
    if text_column not in chunks_df.columns:
        raise ValueError(f"Text column not found: {text_column}")

    if id_column not in chunks_df.columns:
        raise ValueError(f"ID column not found: {id_column}")

    if metadata_columns is None:
        metadata_columns = [
            "source",
            "document_name",
            "file_path",
            "page_number",
            "year",
            "theme",
            "language",
        ]

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for _, row in chunks_df.iterrows():
        chunk_id = str(row[id_column])
        text = str(row[text_column]) if row[text_column] is not None else ""

        metadata = {}

        for column in metadata_columns:
            if column in chunks_df.columns:
                metadata[column] = prepare_metadata_value(row[column])

        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(metadata)

    return ids, documents, metadatas


def add_chunks_to_collection(
    collection,
    chunks_df: pd.DataFrame,
    model: SentenceTransformer,
    text_column: str = "chunk_text",
    id_column: str = "chunk_id",
    metadata_columns: list[str] | None = None,
    batch_size: int = 128,
) -> None:
    """
    Add document chunks to a ChromaDB collection.

    Parameters
    ----------
    collection : chromadb.Collection
        ChromaDB collection.

    chunks_df : pandas.DataFrame
        Chunk-level DataFrame.

    model : SentenceTransformer
        Embedding model.

    text_column : str
        Column containing chunk text.

    id_column : str
        Column containing unique chunk IDs.

    metadata_columns : list of str, optional
        Metadata columns to store.

    batch_size : int
        Number of chunks inserted per batch.
    """
    ids, documents, metadatas = dataframe_to_chroma_records(
        chunks_df=chunks_df,
        text_column=text_column,
        id_column=id_column,
        metadata_columns=metadata_columns,
    )

    for start in range(0, len(ids), batch_size):
        end = start + batch_size

        batch_ids = ids[start:end]
        batch_documents = documents[start:end]
        batch_metadatas = metadatas[start:end]

        batch_embeddings = model.encode(
            batch_documents,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        ).tolist()

        collection.add(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas,
            embeddings=batch_embeddings,
        )


def build_vector_store_from_chunks(
    chunks_path: str | Path,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = DEFAULT_COLLECTION_NAME,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    text_column: str = "chunk_text",
    id_column: str = "chunk_id",
    reset_collection: bool = True,
) -> None:
    """
    Build a ChromaDB vector store from a chunks Parquet file.

    Parameters
    ----------
    chunks_path : str or Path
        Path to document_chunks.parquet.

    persist_directory : str or Path
        Directory where ChromaDB files will be stored.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        SentenceTransformers model name.

    text_column : str
        Column containing chunk text.

    id_column : str
        Column containing chunk IDs.

    reset_collection : bool
        If True, delete the existing collection before rebuilding it.
    """
    chunks_path = Path(chunks_path)

    if not chunks_path.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_path}")

    chunks_df = pd.read_parquet(chunks_path)

    if chunks_df.empty:
        raise ValueError("Chunks DataFrame is empty.")

    client = get_chroma_client(persist_directory=persist_directory)

    if reset_collection:
        try:
            client.delete_collection(name=collection_name)
        except Exception:
            pass

    collection = get_or_create_collection(
        client=client,
        collection_name=collection_name,
    )

    model = load_embedding_model(model_name=model_name)

    add_chunks_to_collection(
        collection=collection,
        chunks_df=chunks_df,
        model=model,
        text_column=text_column,
        id_column=id_column,
    )


def query_vector_store(
    question: str,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = DEFAULT_COLLECTION_NAME,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    n_results: int = 5,
    where: dict | None = None,
) -> pd.DataFrame:
    """
    Query the ChromaDB vector store.

    Parameters
    ----------
    question : str
        User question.

    persist_directory : str or Path
        Directory where ChromaDB files are stored.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        SentenceTransformers model name.

    n_results : int
        Number of retrieved chunks.

    where : dict, optional
        Metadata filter for ChromaDB.

        Example:
        {"source": "MapBiomas"}

    Returns
    -------
    pandas.DataFrame
        Retrieved chunks with metadata and distance.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    client = get_chroma_client(persist_directory=persist_directory)
    collection = get_or_create_collection(
        client=client,
        collection_name=collection_name,
    )

    model = load_embedding_model(model_name=model_name)
    query_embedding = model.encode(
        [question],
        normalize_embeddings=True,
    ).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    records: list[dict] = []

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for rank, chunk_id in enumerate(ids, start=1):
        metadata = metadatas[rank - 1] or {}

        record = {
            "rank": rank,
            "chunk_id": chunk_id,
            "distance": distances[rank - 1],
            "chunk_text": documents[rank - 1],
        }

        record.update(metadata)
        records.append(record)

    return pd.DataFrame(records)


def format_retrieved_context(
    retrieved_df: pd.DataFrame,
    max_chars_per_chunk: int = 1200,
) -> str:
    """
    Format retrieved chunks into a context string for the RAG prompt.

    Parameters
    ----------
    retrieved_df : pandas.DataFrame
        DataFrame returned by query_vector_store.

    max_chars_per_chunk : int
        Maximum number of characters included per chunk.

    Returns
    -------
    str
        Formatted context.
    """
    if retrieved_df.empty:
        return "No relevant context was retrieved."

    context_blocks = []

    for _, row in retrieved_df.iterrows():
        source = row.get("source", "unknown source")
        document_name = row.get("document_name", "unknown document")
        page_number = row.get("page_number", "unknown page")
        year = row.get("year", "unknown year")
        theme = row.get("theme", "unknown theme")
        text = str(row.get("chunk_text", ""))[:max_chars_per_chunk]

        block = (
            f"[Retrieved chunk]\n"
            f"Source: {source}\n"
            f"Document: {document_name}\n"
            f"Page: {page_number}\n"
            f"Year: {year}\n"
            f"Theme: {theme}\n"
            f"Text: {text}"
        )

        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)
