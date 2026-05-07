"""
Build the municipality-year environmental panel.

This module combines simplified MapBiomas and INPE / PRODES tables into one
municipality-year panel.

The panel is the structured evidence layer of the RAG system.

Expected MapBiomas input columns:
- municipality_code
- municipality_name
- state
- biome
- year
- mapbiomas_forest_area_ha
- mapbiomas_native_vegetation_area_ha
- mapbiomas_agriculture_area_ha
- mapbiomas_pasture_area_ha

Expected INPE input columns:
- municipality_code
- municipality_name
- state
- biome
- year
- inpe_prodes_deforestation_area_ha

Expected output:
- one row per municipality-year
- MapBiomas indicators
- INPE / PRODES indicators
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PANEL_KEY_COLUMNS = [
    "municipality_code",
    "year",
]


MAPBIOMAS_REQUIRED_COLUMNS = [
    "municipality_code",
    "municipality_name",
    "state",
    "biome",
    "year",
    "mapbiomas_forest_area_ha",
    "mapbiomas_native_vegetation_area_ha",
    "mapbiomas_agriculture_area_ha",
    "mapbiomas_pasture_area_ha",
]


INPE_REQUIRED_COLUMNS = [
    "municipality_code",
    "year",
    "inpe_prodes_deforestation_area_ha",
]


PREFERRED_OUTPUT_COLUMNS = [
    "municipality_code",
    "municipality_name",
    "state",
    "biome",
    "year",
    "mapbiomas_forest_area_ha",
    "mapbiomas_native_vegetation_area_ha",
    "mapbiomas_agriculture_area_ha",
    "mapbiomas_pasture_area_ha",
    "inpe_prodes_deforestation_area_ha",
]


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataframe_name: str,
) -> None:
    """
    Validate whether required columns exist in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate.

    required_columns : list of str
        Required column names.

    dataframe_name : str
        Human-readable DataFrame name.

    Raises
    ------
    ValueError
        If any required column is missing.
    """
    missing_columns = [column for column in required_columns if column not in df.columns]

    if missing_columns:
        raise ValueError(
            f"{dataframe_name} is missing required columns: {missing_columns}"
        )


def standardize_municipality_code(
    df: pd.DataFrame,
    column: str = "municipality_code",
) -> pd.DataFrame:
    """
    Standardize municipality code as a string.

    This avoids merge errors caused by one table using integers and another
    table using strings.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    column : str
        Municipality code column.

    Returns
    -------
    pandas.DataFrame
        DataFrame with standardized municipality code.
    """
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    result = df.copy()

    result[column] = (
        result[column]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.strip()
    )

    return result


def standardize_year(
    df: pd.DataFrame,
    column: str = "year",
) -> pd.DataFrame:
    """
    Standardize year as integer.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    column : str
        Year column.

    Returns
    -------
    pandas.DataFrame
        DataFrame with integer year.
    """
    if column not in df.columns:
        raise ValueError(f"Column not found: {column}")

    result = df.copy()
    result[column] = pd.to_numeric(result[column], errors="coerce").astype("Int64")

    if result[column].isna().any():
        raise ValueError(f"Column '{column}' contains invalid year values.")

    result[column] = result[column].astype(int)

    return result


def convert_numeric_columns(
    df: pd.DataFrame,
    numeric_columns: list[str],
) -> pd.DataFrame:
    """
    Convert selected columns to numeric values.

    Missing or invalid values are converted to 0.0.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame.

    numeric_columns : list of str
        Columns to convert.

    Returns
    -------
    pandas.DataFrame
        DataFrame with numeric columns.
    """
    result = df.copy()

    for column in numeric_columns:
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0.0)

    return result


def prepare_mapbiomas_table(
    mapbiomas_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the MapBiomas table before merging.

    Parameters
    ----------
    mapbiomas_df : pandas.DataFrame
        Raw or cleaned MapBiomas table.

    Returns
    -------
    pandas.DataFrame
        Standardized MapBiomas table.
    """
    validate_required_columns(
        df=mapbiomas_df,
        required_columns=MAPBIOMAS_REQUIRED_COLUMNS,
        dataframe_name="MapBiomas table",
    )

    result = mapbiomas_df.copy()
    result = standardize_municipality_code(result)
    result = standardize_year(result)

    numeric_columns = [
        "mapbiomas_forest_area_ha",
        "mapbiomas_native_vegetation_area_ha",
        "mapbiomas_agriculture_area_ha",
        "mapbiomas_pasture_area_ha",
    ]

    result = convert_numeric_columns(result, numeric_columns)

    result = result[MAPBIOMAS_REQUIRED_COLUMNS].drop_duplicates(
        subset=PANEL_KEY_COLUMNS
    )

    return result


def prepare_inpe_table(
    inpe_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepare the INPE / PRODES table before merging.

    Parameters
    ----------
    inpe_df : pandas.DataFrame
        Raw or cleaned INPE table.

    Returns
    -------
    pandas.DataFrame
        Standardized INPE table.
    """
    validate_required_columns(
        df=inpe_df,
        required_columns=INPE_REQUIRED_COLUMNS,
        dataframe_name="INPE table",
    )

    result = inpe_df.copy()
    result = standardize_municipality_code(result)
    result = standardize_year(result)

    numeric_columns = [
        "inpe_prodes_deforestation_area_ha",
    ]

    result = convert_numeric_columns(result, numeric_columns)

    result = result[INPE_REQUIRED_COLUMNS].drop_duplicates(
        subset=PANEL_KEY_COLUMNS
    )

    return result


def build_environmental_panel(
    mapbiomas_df: pd.DataFrame,
    inpe_df: pd.DataFrame,
    how: str = "left",
) -> pd.DataFrame:
    """
    Build the municipality-year environmental panel.

    Parameters
    ----------
    mapbiomas_df : pandas.DataFrame
        Prepared or raw MapBiomas table.

    inpe_df : pandas.DataFrame
        Prepared or raw INPE / PRODES table.

    how : str
        Merge strategy. Default is "left", keeping the MapBiomas table
        as the reference geography-year structure.

    Returns
    -------
    pandas.DataFrame
        Municipality-year environmental panel.
    """
    mapbiomas_prepared = prepare_mapbiomas_table(mapbiomas_df)
    inpe_prepared = prepare_inpe_table(inpe_df)

    panel = mapbiomas_prepared.merge(
        inpe_prepared,
        on=PANEL_KEY_COLUMNS,
        how=how,
    )

    panel["inpe_prodes_deforestation_area_ha"] = (
        pd.to_numeric(
            panel["inpe_prodes_deforestation_area_ha"],
            errors="coerce",
        ).fillna(0.0)
    )

    ordered_columns = [
        column for column in PREFERRED_OUTPUT_COLUMNS if column in panel.columns
    ]

    remaining_columns = [
        column for column in panel.columns if column not in ordered_columns
    ]

    panel = panel[ordered_columns + remaining_columns]

    panel = panel.sort_values(
        ["state", "municipality_name", "year"],
        na_position="last",
    ).reset_index(drop=True)

    return panel


def read_table(path: str | Path) -> pd.DataFrame:
    """
    Read a CSV or Parquet table.

    Parameters
    ----------
    path : str or Path
        Input file path.

    Returns
    -------
    pandas.DataFrame
        Loaded table.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)

    if suffix in [".parquet", ".pq"]:
        return pd.read_parquet(path)

    raise ValueError(
        f"Unsupported file format: {suffix}. Use CSV or Parquet."
    )


def write_table(
    df: pd.DataFrame,
    path: str | Path,
) -> None:
    """
    Write a table as CSV or Parquet.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to save.

    path : str or Path
        Output file path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    suffix = path.suffix.lower()

    if suffix == ".csv":
        df.to_csv(path, index=False)
        return

    if suffix in [".parquet", ".pq"]:
        df.to_parquet(path, index=False)
        return

    raise ValueError(
        f"Unsupported file format: {suffix}. Use CSV or Parquet."
    )


def build_environmental_panel_file(
    mapbiomas_path: str | Path,
    inpe_path: str | Path,
    output_path: str | Path,
    how: str = "left",
) -> pd.DataFrame:
    """
    Build the environmental panel from input files and save it.

    Parameters
    ----------
    mapbiomas_path : str or Path
        Path to cleaned MapBiomas table.

    inpe_path : str or Path
        Path to cleaned INPE / PRODES table.

    output_path : str or Path
        Output panel path.

    how : str
        Merge strategy.

    Returns
    -------
    pandas.DataFrame
        Environmental panel.
    """
    mapbiomas_df = read_table(mapbiomas_path)
    inpe_df = read_table(inpe_path)

    panel = build_environmental_panel(
        mapbiomas_df=mapbiomas_df,
        inpe_df=inpe_df,
        how=how,
    )

    write_table(panel, output_path)

    return panel
