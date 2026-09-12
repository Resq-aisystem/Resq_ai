"""
Automated Model Validation Tests for IMD Baseline Model in RESQ-AI.

Verifies model binary loading, prediction execution, output class validity,
and reproducibility of accuracy metrics on held-out test data.
"""

from pathlib import Path
import pickle
import unittest
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "flood_risk" / "imd_baseline_model.pkl"
FEATURE_PATH = BASE_DIR / "features" / "rainfall" / "imd_rainfall_features.csv"


def get_severity(mm):
    if mm < 2.5:
        return 'LIGHT'
    elif mm < 64.5:
        return 'MODERATE'
    elif mm < 115.6:
        return 'HEAVY'
    else:
        return 'EXTREME'


class TestIMDBaselineModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load model binary and feature test set."""
        cls.assertTrue(cls, MODEL_PATH.exists(), f"Model binary missing at {MODEL_PATH}")
        with open(MODEL_PATH, 'rb') as f:
            cls.model = pickle.load(f)

        df = pd.read_csv(FEATURE_PATH)
        df['rainfall_severity'] = df['daily_actual_mm'].apply(get_severity)
        df = df.sort_values(by=['state', 'district', 'date']).reset_index(drop=True)

        feature_cols = [
            'daily_normal_mm',
            'cumulative_normal_mm',
            'monthly_normal_mm',
            'rolling_3d_rainfall_mm_lag1',
            'rolling_7d_rainfall_mm_lag1',
            'rolling_14d_rainfall_mm_lag1',
            'rolling_30d_rainfall_mm_lag1',
            'rolling_3d_max_mm_lag1',
            'rolling_7d_max_mm_lag1',
            'rolling_14d_max_mm_lag1',
            'consecutive_rainy_days_lag1',
            'rolling_7d_rainy_days_count_lag1',
            'cumulative_actual_mm_lag1',
            'monthly_actual_mm_lag1'
        ]

        grouped = df.groupby(['state', 'district'])
        df_lagged = df.copy()
        lag_sources = [
            'rolling_3d_rainfall_mm', 'rolling_7d_rainfall_mm', 'rolling_14d_rainfall_mm', 'rolling_30d_rainfall_mm',
            'rolling_3d_max_mm', 'rolling_7d_max_mm', 'rolling_14d_max_mm',
            'consecutive_rainy_days', 'rolling_7d_rainy_days_count',
            'cumulative_actual_mm', 'monthly_actual_mm'
        ]
        for col in lag_sources:
            df_lagged[f'{col}_lag1'] = grouped[col].shift(1)

        df_lagged = df_lagged.fillna(0)

        test_df = df_lagged[df_lagged['date'] >= '2026-09-05']
        cls.X_test = test_df[feature_cols]
        cls.y_test = test_df['rainfall_severity']

    def test_model_loaded_and_predicts(self):
        """Verify model binary predicts on sample test data."""
        sample_x = self.X_test.iloc[:10]
        preds = self.model.predict(sample_x)
        self.assertEqual(len(preds), 10)
        valid_classes = {'LIGHT', 'MODERATE', 'HEAVY', 'EXTREME'}
        for p in preds:
            self.assertIn(p, valid_classes)

    def test_reproducible_accuracy(self):
        """Verify accuracy metric matches expected baseline accuracy on test set."""
        preds = self.model.predict(self.X_test)
        acc = accuracy_score(self.y_test, preds)
        self.assertAlmostEqual(acc, 0.680541920282741, places=2)


if __name__ == "__main__":
    unittest.main()
