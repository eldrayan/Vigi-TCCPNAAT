/**
 * Descrição: Exibe o histórico paginado e os filtros avançados de inspeções.
 * Autor: Leôncio Ferreira
 */

import { CheckCircle2, Search, XCircle } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import type { PageData } from "../../app/page-types";
import { labelType, formatDate } from "../../lib/formatters";
import { PageSection } from "../layout/PageSection";
import { Pagination } from "./Pagination";
import styles from "./InspectionsPage.module.scss";

function dateRange(
  period: string,
  filters: PageData["onFilterInspections"] extends (filters: infer T) => void ? T : never,
) {
  if (period === "custom") return { start_at: filters.start_at, end_at: filters.end_at };
  const end = new Date();
  const start = new Date(end);
  if (period === "today") start.setHours(0, 0, 0, 0);
  if (period === "24h") start.setHours(start.getHours() - 24);
  if (period === "7d") start.setDate(start.getDate() - 7);
  return { start_at: start.toISOString(), end_at: end.toISOString() };
}

export function InspectionsPage({
  inspections,
  inspectionTotal,
  inspectionLimit,
  inspectionOffset,
  onFilterInspections,
}: PageData) {
  const [filters, setFilters] = useState<Record<string, string | undefined>>({});
  const [period, setPeriod] = useState("custom");
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const load = useCallback(
    (limit = inspectionLimit, offset = 0) => {
      onFilterInspections({ ...filters, ...dateRange(period, filters) }, limit, offset);
    },
    [filters, inspectionLimit, onFilterInspections, period],
  );

  useEffect(() => {
    const timeout = window.setTimeout(() => load(), 300);
    return () => window.clearTimeout(timeout);
  }, [load]);

  const update = (name: string, value: string) => {
    setFilters((current) => ({ ...current, [name]: value || undefined }));
  };
  const reset = () => {
    setFilters({});
    setPeriod("custom");
    onFilterInspections({}, inspectionLimit, 0);
  };

  return (
    <PageSection
      title="Inspeções"
      description="Consulte o histórico de inspeções realizadas pelas estações."
      action={
        <button className={styles.advancedFilterBtn} type="button" onClick={() => setAdvancedOpen((open) => !open)}>
          <Search size={16} />
          Pesquisa avançada
        </button>
      }
    >
      {advancedOpen && (
        <form className={styles.filters} onSubmit={(event) => event.preventDefault()}>
          <input
            aria-label="Código da estação"
            placeholder="Estação"
            value={filters.station_code ?? ""}
            onChange={(event) => update("station_code", event.target.value)}
          />
          <input
            aria-label="Código do lote"
            placeholder="Lote"
            value={filters.batch_code ?? ""}
            onChange={(event) => update("batch_code", event.target.value)}
          />
          <label>
            Intervalo
            <select value={period} onChange={(event) => setPeriod(event.target.value)}>
              <option value="today">Hoje</option>
              <option value="24h">Últimas 24 horas</option>
              <option value="7d">Últimos 7 dias</option>
              <option value="custom">Personalizado</option>
            </select>
          </label>
          {period === "custom" && (
            <>
              <label>
                De
                <input
                  type="datetime-local"
                  value={filters.start_at ?? ""}
                  onChange={(event) => update("start_at", event.target.value)}
                />
              </label>
              <label>
                Até
                <input
                  type="datetime-local"
                  value={filters.end_at ?? ""}
                  onChange={(event) => update("end_at", event.target.value)}
                />
              </label>
            </>
          )}
          <select
            aria-label="Resultado"
            value={filters.result ?? ""}
            onChange={(event) => {
              update("result", event.target.value);
              if (event.target.value !== "NAO_CONFORME") update("nonconformity_type", "");
            }}
          >
            <option value="">Todos os resultados</option>
            <option value="CONFORME">Conforme</option>
            <option value="NAO_CONFORME">Não conforme</option>
          </select>
          {filters.result === "NAO_CONFORME" && (
            <select
              aria-label="Tipo de não conformidade"
              value={filters.nonconformity_type ?? ""}
              onChange={(event) => update("nonconformity_type", event.target.value)}
            >
              <option value="">Todos os tipos</option>
              <option value="SEM_TAMPA">Sem tampa</option>
              <option value="TAMPA_TORTA">Tampa torta</option>
              <option value="AMASSADO">Amassado</option>
            </select>
          )}
          <button type="button" onClick={reset}>
            Limpar filtros
          </button>
        </form>
      )}
      <div className={styles.tableWrap}>
        <div className={styles.tableScroll}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Estação</th>
                <th>Data e hora</th>
                <th>Resultado</th>
                <th>Tipo</th>
                <th>Confiança</th>
              </tr>
            </thead>
            <tbody>
              {inspections.map((inspection) => {
                const compliant = inspection.result === "CONFORME";
                return (
                  <tr key={inspection.inspection_id}>
                    <td>INS-{String(inspection.inspection_id).padStart(5, "0")}</td>
                    <td>{inspection.station_code ?? "—"}</td>
                    <td>{formatDate(inspection.timestamp)}</td>
                    <td>
                      <span className={compliant ? styles.ok : styles.danger}>
                        {compliant ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                        {inspection.result.replaceAll("_", " ")}
                      </span>
                    </td>
                    <td>
                      {compliant ? "—" : labelType(inspection.nonconformity_type ?? inspection.technical_failure_type)}
                    </td>
                    <td>{inspection.confidence ? `${Math.round(inspection.confidence * 100)}%` : "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <Pagination
          total={inspectionTotal}
          limit={inspectionLimit}
          offset={inspectionOffset}
          onPageChange={(page) => load(inspectionLimit, (page - 1) * inspectionLimit)}
          onPageSizeChange={(size) => load(size)}
        />
      </div>
    </PageSection>
  );
}
