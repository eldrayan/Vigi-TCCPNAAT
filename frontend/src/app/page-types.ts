/**
 * Descrição: Define os dados compartilhados pelas páginas do dashboard.
 * Autor: Leôncio Ferreira
 */

import type { Alarm, Inspection, InspectionFilters, InspectionSummary } from "../lib/api";
import type { StationWithStatus } from "../hooks/useDashboard";

export interface PageData {
  summary: InspectionSummary;
  inspections: Inspection[];
  inspectionTotal: number;
  inspectionLimit: number;
  inspectionOffset: number;
  stations: StationWithStatus[];
  alarms: Alarm[];
  onFilterInspections: (filters: InspectionFilters, limit?: number, offset?: number) => void;
  onAcknowledgeAlarm: (id: number, acknowledgedBy: string) => Promise<void>;
  onConfigureAlarm: (name: string, limit: number, stationId: number) => Promise<void>;
  onConfigureContext: (stationCode: string, batchCode: string) => Promise<void>;
}
