"""
LLM Client Interface & Deterministic Fallback Pipeline for RESQ-AI.

Interfaces with external LLM providers (e.g. OpenAI) when credentials are available,
and provides a zero-dependency deterministic fallback engine when API keys are unconfigured or unavailable.
"""

from pathlib import Path
import os
import json
import urllib.request
import urllib.parse
import yaml

from action_plan.grounded_context import GroundedContext
from action_plan.action_plan_contract import ActionPlanContract
from action_plan.prompt_builder import SYSTEM_PROMPT, build_llm_prompt

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "action_plan.yaml"

_CONFIG_CACHE = None


def _load_action_plan_config():
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                _CONFIG_CACHE = yaml.safe_load(f)
        else:
            _CONFIG_CACHE = {
                "llm": {
                    "provider": "openai",
                    "model_name": "gpt-4o-mini",
                    "api_timeout_seconds": 10.0,
                    "api_key_env_var": "OPENAI_API_KEY"
                },
                "pipeline": {"fallback_enabled": True}
            }
    return _CONFIG_CACHE


def generate_llm_action_plan(context: GroundedContext) -> ActionPlanContract:
    """
    Generate an Emergency Action Plan via deterministic rule-based engine.
    External LLM calls are disabled per system policy.
    """
    return generate_deterministic_fallback_plan(context)

    # Attempt LLM API call if key is present
    try:
        user_prompt = build_llm_prompt(context)
        payload = {
            "model": llm_cfg.get("model_name", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": float(llm_cfg.get("temperature", 0.1)),
            "max_tokens": int(llm_cfg.get("max_output_tokens", 800)),
            "response_format": {"type": "json_object"}
        }

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        timeout = float(llm_cfg.get("api_timeout_seconds", 10.0))

        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                res_body = json.loads(response.read().decode("utf-8"))
                content = res_body["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)

                return ActionPlanContract(
                    district=context.district,
                    observation_date=context.observation_date,
                    risk={"score": context.risk_score, "level": context.risk_level},
                    priority={"score": context.priority_score, "level": context.priority_level},
                    situation_summary=parsed_json.get("situation_summary", ""),
                    key_evidence=parsed_json.get("key_evidence", []),
                    recommended_actions=parsed_json.get("recommended_actions", []),
                    route_recommendation=parsed_json.get("route_recommendation", {
                        "mode": "BALANCED", "risk_score": 0.0, "explanation": "Route evaluation unsupplied"
                    }),
                    monitoring_actions=parsed_json.get("monitoring_actions", []),
                    limitations=parsed_json.get("limitations", context.limitations),
                    evidence_quality=context.evidence_quality,
                    is_fallback=False
                )
    except Exception as e:
        # Graceful fallback on network timeout, quota failure, or invalid response
        pass

    return generate_deterministic_fallback_plan(context)


def generate_deterministic_fallback_plan(context: GroundedContext) -> ActionPlanContract:
    """
    Deterministic rule-based Action Plan generator used when LLM credentials are unconfigured or offline.
    """
    p_lvl = context.priority_level
    r_lvl = context.risk_level
    d_name = context.district
    v_flags = context.vulnerability_flags

    # 1. Generate Situation Summary
    if p_lvl == "P1":
        summary = (
            f"District {d_name} is classified as P1 (Immediate Attention) with a Risk Score of "
            f"{context.risk_score:.1f} ({r_lvl}) and Priority Score of {context.priority_score:.1f}. "
            f"Active risk drivers include high terrain flood susceptibility and historical recurrence."
        )
    elif p_lvl == "P2":
        summary = (
            f"District {d_name} is classified as P2 (High Priority) with a Risk Score of "
            f"{context.risk_score:.1f} ({r_lvl}) and Priority Score of {context.priority_score:.1f}. "
            f"Elevated hazard exposure indicates high readiness requirement."
        )
    elif p_lvl == "P3":
        summary = (
            f"District {d_name} is classified as P3 (Monitor / Prepare) with a Risk Score of "
            f"{context.risk_score:.1f} ({r_lvl}) and Priority Score of {context.priority_score:.1f}. "
            f"Situation calls for routine watch and resource pre-positioning review."
        )
    else:
        summary = (
            f"District {d_name} is classified as P4 (Routine Monitoring) with a Risk Score of "
            f"{context.risk_score:.1f} ({r_lvl}) and Priority Score of {context.priority_score:.1f}. "
            f"Baseline situational risk is low."
        )

    # 2. Extract Key Evidence
    evidence_list = []
    for f in context.priority_factors:
        evidence_list.append(f"{f['factor']}: {f['evidence']}")

    # 3. Recommended Actions
    actions = []
    if p_lvl in ["P1", "P2"]:
        actions.append(f"Prioritize District {d_name} for immediate situational monitoring and operational review.")
        actions.append("Verify pre-positioning of local emergency response equipment and personnel.")
    else:
        actions.append(f"Maintain routine watch over weather developments in District {d_name}.")
        actions.append("Review standard response protocols.")

    if "HIGH_FLOOD_SUSCEPTIBILITY" in v_flags:
        actions.append("Focus monitoring on low-lying terrain zones identified by 30m GFSM susceptibility ratings.")
    if "HIGH_HYDROLOGICAL_VULNERABILITY" in v_flags:
        actions.append("Track catchment runoff and soil moisture saturation indicators.")

    # 4. Route Recommendation
    if context.route_info and isinstance(context.route_info, dict):
        route_rec = {
            "mode": context.route_info.get("mode", "BALANCED"),
            "risk_score": context.route_info.get("route_risk_score", 0.0),
            "explanation": context.route_info.get("explanation", "Evaluated via RESQ-AI Route Engine.")
        }
    else:
        route_rec = {
            "mode": "BALANCED",
            "risk_score": round(context.risk_score * 0.9, 2),
            "explanation": f"Evaluated default BALANCED rescue corridor for {d_name}."
        }

    # 5. Monitoring Actions
    monitoring = [
        "Continue tracking IMD daily rainfall updates and 7-day rolling precipitation trends.",
        "Re-evaluate priority score if new extreme precipitation observations arrive.",
        "Verify alternative access routes before dispatching emergency teams."
    ]

    return ActionPlanContract(
        district=context.district,
        observation_date=context.observation_date,
        risk={"score": context.risk_score, "level": context.risk_level},
        priority={"score": context.priority_score, "level": context.priority_level},
        situation_summary=summary,
        key_evidence=evidence_list,
        recommended_actions=actions,
        route_recommendation=route_rec,
        monitoring_actions=monitoring,
        limitations=context.limitations,
        evidence_quality=context.evidence_quality,
        is_fallback=True
    )
