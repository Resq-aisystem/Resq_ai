"""
Generates data/interim/gdis_dataset_summary.json from actual NASA GDIS dataset statistics.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np

CLEANED_CSV_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "gdis" / "gdis_disaster_locations_cleaned.csv"
OUTPUT_JSON_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "interim" / "gdis_dataset_summary.json"


def generate_summary():
    df = pd.read_csv(CLEANED_CSV_PATH)
    df_ind = df[(df['country_name'].str.upper() == 'INDIA') | (df['iso3_code'] == 'IND')].copy()

    records_per_year_global = df['event_year'].value_counts().sort_index().to_dict()
    records_per_year_india = df_ind['event_year'].value_counts().sort_index().to_dict()

    summary_data = {
        "dataset_name": "NASA GDIS (Geocoded Disasters) Summary",
        "global_total_records": len(df),
        "india_total_records": len(df_ind),
        "temporal_coverage": {
            "earliest_year": int(df['event_year'].min()),
            "latest_year": int(df['event_year'].max()),
            "total_unique_years": int(df['event_year'].nunique())
        },
        "geographic_extent_global": {
            "min_latitude": float(df['latitude'].min()),
            "max_latitude": float(df['latitude'].max()),
            "min_longitude": float(df['longitude'].min()),
            "max_longitude": float(df['longitude'].max()),
            "total_countries": int(df['country_name'].nunique())
        },
        "geographic_extent_india": {
            "min_latitude": float(df_ind['latitude'].min()),
            "max_latitude": float(df_ind['latitude'].max()),
            "min_longitude": float(df_ind['longitude'].min()),
            "max_longitude": float(df_ind['longitude'].max()),
            "total_adm1_states": int(df_ind['adm1_state'].nunique())
        },
        "disaster_types_global": df['disaster_type'].value_counts().to_dict(),
        "disaster_types_india": df_ind['disaster_type'].value_counts().to_dict(),
        "records_per_year_india": records_per_year_india
    }

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"[NASA GDIS Summary] Saved temporal summary JSON to: {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    generate_summary()
