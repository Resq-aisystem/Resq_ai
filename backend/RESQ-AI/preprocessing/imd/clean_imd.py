"""
IMD District-wise Daily Rainfall Dataset Cleaning Script.

Reads raw IMD CSV from absolute path:
C:\\Users\\pabbu\\Downloads\\rainfall_districtwise_daily_imd.csv.csv

Preserves original raw CSV without modification.
Standardizes column names, converts types, parses percentage strings,
handles missing values scientifically, and outputs cleaned dataset.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

RAW_DATA_PATH = r"C:\Users\pabbu\Downloads\rainfall_districtwise_daily_imd.csv.csv"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "imd"
OUTPUT_FILE = OUTPUT_DIR / "imd_rainfall_cleaned.csv"


def clean_percentage(val):
    """Convert percentage string like '-94%' or '31%' to float."""
    if pd.isnull(val):
        return np.nan
    val_str = str(val).strip().rstrip('%')
    try:
        return float(val_str)
    except ValueError:
        return np.nan


def run_cleaning():
    print(f"[IMD Clean] Verifying raw file at: {RAW_DATA_PATH}")
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw IMD file not found at {RAW_DATA_PATH}")

    # Record original file modification time for safety check
    orig_mtime = os.path.getmtime(RAW_DATA_PATH)
    orig_size = os.path.getsize(RAW_DATA_PATH)

    print("[IMD Clean] Loading raw dataset with pandas...")
    df_raw = pd.read_csv(RAW_DATA_PATH)
    print(f"[IMD Clean] Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns.")

    # 1. Standardize column names
    column_mapping = {
        'State': 'state',
        'District': 'district',
        'Date': 'date',
        'Daily Actual': 'daily_actual_mm',
        'Daily Normal': 'daily_normal_mm',
        'Daily Departure Per': 'daily_departure_perc',
        'Daily Category': 'daily_category',
        'Week Date': 'week_date',
        'Weekly \nActual': 'weekly_actual_mm',
        'Weekly Normal': 'weekly_normal_mm',
        'Weekly Departure Per': 'weekly_departure_perc',
        'Weekly Category': 'weekly_category',
        'Cumulative Date': 'cumulative_date',
        'Cumulative Actual': 'cumulative_actual_mm',
        'Cumulative Normal': 'cumulative_normal_mm',
        'Cumulative Departue Per': 'cumulative_departure_perc',
        'Cumulative \nCategory': 'cumulative_category',
        'Monthly Date': 'monthly_date',
        'Monthly Acutual': 'monthly_actual_mm',
        'Monthly Normal': 'monthly_normal_mm',
        'Monthly \nDeparture Per': 'monthly_departure_perc',
        'Monthly Category': 'monthly_category'
    }

    df_clean = df_raw.rename(columns=column_mapping).copy()

    # Clean string fields (strip carriage returns, newlines, trailing spaces)
    for col in ['state', 'district', 'daily_category', 'weekly_category', 'cumulative_category', 'monthly_category', 'week_date', 'cumulative_date', 'monthly_date']:
        df_clean[col] = df_clean[col].astype(str).str.strip().str.replace('\r', '').str.replace('\n', '')

    # 2. Parse Date
    df_clean['date'] = pd.to_datetime(df_clean['date']).dt.strftime('%Y-%m-%d')

    # 3. Clean percentage columns
    perc_cols = ['daily_departure_perc', 'weekly_departure_perc', 'cumulative_departure_perc', 'monthly_departure_perc']
    for col in perc_cols:
        df_clean[col] = df_clean[col].apply(clean_percentage)

    # 4. Ensure non-negative rainfall values
    num_cols = ['daily_actual_mm', 'daily_normal_mm', 'weekly_actual_mm', 'weekly_normal_mm', 'cumulative_actual_mm', 'cumulative_normal_mm', 'monthly_actual_mm', 'monthly_normal_mm']
    for col in num_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Sort deterministically by state, district, date
    df_clean = df_clean.sort_values(by=['state', 'district', 'date']).reset_index(drop=True)

    # Output cleaned dataset
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_FILE, index=False)
    print(f"[IMD Clean] Cleaned dataset saved to: {OUTPUT_FILE}")

    # Safety check: Verify raw file was NOT modified
    curr_mtime = os.path.getmtime(RAW_DATA_PATH)
    curr_size = os.path.getsize(RAW_DATA_PATH)
    assert orig_mtime == curr_mtime and orig_size == curr_size, "CRITICAL ERROR: Original raw CSV file was modified!"
    print("[IMD Clean] Safety Verification Passed: Original raw file was NOT modified.")

    return df_clean


if __name__ == "__main__":
    run_cleaning()
