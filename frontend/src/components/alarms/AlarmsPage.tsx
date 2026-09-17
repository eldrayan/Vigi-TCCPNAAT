/**
 * Descrição: Permite configurar e reconhecer os alarmes operacionais.
 * Autor: Leôncio Ferreira
 */

import { CheckCircle2, ShieldAlert } from "lucide-react";
import { useState } from "react";

import type { PageData } from "../../app/page-types";
import type { Alarm } from "../../lib/api";
import { formatDate } from "../../lib/formatters";
import { PageSection } from "../layout/PageSection";
import { ActiveAlarmModal } from "./ActiveAlarmModal";
import { AlarmConfigurationModal } from "./AlarmConfigurationModal";
import styles from "./AlarmsPage.module.scss";

export function AlarmsPage({ alarms, stations, onAcknowledgeAlarm, onConfigureAlarm }: PageData) {
  const [configuring, setConfiguring] = useState(false);
  const [acknowledgingAlarm, setAcknowledgingAlarm] = useState<Alarm | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  return (
    <>
      <PageSection
        title="Alarmes"
        description="Visualize eventos não conformes e alertas que exigem atenção."
        action={
          <button className={styles.configure} type="button" onClick={() => setConfiguring(true)}>
            Configurar alarme
          </button>
        }
      >
        {feedback && (
          <p className={styles.success} role="status" aria-live="polite" aria-atomic="true">
            <CheckCircle2 size={16} aria-hidden="true" />
            {feedback}
          </p>
        )}
        <div className={styles.list}>
          {alarms.length === 0 && (
            <p className={styles.empty} role="status">
              Nenhum alarme disparado. As regras configuradas serão exibidas aqui quando o limite for excedido.
            </p>
          )}
          {alarms.map((alarm) => (
            <article className={styles.alarm} key={alarm.id}>
              <div className={styles.icon}>
                <ShieldAlert size={20} />
              </div>
              <div>
                <h3>{alarm.name}</h3>
                <p>
                  {stations.find((station) => station.id === alarm.station_id)?.name ?? "Estação desconhecida"} · Taxa{" "}
                  {alarm.rate.toLocaleString("pt-BR")}% (limite: {alarm.threshold.toLocaleString("pt-BR")}%)
                </p>
                {alarm.acknowledged_by && <small>Reconhecido por {alarm.acknowledged_by}</small>}
              </div>
              <time>{formatDate(alarm.created_at)}</time>
              {alarm.status === "ABERTO" && (
                <button className={styles.acknowledge} type="button" onClick={() => setAcknowledgingAlarm(alarm)}>
                  Reconhecer
                </button>
              )}
            </article>
          ))}
        </div>
      </PageSection>
      {configuring && (
        <AlarmConfigurationModal
          stations={stations}
          onClose={() => setConfiguring(false)}
          onSave={async (name, limit, stationId) => {
            setFeedback(null);
            await onConfigureAlarm(name, limit, stationId);
            setFeedback(`Regra “${name}” configurada com sucesso.`);
          }}
        />
      )}
      {acknowledgingAlarm && (
        <ActiveAlarmModal
          alarm={acknowledgingAlarm}
          onConfirm={async (id, responsible) => {
            await onAcknowledgeAlarm(id, responsible);
            setAcknowledgingAlarm(null);
          }}
          onClose={() => setAcknowledgingAlarm(null)}
        />
      )}
    </>
  );
}
