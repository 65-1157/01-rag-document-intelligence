# Environmental Risk Summary Prompt

## Instruction

Create a short environmental screening summary using only the provided evidence.

The summary should help an analyst understand whether a municipality or region deserves deeper review.

Do not make legal conclusions.

Do not claim illegal deforestation.

Do not assign responsibility to any company, farm, person or institution.

Use cautious analytical language.

---

## User Request

{question}

---

## Structured Evidence

{structured_evidence}

---

## Retrieved Document Evidence

{context}

---

## Required Output Format

### Environmental Screening Summary

Write a short paragraph explaining the main environmental signals.

### Main Indicators

List the main indicators used, such as:

- INPE / PRODES deforestation area;
- MapBiomas native vegetation area;
- MapBiomas agriculture area;
- MapBiomas pasture area;
- MapBiomas land-use change indicator.

### Risk Interpretation

Classify the screening signal as:

- Low attention;
- Medium attention;
- High attention.

Explain why.

### Evidence Used

List the sources and metadata used.

### Important Limitations

Explain that this is only a screening result.

Mention that the result should not be interpreted as proof of illegal activity, legal non-compliance or regulatory violation.

### Suggested Next Step

Suggest one practical next step, such as:

- review the official source document;
- inspect municipality-level time series;
- compare MapBiomas and INPE indicators;
- perform geospatial analysis in a later stage.
