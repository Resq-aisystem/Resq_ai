export interface GeminiBriefingContent {
  summary: string;
  risk_explanation: string;
  priority_explanation: string;
  route_explanation: string;
  recommended_actions: string[];
  monitoring_actions: string[];
  scenario_explanation: string;
  limitations: string[];
  grounding_sources: string[];
  is_fallback: boolean;
  fallback_reason?: string;
  provider: string;
  model_used: string;
}

export interface GeminiBriefingResponse {
  verified_decision: any;
  gemini_briefing: GeminiBriefingContent;
  provenance: any;
  limitations: string[];
}

export interface GeminiHealthResponse {
  status: string;
  message: string;
  model: string;
  fallback_active: boolean;
}
