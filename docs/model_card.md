# Model Card

## 1. Overview

This document describes the model behavior, intended use, limitations and evaluation approach for the project:

```text
01-rag-document-intelligence
```

The project implements a Retrieval-Augmented Generation system for Brazilian deforestation and land-use monitoring using two source families:

1. MapBiomas
2. INPE / TerraBrasilis

The system combines:

- document retrieval;
- structured environmental indicators;
- prompt templates;
- optional LLM-based answer generation;
- environmental screening summaries;
- retrieval and answer evaluation.

This is not a legal, regulatory or enforcement model.  
It is an evidence organization and environmental screening assistant.

---

## 2. System Name

```text
Agro-Environmental RAG Assistant
```

Repository:

```text
01-rag-document-intelligence/
```

Main application file:

```text
app/streamlit_app.py
```

Main package:

```text
src/agro_rag/
```

---

## 3. System Type

This project is a:

```text
Retrieval-Augmented Generation system
```

with an additional:

```text
structured environmental screening score
```

The system is not a traditional supervised machine learning classifier.  
It does not learn a target label such as legal compliance, illegal deforestation or ESG approval.

Instead, it retrieves evidence from indexed documents and optionally generates answers using an LLM.

---

## 4. Main Capabilities

The system can:

- parse MapBiomas and INPE-related PDF documents;
- clean extracted text;
- split documents into retrieval-ready chunks;
- create embeddings for document chunks;
- store chunks in ChromaDB;
- retrieve relevant evidence for user questions;
- generate RAG answers when an LLM is available;
- run in retrieval-only mode without an LLM;
- build a municipality-year environmental panel;
- calculate an explainable environmental screening score;
- evaluate retrieval behavior using golden questions;
- evaluate generated answers using rule-based quality checks.

---

## 5. Data Sources

The first version uses only two source families.

| Source | Role |
|---|---|
| MapBiomas | Land use, land cover, native vegetation, agriculture and pasture indicators |
| INPE / TerraBrasilis | Official deforestation monitoring evidence, especially PRODES |

The project intentionally avoids additional sources in version 1 to keep the workflow simple and explainable.

Sources not included in version 1:

- IBGE agricultural production;
- CAR / SICAR property-level data;
- private rural property datasets;
- satellite image classification models;
- legal enforcement records.

---

## 6. Input Data

The system uses two types of input.

---

### 6.1 Document Inputs

Expected document folders:

```text
data/raw/mapbiomas/documents/
data/raw/inpe/documents/
```

Expected document types:

- PDF reports;
- methodology documents;
- source documentation;
- deforestation monitoring reports;
- land-use and land-cover reports.

Document processing output:

```text
data/processed/document_chunks.parquet
```

---

### 6.2 Structured Inputs

Expected MapBiomas table:

```text
data/interim/cleaned_mapbiomas/mapbiomas_municipality_year.parquet
```

Expected INPE / PRODES table:

```text
data/interim/cleaned_inpe/inpe_prodes_municipality_year.parquet
```

Structured output:

```text
data/processed/municipality_environmental_panel.parquet
data/processed/municipality_environmental_panel_scored.parquet
```

---

## 7. Output

The system can generate several output types.

---

### 7.1 Retrieved Evidence

The retriever returns relevant chunks with metadata such as:

- source;
- document name;
- page number;
- year;
- theme;
- retrieved text;
- vector distance.

---

### 7.2 RAG Answer

When an LLM is available, the system can produce an answer containing:

- direct answer;
- evidence used;
- interpretation;
- limitations;
- confidence level.

The answer should be grounded in retrieved evidence.

---

### 7.3 Environmental Screening Summary

The system can combine retrieved document evidence with structured numerical indicators to produce an environmental screening summary.

This summary may include:

- INPE / PRODES deforestation area;
- MapBiomas native vegetation area;
- MapBiomas native vegetation loss;
- MapBiomas agriculture area;
- MapBiomas pasture area;
- agriculture or pasture expansion;
- environmental risk score;
- environmental risk class.

---

### 7.4 Environmental Risk Score

The structured pipeline calculates:

```text
environmental_risk_score
```

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

The score is a screening indicator only.

---

## 8. Intended Use

The system is intended for:

- environmental evidence organization;
- document-based question answering;
- retrieval of MapBiomas and INPE-related evidence;
- municipality-year environmental screening;
- analyst support;
- portfolio demonstration of RAG, NLP and data engineering skills;
- educational demonstration of document intelligence architecture.

Appropriate user profiles include:

- data scientists;
- environmental analysts;
- ESG analysts;
- researchers;
- technical reviewers;
- students learning RAG systems;
- software engineering and data science interviewers.

---

## 9. Non-Intended Use

The system must not be used to:

- determine illegal deforestation;
- assign legal responsibility;
- accuse a person, company, municipality or farm of environmental crime;
- determine rural property compliance;
- replace environmental agencies;
- replace legal, agronomic or geospatial expert analysis;
- issue final ESG certification;
- automate credit, insurance or commercial decisions;
- make enforcement decisions;
- publish accusations without human review.

The system output is not a legal conclusion.

---

## 10. Users and Stakeholders

Possible users:

| User | Expected Use |
|---|---|
| Data scientist | Test RAG and environmental screening architecture |
| ESG analyst | Review evidence and identify topics for deeper analysis |
| Environmental analyst | Retrieve documents and compare indicators |
| Student | Learn RAG, vector search and document intelligence |
| Recruiter / interviewer | Evaluate project design, code quality and AI architecture |

Stakeholders affected by misuse:

- municipalities;
- rural producers;
- companies;
- public institutions;
- environmental agencies;
- financial institutions;
- local communities.

Because of this, the system must use cautious language and avoid unsupported claims.

---

## 11. Model Components

The system includes the following components.

| Component | File / Folder | Role |
|---|---|---|
| PDF parser | `src/agro_rag/processing/parse_pdf.py` | Extracts page-level text from PDFs |
| Text cleaner | `src/agro_rag/processing/clean_text.py` | Cleans extracted text |
| Chunker | `src/agro_rag/processing/chunk_documents.py` | Creates retrieval chunks |
| Embeddings | `src/agro_rag/rag/embeddings.py` | Creates vector embeddings |
| Vector store | `src/agro_rag/rag/vector_store.py` | Stores and retrieves chunks |
| Prompt loader | `src/agro_rag/rag/prompts.py` | Loads prompt templates |
| QA chain | `src/agro_rag/rag/qa_chain.py` | Runs retrieval and optional answer generation |
| Panel builder | `src/agro_rag/structured/build_environmental_panel.py` | Builds municipality-year panel |
| Risk score | `src/agro_rag/structured/risk_score.py` | Calculates environmental screening score |
| Golden questions | `src/agro_rag/evaluation/golden_questions.py` | Creates evaluation questions |
| Retrieval evaluation | `src/agro_rag/evaluation/evaluate_retrieval.py` | Evaluates retrieved sources |
| Answer evaluation | `src/agro_rag/evaluation/evaluate_answers.py` | Evaluates answer quality and safety |
| Streamlit app | `app/streamlit_app.py` | Interactive interface |

---

## 12. Embedding Model

The default local embedding model is:

```text
sentence-transformers/all-MiniLM-L6-v2
```

This model is used because it:

- runs locally;
- does not require an API key;
- is lightweight;
- is suitable for a first portfolio version;
- works with ChromaDB.

Embedding output is used for semantic retrieval, not for legal or regulatory classification.

---

## 13. Optional LLM

The system can optionally use an OpenAI chat model for answer generation.

Default model in the code:

```text
gpt-4o-mini
```

The system can also run without an LLM in retrieval-only mode.

When using an LLM, answers must follow the project prompt rules:

- use only retrieved context;
- do not invent facts;
- cite evidence when available;
- state limitations;
- avoid legal conclusions;
- use cautious language.

---

## 14. Prompt Behavior

Prompt templates are stored in:

```text
prompts/
```

Main prompt files:

| Prompt | Purpose |
|---|---|
| `system_prompt.md` | Defines general system behavior and safety rules |
| `rag_answer_prompt.md` | Defines answer format for evidence-based Q&A |
| `risk_summary_prompt.md` | Defines format for environmental screening summaries |

The prompts require the system to:

- answer from retrieved context;
- avoid unsupported claims;
- distinguish facts from interpretation;
- state limitations;
- avoid legal or enforcement conclusions.

---

## 15. Evaluation Approach

The project uses two evaluation layers.

---

### 15.1 Retrieval Evaluation

Retrieval evaluation checks whether the vector store retrieves evidence from the expected source family.

Main file:

```text
src/agro_rag/evaluation/evaluate_retrieval.py
```

Golden questions:

```text
data/processed/rag_eval_questions.csv
```

Output:

```text
reports/rag_retrieval_evaluation.csv
```

Metrics:

| Metric | Meaning |
|---|---|
| `source_hit_at_k` | Whether expected source appears in top-k retrieved chunks |
| `recall_at_k` | Same as source hit in version 1 |
| `precision_at_k` | Fraction of top-k chunks matching expected source |

---

### 15.2 Answer Evaluation

Answer evaluation checks whether the final answer includes:

- citation or evidence terms;
- limitations;
- cautious language;
- no unsafe legal overclaims.

Main file:

```text
src/agro_rag/evaluation/evaluate_answers.py
```

Output:

```text
reports/rag_answer_evaluation.csv
```

Rule-based checks:

| Check | Meaning |
|---|---|
| `citation_or_evidence_present` | Answer refers to evidence or sources |
| `limitation_present` | Answer states limitations |
| `cautious_language_present` | Answer uses careful analytical language |
| `unsafe_claim_flag` | Answer contains unsafe legal language |
| `answer_score` | Simple score from 0 to 3 |

This evaluation is a first automated screening layer. It does not replace expert review.

---

## 16. Performance Targets

Initial target values for version 1:

| Metric | Target |
|---|---|
| Source hit rate@5 | 80% or higher |
| Mean answer score | 2.0 or higher |
| Unsafe claim rate | 0% |
| Limitation rate for risk answers | 90% or higher |

These targets should be updated after real documents are added and the first evaluation is executed.

---

## 17. Ethical and Safety Considerations

Because the project deals with environmental risk, outputs may affect interpretation of municipalities, regions, companies or rural properties.

The system must avoid language such as:

- “illegal deforestation was proven”;
- “the company committed environmental crime”;
- “the farm is non-compliant”;
- “this proves guilt”;
- “this is a final ESG decision.”

Preferred wording:

- “the available evidence suggests”;
- “the indicators point to”;
- “this should be interpreted as a screening signal”;
- “further analysis is required”;
- “this is not a legal conclusion.”

---

## 18. Known Limitations

The system has several limitations.

### 18.1 Data Limitations

- MapBiomas and INPE may use different methods.
- Spatial and temporal definitions may differ.
- Municipality-level aggregation can hide local variation.
- Source documents may be incomplete or outdated.
- Real documents may include tables, figures or maps that are difficult to parse automatically.

### 18.2 RAG Limitations

- Retrieval may miss relevant chunks.
- Retrieval may return irrelevant chunks.
- PDF extraction may lose page structure.
- Chunking may split context incorrectly.
- The LLM may still produce unsupported claims if prompts or retrieval are weak.
- Citations depend on metadata quality.

### 18.3 Risk Score Limitations

- The score is relative to the analyzed dataset.
- Min-max normalization changes when the dataset changes.
- The score is not trained against legal or enforcement outcomes.
- The score does not prove illegal activity.
- The score does not replace geospatial expert review.

---

## 19. Human Review Requirement

Human review is required before using outputs for:

- ESG reports;
- financial decisions;
- credit decisions;
- legal analysis;
- public communication;
- policy recommendations;
- enforcement actions;
- comparison between companies, farms or municipalities.

The safest interpretation is:

```text
The system provides screening evidence that can help analysts decide what to review next.
```

---

## 20. Version 1 Scope

Version 1 includes:

- MapBiomas and INPE / TerraBrasilis only;
- document pipeline;
- structured municipality-year panel;
- environmental screening score;
- local ChromaDB vector store;
- Streamlit app;
- golden question evaluation;
- synthetic demo data in notebooks.

Version 1 does not include:

- IBGE agricultural production;
- CAR / SICAR;
- property-level legal analysis;
- full polygon-level geospatial analysis;
- satellite image classification;
- real-time monitoring;
- production deployment;
- automated legal compliance classification.

---

## 21. Future Improvements

Possible improvements:

- add real MapBiomas and INPE PDF documents;
- add real cleaned MapBiomas and INPE structured tables;
- add DETER as an alert-oriented layer;
- add geospatial visualization;
- add hybrid search;
- add reranking;
- compare embedding models;
- add RAGAS or another RAG evaluation framework;
- add human-reviewed golden questions;
- add Docker support;
- deploy the Streamlit app;
- improve citation handling for tables and figures.

---

## 22. Final Use Statement

This system should be described as:

```text
A RAG-based environmental intelligence assistant for organizing MapBiomas and INPE evidence, supporting retrieval-based explanations, and helping analysts prioritize deeper review.
```

It should not be described as:

```text
A system that determines illegal deforestation, assigns responsibility or replaces expert legal, environmental or geospatial analysis.
```
