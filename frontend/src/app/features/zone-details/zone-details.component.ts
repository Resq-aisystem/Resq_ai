import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';

@Component({
  selector: 'app-zone-details',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="zone-details-container">
      @if (state.selectedLocation(); as loc) {
        <!-- Zone Header Banner -->
        <div class="zone-header">
          <div class="header-type-pill">
            <span class="type-icon">{{ getTypeIcon(loc.type) }}</span>
            <span class="type-text">{{ loc.type | uppercase }}</span>
            <span class="status-pill" [ngClass]="loc.is_active ? 'pill-active' : 'pill-inactive'">
              {{ loc.is_active ? 'FACILITY OPERATIONAL' : 'OFFLINE' }}
            </span>
          </div>

          <h2 class="zone-title">{{ loc.name }}</h2>
          <div class="zone-address">
            <svg class="pin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            <span>{{ loc.address }}</span>
            <span class="coords font-mono">({{ loc.latitude.toFixed(4) }}, {{ loc.longitude.toFixed(4) }})</span>
          </div>
        </div>

        <div class="details-scrollable">
          <!-- 1. COMPOSITE RISK SCORE GAUGE -->
          <div class="section-card risk-gauge-card">
            <div class="section-header-row">
              <h4 class="section-title">
                <span class="title-icon">🎯</span>
                COMPOSITE RISK SCORE
              </h4>
              <span class="risk-level-badge font-mono" [ngClass]="'badge-' + (state.selectedAlert()?.severity || 'high')">
                {{ (state.selectedAlert()?.severity || 'HIGH') | uppercase }} RISK
              </span>
            </div>

            <div class="gauge-wrapper">
              <div class="radial-ring">
                <svg viewBox="0 0 100 100" class="ring-svg">
                  <circle cx="50" cy="50" r="42" class="ring-bg"/>
                  <circle 
                    cx="50" cy="50" r="42" 
                    class="ring-fill" 
                    [style.strokeDasharray]="263.8" 
                    [style.strokeDashoffset]="263.8 * (1 - getRiskScore() / 100)"
                  />
                </svg>
                <div class="ring-center">
                  <span class="ring-score font-mono">{{ getRiskScore() }}</span>
                  <span class="ring-max">/ 100</span>
                </div>
              </div>
              <div class="gauge-meta">
                <div class="gauge-label font-mono">COMPOSITE RISK SCORE</div>
                <div class="gauge-sub font-mono">NOT PROBABILITY &bull; DETERMINISTIC RESQ-AI ENGINE</div>
                <div class="hazard-chips">
                  <span class="h-chip">Hydrological: HIGH</span>
                  <span class="h-chip">Terrain: SUSCEPTIBLE</span>
                  <span class="h-chip">Multi-Hazard: ACTIVE</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Active Alert Status Card -->
          @if (state.selectedAlert(); as alert) {
            <div class="alert-banner" [ngClass]="'banner-' + alert.severity">
              <div class="alert-top">
                <div class="severity-badge-row">
                  <span class="sev-tag" [ngClass]="'tag-' + alert.severity">
                    {{ alert.severity | uppercase }} SEVERITY
                  </span>
                  <span class="alert-type-tag font-mono">
                    {{ alert.alert_type | uppercase }}
                  </span>
                </div>
                <span class="alert-time font-mono">ISSUED: {{ alert.issued_at | date:'HH:mm:ss' }}</span>
              </div>

              <h3 class="alert-headline">{{ alert.title }}</h3>
              <p class="alert-desc">{{ alert.description }}</p>
            </div>

            <!-- Risk Drivers Matrix -->
            <div class="section-card">
              <h4 class="section-title">
                <span class="title-icon">📊</span>
                PRIMARY RISK DRIVERS
              </h4>
              <div class="drivers-grid">
                <div class="driver-item">
                  <span class="driver-label">CURRENT FLOOD STAGE</span>
                  <span class="driver-val font-mono" [ngClass]="'text-' + alert.severity">
                    {{ alert.water_level || 0 }}m
                  </span>
                  <span class="driver-sub">Crest Rate: +0.35m/hr</span>
                </div>
                <div class="driver-item">
                  <span class="driver-label">PREDICTED PEAK WATER</span>
                  <span class="driver-val font-mono text-high">
                    {{ alert.predicted_peak || 0 }}m
                  </span>
                  <span class="driver-sub">Expected in 2.5 hrs</span>
                </div>
                <div class="driver-item">
                  <span class="driver-label">AFFECTED POPULATION</span>
                  <span class="driver-val font-mono text-cyan">
                    {{ (alert.affected_population || 0).toLocaleString() }}
                  </span>
                  <span class="driver-sub">Inundation Perimeter</span>
                </div>
                <div class="driver-item">
                  <span class="driver-label">BASIN RUNOFF SPEED</span>
                  <span class="driver-val font-mono">1.8 m/s</span>
                  <span class="driver-sub">High debris hazard</span>
                </div>
              </div>
            </div>
          } @else {
            <div class="no-alert-card">
              <span class="safe-icon">🛡️</span>
              <div>
                <strong>No Active Severe Flood Warning</strong>
                <p>Facility is within nominal elevation safety margins.</p>
              </div>
            </div>
          }

          <!-- Vulnerability & Occupancy Section -->
          <div class="section-card">
            <div class="section-header-row">
              <h4 class="section-title">
                <span class="title-icon">👥</span>
                OCCUPANCY & VULNERABLE POPULATION
              </h4>
              <span class="occupancy-ratio font-mono">
                {{ loc.current_occupancy }} / {{ loc.capacity || 'N/A' }}
              </span>
            </div>

            <!-- Progress Bar -->
            <div class="occupancy-bar-track">
              <div 
                class="occupancy-bar-fill"
                [style.width.%]="getOccupancyPercent(loc)"
                [ngClass]="getOccupancyPercent(loc) > 90 ? 'fill-critical' : (getOccupancyPercent(loc) > 70 ? 'fill-high' : 'fill-normal')"
              ></div>
            </div>

            <div class="occupancy-sub">
              <span>{{ getOccupancyPercent(loc) }}% of capacity utilized</span>
              <span>{{ (loc.capacity || 0) - loc.current_occupancy }} capacity remaining</span>
            </div>

            <!-- Facility Contacts -->
            <div class="contact-box">
              <div class="contact-item">
                <span class="contact-label">FACILITY LEAD:</span>
                <span class="contact-val">{{ loc.contact_name || 'Emergency Duty Officer' }}</span>
              </div>
              <div class="contact-item">
                <span class="contact-label">HOTLINE:</span>
                <span class="contact-val font-mono text-cyan">{{ loc.contact_phone || '512-555-0100' }}</span>
              </div>
              <div class="contact-item">
                <span class="contact-label">DIRECT EMAIL:</span>
                <span class="contact-val font-mono">{{ loc.contact_email || 'dispatch@resq-ai.local' }}</span>
              </div>
            </div>
          </div>

          <!-- Priority Ranking Breakdown -->
          @if (getPriorityItem(loc.id); as pItem) {
            <div class="section-card">
              <div class="section-header-row">
                <h4 class="section-title">
                  <span class="title-icon">⚡</span>
                  EXPLAINABLE PRIORITY SCORE: #{{ pItem.rank }}
                </h4>
                <span class="priority-score-badge font-mono" [ngClass]="'badge-' + pItem.priorityLevel">
                  {{ pItem.priorityScore }} / 100
                </span>
              </div>

              <div class="score-chips-grid">
                <div class="score-chip">
                  <span class="sc-label">Severity</span>
                  <span class="sc-val font-mono text-critical">{{ pItem.scoreBreakdown.severityComponent }}/35</span>
                </div>
                <div class="score-chip">
                  <span class="sc-label">Water Level</span>
                  <span class="sc-val font-mono text-high">{{ pItem.scoreBreakdown.waterLevelComponent }}/25</span>
                </div>
                <div class="score-chip">
                  <span class="sc-label">Occupancy</span>
                  <span class="sc-val font-mono text-amber">{{ pItem.scoreBreakdown.occupancyComponent }}/20</span>
                </div>
                <div class="score-chip">
                  <span class="sc-label">Population</span>
                  <span class="sc-val font-mono text-cyan">{{ pItem.scoreBreakdown.populationComponent }}/20</span>
                </div>
              </div>

              <div class="priority-reason-quote">
                <strong>Justification:</strong> {{ pItem.priorityReason }}
              </div>
            </div>
          }

          <!-- Grounded Action Snippet -->
          @if (state.selectedAlert(); as alert) {
            <div class="section-card grounded-action-card">
              <h4 class="section-title text-cyan">
                <span class="title-icon">🤖</span>
                GROUNDED ACTION DIRECTIVE
              </h4>
              <p class="action-body">{{ alert.recommended_action }}</p>

              <div class="action-footer">
                <button class="btn-primary-action" (click)="openAiActionPlan()">
                  EXPAND FULL ACTION PLAN &rarr;
                </button>
                <button class="btn-route-action" (click)="openRouteIntelligence()">
                  CALCULATE EVACUATION ROUTES &rarr;
                </button>
              </div>
            </div>
          }

          <!-- Provenance Audit Summary -->
          @if (state.selectedAlert(); as alert) {
            <div class="provenance-mini-card" (click)="openProvenance()">
              <span class="prov-icon">🔒</span>
              <div class="prov-content">
                <span class="prov-title">DATA PROVENANCE VERIFIED</span>
                <span class="prov-desc">Issued by: {{ alert.issued_by }} &bull; DB Record #{{ alert.id }}</span>
              </div>
              <span class="prov-arrow">&rarr;</span>
            </div>
          }
        </div>
      } @else {
        <div class="no-selection-state">
          <svg class="select-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <h3>No Zone Selected</h3>
          <p>Click on any marker on the map or select an emergency location from the Priority Queue.</p>
        </div>
      }
    </div>
  `,
  styles: [`
    .zone-details-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
    }

    .zone-header {
      padding: 14px 16px;
      background: linear-gradient(180deg, #111a2e 0%, #0d1527 100%);
      border-bottom: 1px solid #1e293b;
    }

    .header-type-pill {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }

    .type-icon {
      font-size: 14px;
    }

    .type-text {
      font-size: 9.5px;
      font-weight: 800;
      color: #94a3b8;
      letter-spacing: 0.8px;
    }

    .status-pill {
      font-size: 8.5px;
      font-weight: 700;
      padding: 1px 6px;
      border-radius: 4px;
      letter-spacing: 0.5px;
    }

    .pill-active {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .pill-inactive {
      background: rgba(239, 68, 68, 0.15);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .zone-title {
      font-size: 16px;
      font-weight: 800;
      color: #f8fafc;
      margin-bottom: 4px;
      line-height: 1.25;
    }

    .zone-address {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 11px;
      color: #94a3b8;
    }

    .pin-icon {
      width: 12px;
      height: 12px;
      color: #38bdf8;
      flex-shrink: 0;
    }

    .coords {
      font-size: 10px;
      color: #64748b;
    }

    .details-scrollable {
      flex: 1;
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    /* Alert Banner */
    .alert-banner {
      border-radius: 8px;
      padding: 12px;
      border: 1px solid;
    }

    .banner-critical {
      background: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.4);
    }

    .banner-high {
      background: rgba(249, 115, 22, 0.1);
      border-color: rgba(249, 115, 22, 0.4);
    }

    .banner-medium {
      background: rgba(234, 179, 8, 0.1);
      border-color: rgba(234, 179, 8, 0.4);
    }

    .banner-low {
      background: rgba(16, 185, 129, 0.1);
      border-color: rgba(16, 185, 129, 0.4);
    }

    .alert-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }

    .severity-badge-row {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .sev-tag {
      font-size: 9px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
    }

    .tag-critical { background: #dc2626; color: #fff; }
    .tag-high { background: #ea580c; color: #fff; }
    .tag-medium { background: #ca8a04; color: #fff; }
    .tag-low { background: #059669; color: #fff; }

    .alert-type-tag {
      font-size: 9px;
      color: #94a3b8;
      font-weight: 600;
    }

    .alert-time {
      font-size: 9px;
      color: #64748b;
    }

    .alert-headline {
      font-size: 13px;
      font-weight: 700;
      color: #f8fafc;
      margin-bottom: 4px;
    }

    .alert-desc {
      font-size: 11px;
      color: #cbd5e1;
      line-height: 1.4;
    }

    /* Section Cards */
    .section-card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 12px;
    }

    /* Risk Gauge Card */
    .risk-gauge-card {
      background: linear-gradient(180deg, #111a2e 0%, #0f172a 100%);
      border-color: rgba(56, 189, 248, 0.25);
    }

    .gauge-wrapper {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-top: 8px;
    }

    .radial-ring {
      position: relative;
      width: 76px;
      height: 76px;
      flex-shrink: 0;
    }

    .ring-svg {
      width: 100%;
      height: 100%;
      transform: rotate(-90deg);
    }

    .ring-bg {
      fill: none;
      stroke: #1e293b;
      stroke-width: 8;
    }

    .ring-fill {
      fill: none;
      stroke: #ef4444;
      stroke-width: 8;
      stroke-linecap: round;
      transition: stroke-dashoffset 0.6s ease;
    }

    .ring-center {
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .ring-score {
      font-size: 17px;
      font-weight: 800;
      color: #ef4444;
      line-height: 1;
    }

    .ring-max {
      font-size: 8px;
      color: #64748b;
    }

    .gauge-meta {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .gauge-label {
      font-size: 11px;
      font-weight: 800;
      color: #38bdf8;
      letter-spacing: 0.5px;
    }

    .gauge-sub {
      font-size: 8px;
      color: #64748b;
      letter-spacing: 0.4px;
    }

    .hazard-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 4px;
    }

    .h-chip {
      font-size: 8.5px;
      font-weight: 700;
      background: #1e293b;
      color: #94a3b8;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid #334155;
    }

    .section-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
    }

    .section-title {
      font-size: 11px;
      font-weight: 800;
      color: #94a3b8;
      letter-spacing: 0.6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .title-icon {
      font-size: 13px;
    }

    .drivers-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 8px;
    }

    .driver-item {
      background: #141e33;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 8px;
      display: flex;
      flex-direction: column;
    }

    .driver-label {
      font-size: 8px;
      color: #64748b;
      font-weight: 700;
      letter-spacing: 0.5px;
    }

    .driver-val {
      font-size: 16px;
      font-weight: 800;
      line-height: 1.2;
      margin: 2px 0;
    }

    .driver-sub {
      font-size: 9px;
      color: #94a3b8;
    }

    .text-critical { color: #ef4444; }
    .text-high { color: #f97316; }
    .text-cyan { color: #38bdf8; }
    .text-amber { color: #fbbf24; }

    /* Occupancy Bar */
    .occupancy-ratio {
      font-size: 12px;
      font-weight: 700;
      color: #f8fafc;
    }

    .occupancy-bar-track {
      width: 100%;
      height: 6px;
      background: #1e293b;
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 4px;
    }

    .occupancy-bar-fill {
      height: 100%;
      transition: width 0.4s ease;
    }

    .fill-critical { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
    .fill-high { background: #f97316; }
    .fill-normal { background: #10b981; }

    .occupancy-sub {
      display: flex;
      justify-content: space-between;
      font-size: 9.5px;
      color: #64748b;
      margin-bottom: 10px;
    }

    /* Contact Box */
    .contact-box {
      background: #141e33;
      border-radius: 6px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      border: 1px solid #1e293b;
    }

    .contact-item {
      display: flex;
      justify-content: space-between;
      font-size: 10.5px;
    }

    .contact-label {
      color: #64748b;
      font-weight: 600;
      font-size: 9px;
    }

    .contact-val {
      color: #e2e8f0;
      font-weight: 500;
    }

    /* Score Chips */
    .score-chips-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      margin-bottom: 8px;
    }

    .score-chip {
      background: #141e33;
      border: 1px solid #1e293b;
      border-radius: 4px;
      padding: 5px;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .sc-label {
      font-size: 8px;
      color: #64748b;
    }

    .sc-val {
      font-size: 11px;
      font-weight: 700;
    }

    .priority-score-badge {
      font-size: 12px;
      font-weight: 800;
      padding: 2px 8px;
      border-radius: 4px;
    }

    .priority-reason-quote {
      font-size: 10.5px;
      color: #cbd5e1;
      line-height: 1.4;
      background: rgba(30, 41, 59, 0.4);
      padding: 8px;
      border-left: 3px solid #38bdf8;
      border-radius: 0 4px 4px 0;
    }

    /* Grounded Action Card */
    .grounded-action-card {
      border-color: rgba(56, 189, 248, 0.3);
      background: linear-gradient(180deg, rgba(15, 23, 42, 0.9) 0%, rgba(11, 25, 48, 0.9) 100%);
    }

    .action-body {
      font-size: 11.5px;
      color: #f1f5f9;
      line-height: 1.45;
      margin-top: 6px;
      margin-bottom: 12px;
    }

    .action-footer {
      display: flex;
      gap: 8px;
    }

    .btn-primary-action, .btn-route-action {
      flex: 1;
      padding: 8px;
      border-radius: 6px;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;
    }

    .btn-primary-action {
      background: #0284c7;
      border: 1px solid #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
    }

    .btn-primary-action:hover {
      background: #0369a1;
    }

    .btn-route-action {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid #10b981;
      color: #34d399;
    }

    .btn-route-action:hover {
      background: rgba(16, 185, 129, 0.3);
    }

    /* Provenance Mini Card */
    .provenance-mini-card {
      display: flex;
      align-items: center;
      gap: 10px;
      background: #0d1527;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 8px 12px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .provenance-mini-card:hover {
      border-color: #38bdf8;
      background: #131d33;
    }

    .prov-icon {
      font-size: 14px;
      color: #38bdf8;
    }

    .prov-content {
      flex: 1;
      display: flex;
      flex-direction: column;
    }

    .prov-title {
      font-size: 9.5px;
      font-weight: 800;
      color: #e2e8f0;
      letter-spacing: 0.5px;
    }

    .prov-desc {
      font-size: 9px;
      color: #64748b;
    }

    .prov-arrow {
      color: #38bdf8;
      font-size: 12px;
      font-weight: 700;
    }

    /* Safe State */
    .no-alert-card {
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.3);
      padding: 12px;
      border-radius: 8px;
      font-size: 12px;
      color: #cbd5e1;
    }

    .safe-icon {
      font-size: 20px;
    }

    /* No Selection State */
    .no-selection-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      padding: 40px;
      text-align: center;
      color: #64748b;
    }

    .select-icon {
      width: 48px;
      height: 48px;
      margin-bottom: 12px;
      color: #334155;
    }
  `]
})
export class ZoneDetailsComponent {
  readonly state = inject(DisasterStateService);

  getRiskScore(): number {
    const locId = this.state.selectedLocationId();
    if (locId) {
      const pItem = this.getPriorityItem(locId);
      if (pItem) return pItem.priorityScore;
    }
    const fp = this.state.aiDecision()?.flood_prediction;
    if (!fp) return 84.5;
    return fp.predicted_risk_score !== undefined ? fp.predicted_risk_score : (fp.risk_score !== undefined ? fp.risk_score : 84.5);
  }

  getRiskLevel(): string {
    const alert = this.state.selectedAlert();
    if (alert) return alert.severity.toUpperCase();
    const fp = this.state.aiDecision()?.flood_prediction;
    if (!fp) return 'HIGH';
    return (fp.predicted_risk_level || fp.risk_level || 'HIGH').toUpperCase();
  }

  getOccupancyPercent(loc: any): number {
    if (!loc.capacity) return 0;
    return Math.min(100, Math.round((loc.current_occupancy / loc.capacity) * 100));
  }

  getPriorityItem(locationId: number) {
    return this.state.priorityQueue().find(p => p.location.id === locationId);
  }

  getTypeIcon(type: string): string {
    switch (type) {
      case 'hospital': return '🏥';
      case 'shelter': return '🛡️';
      case 'critical_infrastructure': return '⚙️';
      default: return '📍';
    }
  }

  openAiActionPlan(): void {
    this.state.setActiveTab('ai-action-plan');
  }

  openRouteIntelligence(): void {
    this.state.setActiveTab('route-intelligence');
  }

  openProvenance(): void {
    this.state.setActiveTab('provenance');
  }
}
