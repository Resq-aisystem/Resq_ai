"""
Operational Route Modes Implementation for RESQ-AI.

Implements FASTEST, SAFEST, and BALANCED route mode scoring and ranking logic.
Applies transparent configurable weights between travel duration cost and hazard risk exposure.
"""

from pathlib import Path
import yaml
from route_risk.route_scoring.route_contract import RouteMode, RouteCandidate

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "route_risk.yaml"

_CONFIG_CACHE = None


def _load_mode_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "mode_weights": {
                    "FASTEST": {"time_weight": 0.80, "risk_weight": 0.20},
                    "SAFEST": {"time_weight": 0.20, "risk_weight": 0.80},
                    "BALANCED": {"time_weight": 0.50, "risk_weight": 0.50}
                }
            }
    return _CONFIG_CACHE


def rank_and_select_routes(candidates: list, mode: RouteMode) -> tuple:
    """
    Score and rank candidate routes according to requested mode (FASTEST, SAFEST, BALANCED).

    Args:
        candidates: List of dicts or RouteCandidate objects containing duration_minutes and route_risk_score.
        mode: RouteMode Enum (FASTEST, SAFEST, BALANCED).

    Returns:
        tuple (selected_route: RouteCandidate, alternative_routes: list of RouteCandidate)
    """
    if not candidates:
        raise ValueError("Cannot score empty candidate route list.")

    cfg = _load_mode_config()
    mode_str = mode.value if isinstance(mode, RouteMode) else str(mode).upper()
    weights_dict = cfg.get("mode_weights", {}).get(mode_str, {"time_weight": 0.50, "risk_weight": 0.50})

    w_time = float(weights_dict["time_weight"])
    w_risk = float(weights_dict["risk_weight"])

    max_duration = max(float(c.get("duration_minutes", 1.0) if isinstance(c, dict) else c.duration_minutes) for c in candidates)
    max_duration = max(1.0, max_duration)

    scored_candidates = []

    for c in candidates:
        if isinstance(c, dict):
            r_id = c["route_id"]
            dist_km = float(c["distance_km"])
            dur_min = float(c["duration_minutes"])
            risk_score = float(c["route_risk_score"])
            risk_lvl = c.get("risk_level", "MODERATE")
            exposure_sum = c.get("risk_exposure_summary", {})
            waypoints = c.get("waypoints", [])
        else:
            r_id = c.route_id
            dist_km = float(c.distance_km)
            dur_min = float(c.duration_minutes)
            risk_score = float(c.route_risk_score)
            risk_lvl = c.risk_level
            exposure_sum = c.risk_exposure_summary
            waypoints = c.waypoints

        # Calculate Normalized Time Cost (0 to 100)
        norm_time = (dur_min / max_duration) * 100.0
        # Risk Score is already 0 to 100
        norm_risk = risk_score

        # Composite Mode Score (Lower is better)
        mode_score = w_time * norm_time + w_risk * norm_risk

        # Generate objective explanation
        if mode_str == "FASTEST":
            exp = f"Candidate {r_id} evaluated for FASTEST mode (weight: 80% duration, 20% risk hazard)."
        elif mode_str == "SAFEST":
            exp = f"Candidate {r_id} evaluated for SAFEST mode (weight: 20% duration, 80% risk hazard)."
        else:
            exp = f"Candidate {r_id} evaluated for BALANCED mode (weight: 50% duration, 50% risk hazard)."

        cand_obj = RouteCandidate(
            route_id=r_id,
            distance_km=dist_km,
            duration_minutes=dur_min,
            route_risk_score=risk_score,
            risk_level=risk_lvl,
            route_mode_score=round(mode_score, 4),
            selected=False,
            risk_exposure_summary=exposure_sum,
            explanation=exp,
            waypoints=waypoints
        )
        scored_candidates.append(cand_obj)

    # Sort candidates by route_mode_score ascending (lowest cost / score wins)
    scored_candidates.sort(key=lambda x: x.route_mode_score)

    # Mark selected candidate
    selected_route = scored_candidates[0]
    selected_route.selected = True

    # Update explanation for selected route
    if mode_str == "FASTEST":
        selected_route.explanation = "Selected because it has the lowest estimated routing duration among available candidates."
    elif mode_str == "SAFEST":
        selected_route.explanation = "Selected because it has the lowest RESQ-AI hazard exposure score among available candidates."
    else:
        selected_route.explanation = "Selected because it provides the best configured trade-off between routing duration and hazard exposure."

    alternative_routes = scored_candidates[1:]

    return selected_route, alternative_routes
