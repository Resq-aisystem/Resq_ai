"""
RESQ-AI Grounded Emergency Action Plan Engine Entrypoint.

Exposes generate_action_plan() endpoint to convert structured RESQ-AI evidence
into grounded, validated, human-readable emergency action plans.
"""

from typing import Dict, Any, Optional
from action_plan.grounded_context import build_grounded_context
from action_plan.llm_client import generate_llm_action_plan, generate_deterministic_fallback_plan
from action_plan.validation import validate_action_plan


def generate_action_plan(
    district_name: str,
    observation_date: Optional[str] = None,
    route_mode: str = "BALANCED",
    origin_coords: Optional[tuple] = None,
    dest_coords: Optional[tuple] = None
) -> Dict[str, Any]:
    """
    Generate a validated grounded Emergency Action Plan for a district.

    Args:
        district_name: Name of target district.
        observation_date: ISO date string 'YYYY-MM-DD' (defaults to latest available IMD date).
        route_mode: Operational route mode ("FASTEST", "SAFEST", "BALANCED").
        origin_coords: Optional tuple (lat, lon).
        dest_coords: Optional tuple (lat, lon).

    Returns:
        Structured JSON-compatible dictionary payload matching ActionPlanContract.
    """
    # 1. Build Grounded Context from verified deterministic engines
    context = build_grounded_context(
        district_name=district_name,
        observation_date=observation_date,
        route_mode=route_mode,
        origin_coords=origin_coords,
        dest_coords=dest_coords
    )

    # 2. Generate Action Plan via LLM / Fallback Client
    plan_candidate = generate_llm_action_plan(context)

    # 3. Validate Output Against Schema & Guardrails
    is_valid, validation_errors = validate_action_plan(plan_candidate, context)

    # 4. Fallback to deterministic engine if validation failed
    if not is_valid:
        print(f"Warning: LLM validation failed for district '{district_name}' with errors: {validation_errors}. Triggering deterministic fallback.")
        plan_candidate = generate_deterministic_fallback_plan(context)

    return plan_candidate.to_dict()
