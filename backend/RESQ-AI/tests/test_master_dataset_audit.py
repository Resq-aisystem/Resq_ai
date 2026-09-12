"""
Automated Feasibility & Audit Tests for Master Dataset Integration in RESQ-AI.

Verifies dataset discoverability, geographic key matching across all 5 datasets,
target leakage classification integrity, and audit report generation.
"""

import json
import os
from pathlib import Path
import unittest
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
IMD_PATH = BASE_DIR / "features" / "rainfall" / "imd_rainfall_features.csv"
GFSM_PATH = BASE_DIR / "features" / "susceptibility" / "gfsm_susceptibility_features.csv"
CAMELS_PATH = BASE_DIR / "features" / "hydrology" / "camels_ind_hydrology_features.csv"
IFI_FEAT_PATH = BASE_DIR / "features" / "flood_history" / "ifi_flood_history_features.csv"
IFI_TGT_PATH = BASE_DIR / "data" / "processed" / "ifi" / "ifi_flood_targets.csv"
GDIS_PATH = BASE_DIR / "features" / "disaster_history" / "gdis_disaster_history_features.csv"

AUDIT_JSON_PATH = BASE_DIR / "data" / "interim" / "master_dataset_audit.json"
AUDIT_MD_PATH = BASE_DIR / "reports" / "master_dataset_audit.md"


class TestMasterDatasetAudit(unittest.TestCase):

    def test_all_five_datasets_discoverable(self):
        """Verify that all 5 feature/target datasets exist and load cleanly."""
        self.assertTrue(IMD_PATH.exists(), f"Missing IMD feature file at {IMD_PATH}")
        self.assertTrue(GFSM_PATH.exists(), f"Missing GFSM feature file at {GFSM_PATH}")
        self.assertTrue(CAMELS_PATH.exists(), f"Missing CAMELS feature file at {CAMELS_PATH}")
        self.assertTrue(IFI_FEAT_PATH.exists(), f"Missing IFI feature file at {IFI_FEAT_PATH}")
        self.assertTrue(IFI_TGT_PATH.exists(), f"Missing IFI target file at {IFI_TGT_PATH}")
        self.assertTrue(GDIS_PATH.exists(), f"Missing GDIS feature file at {GDIS_PATH}")

    def test_geographic_key_overlap(self):
        """Verify 100% district key matching (728 districts) across static feature sets."""
        df_imd = pd.read_csv(IMD_PATH)
        df_gfsm = pd.read_csv(GFSM_PATH)
        df_camels = pd.read_csv(CAMELS_PATH)
        df_ifi_feat = pd.read_csv(IFI_FEAT_PATH)
        df_ifi_tgt = pd.read_csv(IFI_TGT_PATH)
        df_gdis = pd.read_csv(GDIS_PATH)

        imd_keys = set(zip(df_imd['state'], df_imd['district']))
        self.assertEqual(len(imd_keys), 728)

        gfsm_keys = set(zip(df_gfsm['state'], df_gfsm['district']))
        camels_keys = set(zip(df_camels['state'], df_camels['district']))
        ifi_feat_keys = set(zip(df_ifi_feat['state'], df_ifi_feat['district']))
        ifi_tgt_keys = set(zip(df_ifi_tgt['state'], df_ifi_tgt['district']))
        gdis_keys = set(zip(df_gdis['state'], df_gdis['district']))

        self.assertEqual(len(imd_keys & gfsm_keys), 728)
        self.assertEqual(len(imd_keys & camels_keys), 728)
        self.assertEqual(len(imd_keys & ifi_feat_keys), 728)
        self.assertEqual(len(imd_keys & ifi_tgt_keys), 728)
        self.assertEqual(len(imd_keys & gdis_keys), 728)

    def test_audit_outputs_exist(self):
        """Verify master dataset audit JSON and Markdown reports exist."""
        self.assertTrue(AUDIT_JSON_PATH.exists(), f"Missing audit JSON at {AUDIT_JSON_PATH}")
        self.assertTrue(AUDIT_MD_PATH.exists(), f"Missing audit report at {AUDIT_MD_PATH}")

        with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
            audit = json.load(f)

        self.assertFalse(audit["fabricated_data_created"])
        self.assertEqual(audit["geographic_join_audit"]["resq_ai_target_districts"], 728)
        self.assertIn("target_leakage_classification", audit)

    def test_target_leakage_classification(self):
        """Verify target leakage checks classify direct leakage features correctly."""
        with open(AUDIT_JSON_PATH, "r", encoding="utf-8") as f:
            audit = json.load(f)

        leak = audit["target_leakage_classification"]
        self.assertIn("DIRECT LEAKAGE", leak["ifi_dfsi_score"]["classification"])
        self.assertIn("DIRECT LEAKAGE", leak["ifi_flooded_area_pct"]["classification"])
        self.assertIn("SAFE", leak["ifi_permanent_water_pct"]["classification"])


if __name__ == "__main__":
    unittest.main()
