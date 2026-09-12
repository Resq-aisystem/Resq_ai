# CAMELS-IND Metadata & Provenance Report

## 1. Dataset Origin & Citation
- **Dataset Title**: CAMELS-IND (Catchment Attributes and Meteorology for India)
- **Local Source Directory**: `C:\Users\pabbu\Downloads\CAMELS_IND_All_Catchments`
- **Primary Data Providers**: Central Water Commission (CWC), India Meteorological Department (IMD), GLEAM, and Indian Institute of Technology (IIT).
- **Temporal Span**: 1980-01-01 to 2020-12-31 (41 years).

---

## 2. Parameter Definitions & Scientific Units
- **`prcp(mm/day)`**: Daily precipitation depth ($mm/day$).
- **`pet_gleam(mm/day)`**: Potential Evapotranspiration from GLEAM ($mm/day$).
- **`aet_gleam(mm/day)`**: Actual Evapotranspiration from GLEAM ($mm/day$).
- **`sm_lvl1(kg/m2)`**: Soil moisture in top layer (0-7 cm depth, $kg/m^2$).
- **`sm_lvl2(kg/m2)`**: Soil moisture in second layer (7-28 cm depth, $kg/m^2$).
- **`sm_lvl3(kg/m2)`**: Soil moisture in third layer (28-100 cm depth, $kg/m^2$).
- **`sm_lvl4(kg/m2)`**: Soil moisture in deep root layer (100-289 cm depth, $kg/m^2$).
- **`runoff_ratio`**: Dimensionless ratio of long-term mean runoff ($Q$) to long-term mean precipitation ($P$).
- **`aridity_index`**: Dimensionless ratio of potential evapotranspiration ($PET$) to precipitation ($P$).

---

## 3. Integration into RESQ-AI Architecture
CAMELS-IND provides static catchment attributes, hydrological characteristics, and root-zone soil moisture metrics.

It connects to the final RESQ-AI master dataset alongside:
- **IMD Rainfall**: Dynamic daily precipitation & antecedent wetness
- **GFSM**: Static 30m flood susceptibility metrics
- **India Flood Inventory (IFI)**: Ground-truth historical flood inundation and severity impact labels
- **NASA GDIS**: Geocoded historical disaster events

> **PROVENANCE NOTICE**: CAMELS-IND is an **input hydrological feature layer**. It does NOT contain future weather forecasts, population counts, or standalone flood predictions.
