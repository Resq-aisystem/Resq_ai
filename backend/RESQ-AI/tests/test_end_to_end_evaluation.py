"""
End-to-End System Evaluation Test for RESQ-AI (Step 10).

Validates complete pipeline execution across:
Raw Input -> IMD Predictor -> Risk Engine -> Priority Engine -> Route Risk Engine -> Action Plan Generator
"""

import unittest
from pathlib import Path
import json

from inference.prediction.imd_baseline_predictor import predict_rainfall_severity
from inference.risk_engine import get_district_risk
from priority.emergency_priority.engine import get_emergency_priority
from route_risk.route_scoring.route_service import get_rescue_route
from action_plan.action_plan_engine import generate_action_plan

BASE_DIR = Path(__file__).resolve().parent.parent


class TestEndToEndEvaluation(unittest.TestCase):

    def test_full_end_to_end_pipeline_execution(self):
        """Test complete pipeline execution from raw features to final action plan."""
        district_name = "PURI"
        obs_date = "2026-09-11"

        # 1. IMD Baseline Predictor
        sample_input = {
            'daily_normal_mm': 5.0,
            'cumulative_normal_mm': 120.0,
            'monthly_normal_mm': 150.0,
            'rolling_3d_rainfall_mm_lag1': 10.0,
            'rolling_7d_rainfall_mm_lag1': 25.0,
            'rolling_14d_rainfall_mm_lag1': 50.0,
            'rolling_30d_rainfall_mm_lag1': 100.0,
            'rolling_3d_max_mm_lag1': 5.0,
            'rolling_7d_max_mm_lag1': 10.0,
            'rolling_14d_max_mm_lag1': 15.0,
            'consecutive_rainy_days_lag1': 2,
            'rolling_7d_rainy_days_count_lag1': 3,
            'cumulative_actual_mm_lag1': 110.0,
            'monthly_actual_mm_lag1': 140.0
        }
        imd_pred = predict_rainfall_severity(sample_input)
        self.assertIn(imd_pred["predicted_severity"], ["LIGHT", "MODERATE", "HEAVY", "EXTREME"])

        # 2. Risk Engine
        risk_output = get_district_risk(district_name, obs_date)
        risk_dict = risk_output.to_dict()
        self.assertEqual(risk_dict["district"], "PURI")
        self.assertTrue(0.0 <= risk_dict["risk_score"] <= 100.0)
        self.assertIn(risk_dict["risk_level"], ["LOW", "MODERATE", "HIGH", "CRITICAL"])

        # 3. Emergency Priority Engine
        priority_dict = get_emergency_priority(district_name, obs_date)
        self.assertEqual(priority_dict["district"], "PURI")
        self.assertTrue(0.0 <= priority_dict["priority_score"] <= 100.0)
        self.assertIn(priority_dict["priority_level"], ["P1", "P2", "P3", "P4"])

        # 4. Route Risk Engine
        route_res = get_rescue_route(
            origin_lat=19.8135, origin_lon=85.8312,
            destination_lat=20.4625, destination_lon=85.8828,
            mode="BALANCED", observation_date=obs_date
        )
        self.assertIn(route_res["mode"], ["FASTEST", "SAFEST", "BALANCED"])
        self.assertTrue(0.0 <= route_res["selected_route"]["route_risk_score"] <= 100.0)

        # 5. Grounded Action Plan Generation Engine
        action_plan = generate_action_plan(
            district_name=district_name,
            observation_date=obs_date,
            route_mode="BALANCED",
            origin_coords=(19.8135, 85.8312),
            dest_coords=(20.4625, 85.8828)
        )
        self.assertEqual(action_plan["district"], "PURI")
        self.assertEqual(action_plan["observation_date"], obs_date)
        self.assertIn("situation_summary", action_plan)
        self.assertGreater(len(action_plan["recommended_actions"]), 0)

    def test_pipeline_numerical_consistency(self):
        """Test numerical score consistency across pipeline stages."""
        d_name = "ALIPURDUAR"
        obs_date = "2026-09-11"

        risk_out = get_district_risk(d_name, obs_date).to_dict()
        priority_out = get_emergency_priority(d_name, obs_date)
        plan_out = generate_action_plan(d_name, obs_date)

        # Risk score in Risk Engine must equal risk score in Priority Engine and Action Plan
        self.assertAlmostEqual(risk_out["risk_score"], priority_out["risk_score"], places=2)
        self.assertAlmostEqual(risk_out["risk_score"], plan_out["risk"]["score"], places=2)

        # Priority score in Priority Engine must equal priority score in Action Plan
        self.assertAlmostEqual(priority_out["priority_score"], plan_out["priority"]["score"], places=2)

    def test_pipeline_deterministic_repeatability(self):
        """Test that running the full pipeline twice with identical inputs yields identical outputs."""
        plan1 = generate_action_plan("DARJEELING", "2026-09-11")
        plan2 = generate_action_plan("DARJEELING", "2026-09-11")

        self.assertEqual(plan1["risk"]["score"], plan2["risk"]["score"])
        self.assertEqual(plan1["priority"]["score"], plan2["priority"]["score"])
        self.assertEqual(plan1["situation_summary"], plan2["situation_summary"])

    def test_zero_leakage_across_pipeline(self):
        """Verify that forbidden target variables are not present in any active feature key set."""
        forbidden_targets = {
            "target_flooded_area_pct",
            "target_risk_level",
            "target_flood_risk_binary",
            "ifi_dfsi_score"
        }
        # Check Risk Engine output breakdown
        risk_out = get_district_risk("PURI").to_dict()
        layer_keys = set(risk_out.get("layer_breakdown", {}).keys())
        self.assertTrue(forbidden_targets.isdisjoint(layer_keys))


if __name__ == "__main__":
    unittest.main()
