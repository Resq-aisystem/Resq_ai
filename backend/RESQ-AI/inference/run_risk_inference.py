"""
RESQ-AI Batch Risk Inference Script.

Runs the Production Risk Inference Engine across all available districts (or a specified district)
for a given observation date (or latest available date).

Outputs results to:
- data/processed/risk/risk_inference_results.csv
- data/processed/risk/risk_inference_results.json
"""

import argparse
from pathlib import Path
import json
import pandas as pd

from inference.risk_engine import get_district_risk, _load_datasets, norm_name

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "risk"


def run_batch_inference(district_filter=None, observation_date=None):
    """
    Run risk inference for all districts or a single district.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    datasets = _load_datasets()
    df_imd = datasets['imd']

    # Get distinct list of districts from IMD
    all_districts = df_imd['district'].dropna().unique().tolist()

    if district_filter:
        norm_filter = norm_name(district_filter)
        all_districts = [d for d in all_districts if norm_name(d) == norm_filter or norm_filter in norm_name(d)]
        if not all_districts:
            print(f"No districts matching filter '{district_filter}' found.")
            return []

    print(f"Starting risk inference for {len(all_districts)} district(s)...")

    results = []
    for idx, d_name in enumerate(all_districts):
        try:
            res_contract = get_district_risk(district_name=d_name, observation_date=observation_date)
            res_dict = res_contract.to_dict()
            results.append(res_dict)
        except Exception as e:
            print(f"Warning: Failed inference for district '{d_name}': {e}")

    if not results:
        print("No risk inference results generated.")
        return []

    # Export to JSON
    json_path = OUTPUT_DIR / "risk_inference_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Export to CSV (flatten top_factors and layer_breakdown for tubular format)
    csv_rows = []
    for r in results:
        top_factor_str = "; ".join([f"{tf['factor_name']}: {tf['description']}" for tf in r.get('top_factors', [])])
        l_break = r.get('layer_breakdown', {})
        csv_rows.append({
            "district": r['district'],
            "observation_date": r['observation_date'],
            "risk_score": r['risk_score'],
            "risk_level": r['risk_level'],
            "evidence_quality": r['evidence_quality'],
            "layer_1_rainfall_score": l_break.get('layer_1_rainfall_score'),
            "layer_2_susceptibility_score": l_break.get('layer_2_susceptibility_score'),
            "layer_3_historical_evidence_score": l_break.get('layer_3_historical_evidence_score'),
            "top_factors_summary": top_factor_str
        })

    df_results = pd.DataFrame(csv_rows)
    csv_path = OUTPUT_DIR / "risk_inference_results.csv"
    df_results.to_csv(csv_path, index=False)

    print(f"\nInference completed successfully!")
    print(f"Total districts processed: {len(df_results)}")
    print(f"Saved JSON: {json_path}")
    print(f"Saved CSV:  {csv_path}")

    # Summary statistics
    print("\nRisk Level Distribution:")
    print(df_results['risk_level'].value_counts().to_string())
    print("\nEvidence Quality Distribution:")
    print(df_results['evidence_quality'].value_counts().to_string())
    print(f"\nRisk Score Range: Min = {df_results['risk_score'].min():.2f}, Max = {df_results['risk_score'].max():.2f}, Mean = {df_results['risk_score'].mean():.2f}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RESQ-AI Production Risk Inference Engine Batch Execution")
    parser.add_argument("--district", type=str, default=None, help="Filter for a specific district")
    parser.add_argument("--date", type=str, default=None, help="Observation date (YYYY-MM-DD)")

    args = parser.parse_args()
    run_batch_inference(district_filter=args.district, observation_date=args.date)
