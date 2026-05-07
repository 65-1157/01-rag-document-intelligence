"""
Prompt utilities for agro_rag.

This module loads prompt templates from the prompts/ folder and formats them
with user questions, retrieved document context and structured evidence.

Expected prompt files:
- prompts/system_prompt.md
- prompts/rag_answer_prompt.md
- prompts/risk_summary_prompt.md
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agro_rag.utils.paths import PROMPTS_DIR
from agro_rag.utils.io import read_text_file


DEFAULT_SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt.md"
DEFAULT_RAG_ANSWER_PROMPT_PATH = PROMPTS_DIR / "rag_answer_prompt.md"
DEFAULT_RISK_SUMMARY_PROMPT_PATH = PROMPTS_DIR / "risk_summary_prompt.md"


def load_prompt_template(prompt_path: str | Path) -> str:
    """
    Load a prompt template from a Markdown file.

    Parameters
    ----------
    prompt_path : str or Path
        Path to the prompt template.

    Returns
    -------
    str
        Prompt template content.
    """
    prompt_path = Path(prompt_path)

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

    return read_text_file(prompt_path)


def format_template(template: str, **kwargs: Any) -> str:
    """
    Format a prompt template using Python string formatting.

    Parameters
    ----------
    template : str
        Prompt template containing placeholders such as {question}.

    **kwargs
        Values used to replace placeholders.

    Returns
    -------
    str
        Formatted prompt.
    """
    try:
        return template.format(**kwargs)
    except KeyError as error:
        missing_key = error.args[0]
        raise KeyError(
            f"Missing value for prompt placeholder: {missing_key}"
        ) from error


def load_system_prompt(
    prompt_path: str | Path = DEFAULT_SYSTEM_PROMPT_PATH,
) -> str:
    """
    Load the system prompt.

    Parameters
    ----------
    prompt_path : str or Path
        Path to system_prompt.md.

    Returns
    -------
    str
        System prompt content.
    """
    return load_prompt_template(prompt_path)


def build_rag_answer_prompt(
    question: str,
    context: str,
    prompt_path: str | Path = DEFAULT_RAG_ANSWER_PROMPT_PATH,
) -> str:
    """
    Build the RAG answer prompt.

    Parameters
    ----------
    question : str
        User question.

    context : str
        Retrieved context formatted as text.

    prompt_path : str or Path
        Path to rag_answer_prompt.md.

    Returns
    -------
    str
        Formatted RAG prompt.
    """
    template = load_prompt_template(prompt_path)

    return format_template(
        template,
        question=question,
        context=context,
    )


def build_risk_summary_prompt(
    question: str,
    structured_evidence: str,
    context: str,
    prompt_path: str | Path = DEFAULT_RISK_SUMMARY_PROMPT_PATH,
) -> str:
    """
    Build the environmental risk summary prompt.

    Parameters
    ----------
    question : str
        User request.

    structured_evidence : str
        Structured evidence, usually from the municipality-year panel.

    context : str
        Retrieved document evidence.

    prompt_path : str or Path
        Path to risk_summary_prompt.md.

    Returns
    -------
    str
        Formatted risk summary prompt.
    """
    template = load_prompt_template(prompt_path)

    return format_template(
        template,
        question=question,
        structured_evidence=structured_evidence,
        context=context,
    )


def build_messages_for_chat_model(
    system_prompt: str,
    user_prompt: str,
) -> list[dict[str, str]]:
    """
    Build a chat-style message list.

    This format can be used with chat-based LLM APIs.

    Parameters
    ----------
    system_prompt : str
        System-level instructions.

    user_prompt : str
        User-level prompt containing question and context.

    Returns
    -------
    list[dict[str, str]]
        Chat messages.
    """
    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]


def build_rag_messages(
    question: str,
    context: str,
    system_prompt_path: str | Path = DEFAULT_SYSTEM_PROMPT_PATH,
    rag_prompt_path: str | Path = DEFAULT_RAG_ANSWER_PROMPT_PATH,
) -> list[dict[str, str]]:
    """
    Build chat messages for a standard RAG answer.

    Parameters
    ----------
    question : str
        User question.

    context : str
        Retrieved context.

    system_prompt_path : str or Path
        Path to system prompt.

    rag_prompt_path : str or Path
        Path to RAG answer prompt.

    Returns
    -------
    list[dict[str, str]]
        Chat messages.
    """
    system_prompt = load_system_prompt(system_prompt_path)
    user_prompt = build_rag_answer_prompt(
        question=question,
        context=context,
        prompt_path=rag_prompt_path,
    )

    return build_messages_for_chat_model(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )


def build_risk_summary_messages(
    question: str,
    structured_evidence: str,
    context: str,
    system_prompt_path: str | Path = DEFAULT_SYSTEM_PROMPT_PATH,
    risk_prompt_path: str | Path = DEFAULT_RISK_SUMMARY_PROMPT_PATH,
) -> list[dict[str, str]]:
    """
    Build chat messages for an environmental risk summary.

    Parameters
    ----------
    question : str
        User request.

    structured_evidence : str
        Structured municipality-year evidence.

    context : str
        Retrieved document context.

    system_prompt_path : str or Path
        Path to system prompt.

    risk_prompt_path : str or Path
        Path to risk summary prompt.

    Returns
    -------
    list[dict[str, str]]
        Chat messages.
    """
    system_prompt = load_system_prompt(system_prompt_path)
    user_prompt = build_risk_summary_prompt(
        question=question,
        structured_evidence=structured_evidence,
        context=context,
        prompt_path=risk_prompt_path,
    )

    return build_messages_for_chat_model(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )
