"""
RESQ-AI Batch Emergency Priority Ranking Script.

Processes all available districts for the latest observation date,
calculates priority scores, ranks districts descending by priority_score, and exports:
- data/processed/priority/emergency_priority_results.csv
- data/processed/priority/emergency_priority_results.json
- data/processed/priority/emergency_priority_ranking.csv
"""

import argparse
from pathlib import Path
import json
import pandas as pd

from priority.emergency_priority.engine import get_emergency_priority
from inference.risk_engine import _load_datasets

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "priority"


def run_batch_priority_scoring(observation_date=None):
    """
    Run emergency priority scoring across all districts and generate ranked outputs.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    datasets = _load_datasets()
    df_imd = datasets['imd']
    all_districts = df_imd['district'].dropna().unique().tolist()

    print(f"Starting emergency priority scoring for {len(all_districts)} district(s)...")

    raw_results = []
    for idx, d_name in enumerate(all_districts):
        try:
            res_dict = get_emergency_priority(district_name=d_name, observation_date=observation_date)
            raw_results.append(res_dict)
        except Exception as e:
            print(f"Warning: Failed priority scoring for district '{d_name}': {e}")

    if not raw_results:
        print("No priority results generated.")
        return []

    # Sort results descending by priority_score
    sorted_results = sorted(raw_results, key=lambda x: x['priority_score'], reverse=True)

    # Assign ranks
    for rank_idx, item in enumerate(sorted_results, 1):
        item['rank'] = rank_idx

    # Export full JSON
    json_path = OUTPUT_DIR / "emergency_priority_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, indent=2)

    # Export Full Results CSV
    csv_rows = []
    for r in sorted_results:
        factors_summary = "; ".join([f"{f['factor']}: {f['evidence']}" for f in r['priority_factors']])
        flags_summary = "|".join(r['vulnerability_flags'])
        csv_rows.append({
            "rank": r['rank'],
            "district": r['district'],
            "state": r['state'],
            "observation_date": r['observation_date'],
            "risk_score": r['risk_score'],
            "risk_level": r['risk_level'],
            "priority_score": r['priority_score'],
            "priority_level": r['priority_level'],
            "evidence_quality": r['evidence_quality'],
            "vulnerability_flags": flags_summary,
            "priority_factors_summary": factors_summary,
            "recommended_attention_reason": r['recommended_attention_reason']
        })

    df_full = pd.DataFrame(csv_rows)
    csv_path = OUTPUT_DIR / "emergency_priority_results.csv"
    df_full.to_csv(csv_path, index=False)

    # Export Clean Ranking CSV
    ranking_cols = [
        "rank", "district", "state", "observation_date", "risk_score",
        "risk_level", "priority_score", "priority_level", "evidence_quality",
        "vulnerability_flags", "recommended_attention_reason"
    ]
    df_ranking = df_full[ranking_cols]
    ranking_path = OUTPUT_DIR / "emergency_priority_ranking.csv"
    df_ranking.to_csv(ranking_path, index=False)

    print(f"\nPriority Scoring Completed Successfully!")
    print(f"Total districts processed: {len(df_ranking)}")
    print(f"Saved JSON:     {json_path}")
    print(f"Saved CSV:      {csv_path}")
    print(f"Saved Ranking:  {ranking_path}")

    # Display Priority Level Distribution
    print("\nPriority Level Distribution:")
    print(df_full['priority_level'].value_counts().to_string())

    print(f"\nPriority Score Range: Min = {df_full['priority_score'].min():.2f}, Max = {df_full['priority_score'].max():.2f}, Mean = {df_full['priority_score'].mean():.2f}")

    print("\nTop 10 Priority Districts:")
    print(df_ranking[['rank', 'district', 'state', 'risk_score', 'priority_score', 'priority_level']].head(10).to_string(index=False))

    return sorted_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RESQ-AI Emergency Priority Scoring Engine Batch Execution")
    parser.add_argument("--date", type=str, default=None, help="Observation date (YYYY-MM-DD)")

    args = parser.parse_args()
    run_batch_priority_scoring(observation_date=args.date)
