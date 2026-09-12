# RESQ-AI Data Management Governance

## Principles
1. **RAW DATA IMMUTABILITY**: Files stored under `data/raw/` must NEVER be modified, renamed in place, cleaned in place, or overwritten. They represent the single source of ground truth from primary data providers.
2. **ISOLATED STAGING**:
   - `data/raw/`: Original unedited files received from primary sources.
   - `data/interim/`: Intermediate files during multi-stage cleaning and transformation.
   - `data/processed/`: Standardized, cleaned, and validated dataset artifacts ready for feature engineering.
3. **DATASET SUBDIRECTORIES**:
   - `imd/`: IMD District-wise Daily Rainfall data
   - `gfsm/`: GFSM Global Flood Susceptibility Map data
   - `camels_ind/`: CAMELS-IND Catchment Attributes & Meteorology data
   - `ifi/`: India Flood Inventory data (DFSI, District_FloodedArea, District_FloodImpact, India_Flood_Inventory_v3)
   - `gdis/`: NASA GDIS Geocoded Disasters dataset
