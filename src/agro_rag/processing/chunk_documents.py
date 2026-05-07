"""
Document chunking utilities for agro_rag.

This module converts cleaned page-level text into smaller text chunks that are
suitable for embedding and retrieval in a RAG system.

Expected input:
- cleaned page-level DataFrame produced by clean_text.py

Expected output:
- chunk-level DataFrame with text and metadata
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_METADATA_COLUMNS = [
    "source",
    "document_name",
    "file_path",
    "page_number",
    "year",
    "theme",
    "language",
]


def split_text_by_words(
    text: str,
    chunk_size: int = 250,
    chunk_overlap: int = 40,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    Parameters
    ----------
    text : str
        Input text.

    chunk_size : int
        Maximum number of words per chunk.

    chunk_overlap : int
        Number of overlapping words between consecutive chunks.

    Returns
    -------
    list[str]
        List of text chunks.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    words = text.split()

    if len(words) <= chunk_size:
        return [" ".join(words)]

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))

        if end >= len(words):
            break

        start = end - chunk_overlap

    return chunks


def build_chunk_id(
    source: str,
    document_name: str,
    page_number: int,
    chunk_index: int,
) -> str:
    """
    Build a stable chunk identifier.

    Parameters
    ----------
    source : str
        Source family, such as MapBiomas or INPE.

    document_name : str
        Document name.

    page_number : int
        Page number.

    chunk_index : int
        Chunk index within the page.

    Returns
    -------
    str
        Stable chunk identifier.
    """
    safe_source = str(source).lower().replace(" ", "_").replace("/", "_")
    safe_document = str(document_name).lower().replace(" ", "_").replace("/", "_")

    return f"{safe_source}__{safe_document}__p{page_number:04d}__c{chunk_index:03d}"


def chunk_page_row(
    row: pd.Series,
    text_column: str = "clean_text",
    metadata_columns: Iterable[str] = DEFAULT_METADATA_COLUMNS,
    chunk_size: int = 250,
    chunk_overlap: int = 40,
) -> list[dict]:
    """
    Convert one page row into one or more chunk dictionaries.

    Parameters
    ----------
    row : pandas.Series
        One row from a cleaned page-level DataFrame.

    text_column : str
        Name of the column containing cleaned text.

    metadata_columns : iterable of str
        Metadata columns to preserve in each chunk.

    chunk_size : int
        Maximum number of words per chunk.

    chunk_overlap : int
        Number of overlapping words between chunks.

    Returns
    -------
    list[dict]
        Chunk records.
    """
    if text_column not in row.index:
        raise ValueError(f"Column not found in row: {text_column}")

    text = row[text_column]
    chunks = split_text_by_words(
        text=text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    source = row.get("source", "unknown_source")
    document_name = row.get("document_name", "unknown_document")
    page_number = int(row.get("page_number", 0) or 0)

    records: list[dict] = []

    for chunk_index, chunk_text in enumerate(chunks, start=1):
        record = {
            "chunk_id": build_chunk_id(
                source=source,
                document_name=document_name,
                page_number=page_number,
                chunk_index=chunk_index,
            ),
            "chunk_index": chunk_index,
            "chunk_text": chunk_text,
            "chunk_word_count": len(chunk_text.split()),
            "chunk_char_count": len(chunk_text),
        }

        for column in metadata_columns:
            if column in row.index:
                record[column] = row[column]

        records.append(record)

    return records


def chunk_pages_dataframe(
    pages_df: pd.DataFrame,
    text_column: str = "clean_text",
    metadata_columns: Iterable[str] = DEFAULT_METADATA_COLUMNS,
    chunk_size: int = 250,
    chunk_overlap: int = 40,
) -> pd.DataFrame:
    """
    Convert a cleaned page-level DataFrame into a chunk-level DataFrame.

    Parameters
    ----------
    pages_df : pandas.DataFrame
        Cleaned page-level DataFrame.

    text_column : str
        Name of the column containing cleaned text.

    metadata_columns : iterable of str
        Metadata columns to preserve in each chunk.

    chunk_size : int
        Maximum number of words per chunk.

    chunk_overlap : int
        Number of overlapping words between chunks.

    Returns
    -------
    pandas.DataFrame
        Chunk-level DataFrame.
    """
    if text_column not in pages_df.columns:
        raise ValueError(f"Column not found: {text_column}")

    all_records: list[dict] = []

    for _, row in pages_df.iterrows():
        page_chunks = chunk_page_row(
            row=row,
            text_column=text_column,
            metadata_columns=metadata_columns,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        all_records.extend(page_chunks)

    if not all_records:
        return pd.DataFrame(
            columns=[
                "chunk_id",
                "chunk_index",
                "chunk_text",
                "chunk_word_count",
                "chunk_char_count",
                *list(metadata_columns),
            ]
        )

    chunks_df = pd.DataFrame(all_records)

    # Keep a stable and readable column order.
    front_columns = [
        "chunk_id",
        "source",
        "document_name",
        "page_number",
        "chunk_index",
        "year",
        "theme",
        "language",
        "chunk_text",
        "chunk_word_count",
        "chunk_char_count",
    ]

    ordered_columns = [col for col in front_columns if col in chunks_df.columns]
    remaining_columns = [col for col in chunks_df.columns if col not in ordered_columns]

    return chunks_df[ordered_columns + remaining_columns]


def chunk_pages_file(
    input_path: str | Path,
    output_path: str | Path,
    text_column: str = "clean_text",
    chunk_size: int = 250,
    chunk_overlap: int = 40,
) -> pd.DataFrame:
    """
    Load cleaned pages from Parquet, create chunks and save them.

    Parameters
    ----------
    input_path : str or Path
        Input Parquet file with cleaned page-level text.

    output_path : str or Path
        Output Parquet file for chunk-level data.

    text_column : str
        Name of the column containing cleaned text.

    chunk_size : int
        Maximum number of words per chunk.

    chunk_overlap : int
        Number of overlapping words between chunks.

    Returns
    -------
    pandas.DataFrame
        Chunk-level DataFrame.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    pages_df = pd.read_parquet(input_path)

    chunks_df = chunk_pages_dataframe(
        pages_df=pages_df,
        text_column=text_column,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunks_df.to_parquet(output_path, index=False)

    return chunks_df


def combine_chunk_files(
    input_paths: list[str | Path],
    output_path: str | Path,
) -> pd.DataFrame:
    """
    Combine multiple chunk Parquet files into one file.

    This is useful when MapBiomas and INPE documents are processed separately.

    Parameters
    ----------
    input_paths : list[str or Path]
        List of chunk Parquet files.

    output_path : str or Path
        Combined output Parquet path.

    Returns
    -------
    pandas.DataFrame
        Combined chunk-level DataFrame.
    """
    dataframes = []

    for input_path in input_paths:
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        dataframes.append(pd.read_parquet(input_path))

    if not dataframes:
        combined_df = pd.DataFrame()
    else:
        combined_df = pd.concat(dataframes, ignore_index=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    combined_df.to_parquet(output_path, index=False)

    return combined_df
