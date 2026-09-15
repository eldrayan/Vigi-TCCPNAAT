/**
 * Descrição: Gerencia os dados, eventos e ações do dashboard Vigi.
 * Autor: Leôncio Ferreira
 */

import { useCallback, useEffect, useRef, useState } from "react";

import {
  api,
  type Alarm,
  type DeviceStatus,
  type Inspection,
  type InspectionFilters,
  type InspectionSummary,
  type Station,
} from "../lib/api";

export interface StationWithStatus extends Station {
  status: DeviceStatus | null;
}
interface DashboardData {
  summary: InspectionSummary;
  inspections: Inspection[];
  inspectionTotal: number;
  inspectionLimit: number;
  inspectionOffset: number;
  stations: StationWithStatus[];
  alarms: Alarm[];
}

function playAlarmSound() {
  try {
    const AudioContextConstructor = window.AudioContext;
    if (!AudioContextConstructor) return;
    const context = new AudioContextConstructor();
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.frequency.value = 880;
    gain.gain.setValueAtTime(0.08, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.35);
    oscillator.connect(gain).connect(context.destination);
    oscillator.onended = () => {
      void context.close().catch(() => {});
    };
    oscillator.start();
    oscillator.stop(context.currentTime + 0.35);
  } catch {
    // Silently ignore autoplay restrictions or audio context limits
  }
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const currentFiltersRef = useRef<InspectionFilters>({});
  const currentLimitRef = useRef(10);
  const currentOffsetRef = useRef(0);

  const refresh = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const [summary, inspectionPage, stations, alarms] = await Promise.all([
        api.summary(),
        api.inspectionsPage(currentFiltersRef.current, currentLimitRef.current, currentOffsetRef.current),
        api.stations(),
        api.alarms(),
      ]);
      const stationsWithStatus = await Promise.all(
        stations.map(async (station) => {
          try {
            return { ...station, status: await api.stationStatus(station.id) };
          } catch {
            return { ...station, status: null };
          }
        }),
      );
      setData({
        summary,
        inspections: inspectionPage.items,
        inspectionTotal: inspectionPage.total,
        inspectionLimit: inspectionPage.limit,
        inspectionOffset: inspectionPage.offset,
        stations: stationsWithStatus,
        alarms,
      });
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível carregar o dashboard.");
    } finally {
      if (!silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh(false);
  }, [refresh]);

  useEffect(() => {
    const events = new EventSource(api.eventsUrl);
    let timer: number | undefined;

    const scheduleRefresh = () => {
      if (timer) window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        void refresh(true);
      }, 400);
    };

    events.addEventListener("inspection.created", scheduleRefresh);
    events.addEventListener("device.status", scheduleRefresh);
    events.addEventListener("alarm.created", () => {
      playAlarmSound();
      scheduleRefresh();
    });
    return () => {
      if (timer) window.clearTimeout(timer);
      events.close();
    };
  }, [refresh]);

  const filterInspections = useCallback(async (filters: InspectionFilters, limit = 10, offset = 0) => {
    currentFiltersRef.current = filters;
    currentLimitRef.current = limit;
    currentOffsetRef.current = offset;
    try {
      const page = await api.inspectionsPage(filters, limit, offset);
      setData((current) =>
        current
          ? {
              ...current,
              inspections: page.items,
              inspectionTotal: page.total,
              inspectionLimit: page.limit,
              inspectionOffset: page.offset,
            }
          : current,
      );
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível filtrar as inspeções.");
    }
  }, []);

  const acknowledgeAlarm = useCallback(
    async (alarmId: number, acknowledgedBy: string) => {
      await api.acknowledgeAlarm(alarmId, acknowledgedBy);
      await refresh(true);
    },
    [refresh],
  );

  const configureAlarm = useCallback(
    async (name: string, limit: number, stationId?: number, batchId?: number) => {
      const targetStationId = stationId ?? data?.stations[0]?.id ?? 1;
      let targetBatchId = batchId;
      if (!targetBatchId) {
        try {
          const batches = await api.batches(targetStationId);
          const activeBatch = batches.find((b) => b.status === "EM_ANDAMENTO" || b.status === "ATIVO") ?? batches[batches.length - 1];
          targetBatchId = activeBatch?.id ?? 1;
        } catch {
          targetBatchId = 1;
        }
      }
      await api.configureAlarm(targetStationId, targetBatchId, name, limit);
      await refresh(true);
    },
    [data?.stations, refresh],
  );

  const configureContext = useCallback(
    async (stationCode: string, batchCode: string) => {
      const station = data?.stations.find((item) => item.code === stationCode);
      if (!station) throw new Error("Estação ativa não encontrada.");
      const batches = await api.batches(station.id);
      const existing = batches.find((batch) => batch.code === batchCode);
      const batch = existing ?? (await api.createBatch(station.id, batchCode));
      await api.activateBatch(station.id, batch.id);
      await refresh(true);
    },
    [data?.stations, refresh],
  );

  return { data, error, loading, refresh, filterInspections, acknowledgeAlarm, configureAlarm, configureContext };
}
