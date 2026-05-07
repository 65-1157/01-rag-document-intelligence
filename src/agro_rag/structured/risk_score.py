"""
Environmental risk scoring utilities for agro_rag.

This module calculates a simple explainable environmental screening score
using MapBiomas and INPE indicators.

The score is intended for prioritization and analyst support only.

It must not be interpreted as:
- proof of illegal deforestation;
- legal non-compliance;
- environmental crime evidence;
- final ESG classification.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


DEFAULT_SCORE_WEIGHTS = {
    "inpe_prodes_deforestation_area_ha": 0.50,
    "mapbiomas_native_vegetation_loss_ha": 0.30,
    "mapbiomas_agriculture_or_pasture_expansion_ha": 0.20,
}


def min_max_normalize(series: pd.Series) -> pd.Series:
    """
    Normalize a numeric pandas Series using min-max normalization.

    Parameters
    ----------
    series : pandas.Series
        Numeric input series.

    Returns
    -------
    pandas.Series
        Normalized values between 0 and 1.

    Notes
    -----
    If all valid values are equal, the function returns 0.0 for all rows.
    This avoids division by zero.
    """
    numeric_series = pd.to_numeric(series, errors="coerce")

    min_value = numeric_series.min()
    max_value = numeric_series.max()

    if pd.isna(min_value) or pd.isna(max_value):
        return pd.Series(0.0, index=series.index)

    if max_value == min_value:
        return pd.Series(0.0, index=series.index)

    normalized = (numeric_series - min_value) / (max_value - min_value)

    return normalized.fillna(0.0)


def add_agriculture_or_pasture_expansion(
    df: pd.DataFrame,
    agriculture_column: str = "mapbiomas_agriculture_area_ha",
    pasture_column: str = "mapbiomas_pasture_area_ha",
    group_columns: list[str] | None = None,
    year_column: str = "year",
    output_column: str = "mapbiomas_agriculture_or_pasture_expansion_ha",
) -> pd.DataFrame:
    """
    Calculate annual agriculture-or-pasture expansion.

    The function computes the year-to-year difference of:

        agriculture area + pasture area

    Negative differences are clipped to zero because this variable is meant
    to capture expansion pressure, not contraction.

    Parameters
    ----------
    df : pandas.DataFrame
        Municipality-year environmental panel.

    agriculture_column : str
        Column containing agriculture area in hectares.

    pasture_column : str
        Column containing pasture area in hectares.

    group_columns : list of str, optional
        Columns used to identify each geographic unit.
        Default: ["municipality_code"] if available, otherwise ["municipality_name"].

    year_column : str
        Year column.

    output_column : str
        Name of the output expansion column.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the expansion column added.
    """
    required_columns = [agriculture_column, pasture_column, year_column]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Required column not found: {column}")

    if group_columns is None:
        if "municipality_code" in df.columns:
            group_columns = ["municipality_code"]
        elif "municipality_name" in df.columns:
            group_columns = ["municipality_name"]
        else:
            raise ValueError(
                "No group_columns were provided and neither municipality_code "
                "nor municipality_name exists in the DataFrame."
            )

    for column in group_columns:
        if column not in df.columns:
            raise ValueError(f"Group column not found: {column}")

    result = df.copy()

    result[agriculture_column] = pd.to_numeric(
        result[agriculture_column],
        errors="coerce",
    ).fillna(0.0)

    result[pasture_column] = pd.to_numeric(
        result[pasture_column],
        errors="coerce",
    ).fillna(0.0)

    result["_agriculture_plus_pasture_ha"] = (
        result[agriculture_column] + result[pasture_column]
    )

    result = result.sort_values(group_columns + [year_column]).reset_index(drop=True)

    result[output_column] = (
        result.groupby(group_columns)["_agriculture_plus_pasture_ha"]
        .diff()
        .fillna(0.0)
        .clip(lower=0.0)
    )

    result = result.drop(columns=["_agriculture_plus_pasture_ha"])

    return result


def add_native_vegetation_loss(
    df: pd.DataFrame,
    native_vegetation_column: str = "mapbiomas_native_vegetation_area_ha",
    group_columns: list[str] | None = None,
    year_column: str = "year",
    output_column: str = "mapbiomas_native_vegetation_loss_ha",
) -> pd.DataFrame:
    """
    Calculate annual native vegetation loss.

    The function computes the year-to-year reduction in native vegetation area.

    If native vegetation decreases from 10,000 ha to 9,500 ha, the loss is 500 ha.
    If native vegetation increases, the loss is clipped to zero.

    Parameters
    ----------
    df : pandas.DataFrame
        Municipality-year environmental panel.

    native_vegetation_column : str
        Column containing native vegetation area in hectares.

    group_columns : list of str, optional
        Columns used to identify each geographic unit.
        Default: ["municipality_code"] if available, otherwise ["municipality_name"].

    year_column : str
        Year column.

    output_column : str
        Name of the output native vegetation loss column.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the native vegetation loss column added.
    """
    required_columns = [native_vegetation_column, year_column]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Required column not found: {column}")

    if group_columns is None:
        if "municipality_code" in df.columns:
            group_columns = ["municipality_code"]
        elif "municipality_name" in df.columns:
            group_columns = ["municipality_name"]
        else:
            raise ValueError(
                "No group_columns were provided and neither municipality_code "
                "nor municipality_name exists in the DataFrame."
            )

    for column in group_columns:
        if column not in df.columns:
            raise ValueError(f"Group column not found: {column}")

    result = df.copy()

    result[native_vegetation_column] = pd.to_numeric(
        result[native_vegetation_column],
        errors="coerce",
    ).fillna(0.0)

    result = result.sort_values(group_columns + [year_column]).reset_index(drop=True)

    previous_native_vegetation = result.groupby(group_columns)[
        native_vegetation_column
    ].shift(1)

    result[output_column] = (
        previous_native_vegetation - result[native_vegetation_column]
    ).fillna(0.0).clip(lower=0.0)

    return result


def add_normalized_score_components(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
    suffix: str = "_normalized",
) -> pd.DataFrame:
    """
    Add normalized score components to the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Environmental panel.

    weights : dict, optional
        Dictionary where keys are indicator columns and values are weights.

    suffix : str
        Suffix used for normalized component columns.

    Returns
    -------
    pandas.DataFrame
        DataFrame with normalized component columns.
    """
    if weights is None:
        weights = DEFAULT_SCORE_WEIGHTS

    result = df.copy()

    for column in weights:
        if column not in result.columns:
            raise ValueError(f"Score component column not found: {column}")

        normalized_column = f"{column}{suffix}"
        result[normalized_column] = min_max_normalize(result[column])

    return result


def calculate_environmental_risk_score(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
    score_column: str = "environmental_risk_score",
    class_column: str = "environmental_risk_class",
) -> pd.DataFrame:
    """
    Calculate the environmental screening score.

    Default formula:

        environmental_risk_score =
            0.50 * normalized_inpe_prodes_deforestation_area_ha
          + 0.30 * normalized_mapbiomas_native_vegetation_loss_ha
          + 0.20 * normalized_mapbiomas_agriculture_or_pasture_expansion_ha

    Parameters
    ----------
    df : pandas.DataFrame
        Environmental panel.

    weights : dict, optional
        Dictionary with indicator weights.

    score_column : str
        Name of the output score column.

    class_column : str
        Name of the output class column.

    Returns
    -------
    pandas.DataFrame
        DataFrame with risk score and risk class.
    """
    if weights is None:
        weights = DEFAULT_SCORE_WEIGHTS

    total_weight = sum(weights.values())

    if total_weight <= 0:
        raise ValueError("Total weight must be greater than zero.")

    normalized_weights = {
        column: weight / total_weight for column, weight in weights.items()
    }

    result = add_normalized_score_components(
        df=df,
        weights=normalized_weights,
    )

    result[score_column] = 0.0

    for column, weight in normalized_weights.items():
        normalized_column = f"{column}_normalized"
        result[score_column] += weight * result[normalized_column]

    result[class_column] = result[score_column].apply(classify_environmental_risk)

    return result


def classify_environmental_risk(score: float) -> str:
    """
    Convert a numeric risk score into a risk class.

    Parameters
    ----------
    score : float
        Environmental risk score between 0 and 1.

    Returns
    -------
    str
        Risk class: "Low", "Medium" or "High".
    """
    if pd.isna(score):
        return "Unknown"

    if score <= 0.33:
        return "Low"

    if score <= 0.66:
        return "Medium"

    return "High"


def add_environmental_risk_score_pipeline(
    df: pd.DataFrame,
    group_columns: list[str] | None = None,
    year_column: str = "year",
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Run the complete environmental risk scoring pipeline.

    Steps:
    1. Calculate native vegetation loss.
    2. Calculate agriculture-or-pasture expansion.
    3. Normalize indicators.
    4. Calculate environmental risk score.
    5. Assign risk class.

    Parameters
    ----------
    df : pandas.DataFrame
        Municipality-year environmental panel.

    group_columns : list of str, optional
        Geographic grouping columns.

    year_column : str
        Year column.

    weights : dict, optional
        Score weights.

    Returns
    -------
    pandas.DataFrame
        DataFrame with risk score and risk class.
    """
    result = add_native_vegetation_loss(
        df=df,
        group_columns=group_columns,
        year_column=year_column,
    )

    result = add_agriculture_or_pasture_expansion(
        df=result,
        group_columns=group_columns,
        year_column=year_column,
    )

    result = calculate_environmental_risk_score(
        df=result,
        weights=weights,
    )

    return result


def score_environmental_panel_file(
    input_path: str | Path,
    output_path: str | Path,
    group_columns: list[str] | None = None,
    year_column: str = "year",
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """
    Load a municipality-year panel, calculate the risk score and save it.

    Parameters
    ----------
    input_path : str or Path
        Input Parquet file.

    output_path : str or Path
        Output Parquet file.

    group_columns : list of str, optional
        Geographic grouping columns.

    year_column : str
        Year column.

    weights : dict, optional
        Score weights.

    Returns
    -------
    pandas.DataFrame
        Scored environmental panel.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    df = pd.read_parquet(input_path)

    scored_df = add_environmental_risk_score_pipeline(
        df=df,
        group_columns=group_columns,
        year_column=year_column,
        weights=weights,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    scored_df.to_parquet(output_path, index=False)

    return scored_df
