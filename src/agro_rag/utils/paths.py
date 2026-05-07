"""
Path utilities for the agro_rag package.

This module centralizes the main project paths so notebooks and scripts
can reuse the same folder references.
"""

from pathlib import Path


def get_project_root() -> Path:
    """
    Return the project root directory.

    Assumption:
    This file is located at:
    src/agro_rag/utils/paths.py

    Therefore, the project root is three levels above this file.
    """
    return Path(__file__).resolve().parents[3]


PROJECT_ROOT = get_project_root()

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

MAPBIOMAS_RAW_DIR = RAW_DATA_DIR / "mapbiomas"
INPE_RAW_DIR = RAW_DATA_DIR / "inpe"

PARSED_DOCUMENTS_DIR = INTERIM_DATA_DIR / "parsed_documents"
CLEANED_MAPBIOMAS_DIR = INTERIM_DATA_DIR / "cleaned_mapbiomas"
CLEANED_INPE_DIR = INTERIM_DATA_DIR / "cleaned_inpe"

REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

PROMPTS_DIR = PROJECT_ROOT / "prompts"
DOCS_DIR = PROJECT_ROOT / "docs"

VECTOR_STORE_DIR = PROJECT_ROOT / "vector_store"
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"


def ensure_directory(path: Path) -> Path:
    """
    Create a directory if it does not exist.

    Parameters
    ----------
    path : Path
        Directory path to create.

    Returns
    -------
    Path
        The same path, after ensuring it exists.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_project_directories() -> None:
    """
    Create the main project directories if they do not exist.

    This is useful when running the project locally for the first time.
    """
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        INTERIM_DATA_DIR,
        PROCESSED_DATA_DIR,
        MAPBIOMAS_RAW_DIR,
        INPE_RAW_DIR,
        PARSED_DOCUMENTS_DIR,
        CLEANED_MAPBIOMAS_DIR,
        CLEANED_INPE_DIR,
        REPORTS_DIR,
        FIGURES_DIR,
        PROMPTS_DIR,
        DOCS_DIR,
        VECTOR_STORE_DIR,
        CHROMA_DB_DIR,
    ]

    for directory in directories:
        ensure_directory(directory)
