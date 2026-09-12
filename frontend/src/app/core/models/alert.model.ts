export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';
export type AlertType = 'flood_warning' | 'evacuation_order' | 'all_clear';
export type AlertStatus = 'active' | 'resolved' | 'expired';

export interface AlertBase {
  location_id: number;
  severity: AlertSeverity;
  alert_type: AlertType;
  title: string;
  description: string;
  water_level?: number | null;
  predicted_peak?: number | null;
  affected_population?: number | null;
  recommended_action: string;
  justification: string;
  issued_by: string;
  expires_at?: string | null;
}

export interface AlertResponse extends AlertBase {
  id: number;
  status: AlertStatus;
  issued_at: string;
  resolved_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertCreate extends AlertBase {}

export interface AlertUpdate {
  severity?: AlertSeverity;
  alert_type?: AlertType;
  title?: string;
  description?: string;
  water_level?: number;
  predicted_peak?: number;
  affected_population?: number;
  recommended_action?: string;
  justification?: string;
  status?: AlertStatus;
  expires_at?: string;
  resolved_at?: string;
}
