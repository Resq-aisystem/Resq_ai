import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';

@Component({
  selector: 'app-gemini-briefing-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="gemini-container">
      <!-- Header -->
      <div class="gemini-header">
        <div class="header-title-row">
          <span class="sparkle-icon">✨</span>
          <h2 class="gemini-title">GOOGLE GEMINI EMERGENCY COORDINATOR BRIEFING</h2>
          @if (briefing()?.is_fallback) {
            <span class="badge badge-fallback font-mono">DETERMINISTIC FALLBACK ACTIVE</span>
          } @else {
            <span class="badge badge-grounded font-mono">GROUNDED IN VERIFIED RESQ-AI DATA</span>
          }
        </div>
        <p class="gemini-subtitle">
          Natural-language operational synthesis powered by {{ briefing()?.provider || 'Google Gemini AI' }} ({{ briefing()?.model_used || 'gemini-3.6-flash' }})
        </p>

        <!-- UX & Latency Metrics Bar -->
        <div class="latency-metrics-bar font-mono">
          <span class="metric-chip chip-core">⚡ Core Telemetry: {{ state.timeToFirstCoreIntelligenceMs() }}ms</span>
          @if (state.geminiBriefingLatencyMs() > 0) {
            <span class="metric-chip chip-gemini">✨ Gemini Latency: {{ state.geminiBriefingLatencyMs() }}ms</span>
            <span class="metric-chip chip-total">⏱️ Total Load: {{ state.totalDashboardTimeMs() }}ms</span>
          } @else {
            <span class="metric-chip chip-loading">⏳ Gemini Loading...</span>
          }
        </div>

        @if (briefing()?.is_fallback) {
          <div class="fallback-warning-banner">
            <span class="warning-icon">⚠️</span>
            <span>Gemini briefing unavailable — deterministic emergency guidance is active.</span>
          </div>
        }
      </div>

      <!-- Scrollable Content -->
      <div class="gemini-scrollable">
        @if (state.geminiLoading()) {
          <div class="loading-state">
            <span class="loading-spinner"></span>
            <p class="loading-text font-mono">Generating coordinator briefing...</p>
            <span class="loading-subtext">Fetching grounded decision context from RESQ-AI...</span>
          </div>
        } @else {
          @if (briefing(); as b) {
            <!-- 1. Executive Summary -->
            <div class="briefing-card card-summary">
              <div class="bc-header">
                <span class="bc-icon">📋</span>
                <span class="bc-title">EXECUTIVE SITUATION BRIEFING</span>
                <span class="bc-badge font-mono">COMMAND OVERVIEW</span>
              </div>
              <p class="bc-text summary-highlight">{{ b.summary }}</p>
            </div>

            <!-- 2. Risk & Priority Synthesis -->
            <div class="briefing-grid">
              <div class="briefing-card card-risk">
                <div class="bc-header">
                  <span class="bc-icon">⚠️</span>
                  <span class="bc-title">6-HOUR FLOOD RISK ANALYSIS</span>
                </div>
                <p class="bc-text">{{ b.risk_explanation }}</p>
              </div>

              <div class="briefing-card card-priority">
                <div class="bc-header">
                  <span class="bc-icon">🚨</span>
                  <span class="bc-title">EVACUATION PRIORITY REASONING</span>
                </div>
                <p class="bc-text">{{ b.priority_explanation }}</p>
              </div>
            </div>

            <!-- 3. Rescue Route Comparative Analysis -->
            <div class="briefing-card card-routes">
              <div class="bc-header">
                <span class="bc-icon">🗺️</span>
                <span class="bc-title">RESCUE ROUTE COMPARATIVE ANALYSIS</span>
                <span class="bc-badge font-mono">FASTEST vs SAFEST vs BALANCED</span>
              </div>
              <p class="bc-text">{{ b.route_explanation }}</p>
            </div>

            <!-- 4. Recommended Actions & Monitoring -->
            <div class="briefing-grid">
              <div class="briefing-card card-actions">
                <div class="bc-header">
                  <span class="bc-icon">⚡</span>
                  <span class="bc-title">IMMEDIATE OPERATIONAL DIRECTIVES</span>
                </div>
                <ul class="bc-list">
                  @for (act of b.recommended_actions; track act) {
                    <li>{{ act }}</li>
                  }
                </ul>
              </div>

              <div class="briefing-card card-monitoring">
                <div class="bc-header">
                  <span class="bc-icon">📡</span>
                  <span class="bc-title">CONTINUOUS TELEMETRY WATCH</span>
                </div>
                <ul class="bc-list">
                  @for (mon of b.monitoring_actions; track mon) {
                    <li>{{ mon }}</li>
                  }
                </ul>
              </div>
            </div>

            <!-- 5. What-If Scenario Interpretation -->
            <div class="briefing-card card-scenario">
              <div class="bc-header">
                <span class="bc-icon">🌊</span>
                <span class="bc-title">WHAT-IF SCENARIO IMPACT SUMMARY</span>
              </div>
              <p class="bc-text">{{ b.scenario_explanation }}</p>
            </div>

            <!-- 6. Grounding Sources & Data Audit -->
            <div class="briefing-card card-sources">
              <div class="bc-header">
                <span class="bc-icon">🛡️</span>
                <span class="bc-title">GROUNDED HYDROLOGICAL DATASETS</span>
              </div>
              <div class="sources-pill-row">
                @for (src of b.grounding_sources; track src) {
                  <span class="source-pill font-mono">{{ src }}</span>
                }
              </div>
            </div>

            <!-- 7. System Disclaimers & Limitations -->
            <div class="briefing-card card-limitations">
              <div class="bc-header">
                <span class="bc-icon">🔒</span>
                <span class="bc-title">SCIENTIFIC BOUNDARIES & DISCLAIMERS</span>
              </div>
              <ul class="bc-list limitations-list">
                @for (lim of b.limitations; track lim) {
                  <li>{{ lim }}</li>
                }
              </ul>
            </div>
          }
        }
      </div>
    </div>
  `,
  styles: [`
    .gemini-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
      font-family: inherit;
    }

    .gemini-header {
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

    .sparkle-icon {
      font-size: 16px;
    }

    .gemini-title {
      font-size: 13px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: 0.8px;
    }

    .gemini-subtitle {
      font-size: 11px;
      color: #94a3b8;
      margin: 0;
    }

    .badge {
      font-size: 9px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }

    .badge-grounded {
      background: rgba(16, 185, 129, 0.15);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.4);
    }

    .badge-fallback {
      background: rgba(245, 158, 11, 0.15);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.4);
    }

    .fallback-warning-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 8px;
      padding: 6px 10px;
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 4px;
      font-size: 11px;
      color: #fbbf24;
    }

    .gemini-scrollable {
      flex: 1;
      padding: 14px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .briefing-card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 12px;
    }

    .briefing-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    @media (max-width: 768px) {
      .briefing-grid {
        grid-template-columns: 1fr;
      }
    }

    .bc-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 8px;
    }

    .bc-icon {
      font-size: 14px;
    }

    .bc-title {
      font-size: 11px;
      font-weight: 700;
      color: #e2e8f0;
      letter-spacing: 0.5px;
    }

    .bc-badge {
      margin-left: auto;
      font-size: 9px;
      color: #38bdf8;
    }

    .bc-text {
      font-size: 12px;
      line-height: 1.5;
      color: #cbd5e1;
      margin: 0;
    }

    .summary-highlight {
      font-size: 12.5px;
      color: #f1f5f9;
      border-left: 3px solid #38bdf8;
      padding-left: 10px;
    }

    .bc-list {
      margin: 0;
      padding-left: 16px;
      font-size: 11.5px;
      color: #cbd5e1;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .limitations-list {
      color: #94a3b8;
    }

    .sources-pill-row {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .source-pill {
      font-size: 10px;
      padding: 3px 8px;
      background: #1e293b;
      color: #38bdf8;
      border-radius: 4px;
      border: 1px solid rgba(56, 189, 248, 0.2);
    }

    .latency-metrics-bar {
      display: flex;
      gap: 8px;
      margin-top: 6px;
      flex-wrap: wrap;
    }

    .metric-chip {
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 500;
    }

    .chip-core {
      background: rgba(16, 185, 129, 0.12);
      color: #10b981;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .chip-gemini {
      background: rgba(56, 189, 248, 0.12);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.3);
    }

    .chip-total {
      background: rgba(168, 85, 247, 0.12);
      color: #c084fc;
      border: 1px solid rgba(168, 85, 247, 0.3);
    }

    .chip-loading {
      background: rgba(245, 158, 11, 0.12);
      color: #f59e0b;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .loading-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
      color: #94a3b8;
      gap: 12px;
    }

    .loading-text {
      font-size: 13px;
      color: #f8fafc;
      margin: 0;
      font-weight: 600;
    }

    .loading-subtext {
      font-size: 11px;
      color: #64748b;
    }

    .loading-spinner {
      width: 28px;
      height: 28px;
      border: 3px solid #1e293b;
      border-top-color: #38bdf8;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `]
})
export class GeminiBriefingPanelComponent {
  state = inject(DisasterStateService);

  briefing() {
    const res = this.state.geminiBriefing();
    return res?.gemini_briefing || null;
  }
}

