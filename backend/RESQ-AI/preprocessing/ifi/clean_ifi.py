"""
India Flood Inventory (IFI) Ingestion & Preprocessing Script for RESQ-AI.

Reads raw IFI files from absolute path:
C:\\Users\\pabbu\\Downloads\\16994648

Ingests:
1. DFSI.csv (District Flood Susceptibility Index)
2. District_FloodedArea.csv (Percent Flooded Area)
3. District_FloodImpact.csv (Human Fatalities, Injured, Duration)
4. India_Flood_Inventory_v3.csv (Historical Event Inventory 1967-2023)

Standardizes columns, normalizes location names, aggregates event inventory,
and outputs processed datasets under data/processed/ifi/.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

RAW_DIR = r"C:\Users\pabbu\Downloads\16994648"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "ifi"

OUTPUT_DISTRICTS_CLEANED = OUTPUT_DIR / "ifi_districts_cleaned.csv"
OUTPUT_EVENTS_CLEANED = OUTPUT_DIR / "ifi_event_inventory_cleaned.csv"
OUTPUT_METADATA_JSON = OUTPUT_DIR / "ifi_metadata.json"


def norm_name(s):
    """Normalize district/state names for clean string matching."""
    if not isinstance(s, str):
        return ""
    return s.upper().replace('_', ' ').replace('-', ' ').replace('.', '').strip()


def run_preprocessing():
    print(f"[IFI Ingestion] Checking raw directory at: {RAW_DIR}")
    if not os.path.exists(RAW_DIR):
        raise FileNotFoundError(f"IFI directory missing at: {RAW_DIR}")

    # 1. Ingest DFSI.csv
    dfsi_path = os.path.join(RAW_DIR, "DFSI.csv")
    df_dfsi = pd.read_csv(dfsi_path)
    df_dfsi = df_dfsi.rename(columns={'Unnamed: 0': 'district_name', 'State_Name': 'state_name', 'DFSI': 'dfsi_score'})
    df_dfsi['norm_district'] = df_dfsi['district_name'].apply(norm_name)
    df_dfsi['norm_state'] = df_dfsi['state_name'].apply(norm_name)

    # 2. Ingest District_FloodedArea.csv
    area_path = os.path.join(RAW_DIR, "District_FloodedArea.csv")
    df_area = pd.read_csv(area_path)
    df_area = df_area.rename(columns={
        'Dist_Name': 'district_name',
        'Percent_Flooded_Area': 'percent_flooded_area',
        'Parmanent_Water': 'permanent_water_pct',
        'Corrected_Percent_Flooded_Area': 'corrected_flooded_area_pct'
    })
    df_area['norm_district'] = df_area['district_name'].apply(norm_name)

    # 3. Ingest District_FloodImpact.csv
    impact_path = os.path.join(RAW_DIR, "District_FloodImpact.csv")
    df_impact = pd.read_csv(impact_path)
    df_impact = df_impact.rename(columns={
        'Dist_Name': 'district_name',
        'Human_fatality': 'total_human_fatalities',
        'Human_injured': 'total_human_injured',
        'Population': 'census_population',
        'Mean_Flood_Duration': 'mean_flood_duration_days'
    })
    df_impact['norm_district'] = df_impact['district_name'].apply(norm_name)

    # Merge District-Level Tables: df_area (732) with df_impact (732) and df_dfsi (744)
    # df_area and df_impact have 1-to-1 row alignment
    merged_dist = df_area.copy()
    merged_dist['total_human_fatalities'] = df_impact['total_human_fatalities']
    merged_dist['total_human_injured'] = df_impact['total_human_injured']
    merged_dist['census_population'] = df_impact['census_population']
    merged_dist['mean_flood_duration_days'] = df_impact['mean_flood_duration_days']

    # Map DFSI scores using deduplicated district mapping
    dfsi_map = df_dfsi.groupby('norm_district')['dfsi_score'].first().to_dict()
    dfsi_state_map = df_dfsi.groupby('norm_district')['state_name'].first().to_dict()

    merged_dist['dfsi_score'] = merged_dist['norm_district'].map(dfsi_map)
    merged_dist['state_name'] = merged_dist['norm_district'].map(dfsi_state_map)


    # 4. Ingest & Process India_Flood_Inventory_v3.csv (Event-Level)
    inv_path = os.path.join(RAW_DIR, "India_Flood_Inventory_v3.csv")
    df_inv = pd.read_csv(inv_path)

    # Standardize inventory columns
    df_inv = df_inv.rename(columns={
        'UEI': 'event_uei',
        'Start Date': 'start_date',
        'End Date': 'end_date',
        'Duration(Days)': 'duration_days',
        'Main Cause': 'main_cause',
        'Districts': 'districts_raw',
        'State': 'state_raw',
        'Human fatality': 'human_fatalities',
        'Human injured': 'human_injured',
        'Human Displaced': 'human_displaced',
        'Animal Fatality': 'animal_fatalities',
        'District_LGD_Codes': 'district_lgd_codes',
        'State_Codes': 'state_codes'
    })

    # Select clean inventory columns
    inv_cols = ['event_uei', 'start_date', 'end_date', 'duration_days', 'main_cause', 'districts_raw', 'state_raw', 'human_fatalities', 'human_injured', 'district_lgd_codes', 'state_codes']
    df_inv_clean = df_inv[inv_cols].copy()
    df_inv_clean['start_date'] = pd.to_datetime(df_inv_clean['start_date'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')
    df_inv_clean['end_date'] = pd.to_datetime(df_inv_clean['end_date'], format='mixed', errors='coerce').dt.strftime('%Y-%m-%d')

    # Save Processed Datasets
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merged_dist.to_csv(OUTPUT_DISTRICTS_CLEANED, index=False)
    df_inv_clean.to_csv(OUTPUT_EVENTS_CLEANED, index=False)

    metadata_payload = {
        "dataset_name": "India Flood Inventory (IFI)",
        "source_directory": RAW_DIR,
        "district_table_rows": len(merged_dist),
        "event_inventory_rows": len(df_inv_clean),
        "temporal_range": "1967-01-08 to 2023-12-09 (57 years of recorded flood events)",
        "district_sources": ["DFSI.csv", "District_FloodedArea.csv", "District_FloodImpact.csv"],
        "event_source": "India_Flood_Inventory_v3.csv",
        "raw_directory_modified": False
    }

    with open(OUTPUT_METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)

    print(f"[IFI Ingestion] Cleaned district metrics saved to: {OUTPUT_DISTRICTS_CLEANED}")
    print(f"[IFI Ingestion] Cleaned event inventory saved to: {OUTPUT_EVENTS_CLEANED}")
    print(f"[IFI Ingestion] Metadata JSON saved to: {OUTPUT_METADATA_JSON}")

    return merged_dist, df_inv_clean, metadata_payload


if __name__ == "__main__":
    run_preprocessing()
