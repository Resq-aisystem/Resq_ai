export interface AiForecast {
  city_name: string;
  district_name: string;
  timestamp: string;
  total_forecast_6h_mm: number;
  forecast_intensity_mm_per_hr: number;
  is_heavy_rain_predicted: boolean;
  model_version: string;
  confidence_status: string;
}

export interface ContributingFactor {
  factor: string;
  weight: number;
  evidence: string;
}

export interface AiFloodPrediction {
  city_name: string;
  district_name: string;
  observation_date?: string;
  risk_score?: number;
  predicted_risk_score?: number;
  risk_level?: string;
  predicted_risk_level?: string;
  evidence_quality: string;
  contributing_factors?: ContributingFactor[];
  top_contributing_factors?: any[];
  historical_recurrence?: string;
  terrain_vulnerability?: string;
  status?: string;
}

export interface AiEvacuationPriority {
  rank: number;
  facility_id: string;
  facility_name: string;
  priority_level: string;
  priority_score: number;
  justification: string;
  recommended_action: string;
}

export interface AiRouteDetail {
  mode: string;
  distance_km: number;
  estimated_duration_minutes: number;
  route_risk_score: number;
  flood_exposure_segment_count: number;
  geometry: [number, number][];
  explanation: string;
}

export interface AiScenarioResult {
  scenario_id: string;
  scenario_name: string;
  baseline_risk_score: number;
  simulated_risk_score: number;
  risk_delta: number;
  baseline_risk_level: string;
  simulated_risk_level: string;
  critical_zones_count: number;
  status: string;
}

export interface AiRouteRecommendation {
  mode: string;
  risk_score: number;
  explanation: string;
}

export interface AiActionPlan {
  district: string;
  observation_date?: string;
  risk: { score: number; level: string };
  priority: { score: number; level: string };
  situation_summary: string;
  key_evidence: string[];
  recommended_actions: string[];
  route_recommendation: AiRouteRecommendation;
  monitoring_actions: string[];
  limitations: string[];
  evidence_quality: string;
  is_fallback: boolean;
}

export interface AiDataset {
  name: string;
  source: string;
  resolution: string;
  temporal_coverage: string;
  description: string;
}

export interface AiProvenance {
  datasets: AiDataset[];
  pipeline_version: string;
  decision_contract_version: string;
  generated_at: string;
  execution_integrity: string;
}

export interface AiDecisionResponse {
  city_name: string;
  district_name: string;
  analysis_timestamp: string;
  mode_scope: string;
  forecast: AiForecast;
  flood_prediction: AiFloodPrediction;
  flood_depth: { city_name: string; status: string; message: string };
  flood_zones: { city_name: string; total_zones_evaluated: number; critical_zones_count: number; high_risk_zones_count: number; status: string };
  facilities: any[];
  evacuation_priorities: AiEvacuationPriority[];
  routes: {
    fastest?: AiRouteDetail;
    safest?: AiRouteDetail;
    balanced?: AiRouteDetail;
    [key: string]: AiRouteDetail | undefined;
  };
  scenarios: AiScenarioResult[];
  action_plan: AiActionPlan;
  update_status: { city_name: string; last_update_timestamp: string; next_scheduled_update: string; update_interval_minutes: number; status: string };
  provenance: AiProvenance;
  warnings: string[];
}
