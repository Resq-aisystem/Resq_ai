import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { LocationResponse, LocationCreate, LocationUpdate } from '../models/location.model';

@Injectable({
  providedIn: 'root'
})
export class LocationService {
  private api = inject(ApiService);

  getLocations(filter?: { skip?: number; limit?: number; type?: string; is_active?: boolean }): Observable<LocationResponse[]> {
    return this.api.get<LocationResponse[]>('/locations/', filter);
  }

  getLocation(id: number): Observable<LocationResponse> {
    return this.api.get<LocationResponse>(`/locations/${id}`);
  }

  createLocation(location: LocationCreate): Observable<LocationResponse> {
    return this.api.post<LocationResponse>('/locations/', location);
  }

  updateLocation(id: number, location: LocationUpdate): Observable<LocationResponse> {
    return this.api.put<LocationResponse>(`/locations/${id}`, location);
  }

  deleteLocation(id: number): Observable<void> {
    return this.api.delete<void>(`/locations/${id}`);
  }
}
