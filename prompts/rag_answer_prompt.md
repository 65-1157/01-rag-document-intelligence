# RAG Answer Prompt

## Instruction

Answer the user question using only the retrieved context.

If the retrieved context does not contain enough evidence, say that the available evidence is insufficient.

Do not use external knowledge unless it is explicitly included in the retrieved context.

Do not invent citations.

Do not make legal or enforcement conclusions.

---

## User Question

{question}

---

## Retrieved Context

{context}

---

## Required Answer Format

### Answer

Provide a direct answer to the question.

### Evidence Used

List the evidence used to produce the answer.

For each evidence item, include available metadata such as:

- source;
- document name;
- page;
- year;
- biome;
- state;
- municipality;
- dataset field.

### Interpretation

Explain what the evidence suggests.

Use cautious language.

### Limitations

State the main limitations of the answer.

Mention if the context is incomplete, if the data are aggregated, or if the sources use different methodologies.

### Confidence Level

Classify the confidence level as:

- High;
- Medium;
- Low.

Use High only when the retrieved context directly supports the answer.
Use Medium when the answer is supported but incomplete.
Use Low when the evidence is weak, indirect or limited.
