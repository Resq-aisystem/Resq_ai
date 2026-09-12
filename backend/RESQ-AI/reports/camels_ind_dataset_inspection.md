# CAMELS-IND Dataset Quality & Inspection Report

## 1. Source Path & Local Structure
- **Dataset Title**: CAMELS-IND (Catchment Attributes and Meteorology for India)
- **Local Source Path**: `C:\Users\pabbu\Downloads\CAMELS_IND_All_Catchments`
- **Processed Cleaned Catchment File**: `data/processed/camels_ind/camels_ind_catchments_cleaned.csv`
- **Processed Forcings Summary File**: `data/processed/camels_ind/camels_ind_forcings_summary.csv`
- **Metadata Summary File**: `data/processed/camels_ind/camels_ind_metadata.json`
- **Output Feature File**: `features/hydrology/camels_ind_hydrology_features.csv`

---

## 2. Catchment & Temporal Coverage
- **Total Catchments / Gauges**: 472 catchments across 16 major Indian river basins.
- **Temporal Range**: `1980-01-01` to `2020-12-31` (41 complete calendar years).
- **Total Daily Forcing Records**: 14,976 daily timesteps per catchment (7,068,672 daily observations overall across all 472 catchments).
- **Basin Distribution**:
  - Godavari: 110 catchments
  - Krishna: 64 catchments
  - Narmada: 52 catchments
  - Mahanadi: 38 catchments
  - West-Flowing Rivers South (WFRS): 32 catchments
  - Cauvery: 29 catchments
  - East-Flowing Rivers South (EFRS): 25 catchments
  - Tapi: 25 catchments
  - Others (WFRN, Mahi, Brahmani-Baitarani, EFRN, Pennar, Subernarekha, Sabarmati): 97 catchments

---

## 3. Dataset Component Inspection

### `attributes_csv/` (8 Static Attribute CSV Files):
1. `camels_ind_anth.csv` (472 rows × 26 cols): Dams, reservoir storage capacity, anthropogenic impact indices.
2. `camels_ind_clim.csv` (472 rows × 43 cols): Mean precipitation, aridity index, high/low precipitation frequencies.
3. `camels_ind_geol.csv` (472 rows × 8 cols): Subsurface porosity, permeability, dominant geology classes.
4. `camels_ind_hydro.csv` (472 rows × 74 cols): Mean runoff ($Q$), runoff ratio ($Q/P$), flow duration curve slopes.
5. `camels_ind_land.csv` (472 rows × 14 cols): Water fraction, forest/tree cover %, crops %, bare ground %, LAI.
6. `camels_ind_name.csv` (472 rows × 7 cols): CWC station names, river names, basin identifiers.
7. `camels_ind_soil.csv` (472 rows × 29 cols): Soil depth, hydraulic conductivity, available water capacity, clay/sand/silt %.
8. `camels_ind_topo.csv` (472 rows × 17 cols): Latitude, longitude, catchment area ($km^2$), mean elevation ($m$), mean slope ($^\circ$).

### `catchment_mean_forcings/` (472 Daily CSV Files):
- **Variables**: `prcp(mm/day)`, `tmax(C)`, `tmin(C)`, `tavg(C)`, `srad_lw(w/m2)`, `srad_sw(w/m2)`, `wind(m/s)`, `rel_hum(%)`, `pet_gleam(mm/day)`, `aet_gleam(mm/day)`, `evap_canopy(mm/day)`, `evap_surface(mm/day)`, `sm_lvl1(kg/m2)` to `sm_lvl4(kg/m2)`.

### `streamflow_timeseries/` (2 CSV Files):
- `streamflow_observed.csv` (14,976 rows × 475 cols): Daily observed streamflow ($m^3/s$) across CWC stream gauges.
- `lstm_pred_streamflow.csv` (14,976 rows × 475 cols): Simulated/predicted streamflow from benchmark LSTM model.

---

## 4. Missing-Value & Data Quality Analysis
- **Static Attributes**: 0 missing values across primary identifiers (`gauge_id`, `cwc_lat`, `cwc_lon`, `area`). Minor missing attributes in specific hydro/geol fields preserved as `NaN`.
- **Forcing Time Series**: 0 missing values in core daily precipitation, temperature, radiation, humidity, GLEAM PET/AET, and 4-level soil moisture series across all 472 forcing CSVs.
- **Observed Streamflow**: Observed streamflow contains missing values (average 60.33% missing per gauge) reflecting real-world hydrometric gauge downtime in historical monitoring records.
- **Duplicates**: 0 duplicate gauge IDs across attribute tables.

---

## 5. Extracted Hydrology Features
District-level features saved to `features/hydrology/camels_ind_hydrology_features.csv` (728 district records):
- `camels_aridity_index`: Catchment aridity index ($PET / P$)
- `camels_p_mean_mm_day`: Long-term mean daily precipitation ($mm/day$)
- `camels_q_mean_mm_day`: Long-term mean daily runoff ($mm/day$)
- `camels_runoff_ratio`: Catchment runoff ratio ($Q / P$)
- `camels_soil_moisture_mean_kg_m2`: Catchment mean root-zone soil moisture ($kg/m^2$)
- `camels_soil_moisture_lvl1_top`: Topsoil moisture ($kg/m^2$)
- `camels_soil_moisture_lvl4_deep`: Deep subsoil moisture ($kg/m^2$)
- `camels_soil_conductivity_top`: Topsoil hydraulic conductivity ($mm/hr$)
- `camels_soil_awc_top`: Soil available water capacity ($mm$)
- `camels_high_precip_freq_days`: High precipitation frequency ($days/year$)
- `camels_low_precip_freq_days`: Low precipitation frequency ($days/year$)
- `camels_elevation_mean_m`: Mean catchment elevation ($m$)
- `camels_slope_mean_deg`: Mean topographic slope ($^\circ$)
- `camels_forest_cover_pct`: Percentage forest cover (%)
- `camels_dam_count`: Count of dams in catchment
- `camels_dam_storage_capacity_mcm`: Total dam reservoir storage capacity ($MCM$)

---

## 6. Verification & Data Integrity
- **Original Files Unmodified**: Verified that `C:\Users\pabbu\Downloads\CAMELS_IND_All_Catchments` directory and contents remain 100% untouched.
- **No Data Fabrication**: Preserved scientific measurement units and ground-truth values without inventing labels or fake predictions.
