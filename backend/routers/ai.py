from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Tuple
import logging
import sys
from pathlib import Path

# Ensure backend/RESQ-AI is in sys.path
RESQ_AI_DIR = Path(__file__).resolve().parent.parent / "RESQ-AI"
if str(RESQ_AI_DIR) not in sys.path:
    sys.path.insert(0, str(RESQ_AI_DIR))

# Import RESQ-AI core engines
try:
    from inference.decision_contract import get_city_decision_intelligence
    from flood_prediction.predictor import predict_6hour_flood_risk
    from priority.emergency_priority.facility_priority import get_facility_evacuation_priorities
    from route_risk.route_scoring.route_service import get_rescue_route
    from scenario.scenario_engine import run_scenario_analysis, ScenarioConfig
    from action_plan.action_plan_engine import generate_action_plan
    from provenance.provenance_schema import create_provenance_record
except ImportError as e:
    logging.error(f"Failed to import RESQ-AI modules: {e}")
    raise e

# Import Gemini service
from backend.services.gemini_service import get_gemini_health, generate_gemini_briefing

router = APIRouter()
logger = logging.getLogger(__name__)


# Request Models
class RiskRequest(BaseModel):
    city_name: str = Field(default="Puri", description="Target city name")
    district_name: str = Field(default="PURI", description="Target district name")
    observation_date: Optional[str] = Field(default=None, description="ISO date YYYY-MM-DD")


class PriorityRequest(BaseModel):
    city_name: str = Field(default="Puri")
    district_name: str = Field(default="PURI")
    observation_date: Optional[str] = None


class RouteRequest(BaseModel):
    origin_lat: float = Field(default=19.8135)
    origin_lon: float = Field(default=85.8312)
    destination_lat: float = Field(default=20.4625)
    destination_lon: float = Field(default=85.8828)
    mode: str = Field(default="BALANCED", description="FASTEST, SAFEST, or BALANCED")
    observation_date: Optional[str] = None


class ScenarioRequest(BaseModel):
    city_name: str = Field(default="Puri")
    district_name: str = Field(default="PURI")
    scenario_id: str = Field(default="sc_surge_80pct")
    scenario_name: str = Field(default="Extreme 80% Rainfall Surge Scenario")
    rainfall_multiplier: float = Field(default=1.8)
    observation_date: Optional[str] = None


class DecisionRequest(BaseModel):
    city_name: str = Field(default="Puri")
    district_name: str = Field(default="PURI")
    observation_date: Optional[str] = None
    route_mode: str = Field(default="BALANCED")
    origin_coords: Tuple[float, float] = Field(default=(19.8135, 85.8312))
    dest_coords: Tuple[float, float] = Field(default=(20.4625, 85.8828))


@router.get("/health")
def ai_health():
    """Verify operational status of RESQ-AI intelligence engines"""
    return {
        "status": "healthy",
        "service": "RESQ-AI Decision Intelligence Engine",
        "engines": {
            "risk_engine": "operational",
            "priority_engine": "operational",
            "route_risk_engine": "operational",
            "scenario_engine": "operational",
            "action_plan_engine": "operational_deterministic",
            "provenance_engine": "operational"
        }
    }


@router.post("/risk")
def get_risk_assessment(req: RiskRequest):
    """6-Hour Predictive Flood Risk Assessment"""
    try:
        result = predict_6hour_flood_risk(
            city_name=req.city_name,
            district_name=req.district_name,
            observation_date=req.observation_date
        )
        return result.to_dict()
    except Exception as e:
        logger.error(f"Risk engine error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk engine assessment failed: {str(e)}"
        )


@router.post("/priority")
def get_evacuation_priorities(req: PriorityRequest):
    """Emergency Evacuation Priorities for Facilities & Zones"""
    try:
        priorities = get_facility_evacuation_priorities(
            city_name=req.city_name,
            district_name=req.district_name,
            observation_date=req.observation_date
        )
        return {"evacuation_priorities": priorities}
    except Exception as e:
        logger.error(f"Priority engine error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Priority engine calculation failed: {str(e)}"
        )


@router.post("/routes")
def get_route_risk(req: RouteRequest):
    """Flood-Aware Rescue Routing Intelligence"""
    try:
        if req.mode.upper() == "ALL":
            routes = {}
            for m in ["FASTEST", "SAFEST", "BALANCED"]:
                routes[m.lower()] = get_rescue_route(
                    origin_lat=req.origin_lat,
                    origin_lon=req.origin_lon,
                    destination_lat=req.destination_lat,
                    destination_lon=req.destination_lon,
                    mode=m,
                    observation_date=req.observation_date
                )
            return {"routes": routes}
        else:
            route = get_rescue_route(
                origin_lat=req.origin_lat,
                origin_lon=req.origin_lon,
                destination_lat=req.destination_lat,
                destination_lon=req.destination_lon,
                mode=req.mode,
                observation_date=req.observation_date
            )
            return {"route": route}
    except Exception as e:
        logger.error(f"Route risk engine error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Route risk calculation failed: {str(e)}"
        )


@router.post("/scenario")
def evaluate_scenario(req: ScenarioRequest):
    """What-If Flood Scenario Simulation"""
    try:
        config = ScenarioConfig(
            scenario_id=req.scenario_id,
            scenario_name=req.scenario_name,
            rainfall_multiplier=req.rainfall_multiplier
        )
        result = run_scenario_analysis(
            city_name=req.city_name,
            district_name=req.district_name,
            scenario=config,
            observation_date=req.observation_date
        )
        return result.to_dict()
    except Exception as e:
        logger.error(f"Scenario engine error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario analysis failed: {str(e)}"
        )


@router.post("/action-plan")
def get_action_plan(req: DecisionRequest):
    """Deterministic Emergency Action Plan"""
    try:
        plan = generate_action_plan(
            district_name=req.district_name,
            observation_date=req.observation_date,
            route_mode=req.route_mode,
            origin_coords=req.origin_coords,
            dest_coords=req.dest_coords
        )
        return plan
    except Exception as e:
        logger.error(f"Action plan engine error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action plan generation failed: {str(e)}"
        )


@router.post("/decision")
@router.get("/decision")
def get_decision_intelligence(
    city_name: str = "Puri",
    district_name: str = "PURI",
    observation_date: Optional[str] = None,
    route_mode: str = "BALANCED",
    origin_lat: float = 19.8135,
    origin_lon: float = 85.8312,
    dest_lat: float = 20.4625,
    dest_lon: float = 85.8828
):
    """Master Decision Intelligence Payload (PRD Aligned)"""
    try:
        payload = get_city_decision_intelligence(
            city_name=city_name,
            district_name=district_name,
            observation_date=observation_date,
            route_mode=route_mode,
            origin_coords=(origin_lat, origin_lon),
            dest_coords=(dest_lat, dest_lon)
        )
        return payload
    except Exception as e:
        logger.error(f"Master decision intelligence error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Master decision payload generation failed: {str(e)}"
        )


class GeminiBriefingRequest(BaseModel):
    city_name: str = Field(default="Puri")
    district_name: str = Field(default="PURI")
    observation_date: Optional[str] = None
    route_mode: str = Field(default="BALANCED")
    decision_context: Optional[Dict[str, Any]] = None


@router.get("/gemini/health")
def gemini_health():
    """Health check for Google Gemini API integration"""
    return get_gemini_health()


@router.post("/gemini/briefing")
def get_gemini_briefing(req: GeminiBriefingRequest):
    """
    Grounded Google Gemini Emergency Coordinator Briefing Endpoint.

    Takes verified RESQ-AI decision intelligence context and returns an
    explainable coordinator briefing. Never alters underlying RESQ-AI numerical scores.
    """
    try:
        # If decision_context is not provided, fetch live master decision contract
        ctx = req.decision_context
        if not ctx:
            ctx = get_city_decision_intelligence(
                city_name=req.city_name,
                district_name=req.district_name,
                observation_date=req.observation_date,
                route_mode=req.route_mode
            )

        briefing = generate_gemini_briefing(ctx)
        return {
            "verified_decision": ctx,
            "gemini_briefing": briefing,
            "provenance": ctx.get("provenance", {}),
            "limitations": briefing.get("limitations", [])
        }
    except Exception as e:
        logger.error(f"Gemini briefing endpoint error: {str(e)}")
        # Fallback to deterministic briefing without failing request
        ctx = get_city_decision_intelligence(city_name=req.city_name, district_name=req.district_name)
        fallback_briefing = generate_gemini_briefing(ctx)
        return {
            "verified_decision": ctx,
            "gemini_briefing": fallback_briefing,
            "provenance": ctx.get("provenance", {}),
            "limitations": fallback_briefing.get("limitations", [])
        }

