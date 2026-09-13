/** Cliente HTTP do dashboard para a API local do Vigi. */

const apiUrl = import.meta.env.VITE_API_URL ?? window.location.origin;

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

export interface InspectionSummary {
  total: number;
  compliant: number;
  noncompliant: number;
  conformity_rate: number;
  nonconformities: Record<string, number>;
}

export interface Station { id: number; code: string; name: string; device_id: string; }
export interface DeviceStatus { connection: string; sensor: string; camera: string; processing: string; timestamp: string; }
export interface Alarm { id: number; station_id: number; batch_id: number; alarm_type: string; rate: number; threshold: number; status: string; created_at: string; acknowledged_at: string | null; acknowledged_by: string | null; }
export interface InspectionFilters { station_code?: string; batch_code?: string; result?: string; nonconformity_type?: string; start_at?: string; end_at?: string; }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) throw new Error(`Falha ao consultar a API (${response.status}).`);
  return response.json() as Promise<T>;
}

export const api = {
  summary: () => request<InspectionSummary>("/api/inspecoes/resumo"),
  inspections: (filters: InspectionFilters = {}) => {
    const params = new URLSearchParams({ limit: "50" });
    Object.entries(filters).forEach(([key, value]) => { if (value) params.set(key, value); });
    return request<Inspection[]>(`/api/inspecoes?${params.toString()}`);
  },
  stations: () => request<Station[]>("/api/estacoes"),
  stationStatus: (id: number) => request<DeviceStatus>(`/api/estacoes/${id}/status`),
  alarms: () => request<Alarm[]>("/api/alarmes"),
  acknowledgeAlarm: (id: number, acknowledgedBy: string) => request<Alarm>(`/api/alarmes/${id}/reconhecer`, { method: "POST", body: JSON.stringify({ acknowledged_by: acknowledgedBy }) }),
  eventsUrl: `${apiUrl}/api/eventos/stream`,
};
