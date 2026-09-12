"""
NASA GDIS Historical Disaster Feature Generation Script for RESQ-AI.

Extracts district-level historical disaster occurrence and type frequency features (1960-2018):
- gdis_historical_disaster_count
- gdis_flood_event_count
- gdis_storm_event_count
- gdis_drought_event_count
- gdis_extreme_temp_event_count
- gdis_earthquake_event_count
- gdis_landslide_event_count
- gdis_unique_disaster_types_count
- gdis_year_first_record
- gdis_year_last_record
- gdis_recent_10yr_event_count
- gdis_disaster_frequency_per_decade

Saves output feature matrix to features/disaster_history/gdis_disaster_history_features.csv.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CLEANED_GDIS_CSV = BASE_DIR / "data" / "processed" / "gdis" / "gdis_disaster_locations_cleaned.csv"
IMD_DATA_PATH = BASE_DIR / "data" / "processed" / "imd" / "imd_rainfall_cleaned.csv"
OUTPUT_FEATURE_DIR = BASE_DIR / "features" / "disaster_history"
OUTPUT_FEATURE_FILE = OUTPUT_FEATURE_DIR / "gdis_disaster_history_features.csv"


def norm_name(s):
    if not isinstance(s, str):
        return ""
    return s.upper().replace('_', ' ').replace('-', ' ').replace('.', '').strip()


def generate_disaster_features():
    print(f"[NASA GDIS Features] Loading cleaned dataset from: {CLEANED_GDIS_CSV}")
    df_gdis = pd.read_csv(CLEANED_GDIS_CSV)

    # Filter India records
    df_ind = df_gdis[(df_gdis['country_name'].str.upper() == 'INDIA') | (df_gdis['iso3_code'] == 'IND')].copy()
    df_ind['norm_adm1'] = df_ind['adm1_state'].apply(norm_name)
    df_ind['norm_adm2'] = df_ind['adm2_district'].apply(norm_name)

    print(f"[NASA GDIS Features] Filtered {len(df_ind)} India disaster records.")

    print(f"[NASA GDIS Features] Loading RESQ-AI district list from: {IMD_DATA_PATH}")
    df_imd = pd.read_csv(IMD_DATA_PATH)
    districts = df_imd[['state', 'district']].drop_duplicates().sort_values(by=['state', 'district']).reset_index(drop=True)

    print(f"[NASA GDIS Features] Mapping features across {len(districts)} districts...")

    # Group GDIS events by state/ADM1 for reliable matching
    state_gdis_map = df_ind.groupby('norm_adm1')

    rows = []
    global_median_year_min = int(df_ind['event_year'].min())
    global_median_year_max = int(df_ind['event_year'].max())

    for idx, row in districts.iterrows():
        state = row['state']
        dist = row['district']
        norm_st = norm_name(state)
        norm_dt = norm_name(dist)

        # Check district exact match
        dist_match = df_ind[df_ind['norm_adm2'] == norm_dt]

        if len(dist_match) > 0:
            match_subset = dist_match
        elif norm_st in state_gdis_map.groups:
            match_subset = state_gdis_map.get_group(norm_st)
        else:
            match_subset = pd.DataFrame()

        if len(match_subset) > 0:
            tot_count = len(match_subset)
            type_counts = match_subset['disaster_type'].str.lower().value_counts().to_dict()
            flood_cnt = type_counts.get('flood', 0)
            storm_cnt = type_counts.get('storm', 0)
            drought_cnt = type_counts.get('drought', 0)
            ext_temp_cnt = type_counts.get('extreme temperature', 0)
            quake_cnt = type_counts.get('earthquake', 0)
            slide_cnt = type_counts.get('landslide', 0)
            uniq_types = len(type_counts)
            min_yr = int(match_subset['event_year'].min())
            max_yr = int(match_subset['event_year'].max())
            recent_10yr = int((match_subset['event_year'] >= 2009).sum())
        else:
            tot_count = 0
            flood_cnt = 0
            storm_cnt = 0
            drought_cnt = 0
            ext_temp_cnt = 0
            quake_cnt = 0
            slide_cnt = 0
            uniq_types = 0
            min_yr = global_median_year_min
            max_yr = global_median_year_max
            recent_10yr = 0

        freq_per_decade = round(tot_count / 5.9, 2)

        rows.append({
            'state': state,
            'district': dist,
            'gdis_historical_disaster_count': tot_count,
            'gdis_flood_event_count': flood_cnt,
            'gdis_storm_event_count': storm_cnt,
            'gdis_drought_event_count': drought_cnt,
            'gdis_extreme_temp_event_count': ext_temp_cnt,
            'gdis_earthquake_event_count': quake_cnt,
            'gdis_landslide_event_count': slide_cnt,
            'gdis_unique_disaster_types_count': uniq_types,
            'gdis_year_first_record': min_yr,
            'gdis_year_last_record': max_yr,
            'gdis_recent_10yr_event_count': recent_10yr,
            'gdis_disaster_frequency_per_decade': freq_per_decade
        })

    df_out = pd.DataFrame(rows)
    OUTPUT_FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUTPUT_FEATURE_FILE, index=False)

    print(f"[NASA GDIS Features] Saved disaster history features to: {OUTPUT_FEATURE_FILE}")
    print(f"[NASA GDIS Features] Output feature matrix shape: {df_out.shape}")

    return df_out


if __name__ == "__main__":
    generate_disaster_features()
