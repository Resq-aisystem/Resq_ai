"""
Comprehensive Real Gemini API & Integration Verification Test Suite.
Verifies requirements 1-10 specified by user.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Step 1 & 2: Load backend/.env and verify GEMINI_API_KEY
dotenv_path = os.path.join(os.getcwd(), "backend", ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("GEMINI_API_KEY", "")
def log(msg):
    print(msg, flush=True)

log("===============================================================")
log("RESQ-AI — GEMINI INTEGRATION VERIFICATION TEST SUITE")
log("===============================================================")

log("\n--- STEP 1 & 2: API KEY LOAD VERIFICATION ---")
if not api_key:
    log("FAILED: GEMINI_API_KEY is not loaded from backend/.env!")
    sys.exit(1)

masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
log(f"GEMINI_API_KEY loaded successfully from backend/.env")
log(f"Masked API Key (security check): {masked_key}")

# Ensure project root is in sys.path
PROJECT_ROOT = os.getcwd()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESQ_AI_DIR = os.path.join(PROJECT_ROOT, "backend", "RESQ-AI")
if RESQ_AI_DIR not in sys.path:
    sys.path.insert(0, RESQ_AI_DIR)

from backend.services.gemini_service import generate_gemini_briefing, _generate_deterministic_briefing
from inference.decision_contract import get_city_decision_intelligence


# Step 3, 4, 5, 6, 7: Test Real Gemini Direct SDK Integration
log("\n--- STEP 3-7: DIRECT REAL GEMINI API CALL & NUMERICAL SCORE IMMUTABILITY ---")
context = get_city_decision_intelligence(city_name="Puri", district_name="PURI")

# Extract original numerical scores
orig_risk_score = context["flood_prediction"]["predicted_risk_score"]
orig_risk_level = context["flood_prediction"]["predicted_risk_level"]
orig_prio_score = context["action_plan"]["priority"]["score"]
orig_prio_level = context["action_plan"]["priority"]["level"]
orig_route_level = context["routes"]["balanced"]["route_risk_level"]

start_time = time.time()
real_briefing = generate_gemini_briefing(context, timeout_seconds=30.0)
latency_ms = (time.time() - start_time) * 1000

log(f"Response Latency: {latency_ms:.2f} ms")
log(f"Is Fallback: {real_briefing.get('is_fallback')}")
log(f"Provider: {real_briefing.get('provider')}")
log(f"Model Used: {real_briefing.get('model_used')}")

# Verify schema
required_keys = ["summary", "risk_explanation", "priority_explanation", "route_explanation", "recommended_actions", "monitoring_actions", "scenario_explanation", "limitations", "grounding_sources"]
schema_valid = all(k in real_briefing for k in required_keys)
log(f"Schema Validation (9 required keys): {'PASS' if schema_valid else 'FAIL'}")

# Verify numerical immutability
post_risk_score = context["flood_prediction"]["predicted_risk_score"]
post_risk_level = context["flood_prediction"]["predicted_risk_level"]
post_prio_score = context["action_plan"]["priority"]["score"]
post_prio_level = context["action_plan"]["priority"]["level"]
post_route_level = context["routes"]["balanced"]["route_risk_level"]

immutable = (
    orig_risk_score == post_risk_score and
    orig_risk_level == post_risk_level and
    orig_prio_score == post_prio_score and
    orig_prio_level == post_prio_level and
    orig_route_level == post_route_level
)

log(f"Numerical Scores Unmodified: {'PASS' if immutable else 'FAIL'}")

# Step 7B: In-Memory Caching Verification
log("\n--- STEP 7B: IN-MEMORY BRIEFING CACHE VERIFICATION ---")
t_cache_start = time.time()
cached_briefing = generate_gemini_briefing(context, timeout_seconds=30.0)
cache_latency_ms = (time.time() - t_cache_start) * 1000
is_cached = cached_briefing.get("is_cached", False)
log(f"Second Call Latency (Cached): {cache_latency_ms:.2f} ms")
log(f"Is Cached Flag: {is_cached}")
cache_pass = is_cached and (cache_latency_ms < 50.0)
log(f"Cache Test: {'PASS' if cache_pass else 'FAIL'}")


real_gemini_pass = (real_briefing.get("is_fallback") is False) and schema_valid and immutable and cache_pass


# Step 8: Test FastAPI Endpoint /api/v1/ai/gemini/briefing
log("\n--- STEP 8: FASTAPI ENDPOINT POST /api/v1/ai/gemini/briefing ---")
backend_url = "http://localhost:8000/api/v1/ai/gemini/briefing"
payload = json.dumps({"city_name": "Puri", "district_name": "PURI"}).encode("utf-8")
headers = {"Content-Type": "application/json"}

try:
    req = urllib.request.Request(backend_url, data=payload, headers=headers, method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req) as resp:
        endpoint_status = resp.status
        resp_data = json.loads(resp.read().decode("utf-8"))
        ep_latency = (time.time() - t0) * 1000
    log(f"HTTP Status: {endpoint_status}")
    log(f"Latency: {ep_latency:.2f} ms")
    ep_briefing = resp_data.get("gemini_briefing", {})
    ep_is_fallback = ep_briefing.get("is_fallback")
    log(f"Endpoint Is Fallback: {ep_is_fallback}")
    log(f"Endpoint Provider: {ep_briefing.get('provider')}")
    log(f"Endpoint Model Used: {ep_briefing.get('model_used')}")
    briefing_endpoint_pass = (endpoint_status == 200) and (ep_is_fallback is False)
except Exception as e:
    log(f"Endpoint test failed: {e}")
    briefing_endpoint_pass = False

# Step 9: Test Frontend Proxy Endpoint (Angular Dev Server :4200)
log("\n--- STEP 9: ANGULAR FRONTEND PROXY DISPLAY VERIFICATION ---")
frontend_url = "http://localhost:4200/api/v1/ai/gemini/briefing"
try:
    req = urllib.request.Request(frontend_url, data=payload, headers=headers, method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req) as resp:
        ng_status = resp.status
        ng_resp_data = json.loads(resp.read().decode("utf-8"))
        ng_latency = (time.time() - t0) * 1000
    log(f"Angular Proxy HTTP Status: {ng_status}")
    log(f"Angular Proxy Latency: {ng_latency:.2f} ms")
    ng_briefing = ng_resp_data.get("gemini_briefing", {})
    ng_is_fallback = ng_briefing.get("is_fallback")
    log(f"Angular Received Is Fallback: {ng_is_fallback}")
    angular_display_pass = (ng_status == 200) and (ng_is_fallback is False)
except Exception as e:
    log(f"Angular proxy test failed: {e}")
    angular_display_pass = False

# Step 10: Test Deterministic Fallback Separately
log("\n--- STEP 10: DETERMINISTIC FALLBACK SEPARATE TEST ---")
fallback_res = _generate_deterministic_briefing(context, fallback_reason="Simulated API Key Absence Test")
fb_is_fallback = fallback_res.get("is_fallback")
fb_provider = fallback_res.get("provider")
log(f"Fallback Is Fallback: {fb_is_fallback}")
log(f"Fallback Provider: {fb_provider}")
deterministic_fallback_pass = (fb_is_fallback is True) and ("Deterministic" in fb_provider)

log("\n===============================================================")
log("SUMMARY RESULTS REPORT:")
log("===============================================================")
log(f"REAL GEMINI API:           {'PASS' if real_gemini_pass else 'FAIL'}")
log(f"GEMINI BRIEFING ENDPOINT:  {'PASS' if briefing_endpoint_pass else 'FAIL'}")
log(f"ANGULAR GEMINI DISPLAY:    {'PASS' if angular_display_pass else 'FAIL'}")
log(f"DETERMINISTIC FALLBACK:    {'PASS' if deterministic_fallback_pass else 'FAIL'}")
log("===============================================================")

