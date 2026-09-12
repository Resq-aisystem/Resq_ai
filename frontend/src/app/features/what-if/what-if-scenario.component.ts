import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { AlertService } from '../../core/services/alert.service';

@Component({
  selector: 'app-what-if-scenario',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="scenario-container">
      <!-- Watermark Banner -->
      <div class="simulation-watermark-banner">
        &#9888; SCENARIO — NOT LIVE OBSERVATION &bull; STRESS TESTING SIMULATION ENGINE
      </div>

      <div class="scenario-header">
        <div class="header-title-row">
          <span class="sim-icon">⚡</span>
          <h2 class="scenario-title">WHAT-IF SCENARIO STRESS TEST</h2>
          <span class="mode-badge font-mono" [ngClass]="{'active': state.isSimulationActive()}">
            {{ state.isSimulationActive() ? 'SIMULATION ENGAGED' : 'BASELINE STANDBY' }}
          </span>
        </div>
        <p class="scenario-subtitle">
          Test secondary stormbursts, 2x rainfall surges, or flood barrier breaches to observe priority shifts
        </p>

        <!-- Scenario Parameter Controls -->
        <div class="controls-panel">
          <!-- 1. Rainfall Surge Slider -->
          <div class="control-row">
            <div class="control-label-row">
              <span class="control-name">RAINFALL SURGE INTENSITY:</span>
              <span class="control-val font-mono text-cyan">+{{ state.scenarioParams().rainfallSurgeMm }} mm/hr</span>
            </div>
            <input 
              type="range" 
              class="slider" 
              min="0" 
              max="150" 
              step="25"
              [ngModel]="state.scenarioParams().rainfallSurgeMm"
              (ngModelChange)="onRainfallChange($event)"
            />
            <div class="slider-marks font-mono">
              <span>0mm</span>
              <span>+25mm</span>
              <span>+50mm</span>
              <span>+100mm (2x)</span>
              <span>+150mm (Catastrophic)</span>
            </div>
          </div>

          <!-- 2. Direct Water Level Delta -->
          <div class="control-row">
            <div class="control-label-row">
              <span class="control-name">PROJECTED WATER RISE (&Delta;):</span>
              <span class="control-val font-mono text-high">+{{ state.scenarioParams().waterLevelDeltaM }} m</span>
            </div>
            <input 
              type="range" 
              class="slider" 
              min="0" 
              max="2.0" 
              step="0.2"
              [ngModel]="state.scenarioParams().waterLevelDeltaM"
              (ngModelChange)="onWaterDeltaChange($event)"
            />
          </div>

          <!-- 3. Infrastructure Failure Toggles -->
          <div class="toggles-row">
            <label class="toggle-checkbox">
              <input 
                type="checkbox" 
                [ngModel]="state.scenarioParams().floodBarrierFailure"
                (ngModelChange)="onBarrierToggle($event)"
              />
              <span>SIMULATE TOWN LAKE FLOODWALL BREACH (+0.6m)</span>
            </label>
          </div>

          <!-- Buttons -->
          <div class="button-bar">
            <button class="btn-reset" (click)="resetScenario()">
              RESET TO LIVE BASELINE
            </button>
            <button class="btn-quick-2x" (click)="applyDoubleRainfall()">
              APPLY 2X RAINFALL SURGE
            </button>
          </div>
        </div>
      </div>

      <!-- Before vs After Impact Delta Table -->
      <div class="scenario-scrollable">
        <div class="impact-summary-cards">
          <div class="impact-card">
            <span class="ic-label">CRITICAL ZONES</span>
            <div class="ic-delta font-mono text-critical">
              +{{ state.scenarioImpact().criticalZonesDelta }}
            </div>
            <span class="ic-sub">New high-danger zones</span>
          </div>

          <div class="impact-card">
            <span class="ic-label">HIGH-RISK ZONES</span>
            <div class="ic-delta font-mono text-high">
              +{{ state.scenarioImpact().highRiskZonesDelta }}
            </div>
            <span class="ic-sub">Threshold transitions</span>
          </div>

          <div class="impact-card">
            <span class="ic-label">EXPOSED POPULATION</span>
            <div class="ic-delta font-mono text-cyan">
              +{{ state.scenarioImpact().affectedPopulationDelta.toLocaleString() }}
            </div>
            <span class="ic-sub">Additional residents at risk</span>
          </div>
        </div>

        <!-- Shift Table -->
        <div class="shifts-table-container">
          <h3 class="table-heading">
            <span>FACILITY SEVERITY &amp; WATER STAGE SHIFTS</span>
            <span class="table-tag font-mono">BEFORE &rarr; AFTER SIMULATION</span>
          </h3>

          <table class="shifts-table">
            <thead>
              <tr>
                <th>FACILITY</th>
                <th>PREV STAGE</th>
                <th>SIMULATED</th>
                <th>SEVERITY SHIFT</th>
              </tr>
            </thead>
            <tbody>
              @for (shift of state.scenarioImpact().priorityShifts; track shift.locationId) {
                <tr [ngClass]="{'row-escalated': shift.simulatedSeverity === 'critical'}">
                  <td class="cell-facility">
                    <span class="fac-name">{{ shift.locationName }}</span>
                  </td>
                  <td class="font-mono text-muted">{{ shift.previousWaterLevel }}m</td>
                  <td class="font-mono" [ngClass]="shift.simulatedWaterLevel > shift.previousWaterLevel ? 'text-critical' : ''">
                    {{ shift.simulatedWaterLevel }}m 
                    @if (shift.simulatedWaterLevel > shift.previousWaterLevel) {
                      <span class="up-arrow">&uarr;</span>
                    }
                  </td>
                  <td>
                    <span class="badge-shift font-mono" [ngClass]="'shift-' + shift.simulatedSeverity">
                      {{ shift.previousSeverity | uppercase }} &rarr; {{ shift.simulatedSeverity | uppercase }}
                    </span>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .scenario-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
    }

    .scenario-header {
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

    .sim-icon {
      font-size: 16px;
      color: #f59e0b;
    }

    .scenario-title {
      font-size: 13px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: 0.8px;
    }

    .mode-badge {
      font-size: 8.5px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 800;
      background: #1e293b;
      color: #64748b;
      border: 1px solid #334155;
    }

    .mode-badge.active {
      background: rgba(245, 158, 11, 0.2);
      color: #fbbf24;
      border-color: #f59e0b;
      box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
    }

    .scenario-subtitle {
      font-size: 10px;
      color: #64748b;
      margin-bottom: 10px;
    }

    .controls-panel {
      background: #141e33;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .control-row {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .control-label-row {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      font-weight: 700;
    }

    .control-name {
      color: #94a3b8;
    }

    .slider {
      width: 100%;
      accent-color: #38bdf8;
      cursor: pointer;
    }

    .slider-marks {
      display: flex;
      justify-content: space-between;
      font-size: 8px;
      color: #64748b;
    }

    .toggles-row {
      font-size: 10.5px;
      color: #e2e8f0;
    }

    .toggle-checkbox {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
    }

    .button-bar {
      display: flex;
      gap: 8px;
      margin-top: 4px;
    }

    .btn-reset, .btn-quick-2x {
      flex: 1;
      padding: 7px;
      border-radius: 5px;
      font-size: 10px;
      font-weight: 800;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-reset {
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
    }

    .btn-reset:hover {
      background: #334155;
      color: #ffffff;
    }

    .btn-quick-2x {
      background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
      border: 1px solid #f59e0b;
      color: #ffffff;
      box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
    }

    .btn-quick-2x:hover {
      background: #f59e0b;
    }

    /* Scrollable Results */
    .scenario-scrollable {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .impact-summary-cards {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
    }

    .impact-card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 8px;
      display: flex;
      flex-direction: column;
    }

    .ic-label {
      font-size: 8px;
      color: #64748b;
      font-weight: 700;
    }

    .ic-delta {
      font-size: 20px;
      font-weight: 800;
      line-height: 1.2;
    }

    .ic-sub {
      font-size: 8.5px;
      color: #94a3b8;
    }

    .shifts-table-container {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 10px;
    }

    .table-heading {
      display: flex;
      justify-content: space-between;
      font-size: 9.5px;
      font-weight: 800;
      color: #94a3b8;
      letter-spacing: 0.6px;
      margin-bottom: 8px;
    }

    .table-tag {
      font-size: 8.5px;
      color: #64748b;
    }

    .shifts-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11px;
    }

    .shifts-table th {
      text-align: left;
      font-size: 8.5px;
      color: #64748b;
      padding: 4px 6px;
      border-bottom: 1px solid #1e293b;
      font-weight: 700;
    }

    .shifts-table td {
      padding: 6px;
      border-bottom: 1px solid rgba(30, 41, 59, 0.5);
    }

    .row-escalated {
      background: rgba(239, 68, 68, 0.08);
    }

    .fac-name {
      font-weight: 700;
      color: #f1f5f9;
    }

    .up-arrow {
      color: #ef4444;
      font-weight: 800;
    }

    .badge-shift {
      font-size: 9px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 3px;
    }

    .shift-critical {
      background: rgba(239, 68, 68, 0.2);
      color: #ef4444;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .shift-high {
      background: rgba(249, 115, 22, 0.2);
      color: #f97316;
    }

    .shift-medium {
      background: rgba(234, 179, 8, 0.2);
      color: #eab308;
    }

    .shift-low {
      background: rgba(16, 185, 129, 0.2);
      color: #10b981;
    }

    .text-critical { color: #ef4444; }
    .text-high { color: #f97316; }
    .text-cyan { color: #38bdf8; }
    .text-muted { color: #64748b; }
  `]
})
export class WhatIfScenarioComponent {
  readonly state = inject(DisasterStateService);
  private alertService = inject(AlertService);

  onRainfallChange(val: number): void {
    // Map rainfall mm surge to approx water level increase
    const waterRise = +(val * 0.012).toFixed(2);
    this.state.setScenarioParams({
      rainfallSurgeMm: val,
      waterLevelDeltaM: waterRise
    });
  }

  onWaterDeltaChange(val: number): void {
    const rainfall = Math.round(val / 0.012);
    this.state.setScenarioParams({
      waterLevelDeltaM: val,
      rainfallSurgeMm: rainfall
    });
  }

  onBarrierToggle(val: boolean): void {
    this.state.setScenarioParams({
      floodBarrierFailure: val
    });
  }

  applyDoubleRainfall(): void {
    this.state.setScenarioParams({
      rainfallSurgeMm: 100,
      waterLevelDeltaM: 1.2,
      floodBarrierFailure: true
    });
  }

  resetScenario(): void {
    this.state.resetSimulation();
  }
}
