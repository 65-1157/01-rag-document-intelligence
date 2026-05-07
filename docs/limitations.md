# Limitations

## 1. Overview

This project implements a Retrieval-Augmented Generation system for Brazilian deforestation and land-use monitoring using two source families:

1. MapBiomas
2. INPE / TerraBrasilis

The system is designed to organize evidence, retrieve relevant information and support environmental screening.

It is not designed to produce legal conclusions, regulatory enforcement decisions or final ESG certification.

---

## 2. Intended Use

This project may be used for:

- organizing environmental evidence;
- retrieving information from MapBiomas and INPE-related documents;
- supporting preliminary environmental screening;
- identifying municipalities or regions that may deserve deeper analysis;
- comparing land-use and deforestation indicators;
- generating cited summaries for analysts.

The system should be interpreted as a decision-support tool.

---

## 3. Non-Intended Use

This project should not be used to:

- determine illegal deforestation;
- assign legal responsibility;
- accuse a municipality, company, farm or person of environmental crime;
- determine rural property compliance;
- replace official environmental agencies;
- replace legal, agronomic or geospatial expert analysis;
- issue final ESG approval or rejection;
- make automated credit, insurance or commercial decisions without human review.

---

## 4. Data Source Limitations

The project uses MapBiomas and INPE / TerraBrasilis. These sources are highly relevant, but they may differ in purpose, methodology, spatial resolution, temporal resolution and classification logic.

### 4.1 MapBiomas

MapBiomas is useful for land-use and land-cover analysis. However:

- land-cover classes are derived from remote sensing classification;
- classification errors may occur;
- transitions between land-use classes require careful interpretation;
- municipality-level aggregation can hide local spatial variation;
- different MapBiomas collections may update or revise previous estimates;
- land-use change is not the same as legal non-compliance.

### 4.2 INPE / TerraBrasilis

INPE / TerraBrasilis is useful for official deforestation monitoring. However:

- PRODES and DETER have different purposes;
- PRODES is generally used for annual deforestation monitoring;
- DETER is alert-oriented and should not be interpreted in the same way as PRODES;
- deforestation area does not automatically imply illegal deforestation;
- official data still require methodological interpretation;
- spatial and temporal aggregation choices can affect conclusions.

---

## 5. Methodological Limitations

The project may use municipality-year as the main analytical unit.

This simplifies the analysis, but it also creates limitations:

- municipalities can be large and environmentally heterogeneous;
- deforestation may be concentrated in specific areas inside a municipality;
- municipality-level indicators may hide property-level or local patterns;
- annual aggregation may hide seasonal dynamics;
- comparison between sources may be affected by different definitions and methods.

The project may also calculate an environmental risk score.

This score is only a screening indicator. It is not a legal, regulatory or scientific final conclusion.

---

## 6. RAG System Limitations

The RAG system depends on the documents and data included in the knowledge base.

Possible limitations include:

- missing documents;
- outdated documents;
- incomplete metadata;
- poor PDF text extraction;
- incorrect chunking;
- retrieval of irrelevant chunks;
- failure to retrieve relevant chunks;
- hallucination risk if prompts and evaluation are weak;
- overconfidence if limitations are not explicitly stated.

The system must therefore be evaluated using golden questions and manual review.

---

## 7. Citation Limitations

The system should cite the evidence used in each answer.

However, citations may be limited by:

- missing page numbers;
- documents without clear structure;
- inconsistent metadata;
- source files without stable URLs;
- extracted text that does not preserve original formatting;
- tables or maps that are difficult to parse automatically.

A cited answer should still be checked against the original source when used for serious analysis.

---

## 8. Environmental Risk Score Limitations

The environmental risk score is designed to help prioritize attention.

It should not be interpreted as:

- proof of illegal activity;
- proof of environmental crime;
- proof of non-compliance;
- final ESG classification;
- official environmental diagnosis.

A high score means:

> The available indicators suggest that the municipality or region deserves deeper review.

A low score means:

> The available indicators do not show strong environmental pressure according to the selected variables, but this does not guarantee absence of risk.

---

## 9. Legal and Ethical Limitations

This project must avoid claims that can unfairly harm people, companies, farms or municipalities.

The system should not produce statements such as:

- “This municipality committed illegal deforestation.”
- “This company is guilty of environmental crime.”
- “This farm is non-compliant.”
- “This evidence proves illegal activity.”

Instead, the system should use cautious language such as:

- “The available evidence suggests environmental pressure.”
- “The indicators point to a screening signal.”
- “Further geospatial and legal analysis is required.”
- “This result is not a legal conclusion.”

---

## 10. Human Review Requirement

All relevant outputs should be reviewed by a human analyst before being used in professional decision-making.

Human review is especially important when the answer involves:

- high environmental risk;
- possible legal interpretation;
- policy recommendation;
- financial or credit decision;
- ESG screening;
- public communication;
- comparison between municipalities, companies or regions.

---

## 11. Version 1 Scope Limitation

The first version is intentionally simple.

It uses only:

- MapBiomas;
- INPE / TerraBrasilis;
- municipality-year indicators;
- selected documents and reports;
- a simple explainable risk score.

The first version does not include:

- IBGE agricultural production data;
- CAR / SICAR property-level data;
- automated legal compliance analysis;
- full geospatial polygon-level analysis;
- satellite image classification;
- real-time monitoring;
- production deployment.

---

## 12. Future Improvements

Future versions may reduce some limitations by adding:

- DETER alert layer;
- geospatial polygon-level analysis;
- municipality maps;
- property-level context where legally appropriate;
- richer metadata;
- hybrid search;
- reranking;
- automated RAG evaluation;
- expert-reviewed golden questions;
- comparison between different MapBiomas collections;
- comparison between PRODES and DETER use cases.

---

## 13. Final Principle

The project should follow this principle:

> The system should support better questions and better evidence retrieval, not replace expert judgment.

The safest interpretation of the system output is:

> An evidence-based environmental screening summary that requires human review before any operational, legal or financial decision.
