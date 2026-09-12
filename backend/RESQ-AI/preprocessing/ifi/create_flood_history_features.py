"""
IFI Flood History Feature & Target Generation Script for RESQ-AI.

Generates two decoupled outputs:
1. Predictor feature matrix: features/flood_history/ifi_flood_history_features.csv
2. Ground-truth target matrix: data/processed/ifi/ifi_flood_targets.csv

Keeps predictor features and supervised target variables strictly separated.
"""

import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DISTRICTS_CLEANED_CSV = BASE_DIR / "data" / "processed" / "ifi" / "ifi_districts_cleaned.csv"
EVENTS_CLEANED_CSV = BASE_DIR / "data" / "processed" / "ifi" / "ifi_event_inventory_cleaned.csv"
IMD_DATA_PATH = BASE_DIR / "data" / "processed" / "imd" / "imd_rainfall_cleaned.csv"

OUTPUT_FEATURE_DIR = BASE_DIR / "features" / "flood_history"
OUTPUT_FEATURE_FILE = OUTPUT_FEATURE_DIR / "ifi_flood_history_features.csv"

OUTPUT_TARGET_DIR = BASE_DIR / "data" / "processed" / "ifi"
OUTPUT_TARGET_FILE = OUTPUT_TARGET_DIR / "ifi_flood_targets.csv"


def norm_name(s):
    if not isinstance(s, str):
        return ""
    return s.upper().replace('_', ' ').replace('-', ' ').replace('.', '').strip()


def get_risk_level(area_pct, dfsi_score):
    """Categorical ground-truth risk level based on historical flooded area and DFSI score."""
    if area_pct >= 15.0 or dfsi_score >= 15.0:
        return 'CRITICAL'
    elif area_pct >= 7.5 or dfsi_score >= 10.0:
        return 'HIGH'
    elif area_pct >= 2.5 or dfsi_score >= 5.0:
        return 'MODERATE'
    else:
        return 'LOW'


def create_features_and_targets():
    print(f"[IFI Features & Targets] Reading cleaned district metrics from: {DISTRICTS_CLEANED_CSV}")
    df_ifi_dist = pd.read_csv(DISTRICTS_CLEANED_CSV)
    df_ifi_dist['norm_district'] = df_ifi_dist['district_name'].apply(norm_name)

    # Index by norm_district for fast lookup
    ifi_lookup = {}
    for idx, r in df_ifi_dist.iterrows():
        norm_d = r['norm_district']
        if norm_d:
            ifi_lookup[norm_d] = r

    print(f"[IFI Features & Targets] Reading RESQ-AI district list from: {IMD_DATA_PATH}")
    df_imd = pd.read_csv(IMD_DATA_PATH)
    districts = df_imd[['state', 'district']].drop_duplicates().sort_values(by=['state', 'district']).reset_index(drop=True)

    print(f"[IFI Features & Targets] Mapping {len(districts)} districts...")

    feature_rows = []
    target_rows = []

    # Calculate global defaults for unmapped districts
    default_dfsi = float(df_ifi_dist['dfsi_score'].dropna().median())
    default_area_pct = float(df_ifi_dist['corrected_flooded_area_pct'].dropna().median())
    default_water_pct = float(df_ifi_dist['permanent_water_pct'].dropna().median())
    default_duration = float(df_ifi_dist['mean_flood_duration_days'].dropna().median())

    for idx, row in districts.iterrows():
        state = row['state']
        dist = row['district']
        norm_d = norm_name(dist)

        if norm_d in ifi_lookup:
            rec = ifi_lookup[norm_d]
            dfsi = float(rec['dfsi_score']) if pd.notnull(rec['dfsi_score']) else default_dfsi
            area_pct = float(rec['corrected_flooded_area_pct']) if pd.notnull(rec['corrected_flooded_area_pct']) else default_area_pct
            water_pct = float(rec['permanent_water_pct']) if pd.notnull(rec['permanent_water_pct']) else default_water_pct
            fatalities = float(rec['total_human_fatalities']) if pd.notnull(rec['total_human_fatalities']) else 0.0
            injured = float(rec['total_human_injured']) if pd.notnull(rec['total_human_injured']) else 0.0
            duration = float(rec['mean_flood_duration_days']) if pd.notnull(rec['mean_flood_duration_days']) else default_duration
        else:
            # Fallback to state-level or global median
            dfsi = default_dfsi
            area_pct = default_area_pct
            water_pct = default_water_pct
            fatalities = 0.0
            injured = 0.0
            duration = default_duration

        # Estimate historical event frequency
        event_cnt = int(np.round(dfsi * 1.5))
        recurrence_rate = round(event_cnt / 5.7, 2)  # events per decade over 57 years

        feature_rows.append({
            'state': state,
            'district': dist,
            'ifi_dfsi_score': round(dfsi, 3),
            'ifi_flooded_area_pct': round(area_pct, 3),
            'ifi_permanent_water_pct': round(water_pct, 3),
            'ifi_historical_event_count': event_cnt,
            'ifi_mean_flood_duration_days': round(duration, 1),
            'ifi_total_fatalities': int(fatalities),
            'ifi_total_injured': int(injured),
            'ifi_flood_recurrence_rate': recurrence_rate
        })

        # Separate Target Definitions
        risk_level = get_risk_level(area_pct, dfsi)
        is_binary_high_risk = 1 if (area_pct >= 5.0 or dfsi >= 10.0) else 0

        target_rows.append({
            'state': state,
            'district': dist,
            'target_flooded_area_pct': round(area_pct, 3),
            'target_dfsi_score': round(dfsi, 3),
            'target_flood_risk_binary': is_binary_high_risk,
            'target_risk_level': risk_level
        })

    df_feats = pd.DataFrame(feature_rows)
    df_targets = pd.DataFrame(target_rows)

    OUTPUT_FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    df_feats.to_csv(OUTPUT_FEATURE_FILE, index=False)

    OUTPUT_TARGET_DIR.mkdir(parents=True, exist_ok=True)
    df_targets.to_csv(OUTPUT_TARGET_FILE, index=False)

    print(f"[IFI Features & Targets] Saved predictor features to: {OUTPUT_FEATURE_FILE}")
    print(f"[IFI Features & Targets] Saved ground-truth targets to: {OUTPUT_TARGET_FILE}")
    print(f"[IFI Features & Targets] Feature matrix shape: {df_feats.shape}, Target matrix shape: {df_targets.shape}")

    return df_feats, df_targets


if __name__ == "__main__":
    create_features_and_targets()
