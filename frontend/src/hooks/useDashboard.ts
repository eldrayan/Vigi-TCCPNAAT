/**
 * Descrição: Gerencia os dados, eventos e ações do dashboard Vigi.
 * Autor: Leôncio Ferreira
 */

import { useCallback, useEffect, useState } from "react";

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
  const AudioContextConstructor = window.AudioContext;
  if (!AudioContextConstructor) return;
  const context = new AudioContextConstructor();
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  oscillator.frequency.value = 880;
  gain.gain.setValueAtTime(0.08, context.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.35);
  oscillator.connect(gain).connect(context.destination);
  oscillator.start();
  oscillator.stop(context.currentTime + 0.35);
}

export function useDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [summary, inspectionPage, stations, alarms] = await Promise.all([
        api.summary(),
        api.inspectionsPage(),
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
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);
  useEffect(() => {
    const events = new EventSource(api.eventsUrl);
    const scheduleRefresh = () => void refresh();
    events.addEventListener("inspection.created", scheduleRefresh);
    events.addEventListener("device.status", scheduleRefresh);
    events.addEventListener("alarm.created", () => {
      playAlarmSound();
      scheduleRefresh();
    });
    return () => events.close();
  }, [refresh]);

  const filterInspections = useCallback(async (filters: InspectionFilters, limit = 10, offset = 0) => {
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
      await refresh();
    },
    [refresh],
  );

  const configureAlarm = useCallback(
    async (name: string, limit: number) => {
      await api.configureAlarm(1, 1, name, limit);
      await refresh();
    },
    [refresh],
  );

  return { data, error, loading, refresh, filterInspections, acknowledgeAlarm, configureAlarm };
}
