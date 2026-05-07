# Architecture

## 1. Overview

This project implements a Retrieval-Augmented Generation system for Brazilian deforestation and land-use monitoring.

The architecture uses two data source families:

1. MapBiomas
2. INPE / TerraBrasilis

The system combines structured environmental indicators and unstructured technical documents to answer questions with cited evidence.

The main design principle is:

> The system should only answer based on retrieved evidence and should clearly indicate limitations when the evidence is insufficient.

---

## 2. Architecture Flow

```text
                 ┌─────────────────────────────┐
                 │ Data Sources                 │
                 │ MapBiomas + INPE             │
                 └──────────────┬──────────────┘
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │ Data Ingestion Layer         │
                 │ reports, CSVs, APIs, files   │
                 └──────────────┬──────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
┌─────────────────────────┐        ┌─────────────────────────┐
│ Document Pipeline       │        │ Structured Data Pipeline│
│ reports, docs, metadata │        │ municipality-year table │
└────────────┬────────────┘        └────────────┬────────────┘
             │                                  │
             ▼                                  ▼
┌─────────────────────────┐        ┌─────────────────────────┐
│ Text Chunks             │        │ Environmental Indicators│
│ source, page, theme     │        │ deforestation, land use │
└────────────┬────────────┘        └────────────┬────────────┘
             │                                  │
             └──────────────┬───────────────────┘
                            ▼
              ┌─────────────────────────────┐
              │ Vector Database             │
              │ Chroma / FAISS / Qdrant     │
              └──────────────┬──────────────┘
                             ▼
              ┌─────────────────────────────┐
              │ RAG Layer                   │
              │ retrieval + prompts + filters│
              └──────────────┬──────────────┘
                             ▼
              ┌─────────────────────────────┐
              │ Final Answer                │
              │ citations + limitations     │
              └─────────────────────────────┘
