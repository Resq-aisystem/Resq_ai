import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { CommandCenterHeaderComponent } from '../header/command-center-header.component';
import { KpiSummaryCardsComponent } from '../kpi/kpi-summary-cards.component';
import { PriorityQueueComponent } from '../priority-queue/priority-queue.component';
import { InteractiveMapComponent } from '../map/interactive-map.component';
import { ZoneDetailsComponent } from '../zone-details/zone-details.component';
import { RouteIntelligenceComponent } from '../routing/route-intelligence.component';
import { AiActionPlanComponent } from '../action-plan/ai-action-plan.component';
import { WhatIfScenarioComponent } from '../what-if/what-if-scenario.component';
import { ProvenancePanelComponent } from '../provenance/provenance-panel.component';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    CommandCenterHeaderComponent,
    KpiSummaryCardsComponent,
    PriorityQueueComponent,
    InteractiveMapComponent,
    ZoneDetailsComponent,
    RouteIntelligenceComponent,
    AiActionPlanComponent,
    WhatIfScenarioComponent,
    ProvenancePanelComponent
  ],
  template: `
    <div class="dashboard-root">
      <!-- 1. Master Header -->
      <app-command-center-header></app-command-center-header>

      <!-- 2. KPI HUD Summary Bar -->
      <app-kpi-summary-cards></app-kpi-summary-cards>

      <!-- 3. Tri-Pane Emergency Operations Workspace -->
      <main class="eoc-workspace">
        <!-- Left Pane: Emergency Priority Queue -->
        <section class="pane-left">
          <app-priority-queue></app-priority-queue>
        </section>

        <!-- Center Pane: Interactive Leaflet Geospatial Risk Map -->
        <section class="pane-center">
          <app-interactive-map></app-interactive-map>
        </section>

        <!-- Right Pane: Multi-Tab Intelligence Drawer -->
        <section class="pane-right">
          <!-- Navigation Tabs Bar -->
          <nav class="intel-tabs-bar">
            <button 
              class="tab-btn" 
              [ngClass]="{'tab-active': state.activeTab() === 'zone-details'}"
              (click)="setTab('zone-details')"
            >
              <span class="tab-icon">📍</span>
              <span class="tab-text">ZONE DETAILS</span>
            </button>

            <button 
              class="tab-btn" 
              [ngClass]="{'tab-active': state.activeTab() === 'route-intelligence'}"
              (click)="setTab('route-intelligence')"
            >
              <span class="tab-icon">🛣️</span>
              <span class="tab-text">ROUTE INTEL</span>
            </button>

            <button 
              class="tab-btn" 
              [ngClass]="{'tab-active': state.activeTab() === 'ai-action-plan'}"
              (click)="setTab('ai-action-plan')"
            >
              <span class="tab-icon">🤖</span>
              <span class="tab-text">AI ACTION PLAN</span>
            </button>

            <button 
              class="tab-btn" 
              [ngClass]="{'tab-active': state.activeTab() === 'what-if'}"
              (click)="setTab('what-if')"
            >
              <span class="tab-icon">⚡</span>
              <span class="tab-text">WHAT-IF</span>
              @if (state.isSimulationActive()) {
                <span class="tab-dot"></span>
              }
            </button>

            <button 
              class="tab-btn" 
              [ngClass]="{'tab-active': state.activeTab() === 'provenance'}"
              (click)="setTab('provenance')"
            >
              <span class="tab-icon">🛡️</span>
              <span class="tab-text">PROVENANCE</span>
            </button>
          </nav>

          <!-- Tab Content Display -->
          <div class="intel-content-area">
            @switch (state.activeTab()) {
              @case ('zone-details') {
                <app-zone-details></app-zone-details>
              }
              @case ('route-intelligence') {
                <app-route-intelligence></app-route-intelligence>
              }
              @case ('ai-action-plan') {
                <app-ai-action-plan></app-ai-action-plan>
              }
              @case ('what-if') {
                <app-what-if-scenario></app-what-if-scenario>
              }
              @case ('provenance') {
                <app-provenance-panel></app-provenance-panel>
              }
            }
          </div>
        </section>
      </main>
    </div>
  `,
  styles: [`
    .dashboard-root {
      display: flex;
      flex-direction: column;
      height: 100vh;
      width: 100vw;
      background: #070b14;
      overflow: hidden;
    }

    .eoc-workspace {
      display: flex;
      flex: 1;
      height: calc(100vh - 128px);
      width: 100%;
      overflow: hidden;
    }

    /* Left Pane: Priority Queue */
    .pane-left {
      width: 380px;
      min-width: 320px;
      max-width: 420px;
      height: 100%;
      background: #090e1a;
      flex-shrink: 0;
    }

    /* Center Pane: Map */
    .pane-center {
      flex: 1;
      height: 100%;
      position: relative;
      background: #0b1120;
    }

    /* Right Pane: Intelligence Drawer */
    .pane-right {
      width: 450px;
      min-width: 380px;
      max-width: 500px;
      height: 100%;
      background: #0b1120;
      border-left: 1px solid #1e293b;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }

    /* Tabs Bar */
    .intel-tabs-bar {
      display: flex;
      background: #0d1527;
      border-bottom: 1px solid #1e293b;
      padding: 0 4px;
      height: 40px;
      overflow-x: auto;
    }

    .tab-btn {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: #94a3b8;
      font-size: 9.5px;
      font-weight: 700;
      letter-spacing: 0.5px;
      cursor: pointer;
      padding: 0 8px;
      white-space: nowrap;
      transition: all 0.2s;
    }

    .tab-btn:hover {
      color: #f8fafc;
      background: rgba(30, 41, 59, 0.4);
    }

    .tab-active {
      color: #38bdf8 !important;
      border-bottom-color: #38bdf8 !important;
      background: rgba(56, 189, 248, 0.08) !important;
    }

    .tab-icon {
      font-size: 12px;
    }

    .tab-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #f59e0b;
      box-shadow: 0 0 6px #f59e0b;
    }

    .intel-content-area {
      flex: 1;
      overflow: hidden;
    }
  `]
})
export class DashboardComponent implements OnInit {
  readonly state = inject(DisasterStateService);

  ngOnInit(): void {
    this.state.loadAllData();
  }

  setTab(tab: 'zone-details' | 'route-intelligence' | 'ai-action-plan' | 'what-if' | 'provenance'): void {
    this.state.setActiveTab(tab);
  }
}
