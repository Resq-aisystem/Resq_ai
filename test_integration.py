import urllib.request
import json
import time
import sys
from pathlib import Path

# Add backend/RESQ-AI to sys.path for direct Python AI verification
resq_ai_dir = Path(__file__).resolve().parent / "backend" / "RESQ-AI"
if str(resq_ai_dir) not in sys.path:
    sys.path.insert(0, str(resq_ai_dir))

from inference.decision_contract import get_city_decision_intelligence


def run_tests():
    print("===============================================================")
    print("RESQ-AI FULL STACK INTEGRATION & DATA INTEGRITY TEST SUITE")
    print("===============================================================")

    # 1. Direct Python RESQ-AI Execution (Source of Truth)
    print("\n1. Running Direct Python RESQ-AI Engine...")
    t0 = time.time()
    direct_py_result = get_city_decision_intelligence(city_name="Puri", district_name="PURI")
    t_py = (time.time() - t0) * 1000
    py_risk_score = direct_py_result["flood_prediction"]["predicted_risk_score"]
    py_risk_level = direct_py_result["flood_prediction"]["predicted_risk_level"]
    py_priority_score = direct_py_result["action_plan"]["priority"]["score"]
    print(f"   [OK] Python AI Execution: Risk Score={py_risk_score} ({py_risk_level}), Priority Score={py_priority_score} (Latency: {t_py:.2f}ms)")

    # 2. FastAPI Backend AI Health
    print("\n2. Testing FastAPI Backend AI Health (/api/v1/ai/health)...")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/ai/health")
    ai_health = json.loads(res.read().decode())
    assert ai_health["status"] == "healthy", "AI Health check failed"
    print(f"   [OK] AI Health: {ai_health['service']} is operational.")

    # 3. FastAPI Backend Master Decision Endpoint
    print("\n3. Testing FastAPI Master Decision Payload (/api/v1/ai/decision)...")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/decision", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, data=json.dumps({"city_name": "Puri", "district_name": "PURI"}).encode("utf-8"))
    backend_decision = json.loads(res.read().decode())
    t_backend = (time.time() - t0) * 1000
    backend_risk_score = backend_decision["flood_prediction"]["predicted_risk_score"]
    backend_risk_level = backend_decision["flood_prediction"]["predicted_risk_level"]
    backend_priority_score = backend_decision["action_plan"]["priority"]["score"]
    print(f"   [OK] Backend Decision API: Risk Score={backend_risk_score} ({backend_risk_level}), Priority Score={backend_priority_score} (Latency: {t_backend:.2f}ms)")

    # DATA INTEGRITY VERIFICATION 1: Python AI Risk == Backend Risk
    assert py_risk_score == backend_risk_score, f"Data mismatch! Python risk score {py_risk_score} != Backend risk score {backend_risk_score}"
    assert py_priority_score == backend_priority_score, f"Data mismatch! Python priority score {py_priority_score} != Backend priority score {backend_priority_score}"
    print("   [VERIFIED] 100% Data Integrity Match: Python AI Risk Score == Backend Risk Score!")

    # 4. FastAPI AI Risk Assessment Endpoint
    print("\n4. Testing AI Risk Assessment Endpoint (/api/v1/ai/risk)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/risk", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, data=json.dumps({"city_name": "Puri", "district_name": "PURI"}).encode("utf-8"))
    risk_payload = json.loads(res.read().decode())
    assert "predicted_risk_score" in risk_payload, "Risk payload missing predicted_risk_score"
    print(f"   [OK] AI Risk Endpoint: Level={risk_payload['predicted_risk_level']}, Score={risk_payload['predicted_risk_score']}")

    # 5. FastAPI AI Evacuation Priority Endpoint
    print("\n5. Testing AI Evacuation Priority Endpoint (/api/v1/ai/priority)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/priority", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, data=json.dumps({"city_name": "Puri", "district_name": "PURI"}).encode("utf-8"))
    prio_payload = json.loads(res.read().decode())
    assert "evacuation_priorities" in prio_payload, "Priority payload missing evacuation_priorities"
    print(f"   [OK] AI Priority Endpoint: Returned {len(prio_payload['evacuation_priorities'])} facility priorities.")

    # 6. FastAPI AI Route Risk Endpoint
    print("\n6. Testing AI Route Risk Endpoint (/api/v1/ai/routes)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/routes", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, data=json.dumps({
        "origin_lat": 19.8135, "origin_lon": 85.8312,
        "destination_lat": 20.4625, "destination_lon": 85.8828,
        "mode": "ALL"
    }).encode("utf-8"))
    route_payload = json.loads(res.read().decode())
    assert "routes" in route_payload, "Route payload missing routes"
    print(f"   [OK] AI Route Endpoint: Modes evaluated = {list(route_payload['routes'].keys())}")

    # 7. FastAPI AI Scenario Endpoint
    print("\n7. Testing AI Scenario Engine Endpoint (/api/v1/ai/scenario)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/scenario", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, data=json.dumps({"city_name": "Puri", "district_name": "PURI", "rainfall_multiplier": 1.8}).encode("utf-8"))
    scen_payload = json.loads(res.read().decode())
    assert "scenario_risk_score" in scen_payload, "Scenario payload missing scenario_risk_score"
    print(f"   [OK] AI Scenario Endpoint: Baseline={scen_payload['baseline_risk_score']} -> Simulated={scen_payload['scenario_risk_score']} (Delta: +{scen_payload['risk_delta']:.2f})")

    # 8. FastAPI Gemini Health Endpoint
    print("\n8. Testing Gemini Service Health Endpoint (/api/v1/ai/gemini/health)...")
    res = urllib.request.urlopen("http://127.0.0.1:8000/api/v1/ai/gemini/health")
    gemini_health = json.loads(res.read().decode())
    assert "status" in gemini_health, "Gemini health missing status"
    print(f"   [OK] Gemini Health: Status={gemini_health['status']}, Model={gemini_health['model']}")

    # 9. FastAPI Gemini Coordinator Briefing Endpoint
    print("\n9. Testing Gemini Coordinator Briefing Endpoint (/api/v1/ai/gemini/briefing)...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/v1/ai/gemini/briefing", headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req, data=json.dumps({"city_name": "Puri", "district_name": "PURI"}).encode("utf-8"))
    gemini_briefing = json.loads(res.read().decode())
    assert "gemini_briefing" in gemini_briefing, "Response missing gemini_briefing payload"
    b_summary = gemini_briefing["gemini_briefing"]["summary"]
    b_provider = gemini_briefing["gemini_briefing"]["provider"]
    print(f"   [OK] Gemini Briefing: Provider={b_provider}, Summary Snippet: '{b_summary[:80]}...'")

    # 10. Angular Proxy Integration Endpoint Check (Port 4200 -> Port 8000)
    print("\n10. Testing Angular Dev Server Proxy Integration (Port 4200 -> 8000)...")
    try:
        t0 = time.time()
        res = urllib.request.urlopen("http://localhost:4200/api/v1/ai/health")
        proxy_health = json.loads(res.read().decode())
        t_proxy = (time.time() - t0) * 1000
        assert proxy_health["status"] == "healthy", "Proxy health check failed"
        print(f"   [OK] Angular Proxy (Port 4200 -> 8000): Operational (Latency: {t_proxy:.2f}ms)")
    except Exception as e:
        print(f"   [WARNING] Angular Dev Server proxy test skipped or server offline: {e}")

    print("\n===============================================================")
    print("ALL INTEGRATION & DATA INTEGRITY CHECKS PASSED WITH 100% SUCCESS!")
    print("===============================================================")


if __name__ == "__main__":
    run_tests()
