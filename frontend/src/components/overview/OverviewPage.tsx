/**
 * Descrição: Apresenta o resumo operacional e as inspeções recentes do Vigi.
 * Autor: Leôncio Ferreira
 */

import { ClipboardCheck, Database, Radio, ShieldAlert } from "lucide-react";
import { useEffect, useState } from "react";

import type { Inspection } from "../../lib/api";
import type { PageData } from "../../app/page-types";
import { NonconformityChart } from "../dashboard/NonconformityChart";
import { InspectionDetailModal } from "./InspectionDetailModal";
import { OverviewMetric } from "./OverviewMetric";
import metricStyles from "./OverviewMetrics.module.scss";
import { RecentInspectionsTable } from "./RecentInspectionsTable";
import styles from "./OverviewPage.module.scss";

function getRange(period: string) {
  if (period === "all") return {};
  const end = new Date();
  const start = new Date(end);
  if (period === "today") start.setHours(0, 0, 0, 0);
  if (period === "24h") start.setHours(start.getHours() - 24);
  if (period === "7d") start.setDate(start.getDate() - 7);
  return { start_at: start.toISOString(), end_at: end.toISOString() };
}

export function OverviewPage({ summary, inspections, stations, alarms, onFilterInspections }: PageData) {
  const [selected, setSelected] = useState<Inspection | null>(null);
  const [period, setPeriod] = useState("all");
  const [batchCode, setBatchCode] = useState("");
  const [result, setResult] = useState("");
  const [type, setType] = useState("");

  useEffect(() => {
    const timeout = window.setTimeout(
      () => {
        onFilterInspections(
          {
            ...getRange(period),
            batch_code: batchCode || undefined,
            result: result || undefined,
            nonconformity_type: type || undefined,
          },
          batchCode ? 10 : 5,
          0,
        );
      },
      batchCode ? 350 : 0,
    );
    return () => window.clearTimeout(timeout);
  }, [batchCode, onFilterInspections, period, result, type]);

  return (
    <>
      <section className={metricStyles.metrics} aria-label="Resumo das inspeções">
        <OverviewMetric
          icon={ClipboardCheck}
          label="Inspeções"
          value={String(summary.total)}
          detail={`${summary.noncompliant} não conformes`}
        />
        <OverviewMetric
          icon={Database}
          label="Taxa de conformidade"
          value={`${summary.conformity_rate.toLocaleString("pt-BR")}%`}
          detail={`${summary.compliant} conformes`}
        />
        <OverviewMetric
          icon={Radio}
          label="Estações online"
          value={`${stations.filter((station) => station.status?.connection === "ONLINE").length}/${stations.length}`}
          detail="Status do dispositivo"
        />
        <OverviewMetric
          icon={ShieldAlert}
          label="Alarmes abertos"
          value={String(alarms.filter((alarm) => alarm.status === "ABERTO").length)}
          detail="Requerem atenção"
        />
      </section>
      <section className={styles.overviewGrid}>
        <div className={styles.activity}>
          <h2>Inspeções recentes</h2>
          <div className={styles.filters}>
            <select value={period} onChange={(event) => setPeriod(event.target.value)} aria-label="Período">
              <option value="all">Todo o período</option>
              <option value="today">Hoje</option>
              <option value="24h">Últimas 24 horas</option>
              <option value="7d">Últimos 7 dias</option>
            </select>
            <input
              placeholder="Lote"
              value={batchCode}
              onChange={(event) => setBatchCode(event.target.value)}
              aria-label="Lote"
            />
            <select
              value={result}
              onChange={(event) => {
                setResult(event.target.value);
                if (event.target.value !== "NAO_CONFORME") setType("");
              }}
              aria-label="Resultado"
            >
              <option value="">Todos os resultados</option>
              <option value="CONFORME">Conforme</option>
              <option value="NAO_CONFORME">Não conforme</option>
            </select>
            {result === "NAO_CONFORME" && (
              <select value={type} onChange={(event) => setType(event.target.value)} aria-label="Tipo de anomalia">
                <option value="">Todas as anomalias</option>
                <option value="SEM_TAMPA">Sem tampa</option>
                <option value="TAMPA_TORTA">Tampa torta</option>
                <option value="AMASSADO">Amassado</option>
              </select>
            )}
          </div>
          <RecentInspectionsTable inspections={inspections.slice(0, 5)} onSelect={setSelected} />
        </div>
        <div className={styles.quality}>
          <header>
            <h2>Não conformidades</h2>
            <span>Por tipo</span>
          </header>
          <NonconformityChart data={summary.nonconformities} />
          <div className={styles.progress}>
            <span style={{ width: `${summary.conformity_rate}%` }} />
          </div>
          <p>Conformidade geral: {summary.conformity_rate.toLocaleString("pt-BR")}%</p>
        </div>
      </section>
      {selected && <InspectionDetailModal inspection={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
