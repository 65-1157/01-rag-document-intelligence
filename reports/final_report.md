# Final Report

# RAG Document Intelligence for Brazilian Deforestation and Land-Use Monitoring

## 1. Executive Summary

This project implements a Retrieval-Augmented Generation system for Brazilian agro-environmental document intelligence.

The system focuses on two source families:

1. **MapBiomas**
2. **INPE / TerraBrasilis**

The project combines:

- document parsing;
- text cleaning;
- document chunking;
- semantic retrieval;
- prompt-based answer generation;
- structured municipality-year indicators;
- an explainable environmental screening score;
- retrieval and answer evaluation;
- a Streamlit interface.

The purpose is to support analysts in organizing evidence and answering questions about deforestation, land use, native vegetation loss, agriculture expansion and pasture expansion.

The system is not designed to determine illegal deforestation, legal responsibility, rural property compliance or final ESG classification.

The safest interpretation is:

> This project provides evidence-based environmental screening support that requires human review before any operational, legal, financial or public use.

---

## 2. Problem Statement

Brazil has extensive public information related to deforestation, land use and native vegetation change. However, this information is distributed across multiple formats and platforms, including:

- PDF reports;
- technical documents;
- structured tables;
- dashboards;
- geospatial platforms;
- methodology notes.

This fragmentation creates a practical challenge for analysts.

Typical questions include:

- What does INPE / PRODES indicate about annual deforestation monitoring?
- What does MapBiomas indicate about land use and land cover?
- How can MapBiomas and INPE evidence complement each other?
- Which municipality-year records deserve deeper environmental review?
- What limitations should be considered before interpreting environmental risk?

This project addresses this problem by creating a RAG-based workflow that retrieves relevant evidence and supports structured environmental screening.

---

## 3. Project Objectives

The main objectives are:

1. Build a document intelligence pipeline for MapBiomas and INPE-related documents.
2. Extract and clean text from PDF documents.
3. Split documents into retrieval-ready chunks.
4. Build a ChromaDB vector store for semantic retrieval.
5. Retrieve evidence for user questions.
6. Generate evidence-based answers when an LLM is available.
7. Support retrieval-only mode when no LLM API key is configured.
8. Build a municipality-year environmental panel.
9. Calculate an explainable environmental screening score.
10. Evaluate retrieval and answer behavior using golden questions.
11. Provide a Streamlit interface for interaction.
12. Document limitations and safe interpretation principles.

---

## 4. Data Sources

The first version intentionally uses only two source families.

| Source | Role in the Project |
|---|---|
| MapBiomas | Land use, land cover, native vegetation, agriculture and pasture indicators |
| INPE / TerraBrasilis | Official deforestation monitoring evidence, especially PRODES |

The reduced scope improves:

- reproducibility;
- clarity;
- evaluation quality;
- portfolio explanation;
- technical focus.

Sources not included in version 1:

- IBGE agricultural production;
- CAR / SICAR;
- property-level legal compliance data;
- private rural property datasets;
- satellite image classification outputs.

---

## 5. System Architecture

The project has two complementary layers:

1. Document RAG layer
2. Structured environmental layer

---

## 5.1 Document RAG Layer

The document RAG layer processes PDF documents and prepares them for retrieval-based question answering.

Workflow:

```text
PDF documents
→ page-level text extraction
→ text cleaning
→ document chunking
→ embeddings
→ ChromaDB vector store
→ semantic retrieval
→ RAG answer
```

Main modules:

| Module | Purpose |
|---|---|
| `parse_pdf.py` | Extracts page-level text from PDF documents |
| `clean_text.py` | Cleans extracted text |
| `chunk_documents.py` | Creates retrieval-ready chunks |
| `embeddings.py` | Creates embeddings with SentenceTransformers |
| `vector_store.py` | Builds and queries ChromaDB |
| `prompts.py` | Loads prompt templates |
| `qa_chain.py` | Runs retrieval and answer generation |

---

## 5.2 Structured Environmental Layer

The structured layer builds numerical environmental evidence.

Workflow:

```text
MapBiomas municipality-year table
+ INPE / PRODES municipality-year table
→ unified environmental panel
→ native vegetation loss
→ agriculture/pasture expansion
→ environmental risk score
→ environmental risk class
```

Main modules:

| Module | Purpose |
|---|---|
| `build_environmental_panel.py` | Merges MapBiomas and INPE indicators |
| `risk_score.py` | Calculates derived indicators and risk score |

---

## 6. Repository Structure

```text
01-rag-document-intelligence/
│
├── README.md
├── requirements.txt
├── .gitignore
├── Makefile
│
├── docs/
│   ├── data_sources.md
│   ├── architecture.md
│   ├── evaluation.md
│   ├── limitations.md
│   ├── how_to_run.md
│   ├── project_workflow.md
│   ├── data_dictionary.md
│   ├── model_card.md
│   └── notebook_guide.md
│
├── prompts/
│   ├── system_prompt.md
│   ├── rag_answer_prompt.md
│   └── risk_summary_prompt.md
│
├── notebooks/
│   ├── 01_document_pipeline_demo.ipynb
│   ├── 02_structured_panel_and_risk_score_demo.ipynb
│   └── 03_rag_evaluation_demo.ipynb
│
├── src/
│   └── agro_rag/
│       ├── utils/
│       ├── processing/
│       ├── structured/
│       ├── rag/
│       └── evaluation/
│
├── app/
│   └── streamlit_app.py
│
├── tests/
│   ├── test_risk_score.py
│   ├── test_chunk_documents.py
│   └── test_golden_questions.py
│
├── reports/
│   ├── final_report.md
│   └── figures/
│
└── data/
    ├── raw/
    ├── interim/
    └── processed/
```

---

## 7. Document Pipeline

The document pipeline is demonstrated in:

```text
notebooks/01_document_pipeline_demo.ipynb
```

It performs the following steps.

---

### 7.1 PDF Parsing

Input folders:

```text
data/raw/mapbiomas/documents/
data/raw/inpe/documents/
```

The parser extracts one row per PDF page.

Expected fields:

| Field | Description |
|---|---|
| `source` | MapBiomas or INPE |
| `document_name` | Name of the document |
| `file_path` | Local document path |
| `page_number` | Page number |
| `year` | Reference year, when available |
| `theme` | Document theme |
| `language` | Document language |
| `text` | Extracted text |
| `text_length` | Character count |

---

### 7.2 Text Cleaning

The cleaning step creates a `clean_text` field.

Cleaning includes:

- whitespace normalization;
- removal of simple page artifacts;
- correction of simple broken hyphenation;
- removal of empty or very short pages.

---

### 7.3 Document Chunking

The chunking step creates the main retrieval table:

```text
data/processed/document_chunks.parquet
```

Default chunking strategy:

```text
chunk_size = 250 words
chunk_overlap = 40 words
```

Expected fields:

| Field | Description |
|---|---|
| `chunk_id` | Unique chunk identifier |
| `source` | Source family |
| `document_name` | Document name |
| `page_number` | Original page |
| `chunk_index` | Chunk number within the page |
| `year` | Reference year |
| `theme` | Theme |
| `language` | Language |
| `chunk_text` | Text used for retrieval |
| `chunk_word_count` | Number of words |
| `chunk_char_count` | Number of characters |

---

### 7.4 Vector Store

The project uses ChromaDB for local semantic search.

Output folder:

```text
chroma_db/
```

This folder is generated locally and should not be committed to GitHub.

Default embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model is useful for the first version because it is lightweight, local and does not require an external API key.

---

## 8. Structured Environmental Panel

The structured panel is demonstrated in:

```text
notebooks/02_structured_panel_and_risk_score_demo.ipynb
```

The main output is:

```text
data/processed/municipality_environmental_panel.parquet
```

Expected columns:

| Column | Description |
|---|---|
| `municipality_code` | Municipality identifier |
| `municipality_name` | Municipality name |
| `state` | Brazilian state |
| `biome` | Biome |
| `year` | Reference year |
| `mapbiomas_forest_area_ha` | Forest area from MapBiomas |
| `mapbiomas_native_vegetation_area_ha` | Native vegetation area from MapBiomas |
| `mapbiomas_agriculture_area_ha` | Agriculture area from MapBiomas |
| `mapbiomas_pasture_area_ha` | Pasture area from MapBiomas |
| `inpe_prodes_deforestation_area_ha` | Annual deforestation from INPE / PRODES |

The current demo notebook uses synthetic data to prove the pipeline.

In future versions, synthetic data should be replaced by real cleaned MapBiomas and INPE tables.

---

## 9. Environmental Screening Score

The project calculates an explainable environmental screening score.

Output file:

```text
data/processed/municipality_environmental_panel_scored.parquet
```

Generated indicators:

| Indicator | Meaning |
|---|---|
| `mapbiomas_native_vegetation_loss_ha` | Year-to-year reduction in native vegetation |
| `mapbiomas_agriculture_or_pasture_expansion_ha` | Year-to-year expansion of agriculture plus pasture |
| `inpe_prodes_deforestation_area_ha` | Annual deforestation evidence from INPE / PRODES |

Default formula:

```text
environmental_risk_score =
    0.50 * normalized_inpe_prodes_deforestation_area_ha
  + 0.30 * normalized_mapbiomas_native_vegetation_loss_ha
  + 0.20 * normalized_mapbiomas_agriculture_or_pasture_expansion_ha
```

Risk classes:

| Score Range | Class |
|---|---|
| 0.00 to 0.33 | Low |
| 0.34 to 0.66 | Medium |
| 0.67 to 1.00 | High |

Interpretation:

| Class | Meaning |
|---|---|
| Low | Lower screening signal in the analyzed dataset |
| Medium | Intermediate screening signal |
| High | Stronger screening signal and candidate for deeper review |

Critical limitation:

> A high score does not prove illegal deforestation. A low score does not guarantee absence of environmental risk.

---

## 10. RAG Answer Generation

The RAG answer flow is:

```text
user question
→ vector retrieval
→ context formatting
→ prompt construction
→ optional LLM answer
→ evidence and limitations
```

The system can run in two modes.

| Mode | Description |
|---|---|
| Retrieval-only | Retrieves and displays evidence without an LLM |
| LLM-based RAG | Retrieves evidence and generates a final answer |

The project uses prompt templates stored in:

```text
prompts/
```

Main prompt files:

| Prompt | Purpose |
|---|---|
| `system_prompt.md` | Defines behavior and safety rules |
| `rag_answer_prompt.md` | Defines evidence-based answer format |
| `risk_summary_prompt.md` | Defines environmental screening summary format |

The prompts require the system to:

- answer only from retrieved evidence;
- avoid invented facts;
- cite available evidence;
- state limitations;
- avoid legal conclusions;
- use cautious language.

---

## 11. Streamlit App

The app file is:

```text
app/streamlit_app.py
```

Run command:

```bash
streamlit run app/streamlit_app.py
```

The app supports:

- user questions;
- source filtering;
- retrieval-only mode;
- optional LLM answer generation;
- retrieved evidence table;
- text chunk inspection;
- execution metadata display.

The app requires the vector store to exist locally:

```text
chroma_db/
```

The vector store is generated by Notebook 01.

---

## 12. Evaluation Strategy

The evaluation workflow is demonstrated in:

```text
notebooks/03_rag_evaluation_demo.ipynb
```

The evaluation has two layers:

1. retrieval evaluation;
2. answer evaluation.

---

### 12.1 Golden Questions

Golden questions are generated by:

```text
src/agro_rag/evaluation/golden_questions.py
```

Output:
```text
data/processed/rag_eval_questions.csv
```

The golden questions test:

- MapBiomas retrieval;
- INPE retrieval;
- source comparison;
- environmental screening behavior;
- insufficient evidence behavior;
- legal overclaim avoidance.

---

### 12.2 Retrieval Evaluation

Retrieval evaluation checks whether the expected source appears in the retrieved chunks.

Output:

```text
reports/rag_retrieval_evaluation.csv
```

Metrics:

| Metric | Meaning |
|---|---|
| `source_hit_at_k` | Whether expected source appears in top-k |
| `recall_at_k` | Same as source hit in version 1 |
| `precision_at_k` | Fraction of top-k chunks matching expected source |

Initial target:

```text
Source hit rate@5 >= 80%
```

---

### 12.3 Answer Evaluation

Answer evaluation checks:

- citation or evidence presence;
- limitation presence;
- cautious language;
- unsafe legal claims;
- basic answer score.

Output:

```text
reports/rag_answer_evaluation.csv
```

Initial targets:

| Metric | Target |
|---|---|
| Mean answer score | 2.0 or higher |
| Unsafe claim rate | 0% |
| Limitation rate for risk answers | 90% or higher |

This rule-based evaluation is a first screening layer. It does not replace expert review.

---

## 13. Tests

The project includes basic unit tests in:

```text
tests/
```

Current test files:

| File | Purpose |
|---|---|
| `test_risk_score.py` | Tests normalization, score generation and risk classes |
| `test_chunk_documents.py` | Tests text chunking and chunk metadata |
| `test_golden_questions.py` | Tests golden question structure |

Run tests with:

```bash
pytest
```

Or:

```bash
make test
```

---

## 14. How to Run

Recommended execution order:

```text
1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Run Notebook 01
5. Run Notebook 02
6. Run Notebook 03
7. Launch Streamlit app
8. Review evaluation outputs
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run app:

```bash
streamlit run app/streamlit_app.py
```

Run tests:

```bash
pytest
```

---

## 15. Main Outputs

After running the notebooks, the project may generate:

```text
data/interim/parsed_documents/all_pages_clean.parquet
data/processed/document_chunks.parquet
data/processed/rag_eval_questions.csv
data/processed/municipality_environmental_panel.parquet
data/processed/municipality_environmental_panel_scored.parquet
reports/rag_retrieval_evaluation.csv
reports/rag_generated_answers.csv
reports/rag_answer_evaluation.csv
reports/rag_evaluation_summary.csv
reports/figures/environmental_risk_score_by_municipality.png
chroma_db/
```

Important:

```text
chroma_db/
data/interim/
data/processed/
```

may contain generated local files and should be handled carefully.

Large generated files should not be committed unless intentionally included as small examples.

---

## 16. Limitations
This project does not determine:

- illegal deforestation;
- legal responsibility;
- rural property compliance;
- environmental crime;
- final ESG approval or rejection.

The system supports:
- evidence organization;
- environmental screening;
- retrieval-based explanation;
- analyst decision support.

Main limitations:

- MapBiomas and INPE may use different methods;
- municipality-level aggregation can hide local spatial variation;
- PDF parsing may lose structure;
- chunking may split important context;
- vector retrieval may miss relevant evidence;
- LLM answers depend on retrieved context and prompt quality;
- the risk score is relative to the analyzed dataset;
- the score is not calibrated against legal outcomes.

---

## 17. Ethical and Safety Considerations
The system must avoid statements such as:

- “illegal deforestation was proven”;
- “the company committed environmental crime”;
- “the farm is non-compliant”;
- “the municipality is guilty”;
- “this is a final ESG decision.”

Preferred language:

- “the available evidence suggests”;
- “the indicators point to”;
- “this should be interpreted as a screening signal”;
- “further analysis is required”;
- “this is not a legal conclusion.”

All outputs should be reviewed by a human analyst before use in:
- ESG reports;
- credit decisions;
- legal analysis;
- public communication;
- policy recommendations;
- enforcement actions.

---

## 18. Version 1 Scope
Version 1 includes:

- MapBiomas and INPE / TerraBrasilis only;
- document parsing;
- text cleaning;
- document chunking;
- local ChromaDB vector store;
- retrieval-only mode;
- optional LLM-based RAG answers;
- structured municipality-year panel;
- environmental screening score;
- Streamlit app;
- golden question evaluation;
- synthetic demo data in notebooks.

Version 1 does not include:
- IBGE agricultural production data;
- CAR / SICAR;
- property-level legal compliance;
- polygon-level geospatial analysis;
- satellite image classification;
- production deployment;
- real-time monitoring.

---

## 19. Future Improvements
Recommended improvements:

1. Add further MapBiomas and INPE documents.
2. Add further cleaned MapBiomas and INPE structured tables.
3. Add DETER as an alert-oriented layer.
4. Add geospatial visualization with GeoPandas or Folium.
5. Add hybrid search.
6. Add reranking.
7. Compare embedding models.
8. Add RAGAS or another RAG evaluation framework.
9. Add human-reviewed golden questions.
10. Improve citation extraction for tables and figures.
11. Add Docker support.
12. Deploy the Streamlit app.

---

## 20. Final Conclusion
This project establishes a complete first version of a RAG-based agro-environmental intelligence assistant.

It demonstrates:
- document intelligence;
- semantic retrieval;
- structured data engineering;
- explainable environmental scoring;
- safe prompt design;
- retrieval evaluation;
- answer evaluation;
- Streamlit-based interaction;
- software engineering organization.

The final interpretation is:
> The project helps organize MapBiomas and INPE evidence and supports environmental screening, but it does not replace expert legal, environmental or geospatial analysis.
