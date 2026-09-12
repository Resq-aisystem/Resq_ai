import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { RouteOption } from '../../core/models/route.model';

@Component({
  selector: 'app-route-intelligence',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="routing-container">
      <div class="routing-header">
        <div class="header-title-row">
          <span class="pulse-emerald"></span>
          <h2 class="routing-title">EVACUATION ROUTE INTELLIGENCE</h2>
          <span class="engine-badge font-mono">FLOOD-AWARE</span>
        </div>
        <p class="routing-subtitle">
          Real-time route risk evaluation &bull; Flood zone clearance &bull; Inundation avoidance
        </p>

        <!-- Origin & Destination Selector -->
        <div class="od-selector-box">
          <div class="od-row">
            <span class="od-badge badge-origin">ORIGIN</span>
            <span class="od-name">
              {{ state.selectedLocation()?.name || 'No Facility Selected' }}
            </span>
          </div>

          <div class="od-arrow-row">
            <div class="line-connector"></div>
            <span class="arrow-text">&darr; EVACUATING TO SAFE HAVEN &darr;</span>
            <div class="line-connector"></div>
          </div>

          <div class="od-row destination-row">
            <span class="od-badge badge-dest">HAVEN</span>
            <select 
              class="shelter-dropdown" 
              [value]="state.selectedDestination()?.id"
              (change)="onShelterChange($event)"
            >
              @for (shelter of state.availableShelters(); track shelter.id) {
                <option [value]="shelter.id">
                  {{ shelter.name }} ({{ shelter.capacity! - shelter.current_occupancy }} beds open)
                </option>
              }
            </select>
          </div>
        </div>
      </div>

      <!-- Routes Alternatives List -->
      <div class="routes-scrollable">
        <div class="alternatives-heading">
          <span>3 CALCULATED ROUTE ALTERNATIVES</span>
          <span class="click-hint">Click route card to highlight on map</span>
        </div>

        @for (route of state.availableRoutes(); track route.id) {
          <div 
            class="route-card"
            [ngClass]="{
              'route-selected': state.selectedRoute()?.id === route.id,
              'border-safest': route.type === 'safest',
              'border-balanced': route.type === 'balanced',
              'border-fastest': route.type === 'fastest'
            }"
            (click)="selectRoute(route)"
          >
            <!-- Card Header -->
            <div class="route-card-top">
              <div class="type-tag-row">
                <span class="type-pill" [ngClass]="'pill-' + route.type">
                  {{ route.type | uppercase }}
                </span>
                @if (route.recommended) {
                  <span class="recommended-badge font-mono">RECOMMENDED EOC PATH</span>
                }
              </div>

              <div class="risk-badge font-mono" [ngClass]="'badge-' + route.riskLevel">
                {{ route.riskLevel | uppercase }} RISK
              </div>
            </div>

            <h3 class="route-name">{{ route.name }}</h3>
            <p class="route-desc">{{ route.description }}</p>

            <!-- Metrics Matrix -->
            <div class="route-metrics-grid font-mono">
              <div class="r-metric">
                <span class="rm-label">DISTANCE</span>
                <span class="rm-val text-cyan">{{ route.distanceKm }} km</span>
              </div>
              <div class="r-metric">
                <span class="rm-label">EST. TRANSIT</span>
                <span class="rm-val">{{ route.durationMinutes }} mins</span>
              </div>
              <div class="r-metric">
                <span class="rm-label">FLOOD BUFFER</span>
                <span class="rm-val" [ngClass]="route.floodHazardClearanceM > 1000 ? 'text-green' : (route.floodHazardClearanceM > 400 ? 'text-amber' : 'text-critical')">
                  {{ route.floodHazardClearanceM }}m
                </span>
              </div>
            </div>

            <!-- Route Warning & Guidance Notes -->
            <div class="route-warnings">
              <span class="warnings-title">TACTICAL GUIDANCE:</span>
              <ul class="warnings-list">
                @for (note of route.warningNotes; track note) {
                  <li>{{ note }}</li>
                }
              </ul>
            </div>

            <!-- Card Bottom Selection Trigger -->
            <div class="route-card-footer">
              <span class="provenance-note font-mono">{{ route.provenance }}</span>
              <button class="btn-select-route" [ngClass]="{'btn-active': state.selectedRoute()?.id === route.id}">
                {{ state.selectedRoute()?.id === route.id ? 'ACTIVE ON MAP' : 'SELECT PATH' }}
              </button>
            </div>
          </div>
        }

        @if (state.availableRoutes().length === 0) {
          <div class="no-routes-state">
            <p>Please select an affected facility and an active shelter to calculate evacuation routes.</p>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .routing-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
    }

    .routing-header {
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

    .pulse-emerald {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }

    .routing-title {
      font-size: 13px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: 0.8px;
    }

    .engine-badge {
      font-size: 9px;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 700;
    }

    .routing-subtitle {
      font-size: 10px;
      color: #64748b;
      margin-bottom: 10px;
    }

    /* O/D Selector */
    .od-selector-box {
      background: #141e33;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 8px 10px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .od-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .od-badge {
      font-size: 8.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      letter-spacing: 0.5px;
      flex-shrink: 0;
    }

    .badge-origin {
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .badge-dest {
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .od-name {
      font-size: 11.5px;
      font-weight: 700;
      color: #f1f5f9;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .od-arrow-row {
      display: flex;
      align-items: center;
      gap: 6px;
      margin: 1px 0;
    }

    .line-connector {
      flex: 1;
      height: 1px;
      background: #334155;
    }

    .arrow-text {
      font-size: 8px;
      color: #64748b;
      font-weight: 700;
      letter-spacing: 0.5px;
    }

    .shelter-dropdown {
      flex: 1;
      background: #0f172a;
      color: #f8fafc;
      border: 1px solid #334155;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      padding: 3px 6px;
      outline: none;
    }

    .shelter-dropdown:focus {
      border-color: #38bdf8;
    }

    /* Routes Scrollable */
    .routes-scrollable {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .alternatives-heading {
      display: flex;
      justify-content: space-between;
      font-size: 9.5px;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.5px;
    }

    .click-hint {
      color: #64748b;
      font-weight: 400;
    }

    .route-card {
      background: linear-gradient(180deg, #0f172a 0%, #0c1220 100%);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .route-card:hover {
      background: #131c31;
      border-color: #38bdf8;
      transform: translateY(-1px);
    }

    .route-selected {
      border-color: #38bdf8 !important;
      background: #121e36 !important;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.2) !important;
    }

    .border-safest { border-left: 4px solid #10b981; }
    .border-balanced { border-left: 4px solid #f59e0b; }
    .border-fastest { border-left: 4px solid #06b6d4; }

    .route-card-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .type-tag-row {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .type-pill {
      font-size: 8.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 3px;
      letter-spacing: 0.5px;
    }

    .pill-safest { background: #065f46; color: #34d399; }
    .pill-balanced { background: #78350f; color: #fbbf24; }
    .pill-fastest { background: #155e75; color: #38bdf8; }

    .recommended-badge {
      font-size: 8px;
      background: rgba(16, 185, 129, 0.2);
      color: #34d399;
      border: 1px solid #10b981;
      padding: 1px 5px;
      border-radius: 3px;
      font-weight: 700;
    }

    .route-name {
      font-size: 13px;
      font-weight: 700;
      color: #f8fafc;
    }

    .route-desc {
      font-size: 11px;
      color: #94a3b8;
      line-height: 1.35;
    }

    .route-metrics-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid #1e293b;
      padding: 6px 8px;
      border-radius: 6px;
    }

    .r-metric {
      display: flex;
      flex-direction: column;
    }

    .rm-label {
      font-size: 8px;
      color: #64748b;
      font-weight: 600;
    }

    .rm-val {
      font-size: 12px;
      font-weight: 700;
      color: #f1f5f9;
    }

    .text-cyan { color: #38bdf8; }
    .text-green { color: #34d399; }
    .text-amber { color: #fbbf24; }
    .text-critical { color: #f87171; }

    .route-warnings {
      background: rgba(30, 41, 59, 0.35);
      border-radius: 4px;
      padding: 6px 8px;
      font-size: 10px;
    }

    .warnings-title {
      font-size: 8.5px;
      font-weight: 700;
      color: #cbd5e1;
      display: block;
      margin-bottom: 2px;
    }

    .warnings-list {
      list-style-type: square;
      padding-left: 14px;
      color: #94a3b8;
      line-height: 1.35;
    }

    .route-card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid rgba(51, 65, 85, 0.4);
      padding-top: 6px;
    }

    .provenance-note {
      font-size: 8px;
      color: #64748b;
      max-width: 65%;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .btn-select-route {
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
      font-size: 9px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-select-route.btn-active {
      background: #0284c7;
      border-color: #38bdf8;
      color: #ffffff;
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.4);
    }

    .no-routes-state {
      padding: 40px 20px;
      text-align: center;
      color: #64748b;
      font-size: 12px;
    }
  `]
})
export class RouteIntelligenceComponent {
  readonly state = inject(DisasterStateService);

  onShelterChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    if (target && target.value) {
      this.state.selectDestination(+target.value);
    }
  }

  selectRoute(route: RouteOption): void {
    this.state.selectRoute(route);
  }
}
