import { Component, inject, OnInit, OnDestroy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { HealthService } from '../../core/services/health.service';
import { Subscription, interval } from 'rxjs';

@Component({
  selector: 'app-command-center-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="header-container">
      <div class="brand-section">
        <div class="logo-badge">
          <svg class="shield-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            <path d="M12 8v4" stroke-linecap="round"/>
            <path d="M12 16h.01" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="brand-titles">
          <div class="brand-name">
            <span class="brand-resq">RESQ</span><span class="brand-ai">-AI</span>
            <span class="eoc-badge">DEFCON-2 ACTIVE</span>
          </div>
          <div class="brand-subtitle">FLOOD EMERGENCY DECISION INTELLIGENCE COMMAND CENTER</div>
        </div>
      </div>

      <!-- Center: Event Status Banner -->
      <div class="incident-status-pill">
        <div class="pulse-dot"></div>
        <div class="incident-info">
          <span class="incident-label">REGIONAL FLASH FLOOD INCIDENT:</span>
          <span class="incident-basin">COLORADO RIVER & RED RIVER TRIBUTARY BASIN</span>
        </div>
        <span class="incident-window">6-HR PREDICTIVE WINDOW</span>
      </div>

      <!-- Right: Telemetry, Clock & Backend Health -->
      <div class="controls-section">
        <!-- Live UTC Clock -->
        <div class="clock-display">
          <span class="clock-label">EOC LOCAL TIME</span>
          <span class="clock-value font-mono">{{ currentTime() }}</span>
        </div>

        <!-- Backend Health Indicator -->
        <div class="health-indicator" [ngClass]="{'health-online': isBackendOnline(), 'health-offline': !isBackendOnline()}">
          <span class="status-dot"></span>
          <div class="health-meta">
            <span class="health-status">{{ isBackendOnline() ? 'API OPERATIONAL' : 'API DISCONNECTED' }}</span>
            <span class="health-port font-mono">PORT 8000</span>
          </div>
        </div>

        <!-- Actions -->
        <button class="btn-refresh" (click)="refreshData()" [disabled]="state.loading()" title="Reload live data from backend">
          <svg class="icon-svg" [ngClass]="{'spinning': state.loading()}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
          </svg>
          <span>SYNC</span>
        </button>

        <button 
          class="btn-simulation" 
          [ngClass]="{'active': state.isSimulationActive()}" 
          (click)="toggleSimulationTab()"
          title="Toggle What-If Scenario Simulation Mode"
        >
          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M2 12h5l3 8 4-16 3 8h5"/>
          </svg>
          <span>{{ state.isSimulationActive() ? 'WHAT-IF ACTIVE' : 'WHAT-IF SIM' }}</span>
        </button>
      </div>
    </header>
  `,
  styles: [`
    .header-container {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: linear-gradient(180deg, #0b1329 0%, #080d1c 100%);
      border-bottom: 1px solid #1e293b;
      padding: 8px 18px;
      height: 60px;
      user-select: none;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
      z-index: 100;
    }

    .brand-section {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(3, 105, 161, 0.4) 100%);
      border: 1px solid rgba(56, 189, 248, 0.5);
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
    }

    .shield-icon {
      width: 22px;
      height: 22px;
      color: #38bdf8;
    }

    .brand-titles {
      display: flex;
      flex-direction: column;
    }

    .brand-name {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 800;
      letter-spacing: 0.5px;
      font-size: 19px;
      line-height: 1.2;
    }

    .brand-resq {
      color: #ffffff;
    }

    .brand-ai {
      color: #38bdf8;
      text-shadow: 0 0 12px rgba(56, 189, 248, 0.6);
    }

    .eoc-badge {
      font-size: 10px;
      font-weight: 700;
      color: #ef4444;
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid rgba(239, 68, 68, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      letter-spacing: 0.8px;
      animation: pulse-critical 2.5s infinite;
    }

    .brand-subtitle {
      font-size: 9.5px;
      color: #64748b;
      letter-spacing: 1px;
      font-weight: 600;
    }

    /* Incident Status Pill */
    .incident-status-pill {
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid #334155;
      padding: 6px 14px;
      border-radius: 30px;
    }

    .pulse-dot {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #f97316;
      box-shadow: 0 0 8px #f97316;
      animation: pulse-critical 1.8s infinite;
    }

    .incident-info {
      font-size: 12px;
      display: flex;
      gap: 6px;
    }

    .incident-label {
      color: #94a3b8;
      font-weight: 600;
    }

    .incident-basin {
      color: #f8fafc;
      font-weight: 700;
    }

    .incident-window {
      font-size: 10px;
      background: rgba(249, 115, 22, 0.2);
      color: #fb923c;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 700;
      border: 1px solid rgba(249, 115, 22, 0.4);
    }

    /* Controls & Health */
    .controls-section {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .clock-display {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
    }

    .clock-label {
      font-size: 8.5px;
      color: #64748b;
      letter-spacing: 0.8px;
      font-weight: 600;
    }

    .clock-value {
      font-size: 13px;
      color: #e2e8f0;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    .health-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 5px 10px;
      border-radius: 6px;
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid #1e293b;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }

    .health-online .status-dot {
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
    }

    .health-offline .status-dot {
      background: #ef4444;
      box-shadow: 0 0 8px #ef4444;
    }

    .health-meta {
      display: flex;
      flex-direction: column;
    }

    .health-status {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.5px;
    }

    .health-online .health-status {
      color: #10b981;
    }

    .health-offline .health-status {
      color: #ef4444;
    }

    .health-port {
      font-size: 8px;
      color: #64748b;
    }

    /* Buttons */
    .btn-refresh, .btn-simulation {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 7px 12px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-refresh {
      background: #1e293b;
      border: 1px solid #334155;
      color: #cbd5e1;
    }

    .btn-refresh:hover:not(:disabled) {
      background: #334155;
      color: #ffffff;
      border-color: #38bdf8;
    }

    .btn-simulation {
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fbbf24;
    }

    .btn-simulation:hover, .btn-simulation.active {
      background: rgba(245, 158, 11, 0.3);
      border-color: #f59e0b;
      box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
    }

    .icon-svg {
      width: 14px;
      height: 14px;
    }

    .spinning {
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      100% { transform: rotate(360deg); }
    }
  `]
})
export class CommandCenterHeaderComponent implements OnInit, OnDestroy {
  readonly state = inject(DisasterStateService);
  private healthService = inject(HealthService);

  readonly isBackendOnline = signal<boolean>(true);
  readonly currentTime = signal<string>('');

  private timerSub?: Subscription;
  private healthSub?: Subscription;

  ngOnInit(): void {
    this.updateClock();
    this.timerSub = interval(1000).subscribe(() => this.updateClock());

    // Health check heartbeat every 10 seconds
    this.checkHealth();
    this.healthSub = interval(10000).subscribe(() => this.checkHealth());
  }

  ngOnDestroy(): void {
    this.timerSub?.unsubscribe();
    this.healthSub?.unsubscribe();
  }

  private updateClock(): void {
    const now = new Date();
    this.currentTime.set(now.toTimeString().split(' ')[0] + ' ' + (now.getTimezoneOffset() <= 0 ? 'UTC+' : 'UTC-') + Math.abs(now.getTimezoneOffset() / 60));
  }

  private checkHealth(): void {
    this.healthService.checkHealth().subscribe(status => {
      this.isBackendOnline.set(status.online);
    });
  }

  refreshData(): void {
    this.state.loadAllData();
  }

  toggleSimulationTab(): void {
    this.state.setActiveTab('what-if');
  }
}
