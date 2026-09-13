import { useCallback, useEffect, useState } from "react";

import { api, type Alarm, type DeviceStatus, type Inspection, type InspectionFilters, type InspectionSummary, type Station } from "../lib/api";

export interface StationWithStatus extends Station { status: DeviceStatus | null; }
interface DashboardData { summary: InspectionSummary; inspections: Inspection[]; stations: StationWithStatus[]; alarms: Alarm[]; }

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
      const [summary, inspections, stations, alarms] = await Promise.all([api.summary(), api.inspections(), api.stations(), api.alarms()]);
      const stationsWithStatus = await Promise.all(stations.map(async (station) => {
        try { return { ...station, status: await api.stationStatus(station.id) }; }
        catch { return { ...station, status: null }; }
      }));
      setData({ summary, inspections, stations: stationsWithStatus, alarms });
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível carregar o dashboard.");
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => {
    const events = new EventSource(api.eventsUrl);
    const scheduleRefresh = () => void refresh();
    events.addEventListener("inspection.created", scheduleRefresh);
    events.addEventListener("device.status", scheduleRefresh);
    events.addEventListener("alarm.created", () => { playAlarmSound(); scheduleRefresh(); });
    return () => events.close();
  }, [refresh]);

  const filterInspections = useCallback(async (filters: InspectionFilters) => {
    try {
      const inspections = await api.inspections(filters);
      setData((current) => current ? { ...current, inspections } : current);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível filtrar as inspeções.");
    }
  }, []);

  const acknowledgeAlarm = useCallback(async (alarmId: number, acknowledgedBy: string) => {
    await api.acknowledgeAlarm(alarmId, acknowledgedBy);
    await refresh();
  }, [refresh]);

  return { data, error, loading, refresh, filterInspections, acknowledgeAlarm };
}
