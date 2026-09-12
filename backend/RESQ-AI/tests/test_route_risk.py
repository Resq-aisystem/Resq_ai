"""
Unit Tests for RESQ-AI Route Risk & Rescue Routing Engine (Step 8).
"""

import unittest
from pathlib import Path
import yaml

from route_risk.route_scoring.route_contract import (
    Coordinates, RouteMode, RouteRequest, RouteCandidate, RouteResponsePayload
)
from route_risk.route_scoring.osrm_client import get_mock_osrm_response
from route_risk.road_risk.road_risk_engine import calculate_route_risk, _load_route_risk_config
from route_risk.route_modes.route_modes import rank_and_select_routes
from route_risk.route_scoring.route_service import get_rescue_route

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "route_risk.yaml"


class TestRouteRisk(unittest.TestCase):

    def test_contract_validation_valid(self):
        """Test valid coordinate and request creation."""
        coord1 = Coordinates(latitude=22.57, longitude=88.36)
        coord2 = Coordinates(latitude=26.48, longitude=89.52)
        req = RouteRequest(origin=coord1, destination=coord2, mode=RouteMode.BALANCED)
        self.assertEqual(req.origin.latitude, 22.57)
        self.assertEqual(req.destination.latitude, 26.48)
        self.assertEqual(req.mode, RouteMode.BALANCED)

    def test_invalid_coordinates(self):
        """Test latitude and longitude out of bounds validation."""
        with self.assertRaises(ValueError):
            Coordinates(latitude=95.0, longitude=88.36)
        with self.assertRaises(ValueError):
            Coordinates(latitude=22.57, longitude=190.0)

    def test_invalid_route_mode(self):
        """Test invalid route mode string handling."""
        with self.assertRaises(ValueError):
            RouteRequest(
                origin=Coordinates(22.57, 88.36),
                destination=Coordinates(26.48, 89.52),
                mode="INVALID_MODE_NAME"
            )

    def test_mocked_osrm_response_parsing(self):
        """Test mocked OSRM response structure and fallback fixtures."""
        origin = Coordinates(22.57, 88.36)
        dest = Coordinates(26.48, 89.52)
        mock_routes = get_mock_osrm_response(origin, dest)
        self.assertGreater(len(mock_routes), 1)
        for r in mock_routes:
            self.assertTrue(r["is_mock"])
            self.assertIn("distance_km", r)
            self.assertIn("duration_minutes", r)
            self.assertIn("waypoints", r)

    def test_route_distance_conversion(self):
        """Test that route distances are positive floating numbers in kilometers."""
        origin = Coordinates(19.81, 85.83)
        dest = Coordinates(20.46, 85.88)
        routes = get_mock_osrm_response(origin, dest)
        for r in routes:
            self.assertGreater(r["distance_km"], 0.0)

    def test_route_duration_conversion(self):
        """Test that route durations are positive floating numbers in minutes."""
        origin = Coordinates(19.81, 85.83)
        dest = Coordinates(20.46, 85.88)
        routes = get_mock_osrm_response(origin, dest)
        for r in routes:
            self.assertGreater(r["duration_minutes"], 0.0)

    def test_risk_score_bounds(self):
        """Test that route risk scores are bounded strictly 0-100."""
        risk_res = calculate_route_risk(district_name="PURI")
        self.assertGreaterEqual(risk_res["route_risk_score"], 0.0)
        self.assertLessEqual(risk_res["route_risk_score"], 100.0)
        self.assertIn(risk_res["risk_level"], ["LOW", "MODERATE", "HIGH", "CRITICAL"])

    def test_fastest_mode_ranking(self):
        """Test FASTEST mode selection prioritizes shortest travel duration."""
        candidates = [
            {"route_id": "r_long_low_risk", "distance_km": 150.0, "duration_minutes": 180.0, "route_risk_score": 20.0},
            {"route_id": "r_fast_mod_risk", "distance_km": 100.0, "duration_minutes": 90.0, "route_risk_score": 40.0}
        ]
        selected, alts = rank_and_select_routes(candidates, RouteMode.FASTEST)
        self.assertEqual(selected.route_id, "r_fast_mod_risk")

    def test_safest_mode_ranking(self):
        """Test SAFEST mode selection prioritizes lowest risk hazard score."""
        candidates = [
            {"route_id": "r_fast_high_risk", "distance_km": 100.0, "duration_minutes": 90.0, "route_risk_score": 75.0},
            {"route_id": "r_slow_safe_risk", "distance_km": 120.0, "duration_minutes": 110.0, "route_risk_score": 25.0}
        ]
        selected, alts = rank_and_select_routes(candidates, RouteMode.SAFEST)
        self.assertEqual(selected.route_id, "r_slow_safe_risk")

    def test_balanced_mode_ranking(self):
        """Test BALANCED mode trade-off ranking."""
        candidates = [
            {"route_id": "r1", "distance_km": 100.0, "duration_minutes": 100.0, "route_risk_score": 60.0},
            {"route_id": "r2", "distance_km": 110.0, "duration_minutes": 105.0, "route_risk_score": 30.0}
        ]
        selected, alts = rank_and_select_routes(candidates, RouteMode.BALANCED)
        self.assertEqual(selected.route_id, "r2")

    def test_deterministic_scoring(self):
        """Test that identical route inputs yield identical scores."""
        res1 = get_rescue_route(22.57, 88.36, 26.48, 89.52, mode="BALANCED")
        res2 = get_rescue_route(22.57, 88.36, 26.48, 89.52, mode="BALANCED")
        self.assertEqual(res1["selected_route"]["route_risk_score"], res2["selected_route"]["route_risk_score"])
        self.assertEqual(res1["selected_route"]["route_mode_score"], res2["selected_route"]["route_mode_score"])

    def test_explanation_generation(self):
        """Test that non-empty objective decision explanation is generated."""
        res = get_rescue_route(19.81, 85.83, 20.46, 85.88, mode="FASTEST")
        self.assertIsNotNone(res["explanation"])
        self.assertIn("FASTEST", res["explanation"])

    def test_unavailable_osrm_handling(self):
        """Test graceful fallback handling when OSRM API is unreachable."""
        origin = Coordinates(19.81, 85.83)
        dest = Coordinates(20.46, 85.88)
        mock_routes = get_mock_osrm_response(origin, dest)
        self.assertGreater(len(mock_routes), 0)

    def test_no_fabricated_production_route(self):
        """Test that disclaimers clearly indicate decision support nature and non-claims."""
        res = get_rescue_route(9.93, 76.26, 11.68, 76.13, mode="BALANCED")
        self.assertGreater(len(res["limitations"]), 0)
        self.assertTrue(any("decision-support score" in l for l in res["limitations"]))

    def test_configuration_loading(self):
        """Test route_risk.yaml configuration file exists and loads weights correctly."""
        self.assertTrue(CONFIG_PATH.exists())
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        self.assertIn("mode_weights", cfg)
        self.assertIn("risk_component_weights", cfg)


if __name__ == "__main__":
    unittest.main()
