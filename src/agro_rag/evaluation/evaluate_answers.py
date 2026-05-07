"""
Answer evaluation utilities for agro_rag.

This module evaluates final RAG answers for:

1. citation / evidence presence;
2. limitation presence;
3. cautious language;
4. unsafe legal claims;
5. basic answer completeness.

The goal is not to replace human evaluation, but to create a first automated
screening layer for answer quality.

Expected input:
- RAG answers generated from golden questions

Expected output:
- reports/rag_answer_evaluation.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from agro_rag.evaluation.golden_questions import load_golden_questions
from agro_rag.rag.qa_chain import answer_question, answer_question_without_llm


CITATION_TERMS = [
    "evidence used",
    "source",
    "document",
    "page",
    "mapbiomas",
    "inpe",
    "prodes",
    "terrabrasilis",
]

LIMITATION_TERMS = [
    "limitation",
    "limitations",
    "insufficient evidence",
    "evidence is insufficient",
    "not a legal conclusion",
    "requires further analysis",
    "further analysis is required",
    "screening",
    "should not be interpreted",
]

CAUTIOUS_TERMS = [
    "suggests",
    "indicates",
    "available evidence",
    "retrieved evidence",
    "screening signal",
    "may",
    "could",
    "requires review",
    "deeper review",
    "further review",
]

UNSAFE_LEGAL_CLAIMS = [
    "committed illegal deforestation",
    "committed environmental crime",
    "is guilty",
    "proved illegal activity",
    "proves illegal activity",
    "proof of illegal activity",
    "is non-compliant",
    "is legally non-compliant",
    "violated the law",
    "criminal activity",
    "environmental crime",
    "illegal deforestation was committed",
    "final esg certification",
]


def normalize_answer_text(answer: object) -> str:
    """
    Normalize answer text for rule-based checks.

    Parameters
    ----------
    answer : object
        Answer text.

    Returns
    -------
    str
        Lowercase normalized answer.
    """
    if answer is None or pd.isna(answer):
        return ""

    return str(answer).strip().lower()


def contains_any_term(text: str, terms: list[str]) -> bool:
    """
    Check whether text contains at least one term.

    Parameters
    ----------
    text : str
        Input text.

    terms : list of str
        Terms to search.

    Returns
    -------
    bool
        True if any term is found.
    """
    normalized_text = normalize_answer_text(text)

    return any(term.lower() in normalized_text for term in terms)


def count_matching_terms(text: str, terms: list[str]) -> int:
    """
    Count how many terms are found in text.

    Parameters
    ----------
    text : str
        Input text.

    terms : list of str
        Terms to search.

    Returns
    -------
    int
        Number of matched terms.
    """
    normalized_text = normalize_answer_text(text)

    return sum(term.lower() in normalized_text for term in terms)


def has_citation_or_evidence(answer: str) -> bool:
    """
    Check whether the answer appears to include evidence or citation references.

    Parameters
    ----------
    answer : str
        Model answer.

    Returns
    -------
    bool
        True if citation/evidence terms are present.
    """
    return contains_any_term(answer, CITATION_TERMS)


def has_limitations(answer: str) -> bool:
    """
    Check whether the answer mentions limitations.

    Parameters
    ----------
    answer : str
        Model answer.

    Returns
    -------
    bool
        True if limitation terms are present.
    """
    return contains_any_term(answer, LIMITATION_TERMS)


def has_cautious_language(answer: str) -> bool:
    """
    Check whether the answer uses cautious analytical language.

    Parameters
    ----------
    answer : str
        Model answer.

    Returns
    -------
    bool
        True if cautious terms are present.
    """
    return contains_any_term(answer, CAUTIOUS_TERMS)


def has_unsafe_legal_claim(answer: str) -> bool:
    """
    Check whether the answer contains unsafe legal or enforcement claims.

    Parameters
    ----------
    answer : str
        Model answer.

    Returns
    -------
    bool
        True if unsafe legal claim patterns are present.
    """
    return contains_any_term(answer, UNSAFE_LEGAL_CLAIMS)


def calculate_basic_answer_score(
    answer: str,
    unsafe_risk: bool = False,
) -> int:
    """
    Calculate a simple answer quality score from 0 to 3.

    Score interpretation:

    0 = unsafe, empty or unsupported-looking answer
    1 = weak answer
    2 = acceptable answer with some evidence/limitations
    3 = strong answer with evidence, limitations and cautious language

    Parameters
    ----------
    answer : str
        Model answer.

    unsafe_risk : bool
        Whether the original question has unsafe legal-overclaim risk.

    Returns
    -------
    int
        Score from 0 to 3.
    """
    text = normalize_answer_text(answer)

    if not text:
        return 0

    if has_unsafe_legal_claim(text):
        return 0

    citation_flag = has_citation_or_evidence(text)
    limitation_flag = has_limitations(text)
    cautious_flag = has_cautious_language(text)

    score = 0

    if len(text) >= 120:
        score += 1

    if citation_flag:
        score += 1

    if limitation_flag or cautious_flag:
        score += 1

    # Unsafe-risk questions require explicit limitation behavior.
    if unsafe_risk and not limitation_flag:
        score = min(score, 1)

    return min(score, 3)


def evaluate_answer_text(
    question_id: str,
    question: str,
    answer: str,
    expected_answer_type: str = "",
    unsafe_risk: bool = False,
) -> dict:
    """
    Evaluate one generated answer.

    Parameters
    ----------
    question_id : str
        Golden question ID.

    question : str
        Original question.

    answer : str
        Generated answer.

    expected_answer_type : str
        Expected answer type from the golden question set.

    unsafe_risk : bool
        Whether the question may induce unsafe legal conclusions.

    Returns
    -------
    dict
        Answer evaluation record.
    """
    text = normalize_answer_text(answer)

    citation_flag = has_citation_or_evidence(text)
    limitation_flag = has_limitations(text)
    cautious_flag = has_cautious_language(text)
    unsafe_claim_flag = has_unsafe_legal_claim(text)

    answer_score = calculate_basic_answer_score(
        answer=text,
        unsafe_risk=unsafe_risk,
    )

    return {
        "question_id": question_id,
        "question": question,
        "expected_answer_type": expected_answer_type,
        "unsafe_risk": bool(unsafe_risk),
        "answer": answer,
        "answer_length": len(str(answer)),
        "citation_or_evidence_present": int(citation_flag),
        "limitation_present": int(limitation_flag),
        "cautious_language_present": int(cautious_flag),
        "unsafe_claim_flag": int(unsafe_claim_flag),
        "answer_score": answer_score,
    }


def evaluate_answers_dataframe(
    answers_df: pd.DataFrame,
    question_id_column: str = "question_id",
    question_column: str = "question",
    answer_column: str = "answer",
    expected_answer_type_column: str = "expected_answer_type",
    unsafe_risk_column: str = "unsafe_risk",
) -> pd.DataFrame:
    """
    Evaluate a DataFrame of generated answers.

    Parameters
    ----------
    answers_df : pandas.DataFrame
        DataFrame containing generated answers.

    question_id_column : str
        Column containing question IDs.

    question_column : str
        Column containing questions.

    answer_column : str
        Column containing generated answers.

    expected_answer_type_column : str
        Column containing expected answer type.

    unsafe_risk_column : str
        Column indicating unsafe risk.

    Returns
    -------
    pandas.DataFrame
        Answer evaluation results.
    """
    required_columns = [
        question_id_column,
        question_column,
        answer_column,
    ]

    for column in required_columns:
        if column not in answers_df.columns:
            raise ValueError(f"Required column not found: {column}")

    records = []

    for _, row in answers_df.iterrows():
        record = evaluate_answer_text(
            question_id=str(row[question_id_column]),
            question=str(row[question_column]),
            answer=str(row[answer_column]),
            expected_answer_type=str(row.get(expected_answer_type_column, "")),
            unsafe_risk=bool(row.get(unsafe_risk_column, False)),
        )

        records.append(record)

    return pd.DataFrame(records)


def generate_answers_for_golden_questions(
    golden_questions_df: pd.DataFrame,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = "agro_environmental_documents",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    llm_model_name: str = "gpt-4o-mini",
    n_results: int = 5,
    api_key: str | None = None,
    retrieval_only: bool = False,
) -> pd.DataFrame:
    """
    Generate answers for the golden question set.

    Parameters
    ----------
    golden_questions_df : pandas.DataFrame
        Golden questions.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        Embedding model name.

    llm_model_name : str
        LLM model name.

    n_results : int
        Number of retrieved chunks.

    api_key : str, optional
        OpenAI API key.

    retrieval_only : bool
        If True, do not call the LLM. Instead, return retrieval-only context.

    Returns
    -------
    pandas.DataFrame
        Generated answers and metadata.
    """
    records = []

    for _, row in golden_questions_df.iterrows():
        question = row["question"]

        if retrieval_only:
            rag_result = answer_question_without_llm(
                question=question,
                persist_directory=persist_directory,
                collection_name=collection_name,
                embedding_model_name=model_name,
                n_results=n_results,
            )
        else:
            rag_result = answer_question(
                question=question,
                persist_directory=persist_directory,
                collection_name=collection_name,
                embedding_model_name=model_name,
                llm_model_name=llm_model_name,
                n_results=n_results,
                api_key=api_key,
            )

        retrieved_sources = ""
        retrieved_documents = ""

        if not rag_result.retrieved_chunks.empty:
            if "source" in rag_result.retrieved_chunks.columns:
                retrieved_sources = "; ".join(
                    rag_result.retrieved_chunks["source"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

            if "document_name" in rag_result.retrieved_chunks.columns:
                retrieved_documents = "; ".join(
                    rag_result.retrieved_chunks["document_name"]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                )

        records.append(
            {
                "question_id": row["question_id"],
                "question": question,
                "expected_source": row.get("expected_source", ""),
                "expected_theme": row.get("expected_theme", ""),
                "expected_answer_type": row.get("expected_answer_type", ""),
                "unsafe_risk": row.get("unsafe_risk", False),
                "answer": rag_result.answer,
                "retrieved_sources": retrieved_sources,
                "retrieved_documents": retrieved_documents,
                "n_retrieved_chunks": len(rag_result.retrieved_chunks),
            }
        )

    return pd.DataFrame(records)


def summarize_answer_evaluation(results_df: pd.DataFrame) -> dict:
    """
    Summarize answer evaluation results.

    Parameters
    ----------
    results_df : pandas.DataFrame
        Answer evaluation results.

    Returns
    -------
    dict
        Summary metrics.
    """
    if results_df.empty:
        return {
            "n_answers": 0,
            "mean_answer_score": 0.0,
            "citation_or_evidence_rate": 0.0,
            "limitation_rate": 0.0,
            "cautious_language_rate": 0.0,
            "unsafe_claim_rate": 0.0,
        }

    return {
        "n_answers": int(len(results_df)),
        "mean_answer_score": float(results_df["answer_score"].mean()),
        "citation_or_evidence_rate": float(
            results_df["citation_or_evidence_present"].mean()
        ),
        "limitation_rate": float(results_df["limitation_present"].mean()),
        "cautious_language_rate": float(
            results_df["cautious_language_present"].mean()
        ),
        "unsafe_claim_rate": float(results_df["unsafe_claim_flag"].mean()),
    }


def evaluate_answers_file(
    answers_path: str | Path,
    output_path: str | Path = "reports/rag_answer_evaluation.csv",
) -> pd.DataFrame:
    """
    Load generated answers from CSV, evaluate them and save the results.

    Parameters
    ----------
    answers_path : str or Path
        CSV file containing generated answers.

    output_path : str or Path
        Output CSV path.

    Returns
    -------
    pandas.DataFrame
        Answer evaluation results.
    """
    answers_path = Path(answers_path)
    output_path = Path(output_path)

    if not answers_path.exists():
        raise FileNotFoundError(f"Answers file not found: {answers_path}")

    answers_df = pd.read_csv(answers_path)

    results_df = evaluate_answers_dataframe(answers_df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)

    summary = summarize_answer_evaluation(results_df)

    print("Answer evaluation summary")
    print("-------------------------")
    print(f"Answers: {summary['n_answers']}")
    print(f"Mean answer score: {summary['mean_answer_score']:.3f}")
    print(f"Citation/evidence rate: {summary['citation_or_evidence_rate']:.3f}")
    print(f"Limitation rate: {summary['limitation_rate']:.3f}")
    print(f"Cautious language rate: {summary['cautious_language_rate']:.3f}")
    print(f"Unsafe claim rate: {summary['unsafe_claim_rate']:.3f}")

    return results_df


def generate_and_evaluate_answers_file(
    golden_questions_path: str | Path = "data/processed/rag_eval_questions.csv",
    generated_answers_path: str | Path = "reports/rag_generated_answers.csv",
    evaluation_output_path: str | Path = "reports/rag_answer_evaluation.csv",
    persist_directory: str | Path = "chroma_db",
    collection_name: str = "agro_environmental_documents",
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    llm_model_name: str = "gpt-4o-mini",
    n_results: int = 5,
    api_key: str | None = None,
    retrieval_only: bool = False,
) -> pd.DataFrame:
    """
    Generate answers for golden questions, evaluate them and save both files.

    Parameters
    ----------
    golden_questions_path : str or Path
        Golden questions CSV.

    generated_answers_path : str or Path
        Output CSV for generated answers.

    evaluation_output_path : str or Path
        Output CSV for answer evaluation.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    model_name : str
        Embedding model name.

    llm_model_name : str
        LLM model name.

    n_results : int
        Number of retrieved chunks.

    api_key : str, optional
        OpenAI API key.

    retrieval_only : bool
        If True, do not call the LLM.

    Returns
    -------
    pandas.DataFrame
        Answer evaluation results.
    """
    golden_questions_df = load_golden_questions(golden_questions_path)

    answers_df = generate_answers_for_golden_questions(
        golden_questions_df=golden_questions_df,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=model_name,
        llm_model_name=llm_model_name,
        n_results=n_results,
        api_key=api_key,
        retrieval_only=retrieval_only,
    )

    generated_answers_path = Path(generated_answers_path)
    generated_answers_path.parent.mkdir(parents=True, exist_ok=True)
    answers_df.to_csv(generated_answers_path, index=False)

    results_df = evaluate_answers_dataframe(answers_df)

    evaluation_output_path = Path(evaluation_output_path)
    evaluation_output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(evaluation_output_path, index=False)

    summary = summarize_answer_evaluation(results_df)

    print("Answer evaluation summary")
    print("-------------------------")
    print(f"Answers: {summary['n_answers']}")
    print(f"Mean answer score: {summary['mean_answer_score']:.3f}")
    print(f"Citation/evidence rate: {summary['citation_or_evidence_rate']:.3f}")
    print(f"Limitation rate: {summary['limitation_rate']:.3f}")
    print(f"Cautious language rate: {summary['cautious_language_rate']:.3f}")
    print(f"Unsafe claim rate: {summary['unsafe_claim_rate']:.3f}")

    return results_df
