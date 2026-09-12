import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { ProvenanceRecord } from '../../core/models/provenance.model';

@Component({
  selector: 'app-provenance-panel',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="provenance-container">
      <div class="provenance-header">
        <div class="header-title-row">
          <span class="prov-shield">🛡️</span>
          <h2 class="provenance-title">DATA PROVENANCE &amp; AUDIT TRAIL</h2>
          <span class="verified-badge font-mono">BACKEND TRACEABILITY</span>
        </div>
        <p class="provenance-subtitle">
          Cryptographic and source verification metadata grounded in existing FastAPI backend records
        </p>

        <div class="backend-summary-box font-mono">
          <div class="bs-row">
            <span>DATA SOURCE</span>
            <span class="text-cyan">FastAPI (Python) + SQLite (flood_response.db)</span>
          </div>
          <div class="bs-row">
            <span>TOTAL VERIFIED RECORDS</span>
            <span>{{ state.provenanceRecords().length }} Entities</span>
          </div>
          <div class="bs-row">
            <span>AUDIT COMPLIANCE</span>
            <span class="text-green">STRICT (NO FABRICATED DATA)</span>
          </div>
        </div>
      </div>

      <div class="provenance-scrollable">
        <div class="records-stack">
          @for (rec of state.provenanceRecords(); track rec.provenanceHash) {
            <div class="record-card">
              <div class="rc-header">
                <div class="rc-type-tag" [ngClass]="'tag-' + rec.entityType">
                  {{ rec.entityType | uppercase }} #{{ rec.entityId }}
                </div>
                <span class="rc-endpoint font-mono">{{ rec.httpMethod }} {{ rec.endpoint }}</span>
                <span class="rc-status font-mono">{{ rec.status | uppercase }}</span>
              </div>

              <h4 class="rc-title">{{ rec.entityName }}</h4>

              <div class="rc-metadata-grid font-mono">
                <div class="meta-item">
                  <span class="meta-lbl">ISSUED BY:</span>
                  <span class="meta-val">{{ rec.issuedBy }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-lbl">ISSUED AT:</span>
                  <span class="meta-val">{{ rec.issuedAt | date:'yyyy-MM-dd HH:mm:ss' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-lbl">LAST UPDATED:</span>
                  <span class="meta-val">{{ rec.updatedAt | date:'yyyy-MM-dd HH:mm:ss' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-lbl">CONFIDENCE:</span>
                  <span class="meta-val text-cyan">{{ rec.confidenceScore }}%</span>
                </div>
              </div>

              <div class="rc-hash-box font-mono">
                <span class="hash-lbl">INTEGRITY HASH:</span>
                <span class="hash-val">{{ rec.provenanceHash }}</span>
              </div>
            </div>
          }
        </div>
      </div>
    </div>
  `,
  styles: [`
    .provenance-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
    }

    .provenance-header {
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

    .prov-shield {
      font-size: 16px;
    }

    .provenance-title {
      font-size: 13px;
      font-weight: 800;
      color: #f8fafc;
      letter-spacing: 0.8px;
    }

    .verified-badge {
      font-size: 8.5px;
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.4);
      padding: 1px 6px;
      border-radius: 4px;
      font-weight: 700;
    }

    .provenance-subtitle {
      font-size: 10px;
      color: #64748b;
      margin-bottom: 8px;
    }

    .backend-summary-box {
      background: #141e33;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 10px;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }

    .bs-row {
      display: flex;
      justify-content: space-between;
      color: #94a3b8;
    }

    .provenance-scrollable {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
    }

    .records-stack {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .record-card {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .rc-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .rc-type-tag {
      font-size: 8.5px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 3px;
    }

    .tag-alert {
      background: rgba(239, 68, 68, 0.2);
      color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.4);
    }

    .tag-location {
      background: rgba(56, 189, 248, 0.2);
      color: #38bdf8;
      border: 1px solid rgba(56, 189, 248, 0.4);
    }

    .rc-endpoint {
      font-size: 9px;
      color: #94a3b8;
      flex: 1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .rc-status {
      font-size: 8px;
      color: #10b981;
      font-weight: 700;
    }

    .rc-title {
      font-size: 12px;
      font-weight: 700;
      color: #f1f5f9;
    }

    .rc-metadata-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 4px 10px;
      background: #141e33;
      padding: 6px 8px;
      border-radius: 4px;
      font-size: 9.5px;
    }

    .meta-item {
      display: flex;
      flex-direction: column;
    }

    .meta-lbl {
      color: #64748b;
      font-size: 8px;
    }

    .meta-val {
      color: #cbd5e1;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .rc-hash-box {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 8.5px;
      color: #64748b;
      background: rgba(15, 23, 42, 0.7);
      padding: 4px 6px;
      border-radius: 4px;
    }

    .hash-lbl {
      font-weight: 700;
    }

    .hash-val {
      color: #94a3b8;
      word-break: break-all;
    }

    .text-cyan { color: #38bdf8; }
    .text-green { color: #34d399; }
  `]
})
export class ProvenancePanelComponent {
  readonly state = inject(DisasterStateService);
}
