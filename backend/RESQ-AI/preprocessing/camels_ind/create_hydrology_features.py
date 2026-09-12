"""
CAMELS-IND Hydrology Feature Generation Script for RESQ-AI.

Extracts domain-specific hydrological and catchment features per district:
- camels_aridity_index
- camels_p_mean_mm_day
- camels_q_mean_mm_day
- camels_runoff_ratio
- camels_soil_moisture_mean_kg_m2
- camels_soil_moisture_lvl1_top
- camels_soil_moisture_lvl4_deep
- camels_soil_conductivity_top
- camels_soil_awc_top
- camels_high_precip_freq_days
- camels_low_precip_freq_days
- camels_elevation_mean_m
- camels_slope_mean_deg
- camels_forest_cover_pct
- camels_dam_count
- camels_dam_storage_capacity_mcm

Saves output feature matrix to features/hydrology/camels_ind_hydrology_features.csv.
"""

from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CATCHMENT_CSV = BASE_DIR / "data" / "processed" / "camels_ind" / "camels_ind_catchments_cleaned.csv"
FORCINGS_SUMMARY_CSV = BASE_DIR / "data" / "processed" / "camels_ind" / "camels_ind_forcings_summary.csv"
IMD_DATA_PATH = BASE_DIR / "data" / "processed" / "imd" / "imd_rainfall_cleaned.csv"

OUTPUT_FEATURE_DIR = BASE_DIR / "features" / "hydrology"
OUTPUT_FEATURE_FILE = OUTPUT_FEATURE_DIR / "camels_ind_hydrology_features.csv"

STATE_BASIN_MAP = {
    'ANDAMAN & NICOBAR': 'Cauvery',
    'ANDHRA PRADESH': 'Krishna',
    'ARUNACHAL PRADESH': 'Brahmani-Baitarani',
    'ASSAM': 'Subernarekha',
    'BIHAR': 'Mahanadi',
    'CHANDIGARH': 'Sabarmati',
    'CHHATISGARH': 'Mahanadi',
    'DADRA & NAGAR HAVELI': 'WFRN',
    'DAMAN & DIU': 'WFRN',
    'DELHI': 'Mahi',
    'GOA': 'WFRS',
    'GUJARAT': 'Tapi',
    'HARYANA': 'Sabarmati',
    'HIMACHAL PRADESH': 'Narmada',
    'JAMMU & KASHMIR': 'Narmada',
    'JHARKHAND': 'Subernarekha',
    'KARNATAKA': 'Krishna',
    'KERALA': 'WFRS',
    'LAKSHADWEEP': 'WFRS',
    'MADHYA PRADESH': 'Narmada',
    'MAHARASHTRA': 'Godavari',
    'MANIPUR': 'EFRN',
    'MEGHALAYA': 'EFRN',
    'MIZORAM': 'EFRN',
    'NAGALAND': 'EFRN',
    'ODISHA': 'Mahanadi',
    'PUDUCHERRY': 'EFRS',
    'PUNJAB': 'Sabarmati',
    'RAJASTHAN': 'Mahi',
    'SIKKIM': 'Brahmani-Baitarani',
    'TAMIL NADU': 'Cauvery',
    'TELANGANA': 'Godavari',
    'TRIPURA': 'EFRN',
    'UTTAR PRADESH': 'Mahanadi',
    'UTTARAKHAND': 'Narmada',
    'WEST BENGAL': 'Subernarekha'
}


def create_hydrology_features():
    print(f"[CAMELS-IND Features] Reading cleaned catchments from: {CATCHMENT_CSV}")
    df_cat = pd.read_csv(CATCHMENT_CSV)
    df_cat['gauge_id'] = df_cat['gauge_id'].astype(str).str.zfill(5)

    print(f"[CAMELS-IND Features] Reading forcings summary from: {FORCINGS_SUMMARY_CSV}")
    df_force = pd.read_csv(FORCINGS_SUMMARY_CSV)
    df_force['gauge_id'] = df_force['gauge_id'].astype(str).str.zfill(5)

    df_camels = pd.merge(df_cat, df_force, on='gauge_id', how='inner')

    # Pre-calculate basin-level mean hydrological attributes
    basin_means = df_camels.groupby('river_basin').mean(numeric_only=True)

    print(f"[CAMELS-IND Features] Reading district target list from: {IMD_DATA_PATH}")
    df_imd = pd.read_csv(IMD_DATA_PATH)
    districts = df_imd[['state', 'district']].drop_duplicates().sort_values(by=['state', 'district']).reset_index(drop=True)

    print(f"[CAMELS-IND Features] Mapping hydrological features to {len(districts)} districts...")

    rows = []
    global_means = df_camels.mean(numeric_only=True)

    for idx, row in districts.iterrows():
        state = row['state']
        dist = row['district']

        target_basin = STATE_BASIN_MAP.get(state, 'Godavari')
        if target_basin in basin_means.index:
            b_vals = basin_means.loc[target_basin]
        else:
            b_vals = global_means

        # Extract features cleanly
        aridity = float(b_vals.get('aridity_index', 1.05))
        p_mean = float(b_vals.get('p_mean', 3.25))
        q_mean = float(b_vals.get('q_mean', 1.15))
        runoff_ratio = float(b_vals.get('runoff_ratio', 0.35))
        sm_mean = float(b_vals.get('mean_sm_rootzone_kg_m2', 380.0))
        sm_lvl1 = float(b_vals.get('mean_sm_lvl1_kg_m2', 45.0))
        sm_lvl4 = float(b_vals.get('mean_sm_lvl4_kg_m2', 480.0))
        soil_cond = float(b_vals.get('soil_conductivity_top', 12.5))
        soil_awc = float(b_vals.get('soil_awc_top', 140.0))
        high_precip = float(b_vals.get('high_prec_freq', 18.0))
        low_precip = float(b_vals.get('low_prec_freq', 210.0))
        elev_m = float(b_vals.get('elev_mean', 350.0))
        slope_deg = float(b_vals.get('slope_mean', 4.5))
        trees_pct = round(float(b_vals.get('trees_frac', 0.25)) * 100.0, 2)
        n_dams = float(b_vals.get('num_dams', 2.0))
        dam_cap = float(b_vals.get('res_store_sum', 150.0))

        rows.append({
            'state': state,
            'district': dist,
            'camels_aridity_index': round(aridity, 3),
            'camels_p_mean_mm_day': round(p_mean, 3),
            'camels_q_mean_mm_day': round(q_mean, 3),
            'camels_runoff_ratio': round(runoff_ratio, 3),
            'camels_soil_moisture_mean_kg_m2': round(sm_mean, 2),
            'camels_soil_moisture_lvl1_top': round(sm_lvl1, 2),
            'camels_soil_moisture_lvl4_deep': round(sm_lvl4, 2),
            'camels_soil_conductivity_top': round(soil_cond, 2),
            'camels_soil_awc_top': round(soil_awc, 2),
            'camels_high_precip_freq_days': round(high_precip, 1),
            'camels_low_precip_freq_days': round(low_precip, 1),
            'camels_elevation_mean_m': round(elev_m, 1),
            'camels_slope_mean_deg': round(slope_deg, 2),
            'camels_forest_cover_pct': trees_pct,
            'camels_dam_count': int(round(n_dams)),
            'camels_dam_storage_capacity_mcm': round(dam_cap, 2)
        })

    df_out = pd.DataFrame(rows)

    OUTPUT_FEATURE_DIR.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUTPUT_FEATURE_FILE, index=False)

    print(f"[CAMELS-IND Features] Successfully saved hydrology features to: {OUTPUT_FEATURE_FILE}")
    print(f"[CAMELS-IND Features] Final feature matrix shape: {df_out.shape}")

    return df_out


if __name__ == "__main__":
    create_hydrology_features()
