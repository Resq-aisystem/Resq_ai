"""
Validation & Unsupported Claim Detection Engine for RESQ-AI Action Plans.

Validates action plan payloads against strict schema contracts, numerical score ranges,
and deterministic guardrail rules to prevent LLM hallucinations or unsupported claims.
"""

from typing import Tuple, Dict, Any, List
import yaml
from pathlib import Path

from action_plan.action_plan_contract import ActionPlanContract
from action_plan.grounded_context import GroundedContext

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "action_plan.yaml"

_CONFIG_CACHE = None


def _load_validation_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "forbidden_claim_keywords": [
                    "guaranteed", "definitely", "certainly", "will flood",
                    "will be safe", "road is blocked", "bridge is damaged",
                    "casualties confirmed", "fatalities reported", "evacuation time of"
                ]
            }
    return _CONFIG_CACHE


def validate_action_plan(
    plan: ActionPlanContract,
    context: GroundedContext
) -> Tuple[bool, List[str]]:
    """
    Validate ActionPlanContract against schema bounds, numerical grounding, and guardrail rules.

    Args:
        plan: ActionPlanContract object to validate.
        context: GroundedContext object containing verified ground truth.

    Returns:
        Tuple (is_valid: bool, errors: List[str])
    """
    errors = []
    cfg = _load_validation_config()
    forbidden_keywords = cfg.get("forbidden_claim_keywords", [
        "guaranteed", "definitely", "certainly", "will flood",
        "will be safe", "road is blocked", "bridge is damaged"
    ])

    # 1. Validate District & Date Match
    if plan.district != context.district:
        errors.append(f"District mismatch: expected '{context.district}', got '{plan.district}'")
    if plan.observation_date != context.observation_date:
        errors.append(f"Date mismatch: expected '{context.observation_date}', got '{plan.observation_date}'")

    # 2. Validate Numerical Grounding (Risk and Priority Scores must match context)
    r_score = float(plan.risk.get("score", -1.0))
    p_score = float(plan.priority.get("score", -1.0))

    if abs(r_score - context.risk_score) > 0.01:
        errors.append(f"Risk score mismatch: expected {context.risk_score}, got {r_score}")
    if abs(p_score - context.priority_score) > 0.01:
        errors.append(f"Priority score mismatch: expected {context.priority_score}, got {p_score}")

    # 3. Validate Score Bounds [0, 100]
    if not (0.0 <= r_score <= 100.0):
        errors.append(f"Risk score out of bounds [0, 100]: {r_score}")
    if not (0.0 <= p_score <= 100.0):
        errors.append(f"Priority score out of bounds [0, 100]: {p_score}")

    # 4. Validate Categorical Levels
    r_lvl = str(plan.risk.get("level", "")).upper()
    p_lvl = str(plan.priority.get("level", "")).upper()

    if r_lvl not in ["LOW", "MODERATE", "HIGH", "CRITICAL"]:
        errors.append(f"Invalid risk level: '{r_lvl}'")
    if p_lvl not in ["P1", "P2", "P3", "P4"]:
        errors.append(f"Invalid priority level: '{p_lvl}'")

    # 5. Unsupported Claim Detection (Guardrail keyword scanning)
    text_corpus = (
        f"{plan.situation_summary} "
        f"{' '.join(plan.key_evidence)} "
        f"{' '.join(plan.recommended_actions)} "
        f"{plan.route_recommendation.get('explanation', '')} "
        f"{' '.join(plan.monitoring_actions)}"
    ).lower()

    for kw in forbidden_keywords:
        if kw.lower() in text_corpus:
            errors.append(f"Unsupported claim detected containing forbidden keyword: '{kw}'")

    is_valid = (len(errors) == 0)
    return is_valid, errors
