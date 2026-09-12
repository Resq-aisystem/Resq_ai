import { LocationResponse } from './location.model';
import { AlertResponse, AlertSeverity } from './alert.model';

export interface PriorityScoreBreakdown {
  severityComponent: number;      // max 35 pts
  waterLevelComponent: number;    // max 25 pts
  occupancyComponent: number;     // max 20 pts
  populationComponent: number;    // max 20 pts
  totalScore: number;             // max 100 pts
}

export interface PriorityQueueItem {
  rank: number;
  location: LocationResponse;
  alert: AlertResponse;
  priorityScore: number;
  priorityLevel: AlertSeverity;
  scoreBreakdown: PriorityScoreBreakdown;
  priorityReason: string;
  recommendedAction: string;
  justification: string;
}
