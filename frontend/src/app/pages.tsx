import { ClipboardCheck, Database, Radio, ShieldAlert } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";

import type { Alarm, Inspection, InspectionFilters, InspectionSummary } from "../lib/api";
import type { StationWithStatus } from "../hooks/useDashboard";
import { NonconformityChart } from "../components/dashboard/NonconformityChart";
import styles from "./pages.module.scss";

export interface PageData { summary: InspectionSummary; inspections: Inspection[]; stations: StationWithStatus[]; alarms: Alarm[]; onRefresh: () => void; onFilterInspections: (filters: InspectionFilters) => void; onAcknowledgeAlarm: (id: number, acknowledgedBy: string) => Promise<void>; }

function labelType(type: string | null) { return type?.replaceAll("_", " ") ?? "—"; }
function formatDate(value: string) { return new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(new Date(value)); }

export function OverviewPage({ summary, inspections, stations, alarms }: PageData) {
  const [selected, setSelected] = useState<Inspection | null>(null);
  const recent = inspections.slice(0, 3);

  return <>
    <section className={styles.welcome}><div><p className={styles.eyebrow}>ACOMPANHAMENTO EM TEMPO REAL</p><h2>Qualidade sob controle.</h2><p>Monitore suas estações e acompanhe cada inspeção do Vigi.</p></div><div className={styles.dateCard}><span>Hoje</span><strong>13 SET 2026</strong></div></section>
    <section className={styles.metrics} aria-label="Resumo das inspeções">
      <Metric icon={ClipboardCheck} label="Inspeções" value={String(summary.total)} detail={`${summary.noncompliant} não conformes`} />
      <Metric icon={Database} label="Taxa de conformidade" value={`${summary.conformity_rate.toLocaleString("pt-BR")}%`} detail={`${summary.compliant} conformes`} />
      <Metric icon={Radio} label="Estações online" value={`${stations.filter((station) => station.status?.connection === "ONLINE").length}/${stations.length}`} detail="Status do dispositivo" />
      <Metric icon={ShieldAlert} label="Alarmes abertos" value={String(alarms.filter((alarm) => alarm.status === "ABERTO").length)} detail="Requerem atenção" />
    </section>
    <section className={styles.overviewGrid}><div className={styles.activity}><div className={styles.sectionHeading}><h2>Inspeções recentes</h2><span>Últimas 24 horas</span></div><div className={styles.activityList}>{recent.map((inspection) => <div className={styles.activityRow} key={inspection.inspection_id}><time>{formatDate(inspection.timestamp).split(", ")[1]}</time><strong>{inspection.station_code ?? "Sem estação"}</strong><span className={inspection.result === "CONFORME" ? styles.ok : styles.warning}>{inspection.result === "CONFORME" ? "Conforme" : "Não conforme"}</span><small>{inspection.confidence ? `${Math.round(inspection.confidence * 100)}%` : "—"}</small><button type="button" className={styles.detailButton} onClick={() => setSelected(inspection)}>Ver detalhes</button></div>)}</div></div><div className={styles.quality}><div className={styles.sectionHeading}><h2>Não conformidades</h2><span>Por tipo</span></div><NonconformityChart data={summary.nonconformities} /><div className={styles.progress}><span style={{ width: `${summary.conformity_rate}%` }} /></div><p>Conformidade geral: {summary.conformity_rate.toLocaleString("pt-BR")}%</p></div></section>
    {selected && <div className={styles.modalBackdrop} role="presentation" onClick={() => setSelected(null)}><section className={styles.detailModal} role="dialog" aria-modal="true" aria-labelledby="inspection-detail-title" onClick={(event) => event.stopPropagation()}><div className={styles.sectionHeading}><h2 id="inspection-detail-title">Detalhes da inspeção</h2><button type="button" className={styles.closeButton} onClick={() => setSelected(null)} aria-label="Fechar">×</button></div><dl className={styles.detailList}><div><dt>Estação</dt><dd>{selected.station_code ?? "—"}</dd></div><div><dt>Horário</dt><dd>{formatDate(selected.timestamp)}</dd></div><div><dt>Resultado</dt><dd className={selected.result === "CONFORME" ? styles.ok : styles.warning}>{selected.result.replaceAll("_", " ")}</dd></div><div><dt>Confiança do modelo</dt><dd>{selected.confidence ? `${Math.round(selected.confidence * 100)}%` : "—"}</dd></div>{selected.nonconformity_type && <div><dt>Tipo de não conformidade</dt><dd>{labelType(selected.nonconformity_type)}</dd></div>}{selected.technical_failure_type && <div><dt>Falha técnica</dt><dd>{labelType(selected.technical_failure_type)}</dd></div>}</dl></section></div>}
  </>;
}

function Metric({ icon: Icon, label, value, detail }: { icon: typeof ClipboardCheck; label: string; value: string; detail: string }) {
  return <article className={styles.metric}><Icon size={18} /><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

export function InspectionsPage({ inspections, onRefresh, onFilterInspections }: PageData) {
  const [filters, setFilters] = useState<InspectionFilters>({});
  const update = (name: keyof InspectionFilters, value: string) => setFilters((current) => ({ ...current, [name]: value }));
  return <PageSection title="Inspeções" description="Consulte o histórico de inspeções realizadas pelas estações." onRefresh={onRefresh}><form className={styles.filters} onSubmit={(event) => { event.preventDefault(); onFilterInspections(filters); }}><input aria-label="Código da estação" placeholder="Estação" value={filters.station_code ?? ""} onChange={(event) => update("station_code", event.target.value)} /><input aria-label="Código do lote" placeholder="Lote" value={filters.batch_code ?? ""} onChange={(event) => update("batch_code", event.target.value)} /><input aria-label="Início do período" type="datetime-local" value={filters.start_at ?? ""} onChange={(event) => update("start_at", event.target.value)} /><input aria-label="Fim do período" type="datetime-local" value={filters.end_at ?? ""} onChange={(event) => update("end_at", event.target.value)} /><select aria-label="Resultado" value={filters.result ?? ""} onChange={(event) => update("result", event.target.value)}><option value="">Todos os resultados</option><option value="CONFORME">Conforme</option><option value="NAO_CONFORME">Não conforme</option></select><select aria-label="Tipo de não conformidade" value={filters.nonconformity_type ?? ""} onChange={(event) => update("nonconformity_type", event.target.value)}><option value="">Todos os tipos</option><option value="SEM_TAMPA">Sem tampa</option><option value="TAMPA_TORTA">Tampa torta</option><option value="AMASSADO">Amassado</option></select><button type="submit">Filtrar</button><button type="button" onClick={() => { setFilters({}); onFilterInspections({}); }}>Limpar</button></form><div className={styles.tableWrap}><table><thead><tr><th>ID</th><th>Estação</th><th>Data e hora</th><th>Resultado</th><th>Tipo</th><th>Confiança</th></tr></thead><tbody>{inspections.map((inspection) => <tr key={inspection.inspection_id}><td>INS-{String(inspection.inspection_id).padStart(5, "0")}</td><td>{inspection.station_code ?? "—"}</td><td>{formatDate(inspection.timestamp)}</td><td className={inspection.result === "CONFORME" ? styles.ok : styles.warning}>{inspection.result.replaceAll("_", " ")}</td><td>{labelType(inspection.nonconformity_type ?? inspection.technical_failure_type)}</td><td>{inspection.confidence ? `${Math.round(inspection.confidence * 100)}%` : "—"}</td></tr>)}</tbody></table></div></PageSection>;
}

export function StationsPage({ stations, onRefresh }: PageData) {
  return <PageSection title="Estações" description="Acompanhe o estado e a conectividade dos dispositivos de inspeção." onRefresh={onRefresh}><div className={styles.stationGrid}>{stations.map((station) => { const online = station.status?.connection === "ONLINE"; return <article className={styles.stationCard} key={station.id}><div className={styles.stationHeader}><Radio size={19} /><span className={online ? styles.online : styles.offline}>{online ? "Online" : "Offline"}</span></div><h3>{station.name}</h3><p>{station.code} · {station.device_id}</p><small>Sensor: {station.status?.sensor ?? "Sem status"} · Câmera: {station.status?.camera ?? "Sem status"} · Processamento: {station.status?.processing ?? "Sem status"}</small></article>; })}</div></PageSection>;
}

export function AlarmsPage({ alarms, stations, onRefresh, onAcknowledgeAlarm }: PageData) {
  const acknowledge = async (alarm: Alarm) => { const responsible = window.prompt("Informe o responsável pelo reconhecimento:"); if (responsible?.trim()) await onAcknowledgeAlarm(alarm.id, responsible.trim()); };
  return <PageSection title="Alarmes" description="Visualize eventos não conformes e alertas que exigem atenção." onRefresh={onRefresh}><div className={styles.alarmList}>{alarms.map((alarm) => <article className={styles.alarm} key={alarm.id}><div className={styles.alarmIcon}><ShieldAlert size={20} /></div><div><h3>{labelType(alarm.alarm_type)}</h3><p>{stations.find((station) => station.id === alarm.station_id)?.name ?? "Estação desconhecida"} · Taxa {alarm.rate.toLocaleString("pt-BR")}% (limite: {alarm.threshold.toLocaleString("pt-BR")}%)</p>{alarm.acknowledged_by && <small>Reconhecido por {alarm.acknowledged_by}</small>}</div><time>{formatDate(alarm.created_at)}</time>{alarm.status === "ABERTO" && <button className={styles.ackButton} type="button" onClick={() => void acknowledge(alarm)}>Reconhecer</button>}</article>)}</div></PageSection>;
}

function PageSection({ title, description, children, onRefresh }: { title: string; description: string; children: ReactNode; onRefresh: () => void }) {
  return <section className={styles.pageSection}><div className={styles.pageIntro}><div><p className={styles.eyebrow}>CENTRO DE OPERAÇÕES</p><h2>{title}</h2><p>{description}</p></div><button className={styles.refreshButton} type="button" onClick={onRefresh}>Atualizar</button></div>{children}</section>;
}
