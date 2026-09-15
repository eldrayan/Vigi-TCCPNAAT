/**
 * Descrição: Centraliza as chamadas HTTP do dashboard para a API local do Vigi.
 * Autor: Leôncio Ferreira
 */

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

export interface InspectionPage {
  items: Inspection[];
  total: number;
  limit: number;
  offset: number;
}

type InspectionListResponse = Inspection[] | InspectionPage;

export interface InspectionSummary {
  total: number;
  compliant: number;
  noncompliant: number;
  conformity_rate: number;
  nonconformities: Record<string, number>;
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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) throw new Error(`Falha ao consultar a API (${response.status}).`);
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new Error("A API retornou uma resposta inválida. Confirme se o backend está ativo na porta 8000.");
  }
  return response.json() as Promise<T>;
}

export const api = {
  summary: (filters: InspectionFilters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    const query = params.toString();
    return request<InspectionSummary>(`/api/inspecoes/resumo${query ? `?${query}` : ""}`);
  },
  inspectionsPage: async (filters: InspectionFilters = {}, limit = 10, offset = 0): Promise<InspectionPage> => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    const summaryParams = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
        summaryParams.set(key, value);
      }
    });
    const summaryQuery = summaryParams.toString();
    const [items, summary] = await Promise.all([
      request<InspectionListResponse>(`/api/inspecoes?${params.toString()}`),
      request<InspectionSummary>(`/api/inspecoes/resumo${summaryQuery ? `?${summaryQuery}` : ""}`),
    ]);
    const list = Array.isArray(items) ? items : items.items;
    return {
      items: list,
      total: summary.total,
      limit,
      offset,
    };
  },
  inspections: (filters: InspectionFilters = {}) => api.inspectionsPage(filters).then((page) => page.items),
  stations: () => request<Station[]>("/api/estacoes"),
  batches: (stationId: number) => request<Batch[]>(`/api/estacoes/${stationId}/lotes`),
  createBatch: (stationId: number, code: string) =>
    request<Batch>(`/api/estacoes/${stationId}/lotes`, {
      method: "POST",
      body: JSON.stringify({ code }),
    }),
  activateBatch: (stationId: number, batchId: number) =>
    request(`/api/estacoes/${stationId}/lote-ativo`, {
      method: "PUT",
      body: JSON.stringify({ batch_id: batchId }),
    }),
  stationStatus: (id: number) => request<DeviceStatus>(`/api/estacoes/${id}/status`),
  alarms: () => request<Alarm[]>("/api/alarmes"),
  acknowledgeAlarm: (id: number, acknowledgedBy: string) =>
    request<Alarm>(`/api/alarmes/${id}/reconhecer`, {
      method: "POST",
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    }),
  configureAlarm: (stationId: number, batchId: number, name: string, limit: number) =>
    request(`/api/estacoes/${stationId}/lotes/${batchId}/limite`, {
      method: "PUT",
      body: JSON.stringify({ alarm_name: name, max_nonconformity_rate: limit }),
    }),
  eventsUrl: `${apiUrl}/api/eventos/stream`,
};
