# NASA GDIS (Geocoded Disasters) Quality & Inspection Report

## 1. Dataset Overview & Source Location
- **Dataset Title**: NASA Geocoded Disasters Dataset (GDIS 1960–2018)
- **Local Source Path**: `C:\Users\pabbu\Downloads\pend-gdis-1960-2018-disasterlocations-csv\pend-gdis-1960-2018-disasterlocations.csv`
- **Cleaned Target File**: `data/processed/gdis/gdis_disaster_locations_cleaned.csv`
- **Metadata Summary File**: `data/processed/gdis/gdis_metadata.json`
- **Temporal Summary File**: `data/interim/gdis_dataset_summary.json`
- **Output Feature File**: `features/disaster_history/gdis_disaster_history_features.csv`

---

## 2. Dataset Dimensions & Temporal Coverage
- **Total Global Records**: 39,953 geocoded disaster records
- **Total Columns**: 18 columns
- **Temporal Range**: `1960` to `2018` (59 unique years)
- **Global Geographic Range**: Lat $[-54.33^\circ, 68.24^\circ]$, Lon $[-177.98^\circ, 179.85^\circ]$ across 161 countries.
- **India-Specific Records**: **2,253 geocoded disaster records** across 58 unique years ($1960 - 2018$).
  - India Lat Range: $7.5255^\circ\text{ N}$ to $34.2878^\circ\text{ N}$
  - India Lon Range: $69.8037^\circ\text{ E}$ to $96.3449^\circ\text{ E}$
  - India ADM1 States: 34 states/territories

---

## 3. Data Dictionary & Field Inspection

| Field Name | Data Type | Null Count (%) | Description |
| :--- | :---: | :---: | :--- |
| `id` / `emdat_id` | `object` | 0 (0.00%) | Internal EMDAT location record identifier |
| `country` / `country_name` | `object` | 0 (0.00%) | Country name |
| `iso3` / `iso3_code` | `object` | 315 (0.79%) | ISO 3-letter country code |
| `gwno` / `gwno_code` | `float64` | 434 (1.09%) | Gleditsch and Ward country code |
| `year` / `event_year` | `int64` | 0 (0.00%) | Year of disaster occurrence |
| `geo_id` | `int64` | 0 (0.00%) | Geocoded location ID |
| `geolocation` / `geolocation_name` | `object` | 0 (0.00%) | Geocoded location feature name |
| `level` / `admin_level` | `int64` | 0 (0.00%) | Administrative level ($1$=State, $2$=District) |
| `adm1` / `adm1_state` | `object` | 0 (0.00%) | ADM1 administrative state/province |
| `adm2` / `adm2_district` | `object` | 25,883 (64.78%) | ADM2 administrative district |
| `adm3` / `adm3_subdistrict` | `object` | 37,543 (93.97%) | ADM3 administrative sub-district |
| `location` / `location_name` | `object` | 0 (0.00%) | Specific location description |
| `historical` / `is_historical_entity` | `int64` | 0 (0.00%) | Flag for historical entity changes ($0/1$) |
| `hist_country` / `hist_country_name` | `object` | 39,717 (99.41%) | Historical country name |
| `disastertype` / `disaster_type` | `object` | 0 (0.00%) | Categorical disaster classification |
| `disasterno` / `emdat_disaster_no` | `object` | 0 (0.00%) | EM-DAT event tracking number |
| `latitude` | `float64` | 0 (0.00%) | Geocoded latitude ($-90^\circ$ to $+90^\circ$) |
| `longitude` | `float64` | 0 (0.00%) | Geocoded longitude ($-180^\circ$ to $+180^\circ$) |

---

## 4. Disaster Type Breakdown

### Global Breakdown (39,953 records):
- `flood`: 17,347 (43.42%)
- `storm`: 12,323 (30.84%)
- `extreme temperature`: 3,506 (8.78%)
- `drought`: 2,938 (7.35%)
- `earthquake`: 2,403 (6.01%)
- `landslide`: 982 (2.46%)
- `volcanic activity`: 405 (1.01%)
- `mass movement (dry)`: 49 (0.12%)

### India Breakdown (2,253 records):
- `flood`: 1,172 (52.02%)
- `storm`: 394 (17.49%)
- `drought`: 315 (13.98%)
- `extreme temperature`: 206 (9.14%)
- `earthquake`: 99 (4.40%)
- `landslide`: 66 (2.93%)
- `mass movement (dry)`: 1 (0.04%)

---

## 5. Extracted Feature Matrix (`features/disaster_history/gdis_disaster_history_features.csv`)
Features extracted for all 728 districts:
- `gdis_historical_disaster_count`: Total historical disaster events recorded
- `gdis_flood_event_count`: Total flood events
- `gdis_storm_event_count`: Total storm events
- `gdis_drought_event_count`: Total drought events
- `gdis_extreme_temp_event_count`: Total extreme temperature events
- `gdis_earthquake_event_count`: Total earthquake events
- `gdis_landslide_event_count`: Total landslide events
- `gdis_unique_disaster_types_count`: Count of unique disaster types experienced
- `gdis_year_first_record`: Earliest recorded disaster year
- `gdis_year_last_record`: Latest recorded disaster year
- `gdis_recent_10yr_event_count`: Recent 10-year disaster event count (2009–2018)
- `gdis_disaster_frequency_per_decade`: Disaster events per decade

---

## 6. Verification & Data Integrity
- **Original Files Unmodified**: `C:\Users\pabbu\Downloads\pend-gdis-1960-2018-disasterlocations-csv\pend-gdis-1960-2018-disasterlocations.csv` was verified completely untouched.
- **Coordinates Validated**: 100% of latitude/longitude coordinates fall strictly within valid geographic bounds ($[-90^\circ, +90^\circ]$ and $[-180^\circ, +180^\circ]$).
- **Exact Duplicates**: 0 exact duplicate rows found.
