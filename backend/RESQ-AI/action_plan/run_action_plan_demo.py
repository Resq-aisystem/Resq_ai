"""
RESQ-AI Batch Emergency Action Plan Generation Demo Script.

Generates grounded Emergency Action Plans for top high-priority districts
and exports results to:
- data/processed/action_plans/action_plans.json
- data/processed/action_plans/action_plans.csv
"""

import argparse
from pathlib import Path
import json
import pandas as pd

from action_plan.action_plan_engine import generate_action_plan

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "action_plans"
PRIORITY_RANKING_PATH = BASE_DIR / "data" / "processed" / "priority" / "emergency_priority_ranking.csv"


def run_action_plan_demo(top_n: int = 10):
    """
    Generate demonstration Emergency Action Plans for top priority districts.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not PRIORITY_RANKING_PATH.exists():
        print(f"Error: Priority ranking file not found at {PRIORITY_RANKING_PATH}")
        return []

    df_priority = pd.read_csv(PRIORITY_RANKING_PATH)
    top_districts = df_priority.head(top_n)['district'].tolist()
    latest_date = str(df_priority.iloc[0]['observation_date'])

    print(f"Generating Grounded Action Plans for top {len(top_districts)} priority districts on date {latest_date}...\n")

    action_plans = []
    csv_rows = []

    for d in top_districts:
        plan = generate_action_plan(district_name=d, observation_date=latest_date, route_mode="BALANCED")
        action_plans.append(plan)

        rec_actions_str = "; ".join(plan["recommended_actions"])
        key_ev_str = "; ".join(plan["key_evidence"])

        csv_rows.append({
            "district": plan["district"],
            "observation_date": plan["observation_date"],
            "risk_score": plan["risk"]["score"],
            "risk_level": plan["risk"]["level"],
            "priority_score": plan["priority"]["score"],
            "priority_level": plan["priority"]["level"],
            "situation_summary": plan["situation_summary"],
            "recommended_actions_summary": rec_actions_str,
            "key_evidence_summary": key_ev_str,
            "route_mode": plan["route_recommendation"]["mode"],
            "route_explanation": plan["route_recommendation"]["explanation"],
            "evidence_quality": plan["evidence_quality"],
            "is_fallback": plan["is_fallback"],
            "output_type": "DEMONSTRATION DECISION-SUPPORT OUTPUT"
        })

        print(f"District [{d:20s}]: Risk={plan['risk']['score']:.1f} ({plan['risk']['level']}), Priority={plan['priority']['score']:.1f} ({plan['priority']['level']}), Fallback Mode={plan['is_fallback']}")

    # Save JSON
    json_path = OUTPUT_DIR / "action_plans.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(action_plans, f, indent=2)

    # Save CSV
    df_plans = pd.DataFrame(csv_rows)
    csv_path = OUTPUT_DIR / "action_plans.csv"
    df_plans.to_csv(csv_path, index=False)

    print("\nBatch Action Plan Demo Generation Completed Successfully!")
    print(f"Saved JSON: {json_path}")
    print(f"Saved CSV:  {csv_path}")

    return action_plans


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RESQ-AI Emergency Action Plan Demo Generator")
    parser.add_argument("--top_n", type=int, default=10, help="Number of top priority districts to generate plans for")
    args = parser.parse_args()
    run_action_plan_demo(top_n=args.top_n)
