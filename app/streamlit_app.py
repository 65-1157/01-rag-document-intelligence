"""
Streamlit app for the agro_rag project.

This app provides a simple interface for asking questions about Brazilian
deforestation and land-use monitoring using MapBiomas and INPE evidence.

Main features:
- ask a question;
- retrieve relevant document chunks;
- generate a RAG answer when OpenAI API key is available;
- run retrieval-only mode;
- inspect retrieved evidence and metadata.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------
# Make src/ importable when running the app from the project root.
# ---------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from agro_rag.rag.qa_chain import answer_question, answer_question_without_llm
from agro_rag.rag.vector_store import DEFAULT_COLLECTION_NAME


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Agro-Environmental RAG Assistant",
    page_icon="🌎",
    layout="wide",
)


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def check_chroma_exists(persist_directory: str | Path) -> bool:
    """
    Check whether the ChromaDB directory exists.

    Parameters
    ----------
    persist_directory : str or Path
        ChromaDB directory.

    Returns
    -------
    bool
        True if directory exists and contains files.
    """
    persist_directory = Path(persist_directory)

    return persist_directory.exists() and any(persist_directory.iterdir())


def show_retrieved_chunks(retrieved_df: pd.DataFrame) -> None:
    """
    Display retrieved chunks in the Streamlit app.

    Parameters
    ----------
    retrieved_df : pandas.DataFrame
        Retrieved chunks returned by the RAG pipeline.
    """
    if retrieved_df.empty:
        st.warning("No retrieved chunks were returned.")
        return

    display_columns = [
        "rank",
        "source",
        "document_name",
        "page_number",
        "year",
        "theme",
        "distance",
    ]

    available_columns = [
        column for column in display_columns if column in retrieved_df.columns
    ]

    st.subheader("Retrieved Evidence Summary")
    st.dataframe(
        retrieved_df[available_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Retrieved Text Chunks")

    for _, row in retrieved_df.iterrows():
        rank = row.get("rank", "")
        source = row.get("source", "Unknown source")
        document_name = row.get("document_name", "Unknown document")
        page_number = row.get("page_number", "Unknown page")
        year = row.get("year", "Unknown year")
        theme = row.get("theme", "Unknown theme")
        distance = row.get("distance", None)
        chunk_text = row.get("chunk_text", "")

        title = (
            f"Rank {rank} | {source} | {document_name} | "
            f"Page {page_number} | Year {year}"
        )

        with st.expander(title):
            st.markdown(f"**Theme:** {theme}")

            if distance is not None:
                st.markdown(f"**Distance:** `{distance}`")

            st.markdown("**Chunk text:**")
            st.write(chunk_text)


def get_source_filter(selected_source: str) -> dict | None:
    """
    Convert selected source into ChromaDB metadata filter.

    Parameters
    ----------
    selected_source : str
        Selected source from the sidebar.

    Returns
    -------
    dict or None
        ChromaDB filter.
    """
    if selected_source == "All sources":
        return None

    return {"source": selected_source}


# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
st.sidebar.title("Settings")

persist_directory = st.sidebar.text_input(
    "ChromaDB directory",
    value="chroma_db",
)

collection_name = st.sidebar.text_input(
    "Collection name",
    value=DEFAULT_COLLECTION_NAME,
)

n_results = st.sidebar.slider(
    "Number of retrieved chunks",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
)

selected_source = st.sidebar.selectbox(
    "Source filter",
    options=[
        "All sources",
        "MapBiomas",
        "INPE",
    ],
)

retrieval_only = st.sidebar.checkbox(
    "Retrieval-only mode",
    value=False,
    help="Use this when you want to test retrieval without calling the LLM.",
)

llm_model_name = st.sidebar.text_input(
    "LLM model",
    value="gpt-4o-mini",
)

temperature = st.sidebar.slider(
    "Temperature",
    min_value=0.0,
    max_value=1.0,
    value=0.0,
    step=0.1,
)

api_key_available = bool(os.getenv("OPENAI_API_KEY"))

if api_key_available:
    st.sidebar.success("OPENAI_API_KEY detected.")
else:
    st.sidebar.warning(
        "OPENAI_API_KEY not detected. Use retrieval-only mode or configure your API key."
    )


# ---------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------
st.title("🌎 Agro-Environmental RAG Assistant")

st.markdown(
    """
This app answers questions using retrieved evidence from **MapBiomas** and
**INPE / TerraBrasilis** documents.

The system is designed for environmental screening and evidence organization.
It should not be used as a legal compliance or enforcement tool.
"""
)

st.info(
    "Before using this app, make sure the ChromaDB vector store has already "
    "been built from `data/processed/document_chunks.parquet`."
)


# ---------------------------------------------------------------------
# Status check
# ---------------------------------------------------------------------
with st.expander("Project Status Check", expanded=False):
    chroma_ok = check_chroma_exists(persist_directory)

    if chroma_ok:
        st.success(f"ChromaDB directory found: `{persist_directory}`")
    else:
        st.error(
            f"ChromaDB directory not found or empty: `{persist_directory}`. "
            "Build the vector store before running retrieval."
        )

    st.markdown("Expected preparation flow:")

    st.code(
        """
from agro_rag.rag.vector_store import build_vector_store_from_chunks

build_vector_store_from_chunks(
    chunks_path="data/processed/document_chunks.parquet",
    persist_directory="chroma_db",
    collection_name="agro_environmental_documents",
)
""",
        language="python",
    )


# ---------------------------------------------------------------------
# Question input
# ---------------------------------------------------------------------
example_questions = [
    "What does INPE / PRODES indicate about annual deforestation monitoring?",
    "What does MapBiomas indicate about land use and land cover?",
    "How can MapBiomas and INPE evidence complement each other?",
    "What limitations should be considered when using municipality-year environmental indicators?",
    "Can this system prove illegal deforestation?",
]

selected_example = st.selectbox(
    "Choose an example question or write your own below",
    options=[""] + example_questions,
)

question = st.text_area(
    "Question",
    value=selected_example,
    height=120,
    placeholder="Ask a question about MapBiomas, INPE, deforestation, land use, or environmental screening...",
)

run_button = st.button("Run RAG Query", type="primary")


# ---------------------------------------------------------------------
# Run query
# ---------------------------------------------------------------------
if run_button:
    if not question.strip():
        st.error("Please enter a question.")
        st.stop()

    where_filter = get_source_filter(selected_source)

    if not check_chroma_exists(persist_directory):
        st.error(
            "ChromaDB directory was not found or is empty. "
            "Build the vector store before querying."
        )
        st.stop()

    if not retrieval_only and not api_key_available:
        st.warning(
            "OPENAI_API_KEY is not available. Switching to retrieval-only mode."
        )
        retrieval_only = True

    with st.spinner("Running retrieval..."):
        try:
            if retrieval_only:
                result = answer_question_without_llm(
                    question=question,
                    persist_directory=persist_directory,
                    collection_name=collection_name,
                    n_results=n_results,
                    where=where_filter,
                )
            else:
                result = answer_question(
                    question=question,
                    persist_directory=persist_directory,
                    collection_name=collection_name,
                    llm_model_name=llm_model_name,
                    n_results=n_results,
                    where=where_filter,
                    temperature=temperature,
                )

        except Exception as error:
            st.error("An error occurred while running the RAG query.")
            st.exception(error)
            st.stop()

    st.success("Query completed.")

    st.subheader("Answer")
    st.markdown(result.answer)

    st.divider()

    show_retrieved_chunks(result.retrieved_chunks)

    with st.expander("Raw Retrieved Context"):
        st.text(result.retrieved_context)

    with st.expander("Execution Metadata"):
        st.json(result.metadata)


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------
st.divider()

st.markdown(
    """
**Important limitation:** this app provides evidence-based environmental
screening support. It does not determine illegal deforestation, legal
responsibility, rural property compliance, or final ESG certification.
"""
)
