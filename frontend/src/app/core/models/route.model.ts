export type RouteType = 'safest' | 'fastest' | 'balanced';

export interface RouteOption {
  id: string;
  type: RouteType;
  name: string;
  description: string;
  distanceKm: number;
  durationMinutes: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  floodHazardClearanceM: number;
  coordinates: [number, number][]; // Leaflet [lat, lng] points
  originName: string;
  destinationName: string;
  originCoords: [number, number];
  destinationCoords: [number, number];
  warningNotes: string[];
  recommended: boolean;
  provenance: string;
}
