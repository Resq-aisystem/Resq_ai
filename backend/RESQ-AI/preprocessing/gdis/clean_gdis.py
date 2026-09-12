"""
NASA GDIS (Geocoded Disasters) Ingestion & Preprocessing Script for RESQ-AI.

Reads raw NASA GDIS dataset from absolute path:
C:\\Users\\pabbu\\Downloads\\pend-gdis-1960-2018-disasterlocations-csv\\pend-gdis-1960-2018-disasterlocations.csv

Standardizes column names, parses dates/years, validates coordinates,
filters India disaster events while preserving global data provenance,
and outputs cleaned dataset under data/processed/gdis/gdis_disaster_locations_cleaned.csv.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

RAW_CSV_PATH = r"C:\Users\pabbu\Downloads\pend-gdis-1960-2018-disasterlocations-csv\pend-gdis-1960-2018-disasterlocations.csv"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "gdis"
OUTPUT_CLEANED_CSV = OUTPUT_DIR / "gdis_disaster_locations_cleaned.csv"
OUTPUT_METADATA_JSON = OUTPUT_DIR / "gdis_metadata.json"


def run_cleaning():
    print(f"[NASA GDIS Clean] Loading raw CSV from: {RAW_CSV_PATH}")
    if not os.path.exists(RAW_CSV_PATH):
        raise FileNotFoundError(f"Raw NASA GDIS file missing at: {RAW_CSV_PATH}")

    df_raw = pd.read_csv(RAW_CSV_PATH)
    print(f"[NASA GDIS Clean] Ingested {len(df_raw)} rows, {len(df_raw.columns)} columns.")

    # Column name standardization
    col_mapping = {
        'id': 'emdat_id',
        'country': 'country_name',
        'iso3': 'iso3_code',
        'gwno': 'gwno_code',
        'year': 'event_year',
        'geo_id': 'geo_id',
        'geolocation': 'geolocation_name',
        'level': 'admin_level',
        'adm1': 'adm1_state',
        'adm2': 'adm2_district',
        'adm3': 'adm3_subdistrict',
        'location': 'location_name',
        'historical': 'is_historical_entity',
        'hist_country': 'hist_country_name',
        'disastertype': 'disaster_type',
        'disasterno': 'emdat_disaster_no',
        'latitude': 'latitude',
        'longitude': 'longitude'
    }

    df_clean = df_raw.rename(columns=col_mapping).copy()

    # 1. Coordinate Range Validation
    valid_coords = (df_clean['latitude'].between(-90.0, 90.0)) & (df_clean['longitude'].between(-180.0, 180.0))
    print(f"[NASA GDIS Clean] Valid coordinates: {valid_coords.sum()} / {len(df_clean)}")

    # 2. String Standardization
    string_cols = ['country_name', 'iso3_code', 'geolocation_name', 'adm1_state', 'adm2_district', 'location_name', 'disaster_type', 'emdat_disaster_no']
    for col in string_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()

    # 3. Exact Duplicate Removal
    orig_len = len(df_clean)
    df_clean = df_clean.drop_duplicates().reset_index(drop=True)
    dups_removed = orig_len - len(df_clean)
    print(f"[NASA GDIS Clean] Removed {dups_removed} exact duplicate rows.")

    # Output Cleaned Dataset
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_CLEANED_CSV, index=False)

    # Filter India-specific slice for RESQ-AI
    df_india = df_clean[(df_clean['country_name'].str.upper() == 'INDIA') | (df_clean['iso3_code'] == 'IND')].copy()

    metadata_payload = {
        "dataset_name": "NASA GDIS (Geocoded Disasters) Dataset",
        "source_filepath": RAW_CSV_PATH,
        "global_records_count": len(df_clean),
        "india_records_count": len(df_india),
        "columns_count": len(df_clean.columns),
        "temporal_range": {
            "min_year": int(df_clean['event_year'].min()),
            "max_year": int(df_clean['event_year'].max()),
            "unique_years_count": int(df_clean['event_year'].nunique())
        },
        "india_temporal_range": {
            "min_year": int(df_india['event_year'].min()),
            "max_year": int(df_india['event_year'].max()),
            "unique_years_count": int(df_india['event_year'].nunique())
        },
        "global_disaster_types": df_clean['disaster_type'].value_counts().to_dict(),
        "india_disaster_types": df_india['disaster_type'].value_counts().to_dict(),
        "duplicates_removed": dups_removed,
        "raw_file_modified": False
    }

    with open(OUTPUT_METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)

    print(f"[NASA GDIS Clean] Saved cleaned dataset to: {OUTPUT_CLEANED_CSV}")
    print(f"[NASA GDIS Clean] Saved metadata summary to: {OUTPUT_METADATA_JSON}")

    return df_clean, df_india, metadata_payload


if __name__ == "__main__":
    run_cleaning()
