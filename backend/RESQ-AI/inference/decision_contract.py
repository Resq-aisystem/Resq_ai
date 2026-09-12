"""
PRD-Aligned Master Decision Intelligence Contract & Service for RESQ-AI.

Assembles complete platform decision intelligence into a unified, API-ready payload:
6h Forecast -> 6h Flood Risk -> Flood Depth -> Spatial Zones -> Facility Impact -> Evacuation Priority -> Route Risk -> Action Plan -> Scenarios -> Provenance
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

from forecast.forecast_client import fetch_6hour_forecast
from flood_prediction.predictor import predict_6hour_flood_risk
from flood_depth.depth_engine import estimate_flood_depth
from flood_zones.spatial_intersection import generate_city_flood_zones
from facility.impact_engine import evaluate_facility_impacts
from priority.emergency_priority.facility_priority import get_facility_evacuation_priorities
from route_risk.route_scoring.route_service import get_rescue_route
from action_plan.action_plan_engine import generate_action_plan
from scenario.scenario_engine import run_scenario_analysis, ScenarioConfig
from update.scheduler import get_current_update_status
from provenance.provenance_schema import create_provenance_record


def get_city_decision_intelligence(
    city_name: str = "Puri",
    district_name: str = "PURI",
    observation_date: Optional[str] = None,
    route_mode: str = "BALANCED",
    origin_coords: tuple = (19.8135, 85.8312),
    dest_coords: tuple = (20.4625, 85.8828)
) -> Dict[str, Any]:
    """
    Get top-level PRD-aligned decision intelligence payload for a city / administrative area.

    Returns:
        Unified JSON-compatible dictionary payload.
    """
    now_str = datetime.now(timezone.utc).isoformat()

    # 1. 6-Hour Forecast Ingestion
    forecast_payload = fetch_6hour_forecast(city_name=city_name, district_name=district_name).to_dict()

    # 2. 6-Hour Predictive Flood Intelligence
    flood_pred_payload = predict_6hour_flood_risk(city_name=city_name, district_name=district_name, observation_date=observation_date).to_dict()

    # 3. Flood Depth Estimation (INSUFFICIENT_DATA status when unconfigured)
    depth_payload = estimate_flood_depth(city_name=city_name, district_name=district_name).to_dict()

    # 4. Spatial Flood Zone Generation
    zones_payload = generate_city_flood_zones(city_name=city_name, district_name=district_name).to_dict()

    # 5. Facility Exposure & Impact Assessment
    facility_impacts = [f.to_dict() for f in evaluate_facility_impacts(city_name=city_name, district_name=district_name, observation_date=observation_date)]

    # 6. Evacuation Priorities (PRD_FACILITY_PRIORITY_V1)
    evac_priorities = get_facility_evacuation_priorities(city_name=city_name, district_name=district_name, observation_date=observation_date)

    # 7. Flood-Aware Rescue Routing
    routes = {}
    for m in ["FASTEST", "SAFEST", "BALANCED"]:
        routes[m.lower()] = get_rescue_route(
            origin_lat=origin_coords[0], origin_lon=origin_coords[1],
            destination_lat=dest_coords[0], destination_lon=dest_coords[1],
            mode=m, observation_date=observation_date
        )

    # 8. Interactive What-If Scenario Analysis
    surge_scenario = ScenarioConfig(
        scenario_id="sc_surge_80pct",
        scenario_name="Extreme 80% Rainfall Surge Scenario",
        rainfall_multiplier=1.8
    )
    scenario_result = run_scenario_analysis(city_name=city_name, district_name=district_name, scenario=surge_scenario, observation_date=observation_date).to_dict()

    # 9. Grounded Emergency Action Plan
    action_plan_payload = generate_action_plan(
        district_name=district_name,
        observation_date=observation_date,
        route_mode=route_mode,
        origin_coords=origin_coords,
        dest_coords=dest_coords
    )

    # 10. Real-Time 30-Minute Update Status & Provenance
    update_status_payload = get_current_update_status(city_name=city_name).to_dict()
    provenance_payload = create_provenance_record().to_dict()

    warnings = [
        "Intelligence outputs are decision-support tools and should be reviewed by authorized emergency management personnel.",
        "Deterministic scoring remains the source of truth for numerical risk, priority, and route scores.",
        "High-resolution DEM raster for continuous 100m flood depth is unconfigured; returning INSUFFICIENT_DATA status for depth."
    ]

    return {
        "city_name": city_name,
        "district_name": district_name,
        "analysis_timestamp": now_str,
        "mode_scope": "CITY_MODE",
        "forecast": forecast_payload,
        "flood_prediction": flood_pred_payload,
        "flood_depth": depth_payload,
        "flood_zones": zones_payload,
        "facilities": facility_impacts,
        "evacuation_priorities": evac_priorities,
        "routes": routes,
        "scenarios": [scenario_result],
        "action_plan": action_plan_payload,
        "update_status": update_status_payload,
        "provenance": provenance_payload,
        "warnings": warnings
    }
