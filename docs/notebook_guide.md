# Notebook Guide

## 1. Overview

This document explains the notebooks included in the project and how they should be executed.

The project currently has two main notebooks:

```text
notebooks/01_document_pipeline_demo.ipynb
notebooks/02_structured_panel_and_risk_score_demo.ipynb
```

Together, they demonstrate the two main project flows:

1. Document RAG pipeline
2. Structured environmental panel and risk score pipeline

---

## 2. Recommended Execution Order

Run the notebooks in this order:

```text
1. notebooks/01_document_pipeline_demo.ipynb
2. notebooks/02_structured_panel_and_risk_score_demo.ipynb
```

Notebook 01 builds the document retrieval foundation.

Notebook 02 builds the structured environmental evidence layer.

---

## 3. Notebook 01 — Document Pipeline Demo

File:

```text
notebooks/01_document_pipeline_demo.ipynb
```

### 3.1 Purpose

This notebook demonstrates the full document RAG preparation workflow.

It processes MapBiomas and INPE / TerraBrasilis documents and prepares them for semantic retrieval.

### 3.2 Main Workflow

```text
PDF documents
→ page-level text extraction
→ text cleaning
→ document chunking
→ document_chunks.parquet
→ ChromaDB vector store
→ retrieval test
→ golden questions
→ retrieval evaluation
```

### 3.3 Input Folders

Expected document folders:

```text
data/raw/mapbiomas/documents/
data/raw/inpe/documents/
```

Expected input files:

- MapBiomas PDF reports;
- MapBiomas methodology documents;
- INPE / TerraBrasilis PDF reports;
- INPE / PRODES methodology documents.

If no PDF files are available, the notebook creates a synthetic fallback dataset.

This allows the pipeline to be tested before real documents are added.

### 3.4 Main Modules Used

| Module | Purpose |
|---|---|
| `agro_rag.processing.parse_pdf` | Extracts page-level text from PDFs |
| `agro_rag.processing.clean_text` | Cleans extracted text |
| `agro_rag.processing.chunk_documents` | Creates retrieval-ready chunks |
| `agro_rag.rag.vector_store` | Builds and queries ChromaDB |
| `agro_rag.rag.qa_chain` | Runs retrieval-only or LLM-based RAG |
| `agro_rag.evaluation.golden_questions` | Creates golden question dataset |
| `agro_rag.evaluation.evaluate_retrieval` | Evaluates retrieval quality |

### 3.5 Main Outputs

Expected outputs:

```text
data/interim/parsed_documents/mapbiomas_pages.parquet
data/interim/parsed_documents/inpe_pages.parquet
data/interim/parsed_documents/all_pages_clean.parquet
data/processed/document_chunks.parquet
data/processed/rag_eval_questions.csv
reports/rag_retrieval_evaluation.csv
chroma_db/
```

### 3.6 Important Notes

The folder:

```text
chroma_db/
```

is generated locally and should not be committed to GitHub.

Large PDF files should also not be committed unless they are small, public and intentionally included as samples.

### 3.7 What to Check After Running

After running Notebook 01, check:

- whether PDF pages were parsed correctly;
- whether `clean_text` was generated;
- whether document chunks were created;
- whether `document_chunks.parquet` exists;
- whether the ChromaDB vector store was created;
- whether retrieval returns relevant chunks;
- whether `rag_eval_questions.csv` was generated;
- whether retrieval evaluation produced a CSV file.

### 3.8 Success Criteria

Notebook 01 is successful when:

```text
data/processed/document_chunks.parquet
chroma_db/
reports/rag_retrieval_evaluation.csv
```

are generated and retrieval returns chunks from the expected source family.

---

## 4. Notebook 02 — Structured Panel and Risk Score Demo

File:

```text
notebooks/02_structured_panel_and_risk_score_demo.ipynb
```

### 4.1 Purpose

This notebook demonstrates the structured data workflow.

It builds a municipality-year environmental panel using simplified MapBiomas and INPE / PRODES indicators, then calculates an explainable environmental screening score.

### 4.2 Main Workflow

```text
MapBiomas municipality-year table
+ INPE / PRODES municipality-year table
→ unified environmental panel
→ native vegetation loss
→ agriculture/pasture expansion
→ normalized indicators
→ environmental risk score
→ environmental risk class
```

### 4.3 Input Tables

Expected MapBiomas table:

```text
data/interim/cleaned_mapbiomas/mapbiomas_municipality_year.parquet
```

Expected columns:

```text
municipality_code
municipality_name
state
biome
year
mapbiomas_forest_area_ha
mapbiomas_native_vegetation_area_ha
mapbiomas_agriculture_area_ha
mapbiomas_pasture_area_ha
```

Expected INPE / PRODES table:

```text
data/interim/cleaned_inpe/inpe_prodes_municipality_year.parquet
```

Expected columns:

```text
municipality_code
year
inpe_prodes_deforestation_area_ha
```

In the current version, Notebook 02 creates synthetic tables for demonstration.

Later, these synthetic tables should be replaced by real cleaned MapBiomas and INPE tables.

### 4.4 Main Modules Used

| Module | Purpose |
|---|---|
| `agro_rag.structured.build_environmental_panel` | Merges MapBiomas and INPE tables |
| `agro_rag.structured.risk_score` | Calculates environmental indicators and risk score |
| `agro_rag.rag.prompts` | Tests structured evidence insertion into the RAG prompt |

### 4.5 Main Outputs

Expected outputs:

```text
data/interim/cleaned_mapbiomas/mapbiomas_municipality_year.parquet
data/interim/cleaned_inpe/inpe_prodes_municipality_year.parquet
data/processed/municipality_environmental_panel.parquet
data/processed/municipality_environmental_panel_scored.parquet
reports/figures/environmental_risk_score_by_municipality.png
```

### 4.6 Generated Indicators

Notebook 02 generates the following derived indicators:

| Indicator | Meaning |
|---|---|
| `mapbiomas_native_vegetation_loss_ha` | Year-to-year reduction in native vegetation |
| `mapbiomas_agriculture_or_pasture_expansion_ha` | Year-to-year expansion of agriculture plus pasture |
| `environmental_risk_score` | Explainable environmental screening score |
| `environmental_risk_class` | Low, Medium or High screening class |

### 4.7 Risk Score Formula

Default formula:

```text
environmental_risk_score =
    0.50 * normalized_inpe_prodes_deforestation_area_ha
  + 0.30 * normalized_mapbiomas_native_vegetation_loss_ha
  + 0.20 * normalized_mapbiomas_agriculture_or_pasture_expansion_ha
```

Risk class thresholds:

| Score Range | Class |
|---|---|
| 0.00 to 0.33 | Low |
| 0.34 to 0.66 | Medium |
| 0.67 to 1.00 | High |

### 4.8 What to Check After Running

After running Notebook 02, check:

- whether the synthetic MapBiomas table was created;
- whether the synthetic INPE table was created;
- whether both tables were merged correctly;
- whether municipality-year records are unique;
- whether the risk score is between 0 and 1;
- whether the risk class is valid;
- whether the figure was saved;
- whether structured evidence text was generated.

### 4.9 Success Criteria

Notebook 02 is successful when:

```text
data/processed/municipality_environmental_panel.parquet
data/processed/municipality_environmental_panel_scored.parquet
reports/figures/environmental_risk_score_by_municipality.png
```

are generated and the scored table contains:

```text
environmental_risk_score
environmental_risk_class
```

---

## 5. How the Notebooks Work Together

The notebooks are complementary.

| Notebook | Main Role | Output Used By |
|---|---|---|
| Notebook 01 | Builds document retrieval layer | Streamlit app and RAG answers |
| Notebook 02 | Builds structured evidence layer | Risk summaries and environmental screening |

The intended combined workflow is:

```text
Notebook 01:
documents → chunks → vector store → retrieved evidence

Notebook 02:
tables → panel → risk score → structured evidence

Combined RAG:
retrieved evidence + structured evidence → environmental screening summary
```

---

## 6. Running the Streamlit App After the Notebooks

After Notebook 01 builds the vector store, run:

```bash
streamlit run app/streamlit_app.py
```

The app expects:

```text
chroma_db/
```

to exist locally.

The app can run in two modes:

| Mode | Requirement |
|---|---|
| Retrieval-only mode | No API key required |
| LLM-based RAG mode | Requires `OPENAI_API_KEY` |

---

## 7. OpenAI API Key

The notebooks and app can run retrieval-only workflows without an API key.

For LLM-based answers, configure:

### macOS / Linux

```bash
export OPENAI_API_KEY="your_key_here"
```

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY="your_key_here"
```

Do not commit keys or `.env` files to GitHub.

---

## 8. Common Problems

### 8.1 `ModuleNotFoundError: No module named 'agro_rag'`

Cause:

- The notebook cannot find the `src/` folder.

Fix:

- Run the notebook from the project root or from the `notebooks/` folder.
- Keep the setup cell that adds `src/` to `sys.path`.

---

### 8.2 ChromaDB directory not found

Cause:

- Notebook 01 has not been run yet.
- The vector store was deleted or generated in another folder.

Fix:

- Run Notebook 01 again.
- Confirm that `chroma_db/` exists in the project root.

---

### 8.3 No PDF files found

Cause:

- No PDFs were placed in the expected folders.

Expected behavior:

- Notebook 01 creates a synthetic fallback dataset.

Fix for real use:

- Add public MapBiomas and INPE PDF documents to:

```text
data/raw/mapbiomas/documents/
data/raw/inpe/documents/
```

---

### 8.4 Risk score does not look meaningful

Cause:

- Notebook 02 currently uses synthetic data.
- Scores are relative to the available dataset.
- Min-max normalization changes when the dataset changes.

Fix:

- Replace synthetic data with real cleaned MapBiomas and INPE tables.
- Review distributions before interpreting scores.
- Treat scores as screening indicators only.

---

## 9. Version 1 Notebook Scope

The notebooks are demonstration notebooks.

They are designed to prove that the pipeline works.

They do not yet include:

- full real MapBiomas download automation;
- full real INPE / TerraBrasilis download automation;
- property-level geospatial analysis;
- legal compliance analysis;
- large-scale production deployment;
- satellite image classification;
- complete ESG workflow automation.

---

## 10. GitHub Commit Guidance

Recommended commit messages:

For Notebook 01:

```text
Add document pipeline demo notebook
```

For Notebook 02:

```text
Add structured panel and risk score demo notebook
```

For this guide:

```text
Add notebook guide documentation
```

---

## 11. Final Interpretation

Notebook outputs should be interpreted as:

```text
evidence and screening support
```

They should not be interpreted as:

```text
legal proof
```

The safest interpretation is:

> The notebooks demonstrate how to organize MapBiomas and INPE evidence,
> retrieve relevant context, build structured environmental indicators and support deeper analyst review.
