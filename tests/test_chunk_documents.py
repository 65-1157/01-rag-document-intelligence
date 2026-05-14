import pandas as pd
import pytest

from agro_rag.processing.chunk_documents import (
    build_chunk_id,
    chunk_pages_dataframe,
    split_text_by_words,
)


def test_split_text_by_words_creates_single_chunk_for_short_text():
    text = "This is a short text about MapBiomas and INPE."

    chunks = split_text_by_words(
        text=text,
        chunk_size=50,
        chunk_overlap=10,
    )

    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_text_by_words_creates_multiple_chunks_for_long_text():
    text = " ".join([f"word{i}" for i in range(100)])

    chunks = split_text_by_words(
        text=text,
        chunk_size=30,
        chunk_overlap=5,
    )

    assert len(chunks) > 1
    assert all(len(chunk.split()) <= 30 for chunk in chunks)


def test_split_text_by_words_rejects_invalid_overlap():
    text = "one two three four five"

    with pytest.raises(ValueError):
        split_text_by_words(
            text=text,
            chunk_size=10,
            chunk_overlap=10,
        )


def test_build_chunk_id_returns_stable_identifier():
    chunk_id = build_chunk_id(
        source="MapBiomas",
        document_name="Annual Report 2024",
        page_number=3,
        chunk_index=2,
    )

    assert chunk_id == "mapbiomas__annual_report_2024__p0003__c002"


def test_chunk_pages_dataframe_outputs_expected_columns():
    pages_df = pd.DataFrame(
        {
            "source": ["MapBiomas"],
            "document_name": ["test_document"],
            "file_path": ["synthetic"],
            "page_number": [1],
            "year": [2024],
            "theme": ["land use"],
            "language": ["en"],
            "clean_text": [
                "MapBiomas provides land use and land cover information. "
                "INPE provides deforestation monitoring evidence. "
                "These sources support environmental screening."
            ],
        }
    )

    chunks_df = chunk_pages_dataframe(
        pages_df=pages_df,
        text_column="clean_text",
        chunk_size=10,
        chunk_overlap=2,
    )

    expected_columns = [
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

    for column in expected_columns:
        assert column in chunks_df.columns

    assert len(chunks_df) >= 1
    assert chunks_df["source"].iloc[0] == "MapBiomas"
    assert chunks_df["document_name"].iloc[0] == "test_document"
