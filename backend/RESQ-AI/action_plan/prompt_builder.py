"""
Grounded Prompt Builder for RESQ-AI Emergency Action Plan Engine.

Constructs strict system and user prompts enforcing zero-hallucination,
grounded context summarization rules for the LLM.
"""

import json
from action_plan.grounded_context import GroundedContext


SYSTEM_PROMPT = """You are an emergency decision-support summarization assistant for the RESQ-AI platform.

STRICT GROUNDING & SUMMARIZATION RULES:
1. Use ONLY the supplied RESQ-AI context provided in the user prompt.
2. Do NOT invent facts or extrapolate unverified information.
3. Do NOT estimate missing population numbers or demographics.
4. Do NOT estimate casualties, fatalities, or injury counts.
5. Do NOT invent infrastructure damage (bridges, buildings, hospitals, schools).
6. Do NOT invent active road closures, traffic congestion, or debris.
7. Do NOT invent flood water depths or river inundation levels.
8. Do NOT invent specific evacuation times or troop dispatch counts.
9. Do NOT invent future weather forecasts beyond the provided observation date.
10. Do NOT convert risk scores into calibrated probabilities or percentages.
11. Do NOT claim guaranteed safety, total immunity, or guaranteed evacuation success.
12. Clearly distinguish historical evidence (GDIS/IFI priors) from current situational evidence (IMD rainfall).
13. If evidence or routing data is unavailable, state it explicitly as unavailable.
14. Return ONLY a single valid JSON object strictly adhering to the specified schema. No conversational preamble or postscript.
"""


def build_llm_prompt(context: GroundedContext) -> str:
    """
    Build structured JSON user prompt containing verified context and JSON output instructions.

    Args:
        context: GroundedContext object containing verified evidence.

    Returns:
        Formatted prompt string.
    """
    ctx_dict = context.to_dict()

    user_prompt = f"""EVALUATE THE FOLLOWING VERIFIED RESQ-AI EVIDENCE AND GENERATE A GROUNDED EMERGENCY ACTION PLAN.

--- VERIFIED RESQ-AI EVIDENCE ---
{json.dumps(ctx_dict, indent=2)}

--- REQUIRED OUTPUT JSON FORMAT ---
Return a JSON object with the exact following fields:
{{
  "district": "{context.district}",
  "observation_date": "{context.observation_date}",
  "risk": {{
    "score": {context.risk_score},
    "level": "{context.risk_level}"
  }},
  "priority": {{
    "score": {context.priority_score},
    "level": "{context.priority_level}"
  }},
  "situation_summary": "<Concise 2-3 sentence grounded summary of current risk level and key drivers>",
  "key_evidence": [
    "<Bullet point listing verified rainfall/terrain/recurrence evidence>"
  ],
  "recommended_actions": [
    "<Bullet point listing practical operational action grounded in evidence>"
  ],
  "route_recommendation": {{
    "mode": "<FASTEST|SAFEST|BALANCED|NOT_AVAILABLE>",
    "risk_score": <float or 0.0>,
    "explanation": "<Objective explanation of route recommendation if available>"
  }},
  "monitoring_actions": [
    "<Bullet point listing monitoring or follow-up action>"
  ],
  "limitations": [
    "Decision-support output only; does not replace official emergency command orders."
  ],
  "evidence_quality": "{context.evidence_quality}",
  "is_fallback": false
}}
"""
    return user_prompt
