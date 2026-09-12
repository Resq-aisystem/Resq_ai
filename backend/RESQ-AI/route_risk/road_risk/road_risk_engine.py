"""
RESQ-AI Road & Route Segment Risk Scoring Engine.

Calculates bounded hazard risk scores (0-100) for route segments/waypoints
by evaluating spatial location against RESQ-AI district risk intelligence,
GFSM terrain susceptibility, CAMELS hydrology, IFI recurrence, and NASA GDIS priors.

Strictly excludes target leakage variables and unverified infrastructure data.
"""

from pathlib import Path
import math
import yaml
import pandas as pd
import numpy as np

from inference.risk_engine import get_district_risk, _load_datasets, norm_name

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "route_risk.yaml"

_CONFIG_CACHE = None
_DISTRICT_COORDS_CACHE = None


def _load_route_risk_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "risk_component_weights": {
                    "current_hazard_risk": 0.40,
                    "terrain_susceptibility": 0.25,
                    "historical_flood_recurrence": 0.15,
                    "hydrological_vulnerability": 0.10,
                    "multi_hazard_history": 0.10
                }
            }
    return _CONFIG_CACHE


def _get_nearest_district(lat: float, lon: float) -> str:
    """
    Find nearest district in RESQ-AI grid using spatial coordinates.
    Uses district centroid cache or fallback lookup.
    """
    # Simple bounding-box heuristic / lookup for Indian geographic zones
    # Major regional district anchor centroids (lat, lon)
    anchors = [
        ("ALIPURDUAR", 26.48, 89.52),
        ("DARJEELING", 27.04, 88.26),
        ("KASARGOD", 12.51, 75.00),
        ("KOTTYAM", 9.59, 76.52),
        ("NAGAPATTINAM", 10.76, 79.84),
        ("PURI", 19.81, 85.83),
        ("PATNA", 25.59, 85.13),
        ("WAYANAD", 11.68, 76.13),
        ("THANE", 19.21, 72.97),
        ("BANGLORE URBAN", 12.97, 77.59),
        ("KHERI", 27.95, 80.78),
        ("N.C HILLS", 25.17, 93.02),
        ("NUAPARHA", 20.84, 82.52),
        ("DELHI", 28.61, 77.20),
        ("KOLKATA", 22.57, 88.36),
        ("CHENNAI", 13.08, 80.27),
        ("MUMBAI", 19.07, 72.87),
        ("HYDERABAD", 17.38, 78.48)
    ]

    min_dist = float('inf')
    best_district = "PURI"  # Default fallback

    for d_name, d_lat, d_lon in anchors:
        dist = math.hypot(lat - d_lat, lon - d_lon)
        if dist < min_dist:
            min_dist = dist
            best_district = d_name

    return best_district


def calculate_route_risk(
    district_name: str = None,
    waypoints: list = None,
    observation_date: str = None
) -> dict:
    """
    Calculate bounded route risk score (0-100) and layer breakdown for a route.

    Args:
        district_name: Name of primary district (if known).
        waypoints: Optional list of [longitude, latitude] or [latitude, longitude] pairs.
        observation_date: ISO date string 'YYYY-MM-DD'.

    Returns:
        Dict payload containing route_risk_score, risk_level, and breakdown.
    """
    cfg = _load_route_risk_config()
    weights = cfg.get("risk_component_weights", {
        "current_hazard_risk": 0.40,
        "terrain_susceptibility": 0.25,
        "historical_flood_recurrence": 0.15,
        "hydrological_vulnerability": 0.10,
        "multi_hazard_history": 0.10
    })

    # 1. Determine target district(s)
    if not district_name and waypoints and len(waypoints) > 0:
        mid_pt = waypoints[len(waypoints) // 2]
        # Check if waypoints are [lon, lat] or [lat, lon]
        if abs(mid_pt[0]) > 40.0 and abs(mid_pt[1]) < 40.0:
            lon, lat = mid_pt[0], mid_pt[1]
        else:
            lat, lon = mid_pt[0], mid_pt[1]
        district_name = _get_nearest_district(lat, lon)

    if not district_name:
        district_name = "PURI"

    # 2. Query Risk Engine for current situational hazard intelligence
    risk_output = get_district_risk(district_name, observation_date)
    risk_dict = risk_output.to_dict()

    actual_district = risk_dict['district']
    c_hazard_risk = float(risk_dict['risk_score'])

    # 3. Retrieve static/historical feature datasets
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

    # 4. Normalize Sub-Components to Bounded [0, 100]

    # Component A: Current Hazard Risk
    score_hazard = float(np.clip(c_hazard_risk, 0.0, 100.0))

    # Component B: Terrain Susceptibility (Internal Ordinal Scaling 1-5 -> 20-100)
    if gfsm_row is not None:
        gfsm_val = float(gfsm_row.get('gfsm_susceptibility_score', 2.0))
        high_pct = float(gfsm_row.get('gfsm_high_susceptibility_pct', 0.0)) + float(gfsm_row.get('gfsm_very_high_susceptibility_pct', 0.0))
        score_susceptibility = float(np.clip(gfsm_val * 20.0 + high_pct * 0.2, 0.0, 100.0))
    else:
        score_susceptibility = 30.0

    # Component C: Historical Flood Recurrence (IFI decoupled prior)
    if ifi_row is not None:
        ifi_rec = float(ifi_row.get('ifi_flood_recurrence_rate', 0.0))
        score_recurrence = float(np.clip(ifi_rec * 18.0, 0.0, 100.0))
    else:
        score_recurrence = 20.0

    # Component D: Hydrological Vulnerability (CAMELS)
    if camels_row is not None:
        runoff_ratio = float(camels_row.get('camels_runoff_ratio', 0.4))
        soil_moisture = float(camels_row.get('camels_soil_moisture_lvl1_top', 15.0))
        score_hydrology = float(np.clip(runoff_ratio * 75.0 + (soil_moisture / 50.0) * 25.0, 0.0, 100.0))
    else:
        score_hydrology = 30.0

    # Component E: Multi-Hazard History (GDIS)
    if gdis_row is not None:
        gdis_cnt = float(gdis_row.get('gdis_historical_disaster_count', 0))
        score_multi_hazard = float(np.clip(gdis_cnt * 2.0, 0.0, 100.0))
    else:
        score_multi_hazard = 10.0

    # 5. Composite Bounded Route Risk Calculation
    w1 = weights.get('current_hazard_risk', 0.40)
    w2 = weights.get('terrain_susceptibility', 0.25)
    w3 = weights.get('historical_flood_recurrence', 0.15)
    w4 = weights.get('hydrological_vulnerability', 0.10)
    w5 = weights.get('multi_hazard_history', 0.10)

    composite_route_risk = (
        w1 * score_hazard +
        w2 * score_susceptibility +
        w3 * score_recurrence +
        w4 * score_hydrology +
        w5 * score_multi_hazard
    )

    # 5b. Intersect waypoints with spatial flood zone polygons if available
    exp_dist_km, exp_pct = 0.0, 0.0
    if waypoints:
        try:
            from flood_zones.spatial_intersection import generate_city_flood_zones, calculate_route_flood_exposure
            fz_payload = generate_city_flood_zones(district_name=actual_district)
            exp_dist_km, exp_pct = calculate_route_flood_exposure(waypoints, fz_payload)
            # Add slight penalty if high flood zone exposure exists
            if exp_pct > 20.0:
                composite_route_risk += (exp_pct * 0.10)
        except Exception:
            pass

    composite_route_risk = float(np.clip(round(composite_route_risk, 2), 0.0, 100.0))

    # 6. Assign Risk Level
    if composite_route_risk >= 80.0:
        risk_lvl = "CRITICAL"
    elif composite_route_risk >= 55.0:
        risk_lvl = "HIGH"
    elif composite_route_risk >= 25.0:
        risk_lvl = "MODERATE"
    else:
        risk_lvl = "LOW"

    return {
        "district": actual_district,
        "route_risk_score": composite_route_risk,
        "risk_level": risk_lvl,
        "flood_exposed_distance_km": exp_dist_km,
        "flood_exposure_percent": exp_pct,
        "risk_exposure_summary": {
            "current_hazard_risk_score": round(score_hazard, 2),
            "terrain_susceptibility_score": round(score_susceptibility, 2),
            "historical_flood_recurrence_score": round(score_recurrence, 2),
            "hydrological_vulnerability_score": round(score_hydrology, 2),
            "multi_hazard_history_score": round(score_multi_hazard, 2),
            "flood_exposed_distance_km": exp_dist_km,
            "flood_exposure_percent": exp_pct
        }
    }
