# Data Sources

## 1. Overview

This project uses two data source families:

1. MapBiomas
2. INPE / TerraBrasilis

The goal is to build a Retrieval-Augmented Generation system for Brazilian deforestation and land-use monitoring using reliable environmental evidence.

The system will combine:

- structured environmental indicators;
- technical documents and reports;
- metadata about source, year, biome, state and municipality;
- retrieval-based answers with citations and limitations.

This first version keeps the scope intentionally simple. It does not use IBGE, CAR/SICAR or agricultural production datasets.

---

## 2. Source Summary

| Source | Institution / Platform | Type | Main Use in the Project |
|---|---|---|---|
| MapBiomas | MapBiomas Network | Structured, geospatial, reports | Land use, land cover, vegetation loss, agriculture and pasture expansion |
| INPE / TerraBrasilis | INPE | Structured, geospatial, dashboards, reports | Official deforestation monitoring through PRODES and, optionally, DETER |

---

## 3. MapBiomas

MapBiomas is used to represent land-use and land-cover dynamics in Brazil.

Expected information includes:

- forest area;
- native vegetation area;
- agriculture area;
- pasture area;
- land-use and land-cover transitions;
- municipality-level statistics;
- biome-level statistics;
- technical reports and documentation.

In this project, MapBiomas supports both:

1. structured environmental indicators;
2. document-based evidence for the RAG system.

### Expected role in the pipeline

MapBiomas data will be used to create variables such as:

| Variable | Description |
|---|---|
| `mapbiomas_forest_area_ha` | Forest area in hectares |
| `mapbiomas_native_vegetation_area_ha` | Native vegetation area in hectares |
| `mapbiomas_agriculture_area_ha` | Agriculture area in hectares |
| `mapbiomas_pasture_area_ha` | Pasture area in hectares |
| `mapbiomas_land_use_change_ha` | Land-use change indicator |

---

## 4. INPE / TerraBrasilis

INPE / TerraBrasilis is used to represent official deforestation monitoring evidence.

Expected information includes:

- PRODES annual deforestation data;
- DETER alert data, if used in a later version;
- geographic deforestation data;
- official dashboards;
- technical documentation.

In this project, INPE supports:

1. official deforestation indicators;
2. environmental evidence retrieval;
3. risk explanation for selected municipalities or regions.

### Expected role in the pipeline

INPE data will be used to create variables such as:

| Variable | Description |
|---|---|
| `inpe_prodes_deforestation_area_ha` | Annual deforestation area from PRODES |
| `inpe_deter_alert_area_ha` | Alert area from DETER, optional for version 2 |

For version 1, the recommended approach is to prioritize PRODES and keep DETER as a later improvement.

---

## 5. Integration Strategy

The project uses municipality-year as the main analytical unit.

The expected structured table is:

| Column | Description |
|---|---|
| `municipality_code` | Official municipality code |
| `municipality_name` | Municipality name |
| `state` | Brazilian state |
| `biome` | Brazilian biome |
| `year` | Reference year |
| `mapbiomas_forest_area_ha` | Forest area from MapBiomas |
| `mapbiomas_native_vegetation_area_ha` | Native vegetation area from MapBiomas |
| `mapbiomas_agriculture_area_ha` | Agriculture area from MapBiomas |
| `mapbiomas_pasture_area_ha` | Pasture area from MapBiomas |
| `mapbiomas_land_use_change_ha` | Land-use change indicator |
| `inpe_prodes_deforestation_area_ha` | Annual deforestation from INPE / PRODES |
| `environmental_risk_score` | Explainable environmental screening score |
| `environmental_risk_class` | Low, medium or high risk class |

---

## 6. RAG Usage

The RAG system will use these data sources in two ways.

### 6.1 Document retrieval

Technical reports, methodological documents and source descriptions will be parsed, chunked and indexed in a vector database.

Each text chunk should include metadata such as:

| Metadata Field | Description |
|---|---|
| `source` | MapBiomas or INPE |
| `document_name` | Name of the report or document |
| `year` | Reference year |
| `page` | Page number, when available |
| `theme` | Deforestation, land use, methodology, alerts, etc. |
| `biome` | Related biome, when available |
| `state` | Related state, when available |

### 6.2 Structured evidence

The municipality-year panel will be used to support answers with numerical evidence.

Example:

> Municipality X showed increased deforestation according to INPE / PRODES and reduction of native vegetation according to MapBiomas.

---

## 7. Environmental Risk Score

The first version may use a simple and explainable screening score.

Suggested formula:

```text
environmental_risk_score =
    0.50 * normalized_inpe_prodes_deforestation
  + 0.30 * normalized_mapbiomas_native_vegetation_loss
  + 0.20 * normalized_mapbiomas_agriculture_or_pasture_expansion
