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
