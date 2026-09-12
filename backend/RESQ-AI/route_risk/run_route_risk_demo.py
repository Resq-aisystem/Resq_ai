"""
RESQ-AI Route Risk & Rescue Routing Demo Script.

Evaluates sample rescue origin-destination coordinate pairs across FASTEST, SAFEST, and BALANCED modes.
Saves evaluated route results to:
- data/processed/routes/route_results.json
- data/processed/routes/route_results.csv
"""

import argparse
from pathlib import Path
import json
import pandas as pd

from route_risk.route_scoring.route_service import get_rescue_route

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "routes"


def run_route_risk_demo():
    """
    Run route risk evaluation for sample origin-destination pairs.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Sample Route Test Coordinates (e.g. Kolkata -> Alipurduar, Puri -> Cuttack, Kochi -> Wayanad)
    sample_scenarios = [
        {
            "name": "Kolkata to Alipurduar Emergency Corridor",
            "origin": (22.5726, 88.3639),
            "destination": (26.4886, 89.5271)
        },
        {
            "name": "Puri to Cuttack Disaster Relief Route",
            "origin": (19.8135, 85.8312),
            "destination": (20.4625, 85.8828)
        },
        {
            "name": "Kochi to Wayanad Rescue Corridor",
            "origin": (9.9312, 76.2673),
            "destination": (11.6854, 76.1320)
        }
    ]

    modes = ["FASTEST", "SAFEST", "BALANCED"]
    all_demo_results = []
    csv_rows = []

    print("Starting RESQ-AI Rescue Routing Engine Demo Evaluation...\n")

    for sc in sample_scenarios:
        sc_name = sc["name"]
        o_lat, o_lon = sc["origin"]
        d_lat, d_lon = sc["destination"]

        print(f"--- Scenario: {sc_name} ---")
        print(f"Origin: ({o_lat}, {o_lon}) -> Destination: ({d_lat}, {d_lon})")

        for m in modes:
            res = get_rescue_route(o_lat, o_lon, d_lat, d_lon, mode=m)
            all_demo_results.append({
                "scenario": sc_name,
                "mode": m,
                "response": res
            })

            sel = res["selected_route"]
            csv_rows.append({
                "scenario": sc_name,
                "mode": m,
                "selected_route_id": sel["route_id"],
                "distance_km": sel["distance_km"],
                "duration_minutes": sel["duration_minutes"],
                "route_risk_score": sel["route_risk_score"],
                "risk_level": res["route_risk_level"],
                "route_mode_score": sel["route_mode_score"],
                "explanation": res["explanation"]
            })

            print(f"  Mode [{m:8s}]: Selected Route = {sel['route_id']}, Distance = {sel['distance_km']} km, Duration = {sel['duration_minutes']} min, Risk Score = {sel['route_risk_score']} ({res['route_risk_level']})")

        print("")

    # Export JSON
    json_path = OUTPUT_DIR / "route_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_demo_results, f, indent=2)

    # Export CSV
    df_routes = pd.DataFrame(csv_rows)
    csv_path = OUTPUT_DIR / "route_results.csv"
    df_routes.to_csv(csv_path, index=False)

    print("Demo Execution Completed Successfully!")
    print(f"Saved JSON: {json_path}")
    print(f"Saved CSV:  {csv_path}")

    return all_demo_results


if __name__ == "__main__":
    run_route_risk_demo()
