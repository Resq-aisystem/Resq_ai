import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';

@Component({
  selector: 'app-kpi-summary-cards',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="kpi-grid">
      <!-- 1. Overall Composite Risk -->
      <div class="kpi-card card-risk">
        <div class="card-header">
          <span class="indicator-dot dot-critical"></span>
          <span class="card-label">CURRENT RISK SCORE</span>
          <span class="badge-priority">{{ getRiskLevel() }}</span>
        </div>
        <div class="card-body">
          <div class="metric-value font-mono text-critical">
            {{ getRiskScore() }}
          </div>
          <div class="metric-subtext">
            <span>COMPOSITE RISK SCORE</span>
            <span class="tag-immediate">Puri District</span>
          </div>
        </div>
      </div>

      <!-- 2. Priority Breakdown (P1 / P2 / P3 / P4) -->
      <div class="kpi-card card-critical" (click)="filterBySeverity('critical')">
        <div class="card-header">
          <span class="indicator-dot dot-critical"></span>
          <span class="card-label">PRIORITY QUEUE</span>
          <span class="badge-priority">P1 - P4</span>
        </div>
        <div class="card-body">
          <div class="priority-breakdown">
            <span class="p-chip p1">P1: {{ state.kpiSummary().criticalZonesCount }}</span>
            <span class="p-chip p2">P2: {{ state.kpiSummary().highRiskZonesCount }}</span>
            <span class="p-chip p3">P3: 1</span>
            <span class="p-chip p4">P4: 1</span>
          </div>
          <div class="metric-subtext">
            <span>Total Active Priorities: {{ state.kpiSummary().activeAlertsCount }}</span>
          </div>
        </div>
      </div>

      <!-- 3. Total Exposed Population -->
      <div class="kpi-card card-population">
        <div class="card-header">
          <span class="indicator-dot dot-cyan"></span>
          <span class="card-label">EXPOSED POPULATION</span>
        </div>
        <div class="card-body">
          <div class="metric-value font-mono text-cyan">
            {{ state.kpiSummary().exposedPopulation.toLocaleString() }}
          </div>
          <div class="metric-subtext">
            <span>Across {{ state.kpiSummary().activeAlertsCount }} active flood zones</span>
          </div>
        </div>
      </div>

      <!-- 4. Rescue Routes -->
      <div class="kpi-card card-infrastructure">
        <div class="card-header">
          <span class="indicator-dot dot-amber"></span>
          <span class="card-label">RESCUE ROUTES</span>
        </div>
        <div class="card-body">
          <div class="metric-value font-mono text-amber">
            {{ state.availableRoutes().length || 3 }}
          </div>
          <div class="metric-subtext">
            <span>Fastest &bull; Safest &bull; Balanced</span>
          </div>
        </div>
      </div>

      <!-- 5. Regional Shelter Occupancy -->
      <div class="kpi-card card-shelters">
        <div class="card-header">
          <span class="indicator-dot dot-green"></span>
          <span class="card-label">SHELTER CAPACITY</span>
        </div>
        <div class="card-body">
          <div class="shelter-metric">
            <span class="metric-value font-mono text-green">
              {{ state.kpiSummary().totalOccupancy }}
            </span>
            <span class="metric-divider">/</span>
            <span class="metric-capacity font-mono">{{ state.kpiSummary().totalCapacity }}</span>
          </div>
          <div class="capacity-bar-track">
            <div 
              class="capacity-bar-fill" 
              [style.width.%]="getShelterOccupancyPercent()"
              [ngClass]="{'bar-full': getShelterOccupancyPercent() > 80}"
            ></div>
          </div>
          <div class="metric-subtext">
            <span>{{ (state.kpiSummary().totalCapacity - state.kpiSummary().totalOccupancy) }} beds available</span>
            <span class="shelter-pct font-mono">{{ getShelterOccupancyPercent() }}% FULL</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      padding: 10px 18px;
      background: #080d1a;
      border-bottom: 1px solid #1e293b;
    }

    .kpi-card {
      background: linear-gradient(180deg, #0f172a 0%, #0b1120 100%);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }

    .kpi-card:hover {
      border-color: #334155;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }

    .card-critical:hover {
      border-color: rgba(239, 68, 68, 0.5);
      box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
    }

    .card-high:hover {
      border-color: rgba(249, 115, 22, 0.5);
      box-shadow: 0 0 15px rgba(249, 115, 22, 0.2);
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 6px;
    }

    .indicator-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
    }

    .dot-critical {
      background: #ef4444;
      box-shadow: 0 0 6px #ef4444;
      animation: pulse-critical 2s infinite;
    }

    .dot-high {
      background: #f97316;
      box-shadow: 0 0 6px #f97316;
    }

    .dot-cyan {
      background: #06b6d4;
      box-shadow: 0 0 6px #06b6d4;
    }

    .dot-amber {
      background: #f59e0b;
      box-shadow: 0 0 6px #f59e0b;
    }

    .dot-green {
      background: #10b981;
      box-shadow: 0 0 6px #10b981;
    }

    .card-label {
      font-size: 10px;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.6px;
      flex-grow: 1;
    }

    .badge-priority, .badge-warning {
      font-size: 9px;
      font-weight: 800;
      padding: 1px 5px;
      border-radius: 3px;
    }

    .badge-priority {
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .badge-warning {
      background: rgba(249, 115, 22, 0.2);
      color: #fb923c;
      border: 1px solid rgba(249, 115, 22, 0.4);
    }

    .card-body {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .metric-value {
      font-size: 24px;
      font-weight: 800;
      line-height: 1.1;
      letter-spacing: -0.5px;
    }

    .text-critical {
      color: #ef4444;
      text-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
    }

    .text-high {
      color: #f97316;
      text-shadow: 0 0 12px rgba(249, 115, 22, 0.3);
    }

    .text-cyan {
      color: #38bdf8;
      text-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
    }

    .text-amber {
      color: #fbbf24;
    }

    .text-green {
      color: #34d399;
    }

    .shelter-metric {
      display: flex;
      align-items: baseline;
      gap: 4px;
    }

    .metric-divider {
      color: #475569;
      font-size: 16px;
    }

    .metric-capacity {
      color: #64748b;
      font-size: 14px;
    }

    .capacity-bar-track {
      width: 100%;
      height: 4px;
      background: #1e293b;
      border-radius: 2px;
      margin: 4px 0 2px 0;
      overflow: hidden;
    }

    .capacity-bar-fill {
      height: 100%;
      background: #10b981;
      border-radius: 2px;
      transition: width 0.4s ease;
    }

    .bar-full {
      background: #f97316;
    }

    .metric-subtext {
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 9.5px;
      color: #64748b;
    }

    .tag-immediate {
      color: #ef4444;
      font-weight: 700;
    }

    .tag-standby {
      color: #f97316;
      font-weight: 700;
    }

    .shelter-pct {
      font-size: 9.5px;
      color: #94a3b8;
      font-weight: 700;
    }

    .priority-breakdown {
      display: flex;
      gap: 4px;
      margin: 4px 0;
    }

    .p-chip {
      font-size: 10px;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      font-family: monospace;
    }

    .p-chip.p1 {
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .p-chip.p2 {
      background: rgba(249, 115, 22, 0.2);
      color: #fb923c;
      border: 1px solid rgba(249, 115, 22, 0.4);
    }

    .p-chip.p3 {
      background: rgba(245, 158, 11, 0.2);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.4);
    }

    .p-chip.p4 {
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
    }
  `]
})
export class KpiSummaryCardsComponent {
  readonly state = inject(DisasterStateService);

  getRiskScore(): number | string {
    const fp = this.state.aiDecision()?.flood_prediction;
    if (!fp) return '84.5';
    return fp.predicted_risk_score !== undefined ? fp.predicted_risk_score : (fp.risk_score !== undefined ? fp.risk_score : '84.5');
  }

  getRiskLevel(): string {
    const fp = this.state.aiDecision()?.flood_prediction;
    if (!fp) return 'HIGH';
    return fp.predicted_risk_level || fp.risk_level || 'HIGH';
  }

  getShelterOccupancyPercent(): number {
    const kpi = this.state.kpiSummary();
    if (!kpi.totalCapacity) return 0;
    return Math.round((kpi.totalOccupancy / kpi.totalCapacity) * 100);
  }

  filterBySeverity(sev: 'critical' | 'high'): void {
    this.state.filterSeverity.set(sev);
  }
}
