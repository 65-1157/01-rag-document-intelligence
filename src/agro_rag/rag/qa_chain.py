"""
Question-answering chain for agro_rag.

This module connects:

1. user question;
2. vector store retrieval;
3. context formatting;
4. prompt construction;
5. LLM answer generation.

The first implementation uses OpenAI when an API key is available.

Expected flow:
question -> ChromaDB retrieval -> context -> prompt -> LLM answer
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from openai import OpenAI

from agro_rag.rag.vector_store import (
    DEFAULT_COLLECTION_NAME,
    format_retrieved_context,
    query_vector_store,
)
from agro_rag.rag.embeddings import DEFAULT_EMBEDDING_MODEL
from agro_rag.rag.prompts import (
    build_rag_messages,
    build_risk_summary_messages,
)


DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


@dataclass
class RagAnswer:
    """
    Container for a RAG answer and its supporting evidence.

    Attributes
    ----------
    question : str
        Original user question.

    answer : str
        Final LLM-generated answer.

    retrieved_context : str
        Context string sent to the model.

    retrieved_chunks : pandas.DataFrame
        Retrieved chunks from the vector store.

    metadata : dict
        Extra execution metadata.
    """

    question: str
    answer: str
    retrieved_context: str
    retrieved_chunks: pd.DataFrame
    metadata: dict[str, Any]


def get_openai_client(api_key: str | None = None) -> OpenAI:
    """
    Create an OpenAI client.

    Parameters
    ----------
    api_key : str, optional
        OpenAI API key. If not provided, the function uses the
        OPENAI_API_KEY environment variable.

    Returns
    -------
    OpenAI
        OpenAI client.

    Raises
    ------
    ValueError
        If no API key is available.
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Set OPENAI_API_KEY in your environment "
            "or pass api_key explicitly."
        )

    return OpenAI(api_key=api_key)


def call_openai_chat_model(
    messages: list[dict[str, str]],
    model_name: str = DEFAULT_OPENAI_MODEL,
    temperature: float = 0.0,
    api_key: str | None = None,
) -> str:
    """
    Call an OpenAI chat model.

    Parameters
    ----------
    messages : list of dict
        Chat messages with roles and content.

    model_name : str
        OpenAI chat model name.

    temperature : float
        Sampling temperature. Use 0.0 for more deterministic answers.

    api_key : str, optional
        OpenAI API key.

    Returns
    -------
    str
        Model answer.
    """
    client = get_openai_client(api_key=api_key)

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
    )

    return response.choices[0].message.content or ""


def answer_question(
    question: str,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
    llm_model_name: str = DEFAULT_OPENAI_MODEL,
    n_results: int = 5,
    where: dict | None = None,
    temperature: float = 0.0,
    api_key: str | None = None,
) -> RagAnswer:
    """
    Answer a user question using the RAG pipeline.

    Parameters
    ----------
    question : str
        User question.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    embedding_model_name : str
        SentenceTransformers model used to embed the query.

    llm_model_name : str
        LLM model name.

    n_results : int
        Number of chunks to retrieve.

    where : dict, optional
        ChromaDB metadata filter.

        Example:
        {"source": "MapBiomas"}

    temperature : float
        LLM temperature.

    api_key : str, optional
        OpenAI API key.

    Returns
    -------
    RagAnswer
        Answer object containing final answer and retrieved evidence.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    retrieved_df = query_vector_store(
        question=question,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=embedding_model_name,
        n_results=n_results,
        where=where,
    )

    context = format_retrieved_context(retrieved_df)

    messages = build_rag_messages(
        question=question,
        context=context,
    )

    answer = call_openai_chat_model(
        messages=messages,
        model_name=llm_model_name,
        temperature=temperature,
        api_key=api_key,
    )

    metadata = {
        "chain_type": "rag_answer",
        "collection_name": collection_name,
        "embedding_model_name": embedding_model_name,
        "llm_model_name": llm_model_name,
        "n_results": n_results,
        "where": where,
    }

    return RagAnswer(
        question=question,
        answer=answer,
        retrieved_context=context,
        retrieved_chunks=retrieved_df,
        metadata=metadata,
    )


def answer_risk_summary(
    question: str,
    structured_evidence: str,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
    llm_model_name: str = DEFAULT_OPENAI_MODEL,
    n_results: int = 5,
    where: dict | None = None,
    temperature: float = 0.0,
    api_key: str | None = None,
) -> RagAnswer:
    """
    Create an environmental risk summary using structured and retrieved evidence.

    Parameters
    ----------
    question : str
        User request.

    structured_evidence : str
        Structured municipality-year evidence formatted as text.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    embedding_model_name : str
        SentenceTransformers model used to embed the query.

    llm_model_name : str
        LLM model name.

    n_results : int
        Number of chunks to retrieve.

    where : dict, optional
        ChromaDB metadata filter.

    temperature : float
        LLM temperature.

    api_key : str, optional
        OpenAI API key.

    Returns
    -------
    RagAnswer
        Answer object containing final answer and retrieved evidence.
    """
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not structured_evidence.strip():
        raise ValueError("Structured evidence cannot be empty.")

    retrieved_df = query_vector_store(
        question=question,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=embedding_model_name,
        n_results=n_results,
        where=where,
    )

    context = format_retrieved_context(retrieved_df)

    messages = build_risk_summary_messages(
        question=question,
        structured_evidence=structured_evidence,
        context=context,
    )

    answer = call_openai_chat_model(
        messages=messages,
        model_name=llm_model_name,
        temperature=temperature,
        api_key=api_key,
    )

    metadata = {
        "chain_type": "risk_summary",
        "collection_name": collection_name,
        "embedding_model_name": embedding_model_name,
        "llm_model_name": llm_model_name,
        "n_results": n_results,
        "where": where,
    }

    return RagAnswer(
        question=question,
        answer=answer,
        retrieved_context=context,
        retrieved_chunks=retrieved_df,
        metadata=metadata,
    )


def answer_question_without_llm(
    question: str,
    persist_directory: str | Path = "chroma_db",
    collection_name: str = DEFAULT_COLLECTION_NAME,
    embedding_model_name: str = DEFAULT_EMBEDDING_MODEL,
    n_results: int = 5,
    where: dict | None = None,
) -> RagAnswer:
    """
    Run only the retrieval part of the RAG pipeline.

    This is useful for testing the vector store before using an LLM.

    Parameters
    ----------
    question : str
        User question.

    persist_directory : str or Path
        ChromaDB directory.

    collection_name : str
        ChromaDB collection name.

    embedding_model_name : str
        SentenceTransformers model used to embed the query.

    n_results : int
        Number of chunks to retrieve.

    where : dict, optional
        ChromaDB metadata filter.

    Returns
    -------
    RagAnswer
        Object containing retrieved context but no generated LLM answer.
    """
    retrieved_df = query_vector_store(
        question=question,
        persist_directory=persist_directory,
        collection_name=collection_name,
        model_name=embedding_model_name,
        n_results=n_results,
        where=where,
    )

    context = format_retrieved_context(retrieved_df)

    metadata = {
        "chain_type": "retrieval_only",
        "collection_name": collection_name,
        "embedding_model_name": embedding_model_name,
        "n_results": n_results,
        "where": where,
    }

    return RagAnswer(
        question=question,
        answer="LLM generation was not executed. Retrieval-only mode was used.",
        retrieved_context=context,
        retrieved_chunks=retrieved_df,
        metadata=metadata,
    )


def rag_answer_to_dict(rag_answer: RagAnswer) -> dict[str, Any]:
    """
    Convert a RagAnswer object to a dictionary.

    Parameters
    ----------
    rag_answer : RagAnswer
        RAG answer object.

    Returns
    -------
    dict
        Dictionary representation.
    """
    return {
        "question": rag_answer.question,
        "answer": rag_answer.answer,
        "retrieved_context": rag_answer.retrieved_context,
        "retrieved_chunks": rag_answer.retrieved_chunks.to_dict(orient="records"),
        "metadata": rag_answer.metadata,
    }
