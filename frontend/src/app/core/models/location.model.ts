export type LocationType = 'hospital' | 'shelter' | 'critical_infrastructure';

export interface LocationBase {
  name: string;
  type: LocationType;
  address: string;
  latitude: number;
  longitude: number;
  capacity?: number | null;
  current_occupancy: number;
  contact_name?: string | null;
  contact_phone?: string | null;
  contact_email?: string | null;
  is_active: boolean;
}

export interface LocationResponse extends LocationBase {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface LocationCreate extends LocationBase {}

export interface LocationUpdate extends Partial<LocationBase> {}
