# Evaluation Strategy

## 1. Overview

This project evaluates a Retrieval-Augmented Generation system for Brazilian deforestation and land-use monitoring.

The system uses two source families:

1. MapBiomas
2. INPE / TerraBrasilis

The evaluation focuses on whether the system can:

- retrieve the correct evidence;
- answer only from retrieved context;
- cite the sources used;
- avoid unsupported claims;
- explain limitations clearly;
- avoid legal or enforcement conclusions.

The goal is not only to check whether the answer sounds good, but whether the answer is grounded in traceable evidence.

---

## 2. Evaluation Layers

The evaluation is divided into three layers:

1. Retrieval evaluation
2. Answer quality evaluation
3. Safety and limitation evaluation

---

## 3. Retrieval Evaluation

Retrieval evaluation checks whether the system finds the correct documents, chunks or structured evidence before generating the answer.

### 3.1 Main Question

> Did the retriever return evidence that is relevant to the user question?

### 3.2 Suggested Metrics

| Metric | Meaning |
|---|---|
| Recall@k | Whether the correct source appears among the top-k retrieved chunks |
| Precision@k | How many of the top-k chunks are actually relevant |
| Source hit rate | Whether the expected source family was retrieved |
| Metadata accuracy | Whether filters such as source, year, biome or state worked correctly |

Recommended first version:

```text
k = 5
