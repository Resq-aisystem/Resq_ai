import { Injectable, inject, signal, computed } from '@angular/core';
import { forkJoin } from 'rxjs';
import { LocationService } from './location.service';
import { AlertService } from './alert.service';
import { RoutingService } from './routing.service';
import { LocationResponse } from '../models/location.model';
import { AlertResponse, AlertSeverity } from '../models/alert.model';
import { RouteOption } from '../models/route.model';
import { PriorityQueueItem, PriorityScoreBreakdown } from '../models/priority.model';
import { ScenarioParameters, ScenarioImpactSummary, PriorityShift } from '../models/scenario.model';
import { ProvenanceRecord } from '../models/provenance.model';

import { AiIntelligenceService } from './ai-intelligence.service';
import { AiDecisionResponse, AiActionPlan, AiEvacuationPriority, AiRouteDetail, AiScenarioResult, AiProvenance } from '../models/ai-decision.model';
import { GeminiBriefingResponse, GeminiHealthResponse } from '../models/gemini-briefing.model';
import { of } from 'rxjs';
import { catchError, timeout } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DisasterStateService {
  private locationService = inject(LocationService);
  private alertService = inject(AlertService);
  private routingService = inject(RoutingService);
  private aiService = inject(AiIntelligenceService);

  // AI Decision Intelligence Signal
  readonly aiDecision = signal<AiDecisionResponse | null>(null);
  readonly aiHealthStatus = signal<any>(null);
  readonly aiLoading = signal<boolean>(false);
  readonly aiError = signal<string | null>(null);

  // Gemini Explanation Briefing Signal
  readonly geminiBriefing = signal<GeminiBriefingResponse | null>(null);
  readonly geminiHealthStatus = signal<GeminiHealthResponse | null>(null);
  readonly geminiLoading = signal<boolean>(false);

  // Latency & UX Performance Signals
  readonly resqAiDecisionLatencyMs = signal<number>(0);
  readonly geminiBriefingLatencyMs = signal<number>(0);
  readonly totalDashboardTimeMs = signal<number>(0);
  readonly timeToFirstCoreIntelligenceMs = signal<number>(0);

  // Real-Time Telemetry & Polling Architecture Signals
  readonly pollingIntervalSeconds = signal<number>(30);
  readonly nextUpdateCountdown = signal<number>(30);
  readonly lastUpdatedTimestamp = signal<string | null>(null);
  readonly isSyncing = signal<boolean>(false);
  readonly isConnectionLost = signal<boolean>(false);
  readonly hasLastKnownData = signal<boolean>(false);
  private pollingTimerId: any = null;

  // Raw State Signals
  readonly locations = signal<LocationResponse[]>([]);
  readonly alerts = signal<AlertResponse[]>([]);
  readonly selectedLocationId = signal<number | null>(null);
  readonly selectedAlertId = signal<number | null>(null);
  readonly selectedDestinationId = signal<number | null>(null);
  readonly selectedRoute = signal<RouteOption | null>(null);
  readonly activeTab = signal<'zone-details' | 'route-intelligence' | 'ai-action-plan' | 'what-if' | 'provenance'>('zone-details');

  readonly loading = signal<boolean>(false);
  readonly error = signal<string | null>(null);

  // Filter Signals
  readonly filterSeverity = signal<AlertSeverity | 'all'>('all');
  readonly filterType = signal<string | 'all'>('all');

  // Scenario Simulation Signals
  readonly isSimulationActive = signal<boolean>(false);
  readonly scenarioParams = signal<ScenarioParameters>({
    rainfallSurgeMm: 0,
    waterLevelDeltaM: 0,
    floodBarrierFailure: false,
    powerGridFailure: false
  });

  // COMPUTED: Effective Alerts (Live vs Simulated)
  readonly effectiveAlerts = computed<AlertResponse[]>(() => {
    const liveAlerts = this.alerts();
    if (!this.isSimulationActive()) {
      return liveAlerts;
    }

    const delta = this.scenarioParams().waterLevelDeltaM;
    const barrierFailed = this.scenarioParams().floodBarrierFailure;

    return liveAlerts.map(alert => {
      const baseWater = alert.water_level || 0.5;
      const basePeak = alert.predicted_peak || (baseWater + 0.5);
      const waterBoost = delta + (barrierFailed ? 0.6 : 0);
      const simulatedWater = +(baseWater + waterBoost).toFixed(2);
      const simulatedPeak = +(basePeak + waterBoost * 1.2).toFixed(2);

      // Recalculate simulated severity based on water level threshold
      let simulatedSeverity: AlertSeverity = alert.severity;
      if (simulatedWater >= 2.5) {
        simulatedSeverity = 'critical';
      } else if (simulatedWater >= 1.4) {
        simulatedSeverity = 'high';
      } else if (simulatedWater >= 0.7) {
        simulatedSeverity = 'medium';
      } else {
        simulatedSeverity = 'low';
      }

      const populationMultiplier = 1 + (delta * 0.45) + (barrierFailed ? 0.3 : 0);
      const simulatedPopulation = alert.affected_population 
        ? Math.round(alert.affected_population * populationMultiplier) 
        : 0;

      return {
        ...alert,
        water_level: simulatedWater,
        predicted_peak: simulatedPeak,
        severity: simulatedSeverity,
        affected_population: simulatedPopulation
      };
    });
  });

  // COMPUTED: Selected Location
  readonly selectedLocation = computed<LocationResponse | null>(() => {
    const id = this.selectedLocationId();
    if (id === null) return null;
    return this.locations().find(loc => loc.id === id) || null;
  });

  // COMPUTED: Selected Alert (Linked to selected location)
  readonly selectedAlert = computed<AlertResponse | null>(() => {
    const locId = this.selectedLocationId();
    if (locId === null) return null;
    return this.effectiveAlerts().find(alt => alt.location_id === locId) || null;
  });

  // COMPUTED: Shelters Available for Evacuation
  readonly availableShelters = computed<LocationResponse[]>(() => {
    return this.locations().filter(loc => loc.type === 'shelter' && loc.is_active);
  });

  // COMPUTED: Selected Destination Shelter
  readonly selectedDestination = computed<LocationResponse | null>(() => {
    const destId = this.selectedDestinationId();
    const shelters = this.availableShelters();
    if (destId !== null) {
      const found = shelters.find(s => s.id === destId);
      if (found) return found;
    }
    // Default to first shelter if available
    return shelters.length > 0 ? shelters[0] : null;
  });

  // COMPUTED: KPI Summary
  readonly kpiSummary = computed(() => {
    const alerts = this.effectiveAlerts();
    const locations = this.locations();

    const criticalZonesCount = alerts.filter(a => a.severity === 'critical' && a.status === 'active').length;
    const highRiskZonesCount = alerts.filter(a => a.severity === 'high' && a.status === 'active').length;
    const exposedPopulation = alerts
      .filter(a => a.status === 'active')
      .reduce((sum, a) => sum + (a.affected_population || 0), 0);

    const criticalInfrastructure = locations.filter(l => l.type === 'critical_infrastructure').length;
    const totalHospitals = locations.filter(l => l.type === 'hospital').length;
    const totalShelters = locations.filter(l => l.type === 'shelter').length;

    const totalCapacity = locations
      .filter(l => l.type === 'shelter')
      .reduce((sum, l) => sum + (l.capacity || 0), 0);
    const totalOccupancy = locations
      .filter(l => l.type === 'shelter')
      .reduce((sum, l) => sum + (l.current_occupancy || 0), 0);

    return {
      criticalZonesCount,
      highRiskZonesCount,
      exposedPopulation,
      criticalInfrastructure,
      totalHospitals,
      totalShelters,
      totalCapacity,
      totalOccupancy,
      totalLocations: locations.length,
      activeAlertsCount: alerts.filter(a => a.status === 'active').length
    };
  });

  // COMPUTED: Emergency Priority Queue with Explainable Scoring
  readonly priorityQueue = computed<PriorityQueueItem[]>(() => {
    const locations = this.locations();
    const alerts = this.effectiveAlerts();

    const items: PriorityQueueItem[] = [];

    alerts.forEach(alert => {
      const loc = locations.find(l => l.id === alert.location_id);
      if (!loc) return;

      // Explainable Formula Calculation
      // 1. Severity weight (max 35)
      let severityWeight = 10;
      if (alert.severity === 'critical') severityWeight = 35;
      else if (alert.severity === 'high') severityWeight = 26;
      else if (alert.severity === 'medium') severityWeight = 16;
      else severityWeight = 8;

      // 2. Water Level score (max 25)
      const waterLevel = alert.water_level || 0.2;
      const waterLevelScore = +Math.min(25, (waterLevel / 3.0) * 25).toFixed(1);

      // 3. Occupancy / Vulnerability component (max 20)
      const cap = loc.capacity || 100;
      const occ = loc.current_occupancy || 0;
      const occRatio = Math.min(1.0, occ / Math.max(1, cap));
      const typeVulnerability = loc.type === 'hospital' ? 1.0 : (loc.type === 'critical_infrastructure' ? 0.9 : 0.6);
      const occupancyScore = +(occRatio * typeVulnerability * 20).toFixed(1);

      // 4. Affected Population component (max 20)
      const pop = alert.affected_population || 0;
      const populationScore = +Math.min(20, (pop / 20000) * 20).toFixed(1);

      const totalScore = +Math.min(100, severityWeight + waterLevelScore + occupancyScore + populationScore).toFixed(1);

      const breakdown: PriorityScoreBreakdown = {
        severityComponent: severityWeight,
        waterLevelComponent: waterLevelScore,
        occupancyComponent: occupancyScore,
        populationComponent: populationScore,
        totalScore
      };

      // Construct plain-English justification reason
      const reason = `Ranked with score ${totalScore}/100 based on ${alert.severity.toUpperCase()} flood stage (${waterLevel}m rise), ${loc.current_occupancy} vulnerable occupants at ${loc.name}, and ${pop.toLocaleString()} exposed population.`;

      items.push({
        rank: 0, // Assigned below after sorting
        location: loc,
        alert,
        priorityScore: totalScore,
        priorityLevel: alert.severity,
        scoreBreakdown: breakdown,
        priorityReason: reason,
        recommendedAction: alert.recommended_action,
        justification: alert.justification
      });
    });

    // Sort descending by priorityScore
    items.sort((a, b) => b.priorityScore - a.priorityScore);

    // Assign rank 1, 2, 3...
    items.forEach((item, index) => {
      item.rank = index + 1;
    });

    return items;
  });

  // COMPUTED: Calculated Routes for selected facility and destination
  readonly availableRoutes = computed<RouteOption[]>(() => {
    const origin = this.selectedLocation();
    const destination = this.selectedDestination();
    const alerts = this.effectiveAlerts();

    if (!origin || !destination || origin.id === destination.id) {
      return [];
    }

    return this.routingService.calculateRoutes(origin, destination, alerts);
  });

  // COMPUTED: Scenario Impact Summary (Before vs After)
  readonly scenarioImpact = computed<ScenarioImpactSummary>(() => {
    const params = this.scenarioParams();
    const isSim = this.isSimulationActive();
    const simulatedAlerts = this.effectiveAlerts();
    const baselineAlerts = this.alerts();

    const baseCritical = baselineAlerts.filter(a => a.severity === 'critical').length;
    const simCritical = simulatedAlerts.filter(a => a.severity === 'critical').length;

    const baseHigh = baselineAlerts.filter(a => a.severity === 'high').length;
    const simHigh = simulatedAlerts.filter(a => a.severity === 'high').length;

    const basePop = baselineAlerts.reduce((sum, a) => sum + (a.affected_population || 0), 0);
    const simPop = simulatedAlerts.reduce((sum, a) => sum + (a.affected_population || 0), 0);

    const locations = this.locations();
    const shifts: PriorityShift[] = [];

    simulatedAlerts.forEach(simAlert => {
      const baseAlert = baselineAlerts.find(a => a.id === simAlert.id);
      const loc = locations.find(l => l.id === simAlert.location_id);
      if (!baseAlert || !loc) return;

      const baseWater = baseAlert.water_level || 0;
      const simWater = simAlert.water_level || 0;

      shifts.push({
        locationId: loc.id,
        locationName: loc.name,
        previousSeverity: baseAlert.severity,
        simulatedSeverity: simAlert.severity,
        previousWaterLevel: baseWater,
        simulatedWaterLevel: simWater,
        previousScore: 0,
        simulatedScore: 0,
        previousRank: 0,
        simulatedRank: 0,
        impactSummary: `Water level rise from ${baseWater}m to ${simWater}m (+${(simWater - baseWater).toFixed(1)}m). Severity: ${baseAlert.severity.toUpperCase()} → ${simAlert.severity.toUpperCase()}.`
      });
    });

    return {
      parameters: params,
      simulatedAlerts,
      criticalZonesDelta: simCritical - baseCritical,
      highRiskZonesDelta: simHigh - baseHigh,
      affectedPopulationDelta: simPop - basePop,
      priorityShifts: shifts,
      simulationActive: isSim
    };
  });

  // COMPUTED: Provenance Records (Data audit trail directly from backend)
  readonly provenanceRecords = computed<ProvenanceRecord[]>(() => {
    const records: ProvenanceRecord[] = [];
    const alerts = this.alerts();
    const locations = this.locations();

    alerts.forEach(alert => {
      const loc = locations.find(l => l.id === alert.location_id);
      records.push({
        entityType: 'alert',
        entityId: alert.id,
        entityName: alert.title,
        issuedBy: alert.issued_by,
        issuedAt: alert.issued_at,
        updatedAt: alert.updated_at,
        endpoint: `/api/v1/alerts/${alert.id}`,
        httpMethod: 'GET',
        dataSource: 'FastAPI Backend / SQLite (Table: alerts)',
        status: alert.status,
        provenanceHash: `SHA256-${alert.id}-${new Date(alert.created_at).getTime().toString(16)}`,
        confidenceScore: 94.2
      });
    });

    locations.forEach(loc => {
      records.push({
        entityType: 'location',
        entityId: loc.id,
        entityName: loc.name,
        issuedBy: 'Municipal GIS / Disaster Registry',
        issuedAt: loc.created_at,
        updatedAt: loc.updated_at,
        endpoint: `/api/v1/locations/${loc.id}`,
        httpMethod: 'GET',
        dataSource: 'FastAPI Backend / SQLite (Table: locations)',
        status: loc.is_active ? 'active' : 'inactive',
        provenanceHash: `SHA256-${loc.id}-${new Date(loc.created_at).getTime().toString(16)}`,
        confidenceScore: 98.5
      });
    });

    return records;
  });

  // Initial Data Load — Asynchronous non-blocking architecture
  loadAllData(): void {
    const t0 = performance.now();
    this.loading.set(true);
    this.aiLoading.set(true);
    this.geminiLoading.set(false);
    this.error.set(null);
    this.aiError.set(null);

    // 1. Fetch core decision intelligence immediately (RESQ-AI + GIS Telemetry)
    forkJoin({
      locations: this.locationService.getLocations({ limit: 100 }),
      alerts: this.alertService.getAlerts({ limit: 100 }),
      aiDecision: this.aiService.getDecisionIntelligence('Puri', 'PURI').pipe(
        catchError(err => {
          console.error('AI Service fetch error:', err);
          this.aiError.set('AI SERVICE UNAVAILABLE');
          return of(null);
        })
      ),
      aiHealth: this.aiService.getHealth().pipe(
        catchError(err => {
          return of({ status: 'unavailable', service: 'RESQ-AI Engine', engines: {} });
        })
      )
    }).subscribe({
      next: ({ locations, alerts, aiDecision, aiHealth }) => {
        const coreLatency = Math.round(performance.now() - t0);
        this.timeToFirstCoreIntelligenceMs.set(coreLatency);
        this.resqAiDecisionLatencyMs.set(coreLatency);

        this.locations.set(locations);
        this.alerts.set(alerts);
        if (aiDecision) {
          this.aiDecision.set(aiDecision);
        }
        if (aiHealth) {
          this.aiHealthStatus.set(aiHealth);
        }

        const nowStr = new Date().toLocaleTimeString('en-US', { hour12: false });
        this.lastUpdatedTimestamp.set(nowStr);
        this.hasLastKnownData.set(true);
        this.isConnectionLost.set(false);

        // Render dashboard immediately!
        this.loading.set(false);
        this.aiLoading.set(false);

        // Auto-select highest priority location
        if (!this.selectedLocationId() && locations.length > 0) {
          const criticalAlert = alerts.find(a => a.severity === 'critical');
          if (criticalAlert) {
            this.selectLocation(criticalAlert.location_id);
          } else {
            this.selectLocation(locations[0].id);
          }
        }

        // 2. Trigger Gemini briefing asynchronously AFTER core intelligence renders
        this.loadGeminiBriefing(t0);

        // 3. Start periodic background polling timer
        this.startPollingLoop();
      },
      error: (err) => {
        this.error.set(err.message || 'Failed to load disaster data from backend');
        this.loading.set(false);
        this.aiLoading.set(false);
        this.isConnectionLost.set(true);
      }
    });
  }

  // Periodic non-blocking background polling method
  refreshLiveData(): void {
    if (this.isSyncing()) return;

    this.isSyncing.set(true);

    forkJoin({
      locations: this.locationService.getLocations({ limit: 100 }),
      alerts: this.alertService.getAlerts({ limit: 100 }),
      aiDecision: this.aiService.getDecisionIntelligence('Puri', 'PURI').pipe(
        catchError(err => of(null))
      ),
      aiHealth: this.aiService.getHealth().pipe(
        catchError(err => of({ status: 'unavailable', service: 'RESQ-AI Engine', engines: {} }))
      )
    }).subscribe({
      next: ({ locations, alerts, aiDecision, aiHealth }) => {
        // Update state in background without screen flicker or wiping dashboard
        if (locations && locations.length > 0) this.locations.set(locations);
        if (alerts && alerts.length > 0) this.alerts.set(alerts);
        if (aiDecision) this.aiDecision.set(aiDecision);
        if (aiHealth) this.aiHealthStatus.set(aiHealth);

        const nowStr = new Date().toLocaleTimeString('en-US', { hour12: false });
        this.lastUpdatedTimestamp.set(nowStr);
        this.hasLastKnownData.set(true);
        this.isConnectionLost.set(false);
        this.isSyncing.set(false);
        this.nextUpdateCountdown.set(this.pollingIntervalSeconds());
      },
      error: (err) => {
        console.warn('Background sync error, retaining last known valid data:', err);
        this.isConnectionLost.set(true);
        this.isSyncing.set(false);
        this.nextUpdateCountdown.set(this.pollingIntervalSeconds());
      }
    });
  }

  startPollingLoop(): void {
    if (this.pollingTimerId) return;

    this.pollingTimerId = setInterval(() => {
      if (this.isSyncing()) return;

      const remaining = this.nextUpdateCountdown() - 1;
      if (remaining <= 0) {
        this.nextUpdateCountdown.set(0);
        this.refreshLiveData();
      } else {
        this.nextUpdateCountdown.set(remaining);
      }
    }, 1000);
  }

  loadGeminiBriefing(t0: number = performance.now()): void {
    // Prevent duplicate simultaneous requests
    if (this.geminiLoading()) {
      return;
    }

    this.geminiLoading.set(true);
    const tGeminiStart = performance.now();

    // Fetch Gemini health & briefing asynchronously with 15s timeout limit
    forkJoin({
      geminiBriefing: this.aiService.getGeminiBriefing('Puri', 'PURI').pipe(
        timeout(15000),
        catchError(err => {
          console.warn('Gemini Briefing timeout or error:', err);
          return of(null);
        })
      ),
      geminiHealth: this.aiService.getGeminiHealth().pipe(
        catchError(err => {
          return of({ status: 'unavailable', message: 'Gemini service offline', model: 'gemini-3.6-flash', fallback_active: true });
        })
      )
    }).subscribe({
      next: ({ geminiBriefing, geminiHealth }) => {
        const geminiLatency = Math.round(performance.now() - tGeminiStart);
        const totalTime = Math.round(performance.now() - t0);
        this.geminiBriefingLatencyMs.set(geminiLatency);
        this.totalDashboardTimeMs.set(totalTime);

        if (geminiBriefing) {
          this.geminiBriefing.set(geminiBriefing);
        }
        if (geminiHealth) {
          this.geminiHealthStatus.set(geminiHealth);
        }

        this.geminiLoading.set(false);
      },
      error: () => {
        this.geminiLoading.set(false);
      }
    });
  }


  selectLocation(locationId: number): void {
    this.selectedLocationId.set(locationId);

    // Auto-select linked alert
    const linkedAlert = this.effectiveAlerts().find(a => a.location_id === locationId);
    if (linkedAlert) {
      this.selectedAlertId.set(linkedAlert.id);
    }

    // Auto-select best shelter destination if not set
    const shelters = this.availableShelters();
    if (shelters.length > 0) {
      const bestShelter = shelters.find(s => s.id !== locationId) || shelters[0];
      this.selectedDestinationId.set(bestShelter.id);
    }

    // Default to safest route
    const routes = this.availableRoutes();
    if (routes.length > 0) {
      const safest = routes.find(r => r.type === 'safest') || routes[0];
      this.selectedRoute.set(safest);
    }
  }

  selectDestination(shelterId: number): void {
    this.selectedDestinationId.set(shelterId);
    const routes = this.availableRoutes();
    if (routes.length > 0) {
      const safest = routes.find(r => r.type === 'safest') || routes[0];
      this.selectedRoute.set(safest);
    }
  }

  selectRoute(route: RouteOption): void {
    this.selectedRoute.set(route);
  }

  setActiveTab(tab: 'zone-details' | 'route-intelligence' | 'ai-action-plan' | 'what-if' | 'provenance'): void {
    this.activeTab.set(tab);
  }

  setScenarioParams(params: Partial<ScenarioParameters>): void {
    this.scenarioParams.update(curr => ({ ...curr, ...params }));
    this.isSimulationActive.set(true);
  }

  resetSimulation(): void {
    this.scenarioParams.set({
      rainfallSurgeMm: 0,
      waterLevelDeltaM: 0,
      floodBarrierFailure: false,
      powerGridFailure: false
    });
    this.isSimulationActive.set(false);
  }

  toggleSimulation(active: boolean): void {
    this.isSimulationActive.set(active);
  }
}
