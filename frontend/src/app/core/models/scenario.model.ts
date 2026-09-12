import { AlertResponse, AlertSeverity } from './alert.model';

export interface ScenarioParameters {
  rainfallSurgeMm: number;
  waterLevelDeltaM: number;
  floodBarrierFailure: boolean;
  powerGridFailure: boolean;
}

export interface PriorityShift {
  locationId: number;
  locationName: string;
  previousSeverity: AlertSeverity;
  simulatedSeverity: AlertSeverity;
  previousWaterLevel: number;
  simulatedWaterLevel: number;
  previousScore: number;
  simulatedScore: number;
  previousRank: number;
  simulatedRank: number;
  impactSummary: string;
}

export interface ScenarioImpactSummary {
  parameters: ScenarioParameters;
  simulatedAlerts: AlertResponse[];
  criticalZonesDelta: number;
  highRiskZonesDelta: number;
  affectedPopulationDelta: number;
  priorityShifts: PriorityShift[];
  simulationActive: boolean;
}
