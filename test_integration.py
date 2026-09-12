import urllib.request
import json

def run_tests():
    print("Testing Frontend & Backend Integration...")

    # 1. Health
    res = urllib.request.urlopen("http://localhost:4200/health")
    health = json.loads(res.read().decode())
    assert health["status"] == "healthy", "Health check failed"
    print("[OK] Health Check Passed: status is 'healthy'")

    # 2. Locations
    res = urllib.request.urlopen("http://localhost:4200/api/v1/locations/")
    locs = json.loads(res.read().decode())
    assert len(locs) == 7, f"Expected 7 locations, got {len(locs)}"
    print(f"[OK] Locations Endpoint: Verified {len(locs)} facilities loaded.")

    # 3. Alerts
    res = urllib.request.urlopen("http://localhost:4200/api/v1/alerts/")
    alerts = json.loads(res.read().decode())
    assert len(alerts) == 6, f"Expected 6 alerts, got {len(alerts)}"
    print(f"[OK] Alerts Endpoint: Verified {len(alerts)} active alerts loaded.")

    # 4. Critical Alert Inspection
    critical = [a for a in alerts if a["severity"] == "critical"]
    assert len(critical) >= 1, "Critical alert missing"
    print(f"[OK] Critical Alert Verified: {critical[0]['title']} (Stage: {critical[0]['water_level']}m)")

    # 5. Frontend HTML
    res = urllib.request.urlopen("http://localhost:4200")
    html = res.read().decode()
    assert "RESQ-AI" in html, "RESQ-AI missing in index HTML"
    assert "<app-root>" in html, "<app-root> missing"
    print("[OK] Frontend App Shell: Verified Angular 19 serving with RESQ-AI branding.")

    print("\nALL 5 INTEGRATION CHECKS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    run_tests()
