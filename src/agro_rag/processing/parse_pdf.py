"""
PDF parsing utilities for agro_rag.

This module extracts text from PDF files and stores the result in a
page-level pandas DataFrame.

The output is designed to support the next RAG steps:

1. text cleaning;
2. document chunking;
3. metadata enrichment;
4. vector database indexing.

Main expected sources:
- MapBiomas reports and methodological documents;
- INPE / TerraBrasilis reports and methodological documents.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import pdfplumber


def extract_text_from_pdf(
    pdf_path: str | Path,
    source: str,
    document_name: Optional[str] = None,
    year: Optional[int] = None,
    theme: Optional[str] = None,
    language: str = "pt-BR",
) -> pd.DataFrame:
    """
    Extract text from a PDF file page by page.

    Parameters
    ----------
    pdf_path : str or Path
        Path to the PDF file.

    source : str
        Source family, for example "MapBiomas" or "INPE".

    document_name : str, optional
        Human-readable document name.
        If not provided, the PDF file name is used.

    year : int, optional
        Reference year of the document, when available.

    theme : str, optional
        Main theme of the document, such as "deforestation",
        "land use", "methodology" or "monitoring".

    language : str
        Document language. Default is "pt-BR".

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per page.

        Columns:
        - source
        - document_name
        - file_path
        - page_number
        - year
        - theme
        - language
        - text
        - text_length
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file, got: {pdf_path.suffix}")

    if document_name is None:
        document_name = pdf_path.stem

    rows: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            rows.append(
                {
                    "source": source,
                    "document_name": document_name,
                    "file_path": str(pdf_path),
                    "page_number": page_index,
                    "year": year,
                    "theme": theme,
                    "language": language,
                    "text": text,
                    "text_length": len(text),
                }
            )

    return pd.DataFrame(rows)


def parse_pdf_folder(
    folder_path: str | Path,
    source: str,
    year: Optional[int] = None,
    theme: Optional[str] = None,
    language: str = "pt-BR",
    recursive: bool = True,
) -> pd.DataFrame:
    """
    Extract text from all PDF files in a folder.

    Parameters
    ----------
    folder_path : str or Path
        Folder containing PDF files.

    source : str
        Source family, for example "MapBiomas" or "INPE".

    year : int, optional
        Reference year applied to all files, when available.

    theme : str, optional
        Main theme applied to all files, when available.

    language : str
        Document language. Default is "pt-BR".

    recursive : bool
        If True, search PDF files in subfolders as well.

    Returns
    -------
    pandas.DataFrame
        Combined page-level DataFrame for all PDFs found.
    """
    folder_path = Path(folder_path)

    if not folder_path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not folder_path.is_dir():
        raise NotADirectoryError(f"Expected a folder, got: {folder_path}")

    pattern = "**/*.pdf" if recursive else "*.pdf"
    pdf_files = sorted(folder_path.glob(pattern))

    if not pdf_files:
        return pd.DataFrame(
            columns=[
                "source",
                "document_name",
                "file_path",
                "page_number",
                "year",
                "theme",
                "language",
                "text",
                "text_length",
            ]
        )

    parsed_documents = []

    for pdf_file in pdf_files:
        parsed_df = extract_text_from_pdf(
            pdf_path=pdf_file,
            source=source,
            document_name=pdf_file.stem,
            year=year,
            theme=theme,
            language=language,
        )

        parsed_documents.append(parsed_df)

    return pd.concat(parsed_documents, ignore_index=True)


def save_parsed_pdf_text(
    parsed_df: pd.DataFrame,
    output_path: str | Path,
) -> None:
    """
    Save parsed PDF text to a Parquet file.

    Parameters
    ----------
    parsed_df : pandas.DataFrame
        Page-level DataFrame produced by extract_text_from_pdf
        or parse_pdf_folder.

    output_path : str or Path
        Output Parquet path.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    parsed_df.to_parquet(output_path, index=False)


def parse_and_save_pdf_folder(
    folder_path: str | Path,
    output_path: str | Path,
    source: str,
    year: Optional[int] = None,
    theme: Optional[str] = None,
    language: str = "pt-BR",
    recursive: bool = True,
) -> pd.DataFrame:
    """
    Parse all PDFs in a folder and save the result.

    This is a convenience function for notebooks and scripts.

    Parameters
    ----------
    folder_path : str or Path
        Folder containing PDF files.

    output_path : str or Path
        Output Parquet file path.

    source : str
        Source family, for example "MapBiomas" or "INPE".

    year : int, optional
        Reference year applied to all files, when available.

    theme : str, optional
        Main theme applied to all files, when available.

    language : str
        Document language. Default is "pt-BR".

    recursive : bool
        If True, search PDF files in subfolders as well.

    Returns
    -------
    pandas.DataFrame
        Parsed page-level DataFrame.
    """
    parsed_df = parse_pdf_folder(
        folder_path=folder_path,
        source=source,
        year=year,
        theme=theme,
        language=language,
        recursive=recursive,
    )

    save_parsed_pdf_text(parsed_df=parsed_df, output_path=output_path)

    return parsed_df
