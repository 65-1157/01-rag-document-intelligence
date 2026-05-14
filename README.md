# 01-rag-document-intelligence
## RAG Document Intelligence for Brazilian Deforestation and Land-Use Monitoring

This project is part of the **Brazil Agro-Environmental AI Portfolio**.

It implements a Retrieval-Augmented Generation (RAG) system to organize, retrieve and explain evidence from Brazilian agro-environmental sources, focusing on:

1. **MapBiomas**
2. **INPE / TerraBrasilis**

The system combines document intelligence, structured environmental indicators and an explainable screening score to support questions about deforestation, land use, native vegetation loss, agriculture expansion and pasture expansion.

The project is designed for **evidence organization and environmental screening**, not for legal judgment or regulatory enforcement.

---

## 1. Problem Statement

Brazil has extensive public information about deforestation, land use and native vegetation change. However, this information is distributed across reports, dashboards, technical documents, geospatial platforms and structured datasets.

This fragmentation makes it difficult for analysts to quickly answer questions such as:

- What does INPE / PRODES indicate about deforestation monitoring?
- What does MapBiomas indicate about land-use and land-cover change?
- How can INPE and MapBiomas evidence complement each other?
- Which municipality-year records deserve deeper environmental review?
- What are the limitations of using these indicators for screening?

This project addresses that problem by creating a RAG-based document intelligence workflow with traceable evidence and clear limitations.

---

## 2. Project Objectives

The main objectives are:

- process MapBiomas and INPE / TerraBrasilis documents;
- extract, clean and chunk text for retrieval;
- build a local vector database with ChromaDB;
- retrieve relevant evidence for user questions;
- generate cited RAG answers when an LLM is available;
- run retrieval-only mode when no LLM API key is configured;
- build a municipality-year environmental panel;
- calculate an explainable environmental screening score;
- evaluate retrieval and answer behavior using golden questions.

---

## 3. Data Sources

This first version intentionally uses only two source families.

| Source | Role in the Project |
|---|---|
| MapBiomas | Land use, land cover, native vegetation, agriculture and pasture indicators |
| INPE / TerraBrasilis | Official deforestation monitoring evidence, especially PRODES |

The reduced scope keeps the project simpler, easier to evaluate and easier to explain in a portfolio or job interview.

More details are available in: docs/data_sources.md

## 4. System Architecture
This project has two layers:
Document RAG layer
PDF documents
→ text extraction
→ text cleaning
→ document chunking
→ vector database
→ semantic retrieval
→ cited RAG answer
Structured Environmental layer
MapBiomas table
+ INPE / PRODES table
→ municipality-year environmental panel
→ environmental indicators
→ risk score
→ structured evidence for RAG

## 5. Repository Structure
´´´ text 
01-rag-document-intelligence/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   ├── data_sources.md
│   ├── architecture.md
│   ├── evaluation.md
│   └── limitations.md
│
├── prompts/
│   ├── system_prompt.md
│   ├── rag_answer_prompt.md
│   └── risk_summary_prompt.md
│
├── notebooks/
│   ├── 01_document_pipeline_demo.ipynb
│   └── 02_structured_panel_and_risk_score_demo.ipynb
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
├── reports/
│   └── figures/
│
└── data/
    ├── raw/
    ├── interim/
    └── processed/

## 6 - Main Components
| Component                  | Purpose                                                      |
| -------------------------- | ------------------------------------------------------------ |
| `src/agro_rag/processing/` | PDF parsing, text cleaning and document chunking             |
| `src/agro_rag/rag/`        | Embeddings, vector store, prompt loading and QA chain        |
| `src/agro_rag/structured/` | Environmental panel construction and risk scoring            |
| `src/agro_rag/evaluation/` | Golden questions, retrieval evaluation and answer evaluation |
| `app/streamlit_app.py`     | Interactive RAG interface                                    |
| `prompts/`                 | Prompt templates for safe and evidence-based answers         |
| `docs/`                    | Technical documentation                                      |
| `notebooks/`               | Executable project demonstrations                            |

## 7 - Environmental Risk Score
environmental_risk_score =
    0.50 * normalized_inpe_prodes_deforestation_area_ha
  + 0.30 * normalized_mapbiomas_native_vegetation_loss_ha
  + 0.20 * normalized_mapbiomas_agriculture_or_pasture_expansion_ha
    
Risk Classes
| Score Range  | Class  |
| ------------ | ------ |
| 0.00 to 0.33 | Low    |
| 0.34 to 0.66 | Medium |
| 0.67 to 1.00 | High   |

## 8. Important Limitations

This project does not determine:

illegal deforestation;
legal responsibility;
rural property compliance;
environmental crime;
final ESG approval or rejection.

The system supports:

evidence organization;
environmental screening;
retrieval-based explanation;
analyst decision support.

All outputs require human review before operational, legal, financial or public use.

## How to Run the Project

This project has two main execution flows:

1. **Document RAG pipeline**
2. **Structured environmental panel and risk score pipeline**

The first pipeline processes MapBiomas and INPE / TerraBrasilis documents for retrieval-based question answering.  
The second pipeline builds a municipality-year environmental panel and calculates an explainable environmental screening score.

---

## 1. Clone the repository

```bash
git clone <your-repository-url>
cd 01-rag-document-intelligence
