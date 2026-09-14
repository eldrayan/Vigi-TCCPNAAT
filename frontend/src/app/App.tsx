/**
 * Descrição: Compõe a navegação e as páginas do dashboard Vigi.
 * Autor: Leôncio Ferreira
 */

import logo from "../assets/vigi-symbol.svg";
import { ClipboardCheck, LayoutGrid, ShieldAlert, Workflow } from "lucide-react";
import { useState } from "react";

import { AlarmsPage, InspectionsPage, OverviewPage, StationsPage } from "./pages";
import { ErrorState } from "../components/feedback/ErrorState";
import { ActiveAlarmModal } from "../components/alarms/ActiveAlarmModal";
import { useDashboard } from "../hooks/useDashboard";

import styles from "./App.module.scss";

const navigation = [
  { label: "Visão geral", icon: LayoutGrid },
  { label: "Inspeções", icon: ClipboardCheck },
  { label: "Estações", icon: Workflow },
  { label: "Alarmes", icon: ShieldAlert },
];

export function App() {
  const [activePage, setActivePage] = useState("Visão geral");
  const dashboard = useDashboard();
  const pageActions = {
    onFilterInspections: dashboard.filterInspections,
    onAcknowledgeAlarm: dashboard.acknowledgeAlarm,
    onConfigureAlarm: dashboard.configureAlarm,
  };
  const pages = dashboard.data ? {
    "Visão geral": <OverviewPage {...dashboard.data} {...pageActions} />,
    Inspeções: <InspectionsPage {...dashboard.data} {...pageActions} />,
    Estações: <StationsPage {...dashboard.data} {...pageActions} />,
    Alarmes: <AlarmsPage {...dashboard.data} {...pageActions} />,
  } : null;
  const activeAlarm = dashboard.data?.alarms.find((alarm) => alarm.status === "ABERTO");

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.brandMark}>
            <img src={logo} alt="" />
            <strong>VIGI</strong>
          </div>
          <span>VISÃO INTELIGENTE PARA GARANTIA DE INSPEÇÃO</span>
        </div>
        <nav aria-label="Navegação principal">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a className={activePage === item.label ? styles.activeLink : ""} href={`#${item.label.toLowerCase()}`} key={item.label} onClick={(event) => { event.preventDefault(); setActivePage(item.label); }}>
                <span aria-hidden="true"><Icon size={18} strokeWidth={1.7} /></span>
                {item.label}
              </a>
            );
          })}
        </nav>
      </aside>

      <main className={styles.content}>
        {activePage === "Visão geral" && (
          <header className={styles.header}>
            <div>
              <h1>{activePage}</h1>
            </div>
          </header>
        )}

        {dashboard.error ? <ErrorState message={dashboard.error} onRetry={() => void dashboard.refresh()} /> : dashboard.loading || pages === null ? <section className={styles.loading}>Carregando dados operacionais…</section> : pages[activePage as keyof typeof pages]}
      </main>
      {activeAlarm && <ActiveAlarmModal alarm={activeAlarm} onConfirm={dashboard.acknowledgeAlarm} />}
    </div>
  );
}
