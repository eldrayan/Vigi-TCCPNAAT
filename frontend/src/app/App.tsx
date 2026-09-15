/**
 * Descrição: Compõe a navegação e as páginas do dashboard Vigi.
 * Autor: Leôncio Ferreira
 */

import { ClipboardCheck, LayoutGrid, Settings, ShieldAlert, Workflow } from "lucide-react";
import { useEffect, useState } from "react";

import { AlarmsPage, InspectionsPage, OverviewPage, SettingsPage, StationsPage } from "./pages";
import { ErrorState } from "../components/feedback/ErrorState";
import { ActiveAlarmModal } from "../components/alarms/ActiveAlarmModal";
import { useDashboard } from "../hooks/useDashboard";
import { Sidebar } from "./Sidebar";

import styles from "./App.module.scss";

const navigation = [
  { label: "Visão geral", icon: LayoutGrid },
  { label: "Inspeções", icon: ClipboardCheck },
  { label: "Estações", icon: Workflow },
  { label: "Alarmes", icon: ShieldAlert },
  { label: "Configurações", icon: Settings },
];

export function App() {
  const [activePage, setActivePage] = useState("Visão geral");
  const [fontScale, setFontScale] = useState(() => {
    const stored = Number(window.localStorage.getItem("vigi-font-scale"));
    return stored === 1.1 || stored === 1.2 ? stored : 1;
  });
  const dashboard = useDashboard();
  useEffect(() => {
    document.documentElement.style.setProperty("--font-scale", String(fontScale));
    window.localStorage.setItem("vigi-font-scale", String(fontScale));
  }, [fontScale]);
  const pageActions = {
    onFilterInspections: dashboard.filterInspections,
    onAcknowledgeAlarm: dashboard.acknowledgeAlarm,
    onConfigureAlarm: dashboard.configureAlarm,
    onConfigureContext: dashboard.configureContext,
  };
  const pages = dashboard.data
    ? {
        "Visão geral": <OverviewPage {...dashboard.data} {...pageActions} />,
        Inspeções: <InspectionsPage {...dashboard.data} {...pageActions} />,
        Estações: <StationsPage {...dashboard.data} {...pageActions} />,
        Alarmes: <AlarmsPage {...dashboard.data} {...pageActions} />,
        Configurações: (
          <SettingsPage
            stations={dashboard.data.stations}
            onConfigureContext={dashboard.configureContext}
            fontScale={fontScale}
            onFontScaleChange={setFontScale}
          />
        ),
      }
    : null;
  const activeAlarm = dashboard.data?.alarms.find((alarm) => alarm.status === "ABERTO");

  return (
    <div className={styles.shell}>
      <Sidebar activePage={activePage} items={navigation} onNavigate={setActivePage} />

      <main className={styles.content}>
        {activePage === "Visão geral" && (
          <header className={styles.header}>
            <div>
              <h1>{activePage}</h1>
            </div>
          </header>
        )}

        {dashboard.error ? (
          <ErrorState message={dashboard.error} onRetry={() => void dashboard.refresh()} />
        ) : (dashboard.loading && !dashboard.data) || pages === null ? (
          <section className={styles.loading}>Carregando dados operacionais…</section>
        ) : (
          pages[activePage as keyof typeof pages]
        )}
      </main>
      {activeAlarm && <ActiveAlarmModal alarm={activeAlarm} onConfirm={dashboard.acknowledgeAlarm} />}
    </div>
  );
}
