"""
PRD-Aligned Target Architecture Integration Test Suite for RESQ-AI (Step 11).
"""

import unittest
from pathlib import Path
import yaml
import json

from forecast.forecast_client import fetch_6hour_forecast, get_mock_6hour_forecast
from flood_prediction.predictor import predict_6hour_flood_risk
from flood_depth.depth_engine import estimate_flood_depth
from flood_zones.spatial_intersection import generate_city_flood_zones, calculate_route_flood_exposure
from facility.impact_engine import evaluate_facility_impacts
from priority.emergency_priority.facility_priority import get_facility_evacuation_priorities
from update.scheduler import get_current_update_status, trigger_pipeline_update
from scenario.scenario_engine import run_scenario_analysis, ScenarioConfig
from provenance.provenance_schema import create_provenance_record
from inference.decision_contract import get_city_decision_intelligence

BASE_DIR = Path(__file__).resolve().parent.parent
CITY_CONFIG_PATH = BASE_DIR / "config" / "city_config.yaml"


class TestPRDPipeline(unittest.TestCase):

    def test_city_config_loading(self):
        """Test Single-City MVP configuration loading."""
        self.assertTrue(CITY_CONFIG_PATH.exists())
        with open(CITY_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.assertIn("city_mvp", cfg)
        self.assertEqual(cfg["city_mvp"]["city_name"], "Puri")

    def test_6hour_forecast_client(self):
        """Test 6-hour forecast client and mock fallback."""
        forecast = fetch_6hour_forecast(city_name="Puri", district_name="PURI")
        self.assertEqual(len(forecast.hourly_points), 6)
        self.assertGreaterEqual(forecast.total_6h_rainfall_mm(), 0.0)

    def test_6hour_flood_prediction(self):
        """Test 6-hour predictive flood risk pipeline."""
        pred = predict_6hour_flood_risk(city_name="Puri", district_name="PURI")
        self.assertEqual(pred.forecast_horizon_hours, 6)
        self.assertTrue(0.0 <= pred.predicted_risk_score <= 100.0)
        self.assertEqual(pred.confidence_level, "UNCALIBRATED")

    def test_flood_depth_insufficient_data_status(self):
        """Test that unconfigured DEM returns INSUFFICIENT_DATA status without depth fabrication."""
        depth = estimate_flood_depth(city_name="Puri", district_name="PURI")
        self.assertEqual(depth.data_status, "INSUFFICIENT_DATA")
        self.assertIsNone(depth.predicted_depth_meters)

    def test_flood_zone_spatial_exposure(self):
        """Test spatial flood zone generation and route exposure calculation."""
        fz = generate_city_flood_zones("Puri", "PURI")
        self.assertEqual(fz.target_resolution_m, 100)
        self.assertGreater(len(fz.zones), 0)

        waypoints = [[85.8312, 19.8135], [85.8350, 19.8150]]
        exp_dist, exp_pct = calculate_route_flood_exposure(waypoints, fz)
        self.assertGreaterEqual(exp_dist, 0.0)

    def test_facility_impact_assessment(self):
        """Test facility impact and vulnerability assessment."""
        impacts = evaluate_facility_impacts("Puri", "PURI")
        self.assertGreater(len(impacts), 0)
        for imp in impacts:
            self.assertTrue(0.0 <= imp.priority_score <= 100.0)
            self.assertIn(imp.priority_level, ["P1", "P2", "P3", "P4"])

    def test_facility_priority_ranking(self):
        """Test facility evacuation priority ranking."""
        prio_list = get_facility_evacuation_priorities("Puri", "PURI")
        self.assertGreater(len(prio_list), 0)
        scores = [p["priority_score"] for p in prio_list]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_update_scheduler_status(self):
        """Test 30-minute real-time update scheduler status."""
        status = get_current_update_status("Puri")
        self.assertEqual(status.update_interval_minutes, 30)
        self.assertEqual(status.status, "COMPLETED")

    def test_scenario_analysis(self):
        """Test what-if scenario planning and risk delta calculation."""
        sc = ScenarioConfig(scenario_id="sc_surge", scenario_name="Surge Test", rainfall_multiplier=1.8)
        res = run_scenario_analysis("Puri", "PURI", scenario=sc)
        self.assertEqual(res.output_type, "WHAT_IF_SCENARIO")
        self.assertGreater(res.scenario_risk_score, res.baseline_risk_score)
        self.assertAlmostEqual(res.risk_delta, res.scenario_risk_score - res.baseline_risk_score, places=2)

    def test_provenance_tracking(self):
        """Test provenance record creation."""
        prov = create_provenance_record()
        self.assertIsNotNone(prov.calculation_timestamp)
        self.assertEqual(prov.dataset_version, "2026.09.11")

    def test_master_city_decision_intelligence(self):
        """Test top-level master decision contract payload generation."""
        master = get_city_decision_intelligence(city_name="Puri", district_name="PURI")
        self.assertIn("forecast", master)
        self.assertIn("flood_prediction", master)
        self.assertIn("flood_depth", master)
        self.assertIn("facilities", master)
        self.assertIn("evacuation_priorities", master)
        self.assertIn("routes", master)
        self.assertIn("scenarios", master)
        self.assertIn("action_plan", master)
        self.assertIn("provenance", master)


if __name__ == "__main__":
    unittest.main()
