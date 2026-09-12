"""
Generates data/interim/imd_dataset_summary.json from actual IMD dataset statistics.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np

RAW_DATA_PATH = r"C:\Users\pabbu\Downloads\rainfall_districtwise_daily_imd.csv.csv"
CLEANED_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "imd" / "imd_rainfall_cleaned.csv"
OUTPUT_JSON_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "interim" / "imd_dataset_summary.json"


def generate_summary():
    df_raw = pd.read_csv(RAW_DATA_PATH)
    df_clean = pd.read_csv(CLEANED_DATA_PATH)

    missing_summary = {}
    for col in df_raw.columns:
        null_cnt = int(df_raw[col].isnull().sum())
        missing_summary[col] = {
            "null_count": null_cnt,
            "null_percentage": round(float(df_raw[col].isnull().mean() * 100), 2)
        }

    rainfall_stats = {}
    num_cols_map = {
        'daily_actual_mm': 'Daily Actual',
        'daily_normal_mm': 'Daily Normal',
        'weekly_actual_mm': 'Weekly Actual',
        'cumulative_actual_mm': 'Cumulative Actual',
        'monthly_actual_mm': 'Monthly Actual'
    }

    for clean_col, orig_name in num_cols_map.items():
        series = df_clean[clean_col]
        rainfall_stats[orig_name] = {
            "min_mm": round(float(series.min()), 2),
            "max_mm": round(float(series.max()), 2),
            "mean_mm": round(float(series.mean()), 2),
            "median_mm": round(float(series.median()), 2),
            "std_mm": round(float(series.std()), 2),
            "zero_count": int((series == 0).sum()),
            "zero_percentage": round(float((series == 0).mean() * 100), 2),
            "negative_count": int((series < 0).sum())
        }

    summary_data = {
        "dataset_name": "IMD District-wise Daily Rainfall Dataset",
        "raw_file_path": RAW_DATA_PATH,
        "processed_file_path": str(CLEANED_DATA_PATH),
        "row_count": len(df_raw),
        "column_count": len(df_raw.columns),
        "raw_columns": df_raw.columns.tolist(),
        "cleaned_columns": df_clean.columns.tolist(),
        "unique_states": int(df_clean['state'].nunique()),
        "unique_districts": int(df_clean['district'].nunique()),
        "date_range": {
            "min_date": str(df_clean['date'].min()),
            "max_date": str(df_clean['date'].max()),
            "unique_days": int(df_clean['date'].nunique())
        },
        "missing_value_summary": missing_summary,
        "duplicate_count": int(df_raw.duplicated().sum()),
        "rainfall_statistics": rainfall_stats,
        "cleaning_summary": {
            "renamed_columns": len(df_raw.columns),
            "parsed_date_format": "YYYY-MM-DD",
            "parsed_percentage_columns": ["daily_departure_perc", "weekly_departure_perc", "cumulative_departure_perc", "monthly_departure_perc"],
            "rows_removed": 0,
            "rows_retained": len(df_clean),
            "raw_file_modified": False
        }
    }

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"[IMD Summary] Generated machine-readable summary at: {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    generate_summary()
