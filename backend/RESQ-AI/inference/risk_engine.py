"""
RESQ-AI Production Risk Inference Engine.

Combines Layer 1 (IMD Observed Rainfall Severity Intelligence),
Layer 2 (GFSM 30m Flood Susceptibility & CAMELS-IND Hydrology), and
Layer 3 (IFI & NASA GDIS Historical Flood/Disaster Evidence Priors).

Strictly excludes target leakage variables.
Calculates explainable district risk score (0-100), risk level (LOW/MODERATE/HIGH/CRITICAL),
evidence quality (HIGH/MEDIUM/LOW), and top contributing factors.
"""

from pathlib import Path
import json
import yaml
import pandas as pd
import numpy as np

from inference.schemas.risk_contract import (
    RiskPredictionOutput, RiskLevel, EvidenceQuality, RiskFactor
)
from inference.prediction.imd_baseline_predictor import predict_rainfall_severity

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "risk_engine.yaml"

IMD_PATH = BASE_DIR / "features" / "rainfall" / "imd_rainfall_features.csv"
GFSM_PATH = BASE_DIR / "features" / "susceptibility" / "gfsm_susceptibility_features.csv"
CAMELS_PATH = BASE_DIR / "features" / "hydrology" / "camels_ind_hydrology_features.csv"
IFI_PATH = BASE_DIR / "features" / "flood_history" / "ifi_flood_history_features.csv"
GDIS_PATH = BASE_DIR / "features" / "disaster_history" / "gdis_disaster_history_features.csv"

_DATASET_CACHE = None
_CONFIG_CACHE = None


def _load_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "weights": {"layer_1_rainfall_intelligence": 0.40, "layer_2_susceptibility_hydrology": 0.30, "layer_3_historical_evidence": 0.30},
                "thresholds": {"LOW": [0.0, 25.0], "MODERATE": [25.0, 55.0], "HIGH": [55.0, 80.0], "CRITICAL": [80.0, 100.0]}
            }
    return _CONFIG_CACHE


def _load_datasets():
    global _DATASET_CACHE
    if _DATASET_CACHE is None:
        df_imd = pd.read_csv(IMD_PATH)
        df_gfsm = pd.read_csv(GFSM_PATH)
        df_camels = pd.read_csv(CAMELS_PATH)
        df_ifi = pd.read_csv(IFI_PATH)
        df_gdis = pd.read_csv(GDIS_PATH)

        # Normalize string keys for fast matching using uniform norm_name function
        for df in [df_imd, df_gfsm, df_camels, df_ifi, df_gdis]:
            df['norm_district'] = df['district'].apply(norm_name)

        _DATASET_CACHE = {
            'imd': df_imd,
            'gfsm': df_gfsm.set_index('norm_district'),
            'camels': df_camels.set_index('norm_district'),
            'ifi': df_ifi.set_index('norm_district'),
            'gdis': df_gdis.set_index('norm_district')
        }
    return _DATASET_CACHE


def norm_name(s):
    if not isinstance(s, str):
        return ""
    return s.upper().replace('_', ' ').replace('-', ' ').replace('.', '').strip()


def calculate_layer_1_score(imd_row):
    """Layer 1: IMD Observed Rainfall Intelligence (0-100)."""
    if imd_row is None:
        return 20.0, "LIGHT", {}

    # Query IMD baseline predictor
    pred_res = predict_rainfall_severity(imd_row.to_dict())
    sev_cat = pred_res.get("predicted_severity", "LIGHT")

    base_scores = {"LIGHT": 15.0, "MODERATE": 45.0, "HEAVY": 75.0, "EXTREME": 95.0}
    score = base_scores.get(sev_cat, 20.0)

    # Adjust for observed daily actual and 7-day rolling precipitation
    daily_act = float(imd_row.get('daily_actual_mm', 0.0))
    roll_7d = float(imd_row.get('rolling_7d_rainfall_mm', 0.0))
    anomaly = float(imd_row.get('rainfall_anomaly_mm', 0.0))

    if daily_act >= 100.0:
        score += 10.0
    elif daily_act >= 50.0:
        score += 5.0

    if roll_7d >= 150.0:
        score += 10.0

    if anomaly > 20.0:
        score += 5.0

    score = float(np.clip(score, 0.0, 100.0))
    metrics = {
        "daily_actual_mm": round(daily_act, 2),
        "rolling_7d_rainfall_mm": round(roll_7d, 2),
        "rainfall_anomaly_mm": round(anomaly, 2),
        "predicted_severity": sev_cat
    }
    return score, sev_cat, metrics


def calculate_layer_2_score(gfsm_row, camels_row):
    """Layer 2: GFSM 30m Susceptibility & CAMELS-IND Hydrology (0-100)."""
    score = 25.0
    metrics = {}

    if gfsm_row is not None:
        sus_score = float(gfsm_row.get('gfsm_susceptibility_score', 2.0))
        high_pct = float(gfsm_row.get('gfsm_high_susceptibility_pct', 10.0))
        # Map GFSM score (1-5) to scale (20-100)
        score = (sus_score / 5.0) * 80.0 + (high_pct / 100.0) * 20.0
        metrics['gfsm_susceptibility_score'] = round(sus_score, 2)
        metrics['gfsm_high_susceptibility_pct'] = round(high_pct, 2)

    if camels_row is not None:
        runoff_ratio = float(camels_row.get('camels_runoff_ratio', 0.35))
        sm_mean = float(camels_row.get('camels_soil_moisture_mean_kg_m2', 380.0))
        dam_cap = float(camels_row.get('camels_dam_storage_capacity_mcm', 0.0))

        if runoff_ratio > 0.5:
            score += 10.0
        if sm_mean > 450.0:
            score += 5.0
        if dam_cap > 500.0:
            score -= 5.0  # Dam capacity provides flood buffering mitigation

        metrics['camels_runoff_ratio'] = round(runoff_ratio, 3)
        metrics['camels_soil_moisture_mean_kg_m2'] = round(sm_mean, 2)
        metrics['camels_dam_storage_capacity_mcm'] = round(dam_cap, 2)

    score = float(np.clip(score, 0.0, 100.0))
    return score, metrics


def calculate_layer_3_score(ifi_row, gdis_row):
    """Layer 3: Historical Flood & Disaster Evidence Priors (0-100)."""
    score = 20.0
    metrics = {}

    if ifi_row is not None:
        # EXCLUDING target leakage variables (ifi_dfsi_score, ifi_flooded_area_pct, fatalities, etc.)
        recurrence = float(ifi_row.get('ifi_flood_recurrence_rate', 0.0))
        water_pct = float(ifi_row.get('ifi_permanent_water_pct', 0.0))
        evt_cnt = float(ifi_row.get('ifi_historical_event_count', 0.0))

        score += min(recurrence * 10.0, 30.0) + min(water_pct * 2.0, 15.0)
        metrics['ifi_flood_recurrence_rate'] = round(recurrence, 2)
        metrics['ifi_historical_event_count'] = int(evt_cnt)
        metrics['ifi_permanent_water_pct'] = round(water_pct, 2)

    if gdis_row is not None:
        gdis_floods = float(gdis_row.get('gdis_flood_event_count', 0.0))
        dec_freq = float(gdis_row.get('gdis_disaster_frequency_per_decade', 0.0))

        score += min(gdis_floods * 2.5, 25.0)
        metrics['gdis_flood_event_count'] = int(gdis_floods)
        metrics['gdis_disaster_frequency_per_decade'] = round(dec_freq, 2)

    score = float(np.clip(score, 0.0, 100.0))
    return score, metrics


def get_district_risk(district_name: str, observation_date: str = None) -> RiskPredictionOutput:
    """
    Production API endpoint calculating explainable district flood risk assessment.

    Args:
        district_name: Name of district (e.g., 'Patna', 'Kolkata', 'Niwari').
        observation_date: ISO date string 'YYYY-MM-DD' (defaults to latest available observation date).

    Returns:
        RiskPredictionOutput validated payload object.
    """
    datasets = _load_datasets()
    cfg = _load_config()

    norm_d = norm_name(district_name)
    df_imd = datasets['imd']

    # 1. Filter IMD observation row
    imd_sub = df_imd[df_imd['norm_district'] == norm_d]
    if len(imd_sub) == 0:
        # Try substring matching
        imd_sub = df_imd[df_imd['norm_district'].str.contains(norm_d, na=False)]

    if len(imd_sub) == 0:
        raise ValueError(f"District '{district_name}' not found in RESQ-AI district grid.")

    if observation_date:
        imd_row_sub = imd_sub[imd_sub['date'] == str(observation_date)]
        if len(imd_row_sub) > 0:
            imd_row = imd_row_sub.iloc[0]
        else:
            imd_row = imd_sub.iloc[-1]  # Default to latest date
    else:
        imd_row = imd_sub.iloc[-1]

    actual_date = str(imd_row['date'])
    actual_district = str(imd_row['district'])

    # 2. Retrieve static & historical rows for district
    gfsm_row = datasets['gfsm'].loc[norm_d] if norm_d in datasets['gfsm'].index else None
    camels_row = datasets['camels'].loc[norm_d] if norm_d in datasets['camels'].index else None
    ifi_row = datasets['ifi'].loc[norm_d] if norm_d in datasets['ifi'].index else None
    gdis_row = datasets['gdis'].loc[norm_d] if norm_d in datasets['gdis'].index else None

    if isinstance(gfsm_row, pd.DataFrame): gfsm_row = gfsm_row.iloc[0]
    if isinstance(camels_row, pd.DataFrame): camels_row = camels_row.iloc[0]
    if isinstance(ifi_row, pd.DataFrame): ifi_row = ifi_row.iloc[0]
    if isinstance(gdis_row, pd.DataFrame): gdis_row = gdis_row.iloc[0]

    # 3. Calculate Layer Scores
    l1_score, l1_cat, l1_metrics = calculate_layer_1_score(imd_row)
    l2_score, l2_metrics = calculate_layer_2_score(gfsm_row, camels_row)
    l3_score, l3_metrics = calculate_layer_3_score(ifi_row, gdis_row)

    w1 = cfg['weights']['layer_1_rainfall_intelligence']
    w2 = cfg['weights']['layer_2_susceptibility_hydrology']
    w3 = cfg['weights']['layer_3_historical_evidence']

    composite_score = float(w1 * l1_score + w2 * l2_score + w3 * l3_score)
    composite_score = float(np.clip(composite_score, 0.0, 100.0))

    # 4. Assign Risk Level
    if composite_score >= 80.0:
        risk_lvl = RiskLevel.CRITICAL
    elif composite_score >= 55.0:
        risk_lvl = RiskLevel.HIGH
    elif composite_score >= 25.0:
        risk_lvl = RiskLevel.MODERATE
    else:
        risk_lvl = RiskLevel.LOW

    # 5. Evidence Quality Assessment
    available_layers = 1 + (1 if gfsm_row is not None else 0) + (1 if camels_row is not None else 0) + (1 if ifi_row is not None else 0) + (1 if gdis_row is not None else 0)
    if available_layers == 5:
        ev_quality = EvidenceQuality.HIGH
    elif available_layers >= 3:
        ev_quality = EvidenceQuality.MEDIUM
    else:
        ev_quality = EvidenceQuality.LOW

    # 6. Generate Top Factors
    top_factors = []

    # Factor 1: Rainfall Severity
    daily_mm = l1_metrics.get('daily_actual_mm', 0.0)
    top_factors.append(RiskFactor(
        factor_name="Observed Rainfall Severity",
        impact_weight=round(l1_score / 100.0, 2),
        description=f"Observed daily rainfall: {daily_mm} mm (Predicted Intensity: {l1_cat})",
        direction="INCREASES_RISK" if l1_score >= 50.0 else "DECREASES_RISK"
    ))

    # Factor 2: GFSM Susceptibility
    gfsm_score = l2_metrics.get('gfsm_susceptibility_score', 2.0)
    high_pct = l2_metrics.get('gfsm_high_susceptibility_pct', 0.0)
    top_factors.append(RiskFactor(
        factor_name="Terrain Flood Susceptibility (GFSM)",
        impact_weight=round(l2_score / 100.0, 2),
        description=f"30m GFSM rating: {gfsm_score}/5.0 ({high_pct}% district area in High/Very High susceptibility)",
        direction="INCREASES_RISK" if gfsm_score >= 3.0 else "DECREASES_RISK"
    ))

    # Factor 3: Historical Flood Prior
    ifi_rec = l3_metrics.get('ifi_flood_recurrence_rate', 0.0)
    gdis_cnt = l3_metrics.get('gdis_flood_event_count', 0)
    top_factors.append(RiskFactor(
        factor_name="Historical Flood & Disaster Evidence",
        impact_weight=round(l3_score / 100.0, 2),
        description=f"IFI recurrence rate: {ifi_rec} events/decade; GDIS recorded floods: {gdis_cnt}",
        direction="INCREASES_RISK" if ifi_rec > 1.0 or gdis_cnt > 2 else "DECREASES_RISK"
    ))

    # Sort factors by impact_weight descending
    top_factors.sort(key=lambda x: x.impact_weight, reverse=True)

    layer_breakdown = {
        "layer_1_rainfall_score": round(l1_score, 2),
        "layer_2_susceptibility_score": round(l2_score, 2),
        "layer_3_historical_evidence_score": round(l3_score, 2),
        "layer_1_metrics": l1_metrics,
        "layer_2_metrics": l2_metrics,
        "layer_3_metrics": l3_metrics
    }

    output_payload = RiskPredictionOutput(
        risk_score=composite_score,
        risk_level=risk_lvl,
        confidence=0.88,
        top_factors=top_factors,
        priority_score=round(composite_score * 0.9, 2),
        evidence_quality=ev_quality,
        district=actual_district,
        observation_date=actual_date,
        layer_breakdown=layer_breakdown
    )

    return output_payload
