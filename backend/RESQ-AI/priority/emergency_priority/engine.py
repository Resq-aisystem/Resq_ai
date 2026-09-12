"""
RESQ-AI Vulnerable Location & Emergency Priority Scoring Engine.

Combines situational Risk Score (from Production Risk Engine) with
terrain susceptibility, hydrological vulnerability, historical flood recurrence, and
multi-hazard exposure priors to rank districts for operational response decision-support.

Exposes:
- get_emergency_priority(district_name, observation_date)
"""

from pathlib import Path
import yaml
import pandas as pd
import numpy as np

from inference.risk_engine import get_district_risk, _load_datasets, norm_name

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "priority_engine.yaml"

_CONFIG_CACHE = None


def _load_priority_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "weights": {
                    "current_risk": 0.45,
                    "terrain_susceptibility": 0.20,
                    "historical_recurrence": 0.15,
                    "hydrological_vulnerability": 0.10,
                    "multi_hazard_history": 0.10
                },
                "thresholds": {
                    "P1": {"min_score": 70.0, "label": "Immediate Attention"},
                    "P2": {"min_score": 50.0, "label": "High Priority"},
                    "P3": {"min_score": 30.0, "label": "Monitor / Prepare"},
                    "P4": {"min_score": 0.0, "label": "Routine Monitoring"}
                }
            }
    return _CONFIG_CACHE


def get_emergency_priority(district_name: str, observation_date: str = None) -> dict:
    """
    Calculate emergency priority ranking and operational attention reason for a district.

    Args:
        district_name: Name of the district.
        observation_date: ISO date string 'YYYY-MM-DD' (defaults to latest available IMD date).

    Returns:
        Structured JSON-compatible dictionary payload.
    """
    cfg = _load_priority_config()
    weights = cfg['weights']

    # 1. Obtain Situational Risk Assessment
    risk_output = get_district_risk(district_name, observation_date)
    risk_dict = risk_output.to_dict()

    actual_district = risk_dict['district']
    actual_date = risk_dict['observation_date']
    risk_score = risk_dict['risk_score']
    risk_lvl = risk_dict['risk_level']
    ev_qual = risk_dict['evidence_quality']

    # 2. Retrieve static/historical feature datasets for district
    datasets = _load_datasets()
    norm_d = norm_name(actual_district)

    gfsm_row = datasets['gfsm'].loc[norm_d] if norm_d in datasets['gfsm'].index else None
    camels_row = datasets['camels'].loc[norm_d] if norm_d in datasets['camels'].index else None
    ifi_row = datasets['ifi'].loc[norm_d] if norm_d in datasets['ifi'].index else None
    gdis_row = datasets['gdis'].loc[norm_d] if norm_d in datasets['gdis'].index else None

    if isinstance(gfsm_row, pd.DataFrame): gfsm_row = gfsm_row.iloc[0]
    if isinstance(camels_row, pd.DataFrame): camels_row = camels_row.iloc[0]
    if isinstance(ifi_row, pd.DataFrame): ifi_row = ifi_row.iloc[0]
    if isinstance(gdis_row, pd.DataFrame): gdis_row = gdis_row.iloc[0]

    state_name = str(gfsm_row['state']) if gfsm_row is not None and 'state' in gfsm_row else "INDIA"

    # 3. Calculate Priority Sub-Scores (Bounded 0-100)

    # Component A: Current Situational Risk
    c_risk = float(risk_score)

    # Component B: Terrain Susceptibility
    if gfsm_row is not None:
        gfsm_score_val = float(gfsm_row.get('gfsm_susceptibility_score', 2.0))
        high_pct = float(gfsm_row.get('gfsm_high_susceptibility_pct', 0.0)) + float(gfsm_row.get('gfsm_very_high_susceptibility_pct', 0.0))
        c_susceptibility = float(np.clip(gfsm_score_val * 20.0 + high_pct * 0.3, 0.0, 100.0))
    else:
        gfsm_score_val = 2.0
        high_pct = 0.0
        c_susceptibility = 30.0

    # Component C: Historical Flood Recurrence (IFI decoupled prior)
    if ifi_row is not None:
        ifi_rec = float(ifi_row.get('ifi_flood_recurrence_rate', 0.0))
        ifi_events = float(ifi_row.get('ifi_historical_event_count', 0.0))
        c_recurrence = float(np.clip(ifi_rec * 15.0 + (ifi_events / 50.0) * 20.0, 0.0, 100.0))
    else:
        ifi_rec = 0.0
        ifi_events = 0.0
        c_recurrence = 20.0

    # Component D: Hydrological Vulnerability (CAMELS)
    if camels_row is not None:
        runoff_ratio = float(camels_row.get('camels_runoff_ratio', 0.4))
        soil_moisture = float(camels_row.get('camels_soil_moisture_lvl1_top', 15.0))
        c_hydrology = float(np.clip(runoff_ratio * 70.0 + (soil_moisture / 50.0) * 30.0, 0.0, 100.0))
    else:
        runoff_ratio = 0.4
        soil_moisture = 15.0
        c_hydrology = 30.0

    # Component E: Multi-Hazard History (GDIS)
    if gdis_row is not None:
        gdis_disasters = float(gdis_row.get('gdis_historical_disaster_count', 0))
        gdis_types = float(gdis_row.get('gdis_unique_disaster_types_count', 0))
        c_exposure = float(np.clip(gdis_disasters * 1.5 + gdis_types * 15.0, 0.0, 100.0))
    else:
        gdis_disasters = 0
        gdis_types = 0
        c_exposure = 10.0

    # 4. Compute Bounded Composite Priority Score (0-100)
    w_r = weights['current_risk']
    w_s = weights['terrain_susceptibility']
    w_h = weights['historical_recurrence']
    w_hy = weights['hydrological_vulnerability']
    w_e = weights['multi_hazard_history']

    priority_score = (
        w_r * c_risk +
        w_s * c_susceptibility +
        w_h * c_recurrence +
        w_hy * c_hydrology +
        w_e * c_exposure
    )
    priority_score = float(np.clip(round(priority_score, 2), 0.0, 100.0))

    # 5. Assign Operational Priority Level (P1 / P2 / P3 / P4)
    if priority_score >= 70.0:
        priority_level = "P1"
    elif priority_score >= 50.0:
        priority_level = "P2"
    elif priority_score >= 30.0:
        priority_level = "P3"
    else:
        priority_level = "P4"

    # 6. Generate Validated Vulnerability Flags (Only using real data features)
    vulnerability_flags = []
    if risk_score >= 55.0:
        vulnerability_flags.append("HIGH_CURRENT_RISK")
    if gfsm_score_val >= 3.5 or high_pct >= 40.0:
        vulnerability_flags.append("HIGH_FLOOD_SUSCEPTIBILITY")
    if ifi_rec >= 3.0:
        vulnerability_flags.append("HIGH_HISTORICAL_FLOOD_RECURRENCE")
    if runoff_ratio >= 0.50 or soil_moisture >= 25.0:
        vulnerability_flags.append("HIGH_HYDROLOGICAL_VULNERABILITY")
    if gdis_types >= 2 or gdis_disasters >= 10:
        vulnerability_flags.append("MULTI_HAZARD_HISTORY")

    # 7. Generate Explainable Priority Factors
    priority_factors = []

    # Factor 1: Current Risk Level
    priority_factors.append({
        "factor": "Current Hazard Risk Score",
        "direction": "INCREASES_PRIORITY" if risk_score >= 45.0 else "NEUTRAL",
        "evidence": f"Production Risk Score: {risk_score:.1f}/100 ({risk_lvl} Risk Level)"
    })

    # Factor 2: Susceptibility
    priority_factors.append({
        "factor": "Terrain Flood Susceptibility",
        "direction": "INCREASES_PRIORITY" if gfsm_score_val >= 3.0 else "NEUTRAL",
        "evidence": f"GFSM score: {gfsm_score_val:.1f}/5.0 ({high_pct:.1f}% area High/Very High)"
    })

    # Factor 3: Historical Recurrence
    priority_factors.append({
        "factor": "Historical Flood Recurrence",
        "direction": "INCREASES_PRIORITY" if ifi_rec >= 2.0 else "NEUTRAL",
        "evidence": f"IFI recurrence rate: {ifi_rec:.2f} events/decade ({int(ifi_events)} recorded historical floods)"
    })

    # Factor 4: Hydrology
    priority_factors.append({
        "factor": "Hydrological Saturation & Runoff Potential",
        "direction": "INCREASES_PRIORITY" if runoff_ratio >= 0.45 else "NEUTRAL",
        "evidence": f"CAMELS runoff ratio: {runoff_ratio:.2f}, soil moisture: {soil_moisture:.1f} kg/m²"
    })

    # 8. Generate Recommended Attention Reason
    reasons = []
    if "HIGH_CURRENT_RISK" in vulnerability_flags:
        reasons.append("elevated current weather-driven hazard risk")
    if "HIGH_FLOOD_SUSCEPTIBILITY" in vulnerability_flags:
        reasons.append("high terrain flood susceptibility")
    if "HIGH_HISTORICAL_FLOOD_RECURRENCE" in vulnerability_flags:
        reasons.append("frequent historical flood recurrence")
    if "MULTI_HAZARD_HISTORY" in vulnerability_flags:
        reasons.append("multi-hazard disaster history")

    if reasons:
        attention_reason = f"District {actual_district} classified as {priority_level} due to " + ", ".join(reasons) + "."
    else:
        attention_reason = f"District {actual_district} classified as {priority_level} for baseline monitoring and routine watch."

    # 9. Return Standard Structured Payload
    return {
        "district": actual_district,
        "state": state_name,
        "observation_date": actual_date,
        "risk_score": risk_score,
        "risk_level": risk_lvl,
        "priority_score": priority_score,
        "priority_level": priority_level,
        "evidence_quality": ev_qual,
        "vulnerability_flags": vulnerability_flags,
        "priority_factors": priority_factors,
        "recommended_attention_reason": attention_reason,
        "component_breakdown": {
            "current_risk_component": round(c_risk, 2),
            "terrain_susceptibility_component": round(c_susceptibility, 2),
            "historical_recurrence_component": round(c_recurrence, 2),
            "hydrological_vulnerability_component": round(c_hydrology, 2),
            "multi_hazard_history_component": round(c_exposure, 2)
        }
    }
