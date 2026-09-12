import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { AlertResponse, AlertCreate, AlertUpdate } from '../models/alert.model';

@Injectable({
  providedIn: 'root'
})
export class AlertService {
  private api = inject(ApiService);

  getAlerts(filter?: { skip?: number; limit?: number; location_id?: number; severity?: string; status?: string }): Observable<AlertResponse[]> {
    return this.api.get<AlertResponse[]>('/alerts/', filter);
  }

  getAlert(id: number): Observable<AlertResponse> {
    return this.api.get<AlertResponse>(`/alerts/${id}`);
  }

  createAlert(alert: AlertCreate): Observable<AlertResponse> {
    return this.api.post<AlertResponse>('/alerts/', alert);
  }

  updateAlert(id: number, alert: AlertUpdate): Observable<AlertResponse> {
    return this.api.put<AlertResponse>(`/alerts/${id}`, alert);
  }

  deleteAlert(id: number): Observable<void> {
    return this.api.delete<void>(`/alerts/${id}`);
  }
}
