"""
Embedding utilities for agro_rag.

This module creates vector embeddings for document chunks.

The first version supports SentenceTransformers because it can run locally
without requiring an external API key.

Expected input:
- data/processed/document_chunks.parquet

Expected output:
- a DataFrame with chunk metadata and embedding vectors
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> SentenceTransformer:
    """
    Load a SentenceTransformers embedding model.

    Parameters
    ----------
    model_name : str
        Name of the embedding model.

    Returns
    -------
    SentenceTransformer
        Loaded embedding model.
    """
    return SentenceTransformer(model_name)


def create_embeddings(
    texts: Iterable[str],
    model: SentenceTransformer,
    batch_size: int = 32,
    normalize_embeddings: bool = True,
) -> np.ndarray:
    """
    Create embeddings for a list of texts.

    Parameters
    ----------
    texts : iterable of str
        Texts to embed.

    model : SentenceTransformer
        Loaded embedding model.

    batch_size : int
        Batch size used during encoding.

    normalize_embeddings : bool
        If True, normalize embeddings to unit length.

    Returns
    -------
    numpy.ndarray
        Embedding matrix.
    """
    texts = [str(text) if text is not None else "" for text in texts]

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=normalize_embeddings,
    )

    return np.asarray(embeddings)


def add_embeddings_to_chunks(
    chunks_df: pd.DataFrame,
    text_column: str = "chunk_text",
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = 32,
    normalize_embeddings: bool = True,
) -> pd.DataFrame:
    """
    Add embeddings to a chunk-level DataFrame.

    Parameters
    ----------
    chunks_df : pandas.DataFrame
        DataFrame containing document chunks.

    text_column : str
        Name of the column containing text to embed.

    model_name : str
        Embedding model name.

    batch_size : int
        Batch size used during encoding.

    normalize_embeddings : bool
        If True, normalize embeddings to unit length.

    Returns
    -------
    pandas.DataFrame
        DataFrame with an additional 'embedding' column.
    """
    if text_column not in chunks_df.columns:
        raise ValueError(f"Column not found: {text_column}")

    df = chunks_df.copy()

    model = load_embedding_model(model_name=model_name)

    embeddings = create_embeddings(
        texts=df[text_column].fillna("").tolist(),
        model=model,
        batch_size=batch_size,
        normalize_embeddings=normalize_embeddings,
    )

    df["embedding"] = embeddings.tolist()
    df["embedding_model"] = model_name
    df["embedding_dimension"] = embeddings.shape[1]

    return df


def embed_chunks_file(
    input_path: str | Path,
    output_path: str | Path,
    text_column: str = "chunk_text",
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = 32,
    normalize_embeddings: bool = True,
) -> pd.DataFrame:
    """
    Load chunk data from Parquet, create embeddings and save the result.

    Parameters
    ----------
    input_path : str or Path
        Input Parquet file containing document chunks.

    output_path : str or Path
        Output Parquet file containing chunks and embeddings.

    text_column : str
        Name of the column containing text to embed.

    model_name : str
        Embedding model name.

    batch_size : int
        Batch size used during encoding.

    normalize_embeddings : bool
        If True, normalize embeddings to unit length.

    Returns
    -------
    pandas.DataFrame
        DataFrame with embeddings.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    chunks_df = pd.read_parquet(input_path)

    embedded_df = add_embeddings_to_chunks(
        chunks_df=chunks_df,
        text_column=text_column,
        model_name=model_name,
        batch_size=batch_size,
        normalize_embeddings=normalize_embeddings,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    embedded_df.to_parquet(output_path, index=False)

    return embedded_df


def validate_embeddings_dataframe(
    df: pd.DataFrame,
    embedding_column: str = "embedding",
    id_column: str = "chunk_id",
) -> None:
    """
    Validate whether a DataFrame contains valid embeddings.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate.

    embedding_column : str
        Name of the embedding column.

    id_column : str
        Name of the chunk identifier column.

    Raises
    ------
    ValueError
        If required columns are missing or embeddings are invalid.
    """
    required_columns = [embedding_column, id_column]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Required column not found: {column}")

    if df.empty:
        raise ValueError("The embeddings DataFrame is empty.")

    first_embedding = df[embedding_column].iloc[0]

    if not isinstance(first_embedding, list):
        raise ValueError(
            f"Expected embeddings to be stored as lists in column '{embedding_column}'."
        )

    if len(first_embedding) == 0:
        raise ValueError("Embedding vector is empty.")
