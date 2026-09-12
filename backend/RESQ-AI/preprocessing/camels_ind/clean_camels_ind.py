"""
CAMELS-IND Ingestion & Preprocessing Script for RESQ-AI.

Reads raw CAMELS-IND files from absolute path:
C:\\Users\\pabbu\\Downloads\\CAMELS_IND_All_Catchments

Ingests 8 static attribute files, 472 catchment forcing time series, and streamflow datasets.
Merges static attributes into a clean master catchment table.
Calculates forcing summaries across all catchments.
Preserves original raw CAMELS-IND directory without modification.
Saves processed datasets under data/processed/camels_ind/.
"""

import glob
import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

RAW_DIR = r"C:\Users\pabbu\Downloads\CAMELS_IND_All_Catchments"
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "camels_ind"
OUTPUT_CATCHMENTS_FILE = OUTPUT_DIR / "camels_ind_catchments_cleaned.csv"
OUTPUT_FORCINGS_SUMMARY_FILE = OUTPUT_DIR / "camels_ind_forcings_summary.csv"
OUTPUT_METADATA_JSON = OUTPUT_DIR / "camels_ind_metadata.json"


def run_preprocessing():
    print(f"[CAMELS-IND Ingestion] Checking raw directory at: {RAW_DIR}")
    if not os.path.exists(RAW_DIR):
        raise FileNotFoundError(f"CAMELS-IND directory missing at {RAW_DIR}")

    # 1. Ingest Static Attributes
    attr_dir = os.path.join(RAW_DIR, "attributes_csv")
    attr_files = sorted(glob.glob(os.path.join(attr_dir, "*.csv")))
    print(f"[CAMELS-IND Ingestion] Found {len(attr_files)} static attribute files.")

    merged_attr = None
    for f in attr_files:
        df = pd.read_csv(f)
        # Ensure gauge_id is 5-character string zero-padded
        if 'gauge_id' in df.columns:
            df['gauge_id'] = df['gauge_id'].astype(str).str.zfill(5)

        if merged_attr is None:
            merged_attr = df
        else:
            # Drop duplicate columns before merging
            cols_to_use = [c for c in df.columns if c not in merged_attr.columns or c == 'gauge_id']
            merged_attr = pd.merge(merged_attr, df[cols_to_use], on='gauge_id', how='outer')

    print(f"[CAMELS-IND Ingestion] Merged Catchment Attributes Shape: {merged_attr.shape}")

    # 2. Ingest Forcings Summaries across 472 Catchments
    forcings_dir = os.path.join(RAW_DIR, "catchment_mean_forcings")
    forcing_files = sorted(glob.glob(os.path.join(forcings_dir, "*.csv")))
    print(f"[CAMELS-IND Ingestion] Processing {len(forcing_files)} catchment forcing files...")

    forcing_summaries = []
    for f_path in forcing_files:
        gauge_id = os.path.basename(f_path).replace('.csv', '').zfill(5)
        df_f = pd.read_csv(f_path)

        # Calculate mean climatology across 1980-2020 (14,976 daily records)
        f_mean = {
            'gauge_id': gauge_id,
            'forcing_rows': len(df_f),
            'start_year': int(df_f['year'].min()),
            'end_year': int(df_f['year'].max()),
            'mean_daily_prcp_mm': round(float(df_f['prcp(mm/day)'].mean()), 3),
            'max_daily_prcp_mm': round(float(df_f['prcp(mm/day)'].max()), 2),
            'mean_tavg_c': round(float(df_f['tavg(C)'].mean()), 2),
            'mean_pet_gleam_mm': round(float(df_f['pet_gleam(mm/day)'].mean()), 3),
            'mean_aet_gleam_mm': round(float(df_f['aet_gleam(mm/day)'].mean()), 3),
            'mean_sm_lvl1_kg_m2': round(float(df_f['sm_lvl1(kg/m2)'].mean()), 2),
            'mean_sm_lvl2_kg_m2': round(float(df_f['sm_lvl2(kg/m2)'].mean()), 2),
            'mean_sm_lvl3_kg_m2': round(float(df_f['sm_lvl3(kg/m2)'].mean()), 2),
            'mean_sm_lvl4_kg_m2': round(float(df_f['sm_lvl4(kg/m2)'].mean()), 2),
            'mean_sm_rootzone_kg_m2': round(float((df_f['sm_lvl1(kg/m2)'] + df_f['sm_lvl2(kg/m2)'] + df_f['sm_lvl3(kg/m2)']).mean()), 2)
        }
        forcing_summaries.append(f_mean)

    df_forcings_summary = pd.DataFrame(forcing_summaries)

    # 3. Streamflow Observed Data Overview
    sf_path = os.path.join(RAW_DIR, "streamflow_timeseries", "streamflow_observed.csv")
    df_sf = pd.read_csv(sf_path)
    sf_gauge_count = len([c for c in df_sf.columns if c not in ['year', 'month', 'day']])

    # Save Processed Datasets
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    merged_attr.to_csv(OUTPUT_CATCHMENTS_FILE, index=False)
    df_forcings_summary.to_csv(OUTPUT_FORCINGS_SUMMARY_FILE, index=False)

    metadata_payload = {
        "dataset_name": "CAMELS-IND Catchment Attributes & Meteorology Dataset",
        "source_directory": RAW_DIR,
        "total_catchments": len(merged_attr),
        "total_forcing_files": len(forcing_files),
        "streamflow_gauges_count": sf_gauge_count,
        "temporal_range": "1980-01-01 to 2020-12-31 (14,976 daily timesteps, 41 years)",
        "attribute_categories": ["anth", "clim", "geol", "hydro", "land", "name", "soil", "topo"],
        "attributes_merged_columns": len(merged_attr.columns),
        "raw_directory_modified": False
    }

    with open(OUTPUT_METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata_payload, f, indent=2)

    print(f"[CAMELS-IND Ingestion] Cleaned catchments saved to: {OUTPUT_CATCHMENTS_FILE}")
    print(f"[CAMELS-IND Ingestion] Forcings summary saved to: {OUTPUT_FORCINGS_SUMMARY_FILE}")
    print(f"[CAMELS-IND Ingestion] Metadata summary saved to: {OUTPUT_METADATA_JSON}")

    return merged_attr, df_forcings_summary, metadata_payload


if __name__ == "__main__":
    run_preprocessing()
