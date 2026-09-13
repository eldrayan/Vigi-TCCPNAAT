import logo from "../assets/vigi-symbol.svg";
import { Workflow } from "lucide-react";
import { useState } from "react";

import { AlarmsPage, InspectionsPage, OverviewPage, StationsPage } from "./pages";
import { ErrorState } from "../components/feedback/ErrorState";
import { useDashboard } from "../hooks/useDashboard";

import styles from "./App.module.scss";

const navigation = [
  { label: "Visão geral", icon: "home", active: true },
  { label: "Inspeções", icon: "inspection", active: false },
  { label: "Estações", icon: Workflow, active: false },
  { label: "Alarmes", icon: "alert", active: false },
];

function NavigationIcon({ name }: { name: string }) {
  const paths = {
    home: <path d="m3 10 5-4 5 4v5H9v-3H7v3H3z" />,
    inspection: <><circle cx="8" cy="8" r="5" /><path d="m8 5 1.5 3L8 9.5 6.5 8z" /></>,
    alert: <><path d="M8 2v7" /><path d="M8 12.5v.5" /></>,
  } as const;

  return <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name as keyof typeof paths]}</svg>;
}

export function App() {
  const [activePage, setActivePage] = useState("Visão geral");
  const dashboard = useDashboard();
  const pageActions = {
    onRefresh: () => void dashboard.refresh(),
    onFilterInspections: (filters: Parameters<typeof dashboard.filterInspections>[0]) => void dashboard.filterInspections(filters),
    onAcknowledgeAlarm: dashboard.acknowledgeAlarm,
  };
  const pages = dashboard.data ? {
    "Visão geral": <OverviewPage {...dashboard.data} {...pageActions} />,
    Inspeções: <InspectionsPage {...dashboard.data} {...pageActions} />,
    Estações: <StationsPage {...dashboard.data} {...pageActions} />,
    Alarmes: <AlarmsPage {...dashboard.data} {...pageActions} />,
  } : null;

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
          {navigation.map((item) => (
            <a className={activePage === item.label ? styles.activeLink : ""} href={`#${item.label.toLowerCase()}`} key={item.label} onClick={(event) => { event.preventDefault(); setActivePage(item.label); }}>
              <span aria-hidden="true">{typeof item.icon === "string" ? <NavigationIcon name={item.icon} /> : <item.icon size={16} strokeWidth={1.7} />}</span>
              {item.label}
            </a>
          ))}
        </nav>
      </aside>

      <main className={styles.content}>
        {activePage === "Visão geral" && (
          <header className={styles.header}>
            <div>
              <p className={styles.eyebrow}>CENTRO DE OPERAÇÕES</p>
              <h1>{activePage}</h1>
            </div>
          </header>
        )}

        {dashboard.error ? <ErrorState message={dashboard.error} onRetry={() => void dashboard.refresh()} /> : dashboard.loading || pages === null ? <section className={styles.loading}>Carregando dados operacionais…</section> : pages[activePage as keyof typeof pages]}
      </main>
    </div>
  );
}
