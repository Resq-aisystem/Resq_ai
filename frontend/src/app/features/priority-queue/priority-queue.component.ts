import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { PriorityQueueItem } from '../../core/models/priority.model';
import { AlertSeverity } from '../../core/models/alert.model';

@Component({
  selector: 'app-priority-queue',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="queue-container">
      <!-- Queue Header -->
      <div class="queue-header">
        <div class="header-title-row">
          <div class="title-with-count">
            <span class="pulse-ring-icon"></span>
            <h2 class="queue-title">EMERGENCY PRIORITY QUEUE</h2>
            <span class="queue-badge font-mono">{{ filteredItems().length }} ACTIVE</span>
          </div>
        </div>
        <p class="queue-subtitle">
          Explainable Multi-Factor Ranking &bull; Risk &bull; Exposure &bull; Capacity
        </p>

        <!-- Filter Chips -->
        <div class="filter-chips">
          <button 
            class="chip-btn" 
            [ngClass]="{'chip-active': currentSeverityFilter() === 'all'}"
            (click)="setSeverityFilter('all')"
          >
            ALL ({{ state.priorityQueue().length }})
          </button>
          <button 
            class="chip-btn chip-critical" 
            [ngClass]="{'chip-active': currentSeverityFilter() === 'critical'}"
            (click)="setSeverityFilter('critical')"
          >
            CRITICAL ({{ countBySeverity('critical') }})
          </button>
          <button 
            class="chip-btn chip-high" 
            [ngClass]="{'chip-active': currentSeverityFilter() === 'high'}"
            (click)="setSeverityFilter('high')"
          >
            HIGH ({{ countBySeverity('high') }})
          </button>
          <button 
            class="chip-btn chip-medium" 
            [ngClass]="{'chip-active': currentSeverityFilter() === 'medium'}"
            (click)="setSeverityFilter('medium')"
          >
            MED ({{ countBySeverity('medium') }})
          </button>
        </div>
      </div>

      <!-- Queue List -->
      <div class="queue-list">
        @if (state.loading()) {
          <div class="loading-state">
            <div class="spinner"></div>
            <span>Evaluating telemetry & ranking priorities...</span>
          </div>
        } @else if (filteredItems().length === 0) {
          <div class="empty-state">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 8v4M12 16h.01"/>
            </svg>
            <p>No locations match the selected filter criteria.</p>
          </div>
        } @else {
          @for (item of filteredItems(); track item.location.id) {
            <div 
              class="queue-card"
              [ngClass]="{
                'card-selected': state.selectedLocationId() === item.location.id,
                'border-critical': item.priorityLevel === 'critical',
                'border-high': item.priorityLevel === 'high',
                'border-medium': item.priorityLevel === 'medium',
                'border-low': item.priorityLevel === 'low'
              }"
              (click)="selectItem(item)"
            >
              <!-- Card Top Row: Rank & Score -->
              <div class="card-top-row">
                <div class="rank-badge" [ngClass]="'rank-' + item.priorityLevel">
                  <span class="rank-hash">#</span>
                  <span class="rank-number font-mono">{{ item.rank }}</span>
                </div>

                <div class="location-heading">
                  <div class="facility-type-tag">
                    <span class="type-icon">{{ getTypeIcon(item.location.type) }}</span>
                    <span class="type-label">{{ item.location.type | uppercase }}</span>
                  </div>
                  <h3 class="location-name">{{ item.location.name }}</h3>
                </div>

                <div class="score-display font-mono">
                  <div class="score-number" [ngClass]="'text-' + item.priorityLevel">
                    {{ item.priorityScore }}
                  </div>
                  <div class="score-caption">SCORE</div>
                </div>
              </div>

              <!-- Card Metrics Grid -->
              <div class="card-metrics-grid">
                <div class="metric-cell">
                  <span class="cell-label">WATER STAGE</span>
                  <span class="cell-val font-mono" [ngClass]="'text-' + item.priorityLevel">
                    {{ item.alert.water_level || 0 }}m
                    <span class="peak-val">(Peak {{ item.alert.predicted_peak || 0 }}m)</span>
                  </span>
                </div>
                <div class="metric-cell">
                  <span class="cell-label">OCCUPANCY / CAP</span>
                  <span class="cell-val font-mono">
                    {{ item.location.current_occupancy }} / {{ item.location.capacity || 'N/A' }}
                  </span>
                </div>
                <div class="metric-cell">
                  <span class="cell-label">EXPOSED POP</span>
                  <span class="cell-val font-mono">
                    {{ (item.alert.affected_population || 0).toLocaleString() }}
                  </span>
                </div>
              </div>

              <!-- Explainable Score Breakdown Bars -->
              <div class="score-breakdown-bar" title="Severity + Water + Occupancy + Population weights">
                <div class="bar-segment bar-sev" [style.width.%]="(item.scoreBreakdown.severityComponent / 35) * 35"></div>
                <div class="bar-segment bar-water" [style.width.%]="(item.scoreBreakdown.waterLevelComponent / 25) * 25"></div>
                <div class="bar-segment bar-occ" [style.width.%]="(item.scoreBreakdown.occupancyComponent / 20) * 20"></div>
                <div class="bar-segment bar-pop" [style.width.%]="(item.scoreBreakdown.populationComponent / 20) * 20"></div>
              </div>

              <!-- Priority Justification Reason -->
              <div class="priority-reason">
                <span class="reason-icon">⚡</span>
                <span class="reason-text">{{ item.priorityReason }}</span>
              </div>

              <!-- Action Bar -->
              <div class="card-action-bar">
                <span class="alert-action-summary">
                  {{ item.alert.alert_type | uppercase }}: {{ truncate(item.alert.recommended_action, 75) }}
                </span>
                <button class="btn-inspect" (click)="inspectItem($event, item)">
                  INSPECT &rarr;
                </button>
              </div>
            </div>
          }
        }
      </div>
    </div>
  `,
  styles: [`
    .queue-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #090e1a;
      border-right: 1px solid #1e293b;
      overflow: hidden;
    }

    .queue-header {
      padding: 12px 14px;
      border-bottom: 1px solid #1e293b;
      background: #0d1527;
    }

    .header-title-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 2px;
    }

    .title-with-count {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .pulse-ring-icon {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ef4444;
      box-shadow: 0 0 8px #ef4444;
      animation: pulse-critical 2s infinite;
    }

    .queue-title {
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.8px;
      color: #f8fafc;
    }

    .queue-badge {
      font-size: 10px;
      background: rgba(56, 189, 248, 0.15);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 700;
    }

    .queue-subtitle {
      font-size: 10px;
      color: #64748b;
      margin-bottom: 10px;
    }

    /* Filter Chips */
    .filter-chips {
      display: flex;
      gap: 6px;
    }

    .chip-btn {
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      font-size: 9.5px;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .chip-btn:hover {
      background: #334155;
      color: #f8fafc;
    }

    .chip-active {
      background: #0284c7 !important;
      border-color: #38bdf8 !important;
      color: #ffffff !important;
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.4);
    }

    .chip-critical.chip-active {
      background: #dc2626 !important;
      border-color: #ef4444 !important;
      box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
    }

    .chip-high.chip-active {
      background: #ea580c !important;
      border-color: #f97316 !important;
      box-shadow: 0 0 8px rgba(249, 115, 22, 0.4);
    }

    /* Queue List */
    .queue-list {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .queue-card {
      background: linear-gradient(180deg, #0f172a 0%, #0c1220 100%);
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .queue-card:hover {
      background: #131c31;
      border-color: #38bdf8;
      transform: translateX(2px);
    }

    .card-selected {
      border-color: #38bdf8 !important;
      background: #142038 !important;
      box-shadow: 0 0 16px rgba(56, 189, 248, 0.25) !important;
    }

    .border-critical {
      border-left: 4px solid #ef4444;
    }

    .border-high {
      border-left: 4px solid #f97316;
    }

    .border-medium {
      border-left: 4px solid #eab308;
    }

    .border-low {
      border-left: 4px solid #10b981;
    }

    .card-top-row {
      display: flex;
      align-items: flex-start;
      gap: 10px;
    }

    .rank-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: #1e293b;
      border: 1px solid #334155;
      flex-shrink: 0;
    }

    .rank-critical {
      background: rgba(239, 68, 68, 0.2);
      border-color: #ef4444;
      color: #ef4444;
      box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
    }

    .rank-high {
      background: rgba(249, 115, 22, 0.2);
      border-color: #f97316;
      color: #f97316;
    }

    .rank-medium {
      background: rgba(234, 179, 8, 0.2);
      border-color: #eab308;
      color: #eab308;
    }

    .rank-low {
      background: rgba(16, 185, 129, 0.2);
      border-color: #10b981;
      color: #10b981;
    }

    .rank-hash {
      font-size: 11px;
      font-weight: 700;
      opacity: 0.7;
    }

    .rank-number {
      font-size: 15px;
      font-weight: 800;
    }

    .location-heading {
      flex: 1;
      min-width: 0;
    }

    .facility-type-tag {
      display: flex;
      align-items: center;
      gap: 4px;
      margin-bottom: 2px;
    }

    .type-icon {
      font-size: 11px;
    }

    .type-label {
      font-size: 8.5px;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.6px;
    }

    .location-name {
      font-size: 13px;
      font-weight: 700;
      color: #f1f5f9;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .score-display {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      flex-shrink: 0;
    }

    .score-number {
      font-size: 18px;
      font-weight: 800;
      line-height: 1.1;
    }

    .score-caption {
      font-size: 7.5px;
      color: #64748b;
      letter-spacing: 0.8px;
    }

    .text-critical { color: #ef4444; }
    .text-high { color: #f97316; }
    .text-medium { color: #eab308; }
    .text-low { color: #10b981; }

    /* Metrics Grid */
    .card-metrics-grid {
      display: grid;
      grid-template-columns: 1.2fr 1fr 1fr;
      gap: 6px;
      background: rgba(15, 23, 42, 0.6);
      padding: 6px 8px;
      border-radius: 6px;
      border: 1px solid #1e293b;
    }

    .metric-cell {
      display: flex;
      flex-direction: column;
    }

    .cell-label {
      font-size: 8px;
      color: #64748b;
      font-weight: 600;
      letter-spacing: 0.4px;
    }

    .cell-val {
      font-size: 11.5px;
      font-weight: 700;
      color: #cbd5e1;
    }

    .peak-val {
      font-size: 9.5px;
      color: #94a3b8;
      font-weight: 400;
    }

    /* Score Breakdown Bar */
    .score-breakdown-bar {
      display: flex;
      height: 3px;
      background: #1e293b;
      border-radius: 2px;
      overflow: hidden;
      gap: 1px;
    }

    .bar-segment {
      height: 100%;
    }

    .bar-sev { background: #ef4444; }
    .bar-water { background: #38bdf8; }
    .bar-occ { background: #f59e0b; }
    .bar-pop { background: #a855f7; }

    /* Priority Reason */
    .priority-reason {
      display: flex;
      align-items: flex-start;
      gap: 6px;
      font-size: 10.5px;
      color: #94a3b8;
      line-height: 1.35;
      background: rgba(30, 41, 59, 0.4);
      padding: 6px 8px;
      border-radius: 4px;
    }

    .reason-icon {
      color: #fbbf24;
      font-size: 11px;
      flex-shrink: 0;
    }

    /* Card Action Bar */
    .card-action-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      border-top: 1px solid rgba(51, 65, 85, 0.4);
      padding-top: 6px;
    }

    .alert-action-summary {
      font-size: 9.5px;
      color: #cbd5e1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-weight: 500;
    }

    .btn-inspect {
      background: transparent;
      border: 1px solid #38bdf8;
      color: #38bdf8;
      font-size: 9px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 4px;
      cursor: pointer;
      flex-shrink: 0;
      transition: all 0.2s;
    }

    .btn-inspect:hover {
      background: #38bdf8;
      color: #0b1120;
    }

    /* Loading & Empty */
    .loading-state, .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
      text-align: center;
      color: #64748b;
      gap: 12px;
      font-size: 12px;
    }

    .spinner {
      width: 28px;
      height: 28px;
      border: 2px solid #1e293b;
      border-top-color: #38bdf8;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    .empty-icon {
      width: 36px;
      height: 36px;
      color: #475569;
    }

    @keyframes spin {
      100% { transform: rotate(360deg); }
    }
  `]
})
export class PriorityQueueComponent {
  readonly state = inject(DisasterStateService);

  currentSeverityFilter(): AlertSeverity | 'all' {
    return this.state.filterSeverity();
  }

  setSeverityFilter(sev: AlertSeverity | 'all'): void {
    this.state.filterSeverity.set(sev);
  }

  countBySeverity(sev: AlertSeverity): number {
    return this.state.priorityQueue().filter(i => i.priorityLevel === sev).length;
  }

  filteredItems(): PriorityQueueItem[] {
    const filter = this.state.filterSeverity();
    const items = this.state.priorityQueue();
    if (filter === 'all') return items;
    return items.filter(i => i.priorityLevel === filter);
  }

  selectItem(item: PriorityQueueItem): void {
    this.state.selectLocation(item.location.id);
  }

  inspectItem(event: MouseEvent, item: PriorityQueueItem): void {
    event.stopPropagation();
    this.state.selectLocation(item.location.id);
    this.state.setActiveTab('zone-details');
  }

  getTypeIcon(type: string): string {
    switch (type) {
      case 'hospital': return '🏥';
      case 'shelter': return '🛡️';
      case 'critical_infrastructure': return '⚙️';
      default: return '📍';
    }
  }

  truncate(str: string, len: number): string {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
  }
}
