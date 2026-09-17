/**
 * Descrição: Centraliza as chamadas HTTP do dashboard para a API local do Vigi.
 * Autor: Leôncio Ferreira
 */

import type {
  Alarm,
  Batch,
  DeviceStatus,
  InspectionFilters,
  InspectionListResponse,
  InspectionPage,
  InspectionSummary,
  InspectionSummaryResponse,
  Station,
} from "./api-types";

const apiUrl = import.meta.env.VITE_API_URL ?? window.location.origin;

export type {
  Alarm,
  Batch,
  DeviceStatus,
  Inspection,
  InspectionFilters,
  InspectionPage,
  InspectionSummary,
  Station,
} from "./api-types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, { headers: { "Content-Type": "application/json" }, ...init });
  if (!response.ok) {
    let detail: string | undefined;
    try {
      const payload = (await response.json()) as { detail?: string };
      detail = payload.detail;
    } catch {
      // Mantém a mensagem padrão quando a API não devolve JSON.
    }
    throw new Error(detail ?? `Falha ao consultar a API (${response.status}).`);
  }
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new Error("A API retornou uma resposta inválida. Confirme se o backend está ativo na porta 8000.");
  }
  return response.json() as Promise<T>;
}

function normalizeInspectionSummary(summary: InspectionSummaryResponse): InspectionSummary {
  return {
    total: summary.total,
    compliant: summary.compliant,
    noncompliant: summary.noncompliant,
    conformity_rate: summary.compliance_rate,
    nonconformities: {
      SEM_TAMPA: summary.sem_tampa,
      TAMPA_TORTA: summary.tampa_torta,
      AMASSADO: summary.amassado,
      FALHA_TECNICA: summary.falha_tecnica,
    },
  };
}

export const api = {
  summary: (filters: InspectionFilters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    const query = params.toString();
    return request<InspectionSummaryResponse>(`/api/inspecoes/resumo${query ? `?${query}` : ""}`).then(
      normalizeInspectionSummary,
    );
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
      request<InspectionSummaryResponse>(`/api/inspecoes/resumo${summaryQuery ? `?${summaryQuery}` : ""}`),
    ]);
    const list = Array.isArray(items) ? items : items.items;
    return {
      items: list,
      total: normalizeInspectionSummary(summary).total,
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
