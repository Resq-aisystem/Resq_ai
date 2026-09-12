import { Component, inject, OnInit, AfterViewInit, OnDestroy, ElementRef, ViewChild, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as L from 'leaflet';
import { DisasterStateService } from '../../core/services/disaster-state.service';
import { LocationResponse } from '../../core/models/location.model';
import { AlertResponse } from '../../core/models/alert.model';
import { RouteOption } from '../../core/models/route.model';

@Component({
  selector: 'app-interactive-map',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="map-wrapper">
      <!-- Leaflet Map Container -->
      <div #mapContainer class="map-container" id="resq-leaflet-map"></div>

      <!-- Layer Control Floating Pill -->
      <div class="map-overlay-controls">
        <div class="layer-toggle" [ngClass]="{'active': showHazards}" (click)="toggleLayer('hazards')">
          <span class="toggle-dot dot-flood"></span>
          <span>FLOOD HAZARDS</span>
        </div>
        <div class="layer-toggle" [ngClass]="{'active': showFacilities}" (click)="toggleLayer('facilities')">
          <span class="toggle-dot dot-facilities"></span>
          <span>FACILITIES</span>
        </div>
        <div class="layer-toggle" [ngClass]="{'active': showRoutes}" (click)="toggleLayer('routes')">
          <span class="toggle-dot dot-routes"></span>
          <span>EVACUATION ROUTES</span>
        </div>
      </div>

      <!-- Map Legend -->
      <div class="map-legend">
        <div class="legend-header">
          <span class="legend-title">SITUATION MAP LEGEND</span>
          <span class="legend-scale font-mono">1:50,000</span>
        </div>
        <div class="legend-items">
          <div class="legend-col">
            <span class="legend-subhead">SEVERITY / FLOOD STAGE</span>
            <div class="legend-row"><span class="legend-color bg-critical"></span> Critical (&gt; 2.5m)</div>
            <div class="legend-row"><span class="legend-color bg-high"></span> High (1.4m - 2.5m)</div>
            <div class="legend-row"><span class="legend-color bg-medium"></span> Medium (0.7m - 1.4m)</div>
            <div class="legend-row"><span class="legend-color bg-low"></span> Low (&lt; 0.7m)</div>
          </div>
          <div class="legend-col">
            <span class="legend-subhead">FACILITY ASSETS</span>
            <div class="legend-row"><span class="icon-sq icon-hosp">🏥</span> Hospital / Medical</div>
            <div class="legend-row"><span class="icon-sq icon-shlt">🛡️</span> Evacuation Haven</div>
            <div class="legend-row"><span class="icon-sq icon-infr">⚙️</span> Utility / Drainage</div>
          </div>
          <div class="legend-col">
            <span class="legend-subhead">ROUTE RISK MATRIX</span>
            <div class="legend-row"><span class="route-line line-safest"></span> Route Alpha (Safest)</div>
            <div class="legend-row"><span class="route-line line-balanced"></span> Route Bravo (Balanced)</div>
            <div class="legend-row"><span class="route-line line-fastest"></span> Route Charlie (Fastest)</div>
          </div>
        </div>
      </div>

      <!-- Quick Reset View Button -->
      <button class="btn-reset-view" (click)="resetMapView()" title="Center Map on Regional Basin">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 2v4M12 18v4M2 12h4M18 12h4"/>
        </svg>
      </button>
    </div>
  `,
  styles: [`
    .map-wrapper {
      position: relative;
      width: 100%;
      height: 100%;
      background: #0b1120;
      overflow: hidden;
    }

    .map-container {
      width: 100%;
      height: 100%;
      z-index: 10;
    }

    /* Floating Layer Controls */
    .map-overlay-controls {
      position: absolute;
      top: 14px;
      left: 14px;
      z-index: 400;
      display: flex;
      gap: 6px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      border: 1px solid #334155;
      padding: 5px 8px;
      border-radius: 8px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    .layer-toggle {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 10px;
      font-weight: 700;
      color: #94a3b8;
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
      user-select: none;
    }

    .layer-toggle:hover {
      background: rgba(51, 65, 85, 0.5);
      color: #f8fafc;
    }

    .layer-toggle.active {
      background: #1e293b;
      color: #38bdf8;
      box-shadow: 0 0 8px rgba(56, 189, 248, 0.2);
    }

    .toggle-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
    }

    .dot-flood { background: #ef4444; }
    .dot-facilities { background: #38bdf8; }
    .dot-routes { background: #10b981; }

    /* Map Legend */
    .map-legend {
      position: absolute;
      bottom: 16px;
      left: 16px;
      z-index: 400;
      background: rgba(15, 23, 42, 0.88);
      backdrop-filter: blur(10px);
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
      max-width: 480px;
    }

    .legend-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #1e293b;
      padding-bottom: 4px;
      margin-bottom: 6px;
    }

    .legend-title {
      font-size: 9px;
      font-weight: 800;
      letter-spacing: 0.8px;
      color: #94a3b8;
    }

    .legend-scale {
      font-size: 8px;
      color: #64748b;
    }

    .legend-items {
      display: grid;
      grid-template-columns: 1.1fr 1fr 1.1fr;
      gap: 12px;
    }

    .legend-subhead {
      font-size: 8px;
      font-weight: 700;
      color: #64748b;
      letter-spacing: 0.5px;
      display: block;
      margin-bottom: 4px;
    }

    .legend-row {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 9.5px;
      color: #cbd5e1;
      margin-bottom: 2px;
    }

    .legend-color {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .bg-critical { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
    .bg-high { background: #f97316; }
    .bg-medium { background: #eab308; }
    .bg-low { background: #10b981; }

    .icon-sq {
      font-size: 11px;
    }

    .route-line {
      width: 14px;
      height: 3px;
      border-radius: 2px;
    }

    .line-safest { background: #10b981; box-shadow: 0 0 6px #10b981; }
    .line-balanced { background: #f59e0b; }
    .line-fastest { background: #06b6d4; }

    /* Reset View Button */
    .btn-reset-view {
      position: absolute;
      top: 14px;
      right: 14px;
      z-index: 400;
      width: 34px;
      height: 34px;
      border-radius: 8px;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid #334155;
      color: #94a3b8;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      transition: all 0.2s;
    }

    .btn-reset-view:hover {
      background: #334155;
      color: #38bdf8;
      border-color: #38bdf8;
    }

    .btn-reset-view svg {
      width: 18px;
      height: 18px;
    }
  `]
})
export class InteractiveMapComponent implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('mapContainer', { static: true }) mapContainer!: ElementRef<HTMLDivElement>;

  readonly state = inject(DisasterStateService);

  private map?: L.Map;
  private markersLayer = L.layerGroup();
  private hazardLayer = L.layerGroup();
  private routesLayer = L.layerGroup();

  showHazards = true;
  showFacilities = true;
  showRoutes = true;

  // Default Basin Center (Austin Metro Basin)
  private defaultCenter: [number, number] = [30.2700, -97.7350];
  private defaultZoom = 12;

  constructor() {
    // Reactive effect: redraw layers when state updates
    effect(() => {
      const locations = this.state.locations();
      const alerts = this.state.effectiveAlerts();
      const selectedLocId = this.state.selectedLocationId();
      const selectedRoute = this.state.selectedRoute();

      if (this.map) {
        this.renderAllLayers(locations, alerts, selectedLocId, selectedRoute);
      }
    });

    // Reactive effect: pan to selected location
    effect(() => {
      const selLoc = this.state.selectedLocation();
      if (selLoc && this.map) {
        this.map.flyTo([selLoc.latitude, selLoc.longitude], 13.5, {
          duration: 1.2
        });
      }
    });
  }

  ngOnInit(): void {}

  ngAfterViewInit(): void {
    this.initMap();
  }

  ngOnDestroy(): void {
    if (this.map) {
      this.map.remove();
    }
  }

  private initMap(): void {
    this.map = L.map(this.mapContainer.nativeElement, {
      center: this.defaultCenter,
      zoom: this.defaultZoom,
      zoomControl: false,
      attributionControl: false
    });

    // Dark Matter CartoDB Basemap
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd'
    }).addTo(this.map);

    // Zoom control at top-right below reset button
    L.control.zoom({ position: 'topright' }).addTo(this.map);

    // Add Layer Groups
    this.hazardLayer.addTo(this.map);
    this.markersLayer.addTo(this.map);
    this.routesLayer.addTo(this.map);

    // Initial render
    setTimeout(() => {
      this.map?.invalidateSize();
      this.renderAllLayers(
        this.state.locations(),
        this.state.effectiveAlerts(),
        this.state.selectedLocationId(),
        this.state.selectedRoute()
      );
    }, 200);
  }

  private renderAllLayers(
    locations: LocationResponse[],
    alerts: AlertResponse[],
    selectedLocId: number | null,
    selectedRoute: RouteOption | null
  ): void {
    if (!this.map) return;

    this.renderHazards(locations, alerts);
    this.renderMarkers(locations, alerts, selectedLocId);
    this.renderRoutes(selectedRoute);
  }

  private renderHazards(locations: LocationResponse[], alerts: AlertResponse[]): void {
    this.hazardLayer.clearLayers();
    if (!this.showHazards) return;

    alerts.forEach(alert => {
      const loc = locations.find(l => l.id === alert.location_id);
      if (!loc) return;

      const waterLevel = alert.water_level || 0.5;
      const radiusMeters = Math.max(300, Math.min(2200, waterLevel * 600));

      let fillColor = '#10b981';
      let strokeColor = '#059669';
      let fillOpacity = 0.25;

      if (alert.severity === 'critical') {
        fillColor = '#ef4444';
        strokeColor = '#dc2626';
        fillOpacity = 0.38;
      } else if (alert.severity === 'high') {
        fillColor = '#f97316';
        strokeColor = '#ea580c';
        fillOpacity = 0.32;
      } else if (alert.severity === 'medium') {
        fillColor = '#eab308';
        strokeColor = '#ca8a04';
        fillOpacity = 0.28;
      }

      // 1. Hazard Inundation Circle
      const circle = L.circle([loc.latitude, loc.longitude], {
        radius: radiusMeters,
        color: strokeColor,
        weight: 2,
        dashArray: alert.severity === 'critical' ? '4, 4' : undefined,
        fillColor: fillColor,
        fillOpacity: fillOpacity
      });

      circle.bindTooltip(
        `<div style="font-size:11px;font-weight:700;">
          <span style="color:${strokeColor};">&#9888; ${alert.severity.toUpperCase()} FLOOD ZONE</span><br/>
          Stage: ${waterLevel}m (Peak: ${alert.predicted_peak || 'N/A'}m)<br/>
          Exposed Pop: ${(alert.affected_population || 0).toLocaleString()}
        </div>`,
        { sticky: true, className: 'leaflet-popup-dark' }
      );

      this.hazardLayer.addLayer(circle);
    });
  }

  private renderMarkers(
    locations: LocationResponse[],
    alerts: AlertResponse[],
    selectedLocId: number | null
  ): void {
    this.markersLayer.clearLayers();
    if (!this.showFacilities) return;

    locations.forEach(loc => {
      const alert = alerts.find(a => a.location_id === loc.id);
      const isSelected = loc.id === selectedLocId;

      let iconClass = 'marker-hospital';
      let iconSymbol = '🏥';
      if (loc.type === 'shelter') {
        iconClass = 'marker-shelter';
        iconSymbol = '🛡️';
      } else if (loc.type === 'critical_infrastructure') {
        iconClass = 'marker-infrastructure';
        iconSymbol = '⚙️';
      }

      const isCritical = alert?.severity === 'critical';
      const selectedClass = isSelected ? 'marker-selected' : '';
      const pulseClass = isCritical ? 'pulse-critical' : '';

      const html = `
        <div class="custom-map-marker">
          <div class="marker-pin ${iconClass} ${selectedClass} ${pulseClass}" style="width:34px;height:34px;">
            <span style="font-size:16px;">${iconSymbol}</span>
          </div>
        </div>
      `;

      const customIcon = L.divIcon({
        html,
        className: '',
        iconSize: [34, 34],
        iconAnchor: [17, 17]
      });

      const marker = L.marker([loc.latitude, loc.longitude], { icon: customIcon });

      // Click to select
      marker.on('click', () => {
        this.state.selectLocation(loc.id);
      });

      // Rich popup content
      const popupHtml = `
        <div style="min-width:200px;font-family:Inter,sans-serif;">
          <div style="font-size:9px;font-weight:700;color:#94a3b8;letter-spacing:0.5px;margin-bottom:2px;">
            ${loc.type.toUpperCase()} &bull; ${loc.is_active ? 'ACTIVE' : 'STANDBY'}
          </div>
          <div style="font-size:13px;font-weight:800;color:#f8fafc;margin-bottom:6px;">
            ${loc.name}
          </div>
          <div style="font-size:11px;color:#cbd5e1;margin-bottom:8px;">
            ${loc.address}
          </div>
          <div style="background:#1e293b;padding:6px 8px;border-radius:4px;font-size:10px;margin-bottom:8px;">
            <div>Occupancy: <strong>${loc.current_occupancy}</strong> / ${loc.capacity || 'N/A'}</div>
            ${alert ? `<div>Stage: <strong style="color:#ef4444;">${alert.water_level || 0}m</strong> (Peak ${alert.predicted_peak || 0}m)</div>` : ''}
          </div>
          <div style="font-size:9.5px;color:#38bdf8;font-weight:700;">
            CLICK TO OPEN FULL ACTION PLAN &rarr;
          </div>
        </div>
      `;
      marker.bindPopup(popupHtml);

      this.markersLayer.addLayer(marker);
    });
  }

  private renderRoutes(selectedRoute: RouteOption | null): void {
    this.routesLayer.clearLayers();
    if (!this.showRoutes || !selectedRoute) return;

    // Render all available routes with lower opacity, selected route highlighted
    const allRoutes = this.state.availableRoutes();

    allRoutes.forEach(route => {
      const isSelected = route.id === selectedRoute.id;

      let color = '#10b981'; // Safest
      if (route.type === 'fastest') color = '#06b6d4';
      if (route.type === 'balanced') color = '#f59e0b';

      const polyline = L.polyline(route.coordinates, {
        color: color,
        weight: isSelected ? 5 : 2.5,
        opacity: isSelected ? 0.95 : 0.45,
        dashArray: isSelected ? undefined : '6, 6'
      });

      polyline.bindTooltip(
        `<div style="font-size:10px;font-weight:700;">
          <strong>${route.name}</strong><br/>
          ${route.distanceKm} km &bull; ${route.durationMinutes} mins &bull; Clearance: ${route.floodHazardClearanceM}m
        </div>`,
        { sticky: true }
      );

      polyline.on('click', () => {
        this.state.selectRoute(route);
      });

      this.routesLayer.addLayer(polyline);
    });
  }

  toggleLayer(layer: 'hazards' | 'facilities' | 'routes'): void {
    if (layer === 'hazards') {
      this.showHazards = !this.showHazards;
      if (this.showHazards) this.map?.addLayer(this.hazardLayer);
      else this.map?.removeLayer(this.hazardLayer);
    } else if (layer === 'facilities') {
      this.showFacilities = !this.showFacilities;
      if (this.showFacilities) this.map?.addLayer(this.markersLayer);
      else this.map?.removeLayer(this.markersLayer);
    } else if (layer === 'routes') {
      this.showRoutes = !this.showRoutes;
      if (this.showRoutes) this.map?.addLayer(this.routesLayer);
      else this.map?.removeLayer(this.routesLayer);
    }
  }

  resetMapView(): void {
    this.map?.flyTo(this.defaultCenter, this.defaultZoom, { duration: 1 });
  }
}
