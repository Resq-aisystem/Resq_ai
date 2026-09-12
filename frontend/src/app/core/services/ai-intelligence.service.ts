import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { AiDecisionResponse, AiFloodPrediction, AiEvacuationPriority, AiRouteDetail, AiActionPlan, AiScenarioResult } from '../models/ai-decision.model';
import { GeminiBriefingResponse, GeminiHealthResponse } from '../models/gemini-briefing.model';

@Injectable({
  providedIn: 'root'
})
export class AiIntelligenceService {
  private api = inject(ApiService);

  getHealth(): Observable<{ status: string; service: string; engines: any }> {
    return this.api.get<{ status: string; service: string; engines: any }>('/ai/health');
  }

  getGeminiHealth(): Observable<GeminiHealthResponse> {
    return this.api.get<GeminiHealthResponse>('/ai/gemini/health');
  }

  getGeminiBriefing(
    cityName: string = 'Puri',
    districtName: string = 'PURI',
    routeMode: string = 'BALANCED',
    decisionContext?: any
  ): Observable<GeminiBriefingResponse> {
    return this.api.post<GeminiBriefingResponse>('/ai/gemini/briefing', {
      city_name: cityName,
      district_name: districtName,
      route_mode: routeMode,
      decision_context: decisionContext
    });
  }

  getDecisionIntelligence(
    cityName: string = 'Puri',
    districtName: string = 'PURI',
    routeMode: string = 'BALANCED'
  ): Observable<AiDecisionResponse> {
    return this.api.get<AiDecisionResponse>('/ai/decision', {
      city_name: cityName,
      district_name: districtName,
      route_mode: routeMode
    });
  }

  getRiskAssessment(cityName: string = 'Puri', districtName: string = 'PURI'): Observable<AiFloodPrediction> {
    return this.api.post<AiFloodPrediction>('/ai/risk', {
      city_name: cityName,
      district_name: districtName
    });
  }

  getEvacuationPriorities(cityName: string = 'Puri', districtName: string = 'PURI'): Observable<{ evacuation_priorities: AiEvacuationPriority[] }> {
    return this.api.post<{ evacuation_priorities: AiEvacuationPriority[] }>('/ai/priority', {
      city_name: cityName,
      district_name: districtName
    });
  }

  getRouteRisk(
    originLat: number,
    originLon: number,
    destLat: number,
    destLon: number,
    mode: string = 'BALANCED'
  ): Observable<{ route?: AiRouteDetail; routes?: { [key: string]: AiRouteDetail } }> {
    return this.api.post<{ route?: AiRouteDetail; routes?: { [key: string]: AiRouteDetail } }>('/ai/routes', {
      origin_lat: originLat,
      origin_lon: originLon,
      destination_lat: destLat,
      destination_lon: destLon,
      mode
    });
  }

  runScenario(
    rainfallMultiplier: number = 1.8,
    cityName: string = 'Puri',
    districtName: string = 'PURI'
  ): Observable<AiScenarioResult> {
    return this.api.post<AiScenarioResult>('/ai/scenario', {
      city_name: cityName,
      district_name: districtName,
      scenario_id: `sc_surge_${Math.round(rainfallMultiplier * 100)}pct`,
      scenario_name: `Rainfall Surge ${Math.round(rainfallMultiplier * 100)}% Scenario`,
      rainfall_multiplier: rainfallMultiplier
    });
  }

  getActionPlan(districtName: string = 'PURI', routeMode: string = 'BALANCED'): Observable<AiActionPlan> {
    return this.api.post<AiActionPlan>('/ai/action-plan', {
      district_name: districtName,
      route_mode: routeMode
    });
  }
}
