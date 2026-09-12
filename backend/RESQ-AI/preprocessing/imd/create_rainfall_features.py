"""
IMD Rainfall Feature Engineering Script.

Engineers domain-specific rainfall risk features from cleaned IMD daily data.
Saves the resulting feature matrix to features/rainfall/imd_rainfall_features.csv.
"""

from pathlib import Path
import pandas as pd
import numpy as np

CLEANED_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "imd" / "imd_rainfall_cleaned.csv"
OUTPUT_FEATURE_DIR = Path(__file__).resolve().parent.parent.parent / "features" / "rainfall"
OUTPUT_FEATURE_FILE = OUTPUT_FEATURE_DIR / "imd_rainfall_features.csv"


def calc_consecutive_rainy(series_is_rainy):
    """Calculate running count of consecutive rainy days."""
    counts = []
    curr = 0
    for is_rain in series_is_rainy:
        if is_rain == 1:
            curr += 1
        else:
            curr = 0
        counts.append(curr)
    return counts


def create_features():
    print(f"[IMD Feature Eng] Reading cleaned dataset from: {CLEANED_DATA_PATH}")
    df = pd.read_csv(CLEANED_DATA_PATH)
    df['date'] = pd.to_datetime(df['date'])

    # Sort deterministically
    df = df.sort_values(by=['state', 'district', 'date']).reset_index(drop=True)

    print("[IMD Feature Eng] Engineering rainfall features per district...")

    # Group by district for rolling window calculations
    grouped = df.groupby(['state', 'district'])

    # 1. Rolling Sums
    df['rolling_3d_rainfall_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(3, min_periods=1).sum())
    df['rolling_7d_rainfall_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(7, min_periods=1).sum())
    df['rolling_14d_rainfall_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(14, min_periods=1).sum())
    df['rolling_30d_rainfall_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(30, min_periods=1).sum())

    # 2. Rolling Maxima
    df['rolling_3d_max_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(3, min_periods=1).max())
    df['rolling_7d_max_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(7, min_periods=1).max())
    df['rolling_14d_max_mm'] = grouped['daily_actual_mm'].transform(lambda x: x.rolling(14, min_periods=1).max())

    # 3. Rainfall Anomaly & Intensity
    df['rainfall_anomaly_mm'] = df['daily_actual_mm'] - df['daily_normal_mm']
    df['rainfall_intensity_ratio'] = df['daily_actual_mm'] / (df['daily_normal_mm'] + 1e-5)

    # 4. Binary Rain Intensity Flags (IMD Standards)
    df['is_rainy_day'] = (df['daily_actual_mm'] >= 2.5).astype(int)
    df['is_heavy_rainy_day'] = (df['daily_actual_mm'] >= 64.5).astype(int)
    df['is_very_heavy_rainy_day'] = (df['daily_actual_mm'] >= 115.6).astype(int)

    # 5. Consecutive Rainy Days
    df['consecutive_rainy_days'] = grouped['is_rainy_day'].transform(calc_consecutive_rainy)

    # 6. Rolling Rainy Days Count
    df['rolling_7d_rainy_days_count'] = grouped['is_rainy_day'].transform(lambda x: x.rolling(7, min_periods=1).sum())

    # Convert date back to YYYY-MM-DD string
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    # Select feature columns
    feature_cols = [
        'state', 'district', 'date',
        'daily_actual_mm', 'daily_normal_mm',
        'rolling_3d_rainfall_mm', 'rolling_7d_rainfall_mm', 'rolling_14d_rainfall_mm', 'rolling_30d_rainfall_mm',
        'rolling_3d_max_mm', 'rolling_7d_max_mm', 'rolling_14d_max_mm',
        'rainfall_anomaly_mm', 'rainfall_intensity_ratio',
        'is_rainy_day', 'is_heavy_rainy_day', 'is_very_heavy_rainy_day',
        'consecutive_rainy_days', 'rolling_7d_rainy_days_count',
        'cumulative_actual_mm', 'cumulative_normal_mm', 'monthly_actual_mm', 'monthly_normal_mm'
    ]

    df_features = df[feature_cols].copy()

    OUTPUT_FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    df_features.to_csv(OUTPUT_FEATURE_FILE, index=False)
    print(f"[IMD Feature Eng] Feature dataset successfully saved to: {OUTPUT_FEATURE_FILE}")
    print(f"[IMD Feature Eng] Final feature matrix shape: {df_features.shape}")

    return df_features


if __name__ == "__main__":
    create_features()
