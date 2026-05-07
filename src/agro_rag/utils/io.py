"""
Input/output utilities for the agro_rag package.

This module provides simple reusable functions to read and write common
project file formats.
"""

from pathlib import Path
from typing import Any

import json
import pandas as pd


def read_text_file(path: str | Path, encoding: str = "utf-8") -> str:
    """
    Read a text file.

    Parameters
    ----------
    path : str or Path
        File path.
    encoding : str
        File encoding.

    Returns
    -------
    str
        File content.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding=encoding)


def write_text_file(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    """
    Write text content to a file.

    Parameters
    ----------
    path : str or Path
        Output file path.
    content : str
        Text content to write.
    encoding : str
        File encoding.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def read_json(path: str | Path, encoding: str = "utf-8") -> dict[str, Any]:
    """
    Read a JSON file.

    Parameters
    ----------
    path : str or Path
        JSON file path.
    encoding : str
        File encoding.

    Returns
    -------
    dict
        Parsed JSON content.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding=encoding) as file:
        return json.load(file)


def write_json(
    path: str | Path,
    data: dict[str, Any],
    encoding: str = "utf-8",
    indent: int = 2,
) -> None:
    """
    Write data to a JSON file.

    Parameters
    ----------
    path : str or Path
        Output file path.
    data : dict
        Data to write.
    encoding : str
        File encoding.
    indent : int
        JSON indentation.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding=encoding) as file:
        json.dump(data, file, ensure_ascii=False, indent=indent)


def read_csv(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame.

    Parameters
    ----------
    path : str or Path
        CSV file path.
    **kwargs
        Additional arguments passed to pandas.read_csv.

    Returns
    -------
    pandas.DataFrame
        Loaded DataFrame.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_csv(path, **kwargs)


def write_csv(path: str | Path, df: pd.DataFrame, index: bool = False, **kwargs: Any) -> None:
    """
    Write a pandas DataFrame to CSV.

    Parameters
    ----------
    path : str or Path
        Output CSV file path.
    df : pandas.DataFrame
        DataFrame to write.
    index : bool
        Whether to write the DataFrame index.
    **kwargs
        Additional arguments passed to pandas.DataFrame.to_csv.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index, **kwargs)


def read_parquet(path: str | Path, **kwargs: Any) -> pd.DataFrame:
    """
    Read a Parquet file into a pandas DataFrame.

    Parameters
    ----------
    path : str or Path
        Parquet file path.
    **kwargs
        Additional arguments passed to pandas.read_parquet.

    Returns
    -------
    pandas.DataFrame
        Loaded DataFrame.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    return pd.read_parquet(path, **kwargs)


def write_parquet(path: str | Path, df: pd.DataFrame, index: bool = False, **kwargs: Any) -> None:
    """
    Write a pandas DataFrame to Parquet.

    Parameters
    ----------
    path : str or Path
        Output Parquet file path.
    df : pandas.DataFrame
        DataFrame to write.
    index : bool
        Whether to write the DataFrame index.
    **kwargs
        Additional arguments passed to pandas.DataFrame.to_parquet.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=index, **kwargs)
