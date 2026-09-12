"""
Unit Tests for RESQ-AI Grounded Emergency Action Plan Engine (Step 9).
"""

import unittest
from pathlib import Path
import yaml
import json

from action_plan.grounded_context import build_grounded_context, GroundedContext
from action_plan.action_plan_contract import ActionPlanContract
from action_plan.prompt_builder import SYSTEM_PROMPT, build_llm_prompt
from action_plan.llm_client import generate_llm_action_plan, generate_deterministic_fallback_plan
from action_plan.validation import validate_action_plan
from action_plan.action_plan_engine import generate_action_plan
from action_plan.run_action_plan_demo import run_action_plan_demo

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "action_plan.yaml"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "action_plans"


class TestActionPlanEngine(unittest.TestCase):

    def test_context_construction(self):
        """Test grounded context builder retrieves verified data for valid district."""
        ctx = build_grounded_context("PURI")
        self.assertIsInstance(ctx, GroundedContext)
        self.assertEqual(ctx.district, "PURI")
        self.assertTrue(0.0 <= ctx.risk_score <= 100.0)
        self.assertTrue(0.0 <= ctx.priority_score <= 100.0)

    def test_missing_field_handling(self):
        """Test that missing route info is represented explicitly as NOT_AVAILABLE."""
        ctx = build_grounded_context("PURI")
        ctx_dict = ctx.to_dict()
        self.assertEqual(ctx_dict["route_info"], "NOT_AVAILABLE")

    def test_contract_validation_valid(self):
        """Test valid ActionPlanContract instantiation."""
        plan = ActionPlanContract(
            district="PURI",
            observation_date="2026-09-11",
            risk={"score": 45.0, "level": "MODERATE"},
            priority={"score": 55.0, "level": "P2"},
            situation_summary="Moderate risk scenario.",
            key_evidence=["Rainfall: 15.0 mm"],
            recommended_actions=["Monitor weather"],
            route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": "Default route"},
            monitoring_actions=["Track IMD data"],
            limitations=["Decision-support only"]
        )
        self.assertEqual(plan.district, "PURI")
        self.assertEqual(plan.risk["score"], 45.0)

    def test_invalid_risk_score(self):
        """Test out of bounds risk score rejection."""
        with self.assertRaises(ValueError):
            ActionPlanContract(
                district="PURI",
                observation_date="2026-09-11",
                risk={"score": 150.0, "level": "MODERATE"},
                priority={"score": 55.0, "level": "P2"},
                situation_summary="Invalid risk score",
                key_evidence=[],
                recommended_actions=[],
                route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": ""},
                monitoring_actions=[],
                limitations=[]
            )

    def test_invalid_priority_score(self):
        """Test out of bounds priority score rejection."""
        with self.assertRaises(ValueError):
            ActionPlanContract(
                district="PURI",
                observation_date="2026-09-11",
                risk={"score": 45.0, "level": "MODERATE"},
                priority={"score": -10.0, "level": "P2"},
                situation_summary="Invalid priority score",
                key_evidence=[],
                recommended_actions=[],
                route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": ""},
                monitoring_actions=[],
                limitations=[]
            )

    def test_invalid_risk_level(self):
        """Test invalid risk level string rejection."""
        with self.assertRaises(ValueError):
            ActionPlanContract(
                district="PURI",
                observation_date="2026-09-11",
                risk={"score": 45.0, "level": "INVALID_RISK_LEVEL"},
                priority={"score": 55.0, "level": "P2"},
                situation_summary="Invalid risk level",
                key_evidence=[],
                recommended_actions=[],
                route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": ""},
                monitoring_actions=[],
                limitations=[]
            )

    def test_invalid_priority_level(self):
        """Test invalid priority level string rejection."""
        with self.assertRaises(ValueError):
            ActionPlanContract(
                district="PURI",
                observation_date="2026-09-11",
                risk={"score": 45.0, "level": "MODERATE"},
                priority={"score": 55.0, "level": "P99"},
                situation_summary="Invalid priority level",
                key_evidence=[],
                recommended_actions=[],
                route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": ""},
                monitoring_actions=[],
                limitations=[]
            )

    def test_invalid_route_mode(self):
        """Test invalid route mode string rejection."""
        with self.assertRaises(ValueError):
            ActionPlanContract(
                district="PURI",
                observation_date="2026-09-11",
                risk={"score": 45.0, "level": "MODERATE"},
                priority={"score": 55.0, "level": "P2"},
                situation_summary="Invalid route mode",
                key_evidence=[],
                recommended_actions=[],
                route_recommendation={"mode": "SUPER_FAST", "risk_score": 40.0, "explanation": ""},
                monitoring_actions=[],
                limitations=[]
            )

    def test_prompt_grounding_rules(self):
        """Test prompt builder contains strict zero-hallucination instruction rules."""
        ctx = build_grounded_context("PURI")
        prompt_str = build_llm_prompt(ctx)
        self.assertIn("STRICT GROUNDING & SUMMARIZATION RULES", SYSTEM_PROMPT)
        self.assertIn("Do NOT invent facts", SYSTEM_PROMPT)
        self.assertIn(ctx.district, prompt_str)

    def test_deterministic_fallback(self):
        """Test deterministic fallback action plan generator."""
        ctx = build_grounded_context("ALIPURDUAR")
        plan = generate_deterministic_fallback_plan(ctx)
        self.assertTrue(plan.is_fallback)
        self.assertEqual(plan.district, "ALIPURDUAR")
        self.assertIn("P1", plan.priority["level"])
        self.assertGreater(len(plan.recommended_actions), 0)

    def test_llm_unavailable_handling(self):
        """Test graceful fallback behavior when API key is unconfigured."""
        ctx = build_grounded_context("DARJEELING")
        plan = generate_llm_action_plan(ctx)
        self.assertIsInstance(plan, ActionPlanContract)
        self.assertTrue(plan.is_fallback)  # Uses fallback seamlessly without API key

    def test_unsupported_claim_detection(self):
        """Test guardrail detects forbidden absolute claim keywords."""
        ctx = build_grounded_context("PURI")
        plan_bad = ActionPlanContract(
            district="PURI",
            observation_date=ctx.observation_date,
            risk={"score": ctx.risk_score, "level": ctx.risk_level},
            priority={"score": ctx.priority_score, "level": ctx.priority_level},
            situation_summary="This area will flood and is guaranteed to be affected.",
            key_evidence=[],
            recommended_actions=[],
            route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": ""},
            monitoring_actions=[],
            limitations=[]
        )
        is_valid, errors = validate_action_plan(plan_bad, ctx)
        self.assertFalse(is_valid)
        self.assertTrue(any("forbidden keyword" in e for e in errors))

    def test_numerical_grounding(self):
        """Test numerical grounding validation rejects altered risk/priority scores."""
        ctx = build_grounded_context("PURI")
        plan_altered = ActionPlanContract(
            district="PURI",
            observation_date=ctx.observation_date,
            risk={"score": ctx.risk_score + 15.0, "level": ctx.risk_level},  # Altered score
            priority={"score": ctx.priority_score, "level": ctx.priority_level},
            situation_summary="Altered score plan.",
            key_evidence=[],
            recommended_actions=[],
            route_recommendation={"mode": "BALANCED", "risk_score": 40.0, "explanation": ""},
            monitoring_actions=[],
            limitations=[]
        )
        is_valid, errors = validate_action_plan(plan_altered, ctx)
        self.assertFalse(is_valid)
        self.assertTrue(any("score mismatch" in e for e in errors))

    def test_deterministic_output(self):
        """Test generate_action_plan produces consistent structured payloads."""
        res1 = generate_action_plan("KASARGOD", observation_date="2026-09-11")
        res2 = generate_action_plan("KASARGOD", observation_date="2026-09-11")
        self.assertEqual(res1["district"], res2["district"])
        self.assertEqual(res1["risk"]["score"], res2["risk"]["score"])
        self.assertEqual(res1["priority"]["score"], res2["priority"]["score"])

    def test_batch_output_generation(self):
        """Test batch demo script creates required JSON and CSV output files."""
        results = run_action_plan_demo(top_n=5)
        self.assertEqual(len(results), 5)
        self.assertTrue((OUTPUT_DIR / "action_plans.json").exists())
        self.assertTrue((OUTPUT_DIR / "action_plans.csv").exists())


if __name__ == "__main__":
    unittest.main()
