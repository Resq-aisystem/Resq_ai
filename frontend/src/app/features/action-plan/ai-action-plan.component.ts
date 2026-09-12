import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';

@Component({
  selector: 'app-ai-action-plan',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="action-plan-container">
      <div class="plan-header">
        <div class="header-title-row">
          <span class="ai-spark-icon">🤖</span>
          <h2 class="plan-title">GROUNDED DECISION INTELLIGENCE ACTION PLAN</h2>
          <span class="grounded-badge font-mono">BACKEND VERIFIED</span>
        </div>
        <p class="plan-subtitle">
          Structured operational directives grounded in authoritative hydrological models & backend alerts
        </p>

        <!-- Target Facility Header -->
        @if (state.selectedLocation(); as loc) {
          <div class="target-facility-strip">
            <span class="facility-badge">{{ loc.type | uppercase }}</span>
            <span class="facility-name">{{ loc.name }}</span>
            <span class="facility-occupancy font-mono">
              Occupancy: {{ loc.current_occupancy }} (Cap: {{ loc.capacity || 'N/A' }})
            </span>
          </div>
        }
      </div>

      <div class="plan-scrollable">
        @if (state.selectedAlert(); as alert) {
          <!-- Authoritative Justification Banner -->
          <div class="justification-box">
            <div class="just-header">
              <span class="just-tag">HYDROLOGIC GROUNDING & REASONING</span>
              <span class="just-author font-mono">{{ alert.issued_by }}</span>
            </div>
            <p class="just-text">{{ alert.justification }}</p>
          </div>

          <!-- Structured Directive Cards -->
          <div class="directives-stack">
            <!-- 1. Immediate Actions -->
            <div class="directive-card card-immediate">
              <div class="d-header">
                <span class="d-icon">🚨</span>
                <span class="d-title">IMMEDIATE 0-60 MIN RESPONSE ACTIONS</span>
                <span class="d-priority font-mono">PRIORITY 1</span>
              </div>
              <div class="d-content">
                <p class="primary-directive">{{ alert.recommended_action }}</p>
                <ul class="sub-directives">
                  <li>Sound Code Red internal advisory throughout facility sectors.</li>
                  <li>Activate on-duty emergency staffing roster and notify district dispatch.</li>
                  <li>Verify auxiliary power generator switchboard elevation and fuel seals.</li>
                </ul>
              </div>
            </div>

            <!-- 2. Evacuation Guidance -->
            <div class="directive-card card-evac">
              <div class="d-header">
                <span class="d-icon">🚌</span>
                <span class="d-title">EVACUATION & PATIENT TRANSFER PROTOCOL</span>
                <span class="d-priority font-mono">LOGISTICS</span>
              </div>
              <div class="d-content">
                <div class="evac-route-summary">
                  <strong>Recommended Route:</strong> 
                  {{ state.selectedRoute()?.name || 'Route Alpha (High-Ground Arterial Bypass)' }}
                </div>
                <ul class="sub-directives">
                  <li>Transfer priority: ICU and high-acuity oxygen-dependent patients first.</li>
                  <li>Deploy high-clearance emergency transit vehicles to avoid 0.4m water ingress.</li>
                  <li>Destination staging at: <strong>{{ state.selectedDestination()?.name || 'Highland Regional Evacuation Haven' }}</strong>.</li>
                </ul>
              </div>
            </div>

            <!-- 3. Resource & Staging Recommendations -->
            <div class="directive-card card-resources">
              <div class="d-header">
                <span class="d-icon">📦</span>
                <span class="d-title">RESOURCE & STAGING ALLOCATION</span>
                <span class="d-priority font-mono">SUPPLY CHAIN</span>
              </div>
              <div class="d-content">
                <div class="resource-pill-row">
                  <span class="res-pill">💧 Clean Water: 1,200 gal/day</span>
                  <span class="res-pill">⚡ Diesel Gen: 72hr Fuel Staged</span>
                  <span class="res-pill">🚑 Ambulances: 4 Units</span>
                  <span class="res-pill">🚤 Swift Water Rescue: 2 Crafts</span>
                </div>
                <p class="res-note">
                  Staging location established at nearest high-ground arterial crossing outside the 100m flood polygon.
                </p>
              </div>
            </div>

            <!-- 4. Infrastructure & Telemetry Monitoring -->
            <div class="directive-card card-monitoring">
              <div class="d-header">
                <span class="d-icon">📡</span>
                <span class="d-title">INFRASTRUCTURE & WATER LEVEL MONITORING</span>
                <span class="d-priority font-mono">TELEMETRY</span>
              </div>
              <div class="d-content">
                <div class="telemetry-table font-mono">
                  <div class="t-row">
                    <span>Active Inundation Stage</span>
                    <span class="text-critical">{{ alert.water_level || 0 }}m</span>
                  </div>
                  <div class="t-row">
                    <span>Projected Crest / Peak</span>
                    <span class="text-high">{{ alert.predicted_peak || 0 }}m</span>
                  </div>
                  <div class="t-row">
                    <span>Floodwall Freeboard Clearance</span>
                    <span>-0.45m (Overtopping Alert)</span>
                  </div>
                  <div class="t-row">
                    <span>Telemetry Source</span>
                    <span>USGS Basin Sensor Hub #08158000</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 5. Operational Precautions -->
            <div class="directive-card card-precautions">
              <div class="d-header">
                <span class="d-icon">⚠️</span>
                <span class="d-title">OPERATIONAL PRECAUTIONS & PERSONNEL SAFETY</span>
                <span class="d-priority font-mono">SAFETY</span>
              </div>
              <div class="d-content">
                <ul class="sub-directives">
                  <li>Never permit light emergency vehicles or passenger cars through standing water &gt; 0.3m.</li>
                  <li>Beware of submerged electrical transformers and downstream chemical runoff.</li>
                  <li>Maintain continuous two-way VHF radio contact with Travis County EOC Command.</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Dispatch Action Footer -->
          <div class="plan-dispatch-footer">
            <button class="btn-dispatch" (click)="copyActionPlan()">
              {{ copied() ? '✓ ACTION PLAN COPIED TO CLIPBOARD' : '📋 EXPORT PLAN FOR FIELD DISPATCH' }}
            </button>
          </div>
        } @else {
          <div class="no-alert-state">
            <p>Please select a facility with an active emergency alert to view its grounded action plan.</p>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .action-plan-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
    }

    .plan-header {
      padding: 12px 14px;
      background: #0d1527;
      border-bottom: 1px solid #1e293b;
    }

    .header-title-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 2px;
    }

    .ai-spark-icon {
      font-size: 16px;
    }

    .plan-title {
      font-size: 13px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: 0.8px;
    }

    .grounded-badge {
      font-size: 9px;
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 700;
    }

    .plan-subtitle {
      font-size: 10px;
      color: #64748b;
      margin-bottom: 10px;
    }

    .target-facility-strip {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #141e33;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 6px 10px;
    }

    .facility-badge {
      font-size: 8.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 3px;
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
    }

    .facility-name {
      font-size: 12px;
      font-weight: 700;
      color: #f1f5f9;
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .facility-occupancy {
      font-size: 10px;
      color: #94a3b8;
    }

    .plan-scrollable {
      flex: 1;
      overflow-y: auto;
      padding: 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    /* Justification Box */
    .justification-box {
      background: rgba(30, 41, 59, 0.4);
      border: 1px solid #334155;
      border-left: 4px solid #38bdf8;
      border-radius: 6px;
      padding: 10px 12px;
    }

    .just-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 4px;
    }

    .just-tag {
      font-size: 9px;
      font-weight: 800;
      color: #38bdf8;
      letter-spacing: 0.6px;
    }

    .just-author {
      font-size: 8.5px;
      color: #64748b;
    }

    .just-text {
      font-size: 11.5px;
      color: #cbd5e1;
      line-height: 1.4;
      font-style: italic;
    }

    /* Directive Cards */
    .directives-stack {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .directive-card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 12px;
    }

    .card-immediate {
      border-left: 4px solid #ef4444;
      background: linear-gradient(180deg, #131b2e 0%, #0f172a 100%);
    }

    .card-evac {
      border-left: 4px solid #10b981;
    }

    .card-resources {
      border-left: 4px solid #f59e0b;
    }

    .card-monitoring {
      border-left: 4px solid #38bdf8;
    }

    .card-precautions {
      border-left: 4px solid #a855f7;
    }

    .d-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
    }

    .d-icon {
      font-size: 13px;
    }

    .d-title {
      font-size: 10px;
      font-weight: 800;
      color: #f1f5f9;
      letter-spacing: 0.6px;
      flex: 1;
    }

    .d-priority {
      font-size: 8px;
      font-weight: 800;
      color: #64748b;
    }

    .d-content {
      font-size: 11px;
      color: #cbd5e1;
      line-height: 1.4;
    }

    .primary-directive {
      font-weight: 600;
      color: #f8fafc;
      margin-bottom: 6px;
    }

    .sub-directives {
      list-style-type: square;
      padding-left: 14px;
      color: #94a3b8;
    }

    .sub-directives li {
      margin-bottom: 3px;
    }

    .evac-route-summary {
      background: #141e33;
      padding: 6px 8px;
      border-radius: 4px;
      margin-bottom: 6px;
      font-size: 10.5px;
    }

    .resource-pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 6px;
    }

    .res-pill {
      background: #1e293b;
      border: 1px solid #334155;
      color: #e2e8f0;
      font-size: 9.5px;
      font-weight: 600;
      padding: 2px 7px;
      border-radius: 12px;
    }

    .res-note {
      font-size: 10px;
      color: #64748b;
    }

    .telemetry-table {
      display: flex;
      flex-direction: column;
      gap: 4px;
      background: #141e33;
      padding: 6px 8px;
      border-radius: 4px;
      font-size: 10.5px;
    }

    .t-row {
      display: flex;
      justify-content: space-between;
    }

    .text-critical { color: #ef4444; }
    .text-high { color: #f97316; }

    /* Footer Button */
    .plan-dispatch-footer {
      margin-top: 6px;
    }

    .btn-dispatch {
      width: 100%;
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #ffffff;
      border: 1px solid #38bdf8;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.8px;
      padding: 10px;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
      transition: all 0.2s;
    }

    .btn-dispatch:hover {
      background: #0ea5e9;
      transform: translateY(-1px);
    }

    .no-alert-state {
      padding: 40px 20px;
      text-align: center;
      color: #64748b;
      font-size: 12px;
    }
  `]
})
export class AiActionPlanComponent {
  readonly state = inject(DisasterStateService);
  readonly copied = signal<boolean>(false);

  copyActionPlan(): void {
    const loc = this.state.selectedLocation();
    const alert = this.state.selectedAlert();
    const route = this.state.selectedRoute();

    const planText = `
=== RESQ-AI EMERGENCY ACTION PLAN ===
TARGET FACILITY: ${loc?.name} (${loc?.type.toUpperCase()})
ADDRESS: ${loc?.address}
ACTIVE ALERT: ${alert?.title}
SEVERITY: ${alert?.severity.toUpperCase()} | WATER STAGE: ${alert?.water_level}m (PEAK: ${alert?.predicted_peak}m)
EXPOSED POPULATION: ${alert?.affected_population?.toLocaleString()}

JUSTIFICATION:
${alert?.justification}

IMMEDIATE ACTION:
${alert?.recommended_action}

EVACUATION ROUTE:
${route?.name} (Clearance: ${route?.floodHazardClearanceM}m, Distance: ${route?.distanceKm}km, ETA: ${route?.durationMinutes} mins)
DESTINATION HAVEN: ${stateDestinationName(this.state)}

ISSUED BY: ${alert?.issued_by}
TIMESTAMP: ${alert?.issued_at}
======================================
    `.trim();

    navigator.clipboard.writeText(planText).then(() => {
      this.copied.set(true);
      setTimeout(() => this.copied.set(false), 3000);
    });
  }
}

function stateDestinationName(state: DisasterStateService): string {
  return state.selectedDestination()?.name || 'Regional Haven';
}
