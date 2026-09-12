import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

export interface HealthStatus {
  online: boolean;
  status: string;
  timestamp: Date;
}

@Injectable({
  providedIn: 'root'
})
export class HealthService {
  private http = inject(HttpClient);
  private healthUrl = environment.healthUrl;

  checkHealth(): Observable<HealthStatus> {
    return this.http.get<{ status: string }>(this.healthUrl).pipe(
      map(res => ({
        online: res.status === 'healthy',
        status: res.status,
        timestamp: new Date()
      })),
      catchError(err => of({
        online: false,
        status: 'disconnected',
        timestamp: new Date()
      }))
    );
  }
}
