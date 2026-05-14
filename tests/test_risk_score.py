import pandas as pd

from agro_rag.structured.risk_score import (
    add_environmental_risk_score_pipeline,
    classify_environmental_risk,
    min_max_normalize,
)


def test_min_max_normalize_returns_values_between_zero_and_one():
    series = pd.Series([10, 20, 30])

    normalized = min_max_normalize(series)

    assert normalized.min() == 0.0
    assert normalized.max() == 1.0
    assert normalized.between(0, 1).all()


def test_min_max_normalize_constant_series_returns_zero():
    series = pd.Series([5, 5, 5])

    normalized = min_max_normalize(series)

    assert (normalized == 0.0).all()


def test_classify_environmental_risk():
    assert classify_environmental_risk(0.10) == "Low"
    assert classify_environmental_risk(0.50) == "Medium"
    assert classify_environmental_risk(0.90) == "High"


def test_environmental_risk_score_pipeline_outputs_expected_columns():
    df = pd.DataFrame(
        {
            "municipality_code": ["001", "001", "001", "002", "002", "002"],
            "municipality_name": ["A", "A", "A", "B", "B", "B"],
            "state": ["MT", "MT", "MT", "PA", "PA", "PA"],
            "biome": ["Amazon", "Amazon", "Amazon", "Amazon", "Amazon", "Amazon"],
            "year": [2022, 2023, 2024, 2022, 2023, 2024],
            "mapbiomas_native_vegetation_area_ha": [
                1000,
                950,
                900,
                2000,
                1980,
                1950,
            ],
            "mapbiomas_agriculture_area_ha": [
                100,
                120,
                140,
                200,
                210,
                230,
            ],
            "mapbiomas_pasture_area_ha": [
                300,
                320,
                350,
                400,
                420,
                450,
            ],
            "inpe_prodes_deforestation_area_ha": [
                10,
                20,
                30,
                5,
                15,
                25,
            ],
        }
    )

    scored_df = add_environmental_risk_score_pipeline(
        df=df,
        group_columns=["municipality_code"],
        year_column="year",
    )

    expected_columns = [
        "mapbiomas_native_vegetation_loss_ha",
        "mapbiomas_agriculture_or_pasture_expansion_ha",
        "inpe_prodes_deforestation_area_ha_normalized",
        "mapbiomas_native_vegetation_loss_ha_normalized",
        "mapbiomas_agriculture_or_pasture_expansion_ha_normalized",
        "environmental_risk_score",
        "environmental_risk_class",
    ]

    for column in expected_columns:
        assert column in scored_df.columns

    assert scored_df["environmental_risk_score"].between(0, 1).all()

    valid_classes = {"Low", "Medium", "High", "Unknown"}
    assert set(scored_df["environmental_risk_class"]).issubset(valid_classes)
