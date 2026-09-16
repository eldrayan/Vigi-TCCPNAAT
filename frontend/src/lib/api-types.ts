/**
 * Descrição: Define os contratos consumidos pelo cliente HTTP do dashboard.
 * Autor: Leôncio Ferreira
 */

export interface Inspection {
  inspection_id: number;
  timestamp: string;
  station_code: string | null;
  batch_code: string | null;
  result: "CONFORME" | "NAO_CONFORME";
  nonconformity_type: "SEM_TAMPA" | "TAMPA_TORTA" | "AMASSADO" | null;
  technical_failure_type: string | null;
  confidence: number | null;
  processing_time_ms: number;
}

export interface InspectionPage {
  items: Inspection[];
  total: number;
  limit: number;
  offset: number;
}

export type InspectionListResponse = Inspection[] | InspectionPage;

export interface InspectionSummary {
  total: number;
  compliant: number;
  noncompliant: number;
  conformity_rate: number;
  nonconformities: Record<string, number>;
}

export interface InspectionSummaryResponse {
  total: number;
  compliant: number;
  noncompliant: number;
  compliance_rate: number;
  sem_tampa: number;
  tampa_torta: number;
  amassado: number;
  falha_tecnica: number;
}

export interface Station {
  id: number;
  code: string;
  name: string;
  device_id: string;
}

export interface Batch {
  id: number;
  code: string;
  station_id: number;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  created_at: string;
  max_nonconformity_rate: number | null;
  alarm_name: string | null;
}

export interface DeviceStatus {
  connection: string;
  sensor: string;
  camera: string;
  processing: string;
  timestamp: string;
}

export interface Alarm {
  id: number;
  station_id: number;
  batch_id: number;
  alarm_type: string;
  name: string;
  rate: number;
  threshold: number;
  status: string;
  created_at: string;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
}

export interface InspectionFilters {
  station_code?: string;
  batch_code?: string;
  result?: string;
  nonconformity_type?: string;
  start_at?: string;
  end_at?: string;
}
