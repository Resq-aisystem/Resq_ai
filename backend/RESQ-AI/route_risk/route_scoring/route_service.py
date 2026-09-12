"""
API-Ready Rescue Route Scoring Service for RESQ-AI.

Exposes get_rescue_route() endpoint to evaluate candidate road routes
using OSRM graph routing and RESQ-AI hazard intelligence across FASTEST, SAFEST, and BALANCED modes.
"""

from pathlib import Path
import json

from route_risk.route_scoring.route_contract import (
    Coordinates, RouteMode, RouteRequest, RouteResponsePayload
)
from route_risk.route_scoring.osrm_client import fetch_osrm_routes
from route_risk.road_risk.road_risk_engine import calculate_route_risk
from route_risk.route_modes.route_modes import rank_and_select_routes


def get_rescue_route(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    mode: str = "BALANCED",
    observation_date: str = None
) -> dict:
    """
    API endpoint to evaluate candidate rescue routes between origin and destination.

    Args:
        origin_lat: Origin latitude (-90 to 90).
        origin_lon: Origin longitude (-180 to 180).
        destination_lat: Destination latitude (-90 to 90).
        destination_lon: Destination longitude (-180 to 180).
        mode: RouteMode string ("FASTEST", "SAFEST", "BALANCED").
        observation_date: ISO date string 'YYYY-MM-DD' (defaults to latest available IMD date).

    Returns:
        Structured JSON-compatible response dictionary payload.
    """
    origin = Coordinates(latitude=origin_lat, longitude=origin_lon)
    destination = Coordinates(latitude=destination_lat, longitude=destination_lon)
    route_mode = RouteMode(mode.upper())

    req = RouteRequest(
        origin=origin,
        destination=destination,
        mode=route_mode,
        observation_date=observation_date
    )

    # 1. Fetch candidate route geometries from OSRM / fallback client
    candidate_raw_routes = fetch_osrm_routes(origin, destination)

    if not candidate_raw_routes:
        raise RuntimeError("No routing candidate could be evaluated from routing service.")

    # 2. Score each candidate route using Road Risk Engine
    for c in candidate_raw_routes:
        risk_res = calculate_route_risk(
            waypoints=c.get("waypoints", []),
            observation_date=observation_date
        )
        c["route_risk_score"] = risk_res["route_risk_score"]
        c["risk_level"] = risk_res["risk_level"]
        c["risk_exposure_summary"] = risk_res["risk_exposure_summary"]

    # 3. Rank and select best route according to operational mode
    selected_route, alt_routes = rank_and_select_routes(candidate_raw_routes, route_mode)

    # 4. Construct overall explanation and limitations
    mode_name = route_mode.value
    overall_exp = (
        f"Route selected for mode '{mode_name}' based on candidate ranking. "
        f"{selected_route.explanation}"
    )

    limitations = [
        "Route calculation is performed by the routing engine. RESQ-AI provides hazard/risk intelligence used for route evaluation.",
        "Route risk is a decision-support score and is not a guarantee of road safety.",
        "No real-time traffic congestion or active road-closure data was inferred."
    ]

    response_payload = RouteResponsePayload(
        origin=origin,
        destination=destination,
        mode=route_mode,
        selected_route=selected_route,
        alternative_routes=alt_routes,
        route_risk_level=selected_route.risk_level,
        explanation=overall_exp,
        evidence_quality="HIGH",
        limitations=limitations
    )

    return response_payload.to_dict()
