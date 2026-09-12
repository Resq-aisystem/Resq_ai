# RESQ-AI Architecture & Module Responsibilities

## 1. System Overview

**RESQ-AI** is a production-oriented Disaster Early Warning & Rescue Intelligence Platform designed to ingest multi-source environmental, meteorological, hydrological, and historical disaster data to produce explainable flood risk predictions, emergency prioritization scores, route-risk intelligence, and actionable emergency response plans.

The system is structured as a decoupled, modular pipeline where data processing, feature engineering, model training, explainability, priority scoring, route risk analysis, and inference are kept isolated.

---

## 2. End-to-End AI/ML Pipeline

```
RAW DATA
   ↓
DATA INSPECTION
   ↓
DATA VALIDATION
   ↓
DATA CLEANING
   ↓
DATASET-SPECIFIC FEATURES
   ↓
MASTER FEATURE DATASET
   ↓
TARGET / LABEL DEFINITION
   ↓
TRAIN / VALIDATION / TEST SPLIT
   ↓
BASELINE MODEL
   ↓
MODEL EVALUATION
   ↓
MODEL IMPROVEMENT
   ↓
EXPLAINABILITY
   ↓
MODEL ARTIFACT
   ↓
INFERENCE
   ↓
RISK SCORE (0-100 & LOW/MODERATE/HIGH/CRITICAL)
   ↓
VULNERABILITY / EXPOSURE
   ↓
EMERGENCY PRIORITY
   ↓
ROUTE RISK
   ↓
EMERGENCY ACTION PLAN
```

---

## 3. Directory & Module Responsibilities

### `data/`
- **`raw/`**: Holds original data files. **IMMUTABLE** (Never modified, overwritten, or cleaned in place). Subdirectories: `imd/`, `gfsm/`, `camels_ind/`, `ifi/`, `gdis/`.
- **`interim/`**: Holds intermediate datasets during transformation.
- **`processed/`**: Standardized and validated datasets ready for feature extraction.

### `preprocessing/`
- Holds dataset-specific logic for inspection, validation, and cleaning.
- Submodules for each dataset: `imd/`, `gfsm/`, `camels_ind/`, `ifi/`, `gdis/`.
- **Rule**: Data cleaning and handling of missing values must occur strictly here without data fabrication.

### `features/`
- Transforms clean data into domain-specific features:
  - `rainfall/`: Weather and precipitation indices.
  - `susceptibility/`: Terrain & land flood susceptibility features.
  - `hydrology/`: Catchment attributes, soil moisture, and runoff metrics.
  - `flood_history/`: Past flood severity and frequency metrics.
  - `disaster_history/`: Geocoded historical disaster event features.
  - `master/`: Combines features into unified feature matrices.

### `datasets/`
- **`master/`**: Stores finalized, versioned feature datasets for model training and evaluation.

### `models/`
- **`flood_risk/`**: Core machine learning models predicting flood risk scores (0–100) and risk categories.
- **`susceptibility/`**: Models predicting land flood susceptibility.
- **`artifacts/`**: Serialized model binaries (`.pkl`, `.onnx`, etc.) registered for production deployment.

### `training/`
- **`scripts/`**: Orchestration scripts for model training, baseline execution, and hyperparameter tuning.
- **`configs/`**: Declarative configuration files (YAML/JSON) for model parameters and pipeline settings.
- **`experiments/`**: Log outputs, run tracking metadata, and performance history.

### `evaluation/`
- **`metrics/`**: Evaluation logic (RMSE, MAE, Precision, Recall, ROC-AUC, F1).
- **`reports/`**: Generated performance summary reports across train/val/test splits.
- **`plots/`**: Diagnostic visualizations (ROC curves, Confusion Matrices, Residual Plots).

### `explainability/`
- **`feature_importance/`**: Global feature importance extraction.
- **`shap/`**: SHAP value generation for local instance-level explainability.
- Provides human-readable justifications for predicted risk levels.

### `inference/`
- **`schemas/`**: Pydantic/dataclass data contracts defining input payloads and output responses.
- **`preprocessing/`**: Real-time feature preprocessing for live inference payloads.
- **`prediction/`**: Unified prediction interface for external consumption by backend/frontend APIs.

### `priority/`
- **`exposure/`**: Evaluates vulnerable population, infrastructure, and asset exposure.
- **`emergency_priority/`**: Combines flood risk scores and exposure to produce emergency response priority scores.
- **Separation**: Kept separate from core ML prediction models.

### `route_risk/`
- **`road_risk/`**: Assesses flood hazard and safety risk across road network segments.
- **`route_scoring/`**: Computes safety scores for routes.
- **`route_modes/`**: Evaluates routes under 3 distinct modes:
  1. `FASTEST`: Travel time minimization.
  2. `SAFEST`: Hazard risk minimization.
  3. `BALANCED`: Multi-objective score balancing speed and safety.
- **Separation**: Does not implement graph/routing engines; provides risk intelligence vectors to downstream routing components.

### `action_plan/`
- Generates structured, emergency action plans detailing response guidelines based on risk level, priority score, and top contributing factors.

### `notebooks/`
- Dedicated for exploratory data analysis (EDA) and visualization experiments.

### `config/`
- Global environment parameters, path definitions, logging configurations, and threshold settings.

### `tests/`
- Unit and integration test suite ensuring structural integrity, import validity, and schema contract adherence.

---

## 4. Planned Dataset Roles (For Future Integration)

| Dataset | Provider | Target Role in Pipeline |
| :--- | :--- | :--- |
| **IMD District-wise Daily Rainfall** | IMD | Daily & cumulative rainfall features, precipitation anomaly metrics |
| **GFSM** | Global Flood Susceptibility Map | Static land susceptibility features, terrain slope/elevation indices |
| **CAMELS-IND** | Catchment Attributes & Meteorology | Catchment hydro-meteorology, soil moisture, runoff attributes |
| **India Flood Inventory (IFI)** | IFI (DFSI, District Flooded Area/Impact) | Ground-truth historical flood events, inundated area, damage impacts |
| **NASA GDIS** | NASA | Geocoded historical disaster events & global severity context |

---

## 5. Risk Output Contract Interface

Backend and frontend applications will interact with RESQ-AI via the following standardized response schema:

```json
{
  "risk_score": 75.5,
  "risk_level": "HIGH",
  "confidence": 0.92,
  "top_factors": [
    {
      "factor_name": "Extreme 24h Rainfall",
      "impact_weight": 0.65,
      "description": "High intensity rainfall recorded in IMD district dataset"
    }
  ],
  "priority_score": 85.0
}
```
