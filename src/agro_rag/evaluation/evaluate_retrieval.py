"""
Retrieval evaluation utilities for agro_rag.

This module evaluates whether the RAG retriever returns relevant evidence
for a set of golden questions.

Expected input:
- data/processed/rag_eval_questions.csv
- ChromaDB vector store built from document chunks

Expected output:
- reports/rag_retrieval_evaluation.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from agro_rag.evaluation.golden_questions import load_golden_questions
from agro_rag.rag.vector_store import query_vector_store


def normalize_text(value: object) -> str:
    """
    Normalize text for simple matching.

    Parameters
    ----------
    value : object
        Input value.

    Returns
    -------
    str
        Lowercase normalized string.
    """
    if value is None or pd.isna(value):
        return ""

    return str(value).strip().lower()


def split_expected_sources(expected_source: object) -> list[str]:
    """
    Split the expected_source field into a list of source names.

    Examples
    --------
    "MapBiomas; INPE" becomes ["mapbiomas", "inpe"].

    Parameters
    ----------
    expected_source : object
        Expected source field.

    Returns
    -------
    list[str]
        Normalized expected source names.
    """
    text = normalize_text(expected_source)

    if not text:
        return []

    return [
        source.strip()
        for source in text.replace(",", ";").split(";")
        if source.strip()
    ]


def source_matches_expected(
    retrieved_source: object,
    expected_sources: list[str],
) -> bool:
    """
    Check whether a retrieved source matches any expected source.

    Parameters
    ----------
    retrieved_source : object
        Retrieved source value.

    expected_sources : list[str]
        Expected source names.

    Returns
    -------
    bool
        True if retrieved source matches expected source.
    """
    retrieved = normalize_text(retrieved_source)

    if not retrieved or not expected_sources:
        return False

    for expected in expected_sources:
        if expected in retrieved or retrieved in expected:
            return True

    return False


def calculate_source_hit(
    retrieved_df: pd.DataFrame,
    expected_source: object,
) -> bool:
    """
    Calculate whether the expected source appears in retrieved results.

    Parameters
    ----------
    retrieved_df : pandas.DataFrame
        Retrieved chunks.

    expected_source : object
        Expected source field from the golden question.

    Returns
    -------
    bool
        True if any retrieved chunk source matches the expected source.
    """
    expected_sources = split_expected_sources(expected_source)

    if retrieved_df.empty:
        return False

    if "source" not in retrieved_df.columns:
        return False

    return any(
        source_matches_expected(source, expected_sources)
        for source in retrieved_df["source"].tolist()
    )


def calculate_precision_at_k(
    retrieved_df: pd.DataFrame,
    expected_source: object,
    k: int = 5,
) -> float:
    """
    Calculate simple source-based Precision@k.

    A retrieved chunk is considered relevant if its source matches one of the
    expected source families.

    Parameters
    ----------
    retrieved_df : pandas.DataFrame
        Retrieved chunks.

    expected_source : object
        Expected source field.

    k : int
        Number of top results considered.

    Returns
    -------
    float
        Precision@k value.
    """
    if retrieved_df.empty:
        return 0.0

    top_k = retrieved_df.head(k)

    if top_k.empty:
        return 0.0

    expected_sources = split_expected_sources(expected_source)

    relevant_count = sum(
        source_matches_expected(source, expected_sources)
        for source in top_k.get("source", pd.Series(dtype=str)).tolist()
    )

    return relevant_count / len(top_k)


def retrieved_sources_to_string(retrieved_df: pd.DataFrame) -> str:
    """
    Convert retrieved sources into a readable string.

    Parameters
    ----------
    retrieved_df : pandas.DataFrame
        Retrieved chunks.

    Returns
    -------
    str
        Semicolon-separated source list.
    """
    if retrieved_df.empty or "source" not in retrieved_df.columns:
        return ""

    sources = [
        str(source)
        for source in retrieved_df["source"].dropna().unique().tolist()
    ]

    return "; ".join(sources)


def retrieved_documents_to_string(retrieved_df: pd.DataFrame) -> str:
    """
    Convert retrieved document names into a readable string.

    Parameters
    ----------
    retrieved_df : pandas.DataFrame
        Retrieved chunks.

    Returns
    -------
    str
        Semicolon-separated document list.
    """
    if retrieved_df.empty or "document_name" not in retrieved_df.columns:
        return ""

    documents = [
        str(document)
        for document in retrieved_df["document_name"].dropna().unique().tolist()
    ]

    return "; ".join(documents)


def evaluate_single_question_retrieval(
    question_row: pd.Series,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = "agro_environmental_documents",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    n_results: int = 5,
) -> dict:
    """
    Evaluate retrieval for one golden question.

    Parameters
    ----------
    question_row : pandas.Series
        One row from the golden question DataFrame.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        Embedding model name.

    n_results : int
        Number of retrieved chunks.

    Returns
    -------
    dict
        Retrieval evaluation record.
    """
    question = question_row["question"]
    expected_source = question_row["expected_source"]

    retrieved_df = query_vector_store(
        question=question,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=model_name,
        n_results=n_results,
    )

    source_hit = calculate_source_hit(
        retrieved_df=retrieved_df,
        expected_source=expected_source,
    )

    precision_at_k = calculate_precision_at_k(
        retrieved_df=retrieved_df,
        expected_source=expected_source,
        k=n_results,
    )

    top_chunk_id = ""
    top_distance = None

    if not retrieved_df.empty:
        top_chunk_id = retrieved_df.iloc[0].get("chunk_id", "")
        top_distance = retrieved_df.iloc[0].get("distance", None)

    return {
        "question_id": question_row["question_id"],
        "question": question,
        "expected_source": expected_source,
        "expected_theme": question_row.get("expected_theme", ""),
        "expected_answer_type": question_row.get("expected_answer_type", ""),
        "unsafe_risk": question_row.get("unsafe_risk", False),
        "n_results": n_results,
        "source_hit_at_k": int(source_hit),
        "recall_at_k": int(source_hit),
        "precision_at_k": precision_at_k,
        "retrieved_sources": retrieved_sources_to_string(retrieved_df),
        "retrieved_documents": retrieved_documents_to_string(retrieved_df),
        "top_chunk_id": top_chunk_id,
        "top_distance": top_distance,
    }


def evaluate_retrieval(
    golden_questions_df: pd.DataFrame,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = "agro_environmental_documents",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    n_results: int = 5,
) -> pd.DataFrame:
    """
    Evaluate retrieval for all golden questions.

    Parameters
    ----------
    golden_questions_df : pandas.DataFrame
        Golden question DataFrame.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        Embedding model name.

    n_results : int
        Number of retrieved chunks.

    Returns
    -------
    pandas.DataFrame
        Retrieval evaluation results.
    """
    records = []

    for _, row in golden_questions_df.iterrows():
        record = evaluate_single_question_retrieval(
            question_row=row,
            persist_directory=persist_directory,
            collection_name=collection_name,
            model_name=model_name,
            n_results=n_results,
        )

        records.append(record)

    return pd.DataFrame(records)


def summarize_retrieval_evaluation(results_df: pd.DataFrame) -> dict:
    """
    Summarize retrieval evaluation results.

    Parameters
    ----------
    results_df : pandas.DataFrame
        Retrieval evaluation results.

    Returns
    -------
    dict
        Summary metrics.
    """
    if results_df.empty:
        return {
            "n_questions": 0,
            "source_hit_rate_at_k": 0.0,
            "mean_precision_at_k": 0.0,
            "mean_recall_at_k": 0.0,
        }

    return {
        "n_questions": int(len(results_df)),
        "source_hit_rate_at_k": float(results_df["source_hit_at_k"].mean()),
        "mean_precision_at_k": float(results_df["precision_at_k"].mean()),
        "mean_recall_at_k": float(results_df["recall_at_k"].mean()),
    }


def evaluate_retrieval_file(
    golden_questions_path: str | Path = "data/processed/rag_eval_questions.csv",
    output_path: str | Path = "reports/rag_retrieval_evaluation.csv",
    persist_directory: str | Path = "chroma_db",
    collection_name: str = "agro_environmental_documents",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    n_results: int = 5,
) -> pd.DataFrame:
    """
    Load golden questions, evaluate retrieval and save results.

    Parameters
    ----------
    golden_questions_path : str or Path
        Path to golden question CSV.

    output_path : str or Path
        Output CSV path.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        Embedding model name.

    n_results : int
        Number of retrieved chunks.

    Returns
    -------
    pandas.DataFrame
        Retrieval evaluation results.
    """
    golden_questions_df = load_golden_questions(golden_questions_path)

    results_df = evaluate_retrieval(
        golden_questions_df=golden_questions_df,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=model_name,
        n_results=n_results,
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)

    summary = summarize_retrieval_evaluation(results_df)

    print("Retrieval evaluation summary")
    print("----------------------------")
    print(f"Questions: {summary['n_questions']}")
    print(f"Source hit rate@{n_results}: {summary['source_hit_rate_at_k']:.3f}")
    print(f"Mean precision@{n_results}: {summary['mean_precision_at_k']:.3f}")
    print(f"Mean recall@{n_results}: {summary['mean_recall_at_k']:.3f}")

    return results_df
