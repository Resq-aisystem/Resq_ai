# NASA GDIS Metadata & Provenance Report

## 1. Dataset Origin & Citation
- **Dataset Title**: NASA Geocoded Disasters Dataset (GDIS 1960–2018)
- **Local Source Path**: `C:\Users\pabbu\Downloads\pend-gdis-1960-2018-disasterlocations-csv\pend-gdis-1960-2018-disasterlocations.csv`
- **Primary Data Providers**: NASA SEDAC (Socioeconomic Data and Applications Center), CIESIN (Columbia University), and EM-DAT (Centre for Research on the Epidemiology of Disasters).
- **Temporal Span**: 1960 to 2018 (59 years).

---

## 2. Key Metadata & Data Dictionary
- **`emdat_id`**: EM-DAT internal event location record identifier.
- **`emdat_disaster_no`**: Official EM-DAT event tracking code (e.g. `2009-0631`).
- **`disaster_type`**: Categorical classification (`flood`, `storm`, `drought`, `extreme temperature`, `earthquake`, `landslide`, `mass movement (dry)`, `volcanic activity`).
- **`adm1_state`**: State or top-level administrative boundary.
- **`adm2_district`**: District or second-level administrative boundary.
- **`latitude` / `longitude`**: Geocoded spatial coordinates ($EPSG:4326$).

---

## 3. Integration into RESQ-AI Architecture
NASA GDIS provides **historical disaster occurrence and multi-hazard frequency metrics** (1960–2018).

It connects to the final RESQ-AI master dataset alongside:
- **IMD Rainfall**: Dynamic daily precipitation & antecedent wetness
- **GFSM**: Static 30m flood susceptibility metrics
- **CAMELS-IND**: Catchment hydrology, soil moisture & river runoff
- **India Flood Inventory (IFI)**: Ground-truth historical flood events and inundated area damage labels

> **PROVENANCE NOTICE**: NASA GDIS is a **historical disaster feature layer**. It does NOT contain 24–48 hour weather forecasts, future disaster probabilities, or real-time telemetry.
