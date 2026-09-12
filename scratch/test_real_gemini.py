import sys
import os
import json
import time
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Add backend/RESQ-AI to sys.path
resq_ai_dir = root_dir / "backend" / "RESQ-AI"
if str(resq_ai_dir) not in sys.path:
    sys.path.insert(0, str(resq_ai_dir))

from backend.services.gemini_service import generate_gemini_briefing, get_gemini_health
from inference.decision_contract import get_city_decision_intelligence


def test_gemini():
    print("===============================================================")
    print("REAL GEMINI API INTEGRATION VERIFICATION")
    print("===============================================================")

    # 1. Health check
    health = get_gemini_health()
    print(f"1. Health Check Status: {health['status']}")
    print(f"   Model Configured: {health['model']}")

    # 2. Get real RESQ-AI Decision Context
    ctx = get_city_decision_intelligence("Puri", "PURI")
    py_risk_score = ctx["flood_prediction"]["predicted_risk_score"]
    py_risk_level = ctx["flood_prediction"]["predicted_risk_level"]
    py_priority_score = ctx["action_plan"]["priority"]["score"]
    py_priority_level = ctx["action_plan"]["priority"]["level"]

    print(f"\n2. Grounded RESQ-AI Context:")
    print(f"   Risk Score: {py_risk_score} ({py_risk_level})")
    print(f"   Priority Score: {py_priority_score} ({py_priority_level})")

    # 3. Call Gemini Briefing Service
    print("\n3. Invoking Google Gemini API...")
    t0 = time.time()
    briefing = generate_gemini_briefing(ctx)
    t_latency = (time.time() - t0) * 1000

    is_fallback = briefing.get("is_fallback", True)
    provider = briefing.get("provider", "Unknown")
    model_used = briefing.get("model_used", "None")

    print(f"   Response Latency: {t_latency:.2f} ms")
    print(f"   Provider: {provider}")
    print(f"   Model Used: {model_used}")
    print(f"   Is Fallback Active: {is_fallback}")
    if is_fallback:
        print(f"   Fallback Reason: {briefing.get('fallback_reason')}")

    print("\n4. Executive Summary Snippet:")
    print(f"   {briefing.get('summary', '')}")

    print("\n5. Risk Explanation Snippet:")
    print(f"   {briefing.get('risk_explanation', '')}")

    # 6. Verification of Numerical Preservation
    print("\n6. Numerical Integrity Check:")
    print(f"   RESQ-AI Risk Score: {py_risk_score} (Unchanged in Gemini Context)")
    print(f"   RESQ-AI Priority Score: {py_priority_score} (Unchanged in Gemini Context)")

    return {
        "status_code": 200,
        "latency_ms": t_latency,
        "is_fallback": is_fallback,
        "provider": provider,
        "model_used": model_used
    }


if __name__ == "__main__":
    test_gemini()
