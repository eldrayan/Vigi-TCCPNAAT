/**
 * Descrição: Permite configurar e reconhecer os alarmes operacionais.
 * Autor: Leôncio Ferreira
 */

import { ShieldAlert } from "lucide-react";
import { useState } from "react";

import type { PageData } from "../../app/page-types";
import type { Alarm } from "../../lib/api";
import { formatDate } from "../../lib/formatters";
import { PageSection } from "../layout/PageSection";
import { AlarmConfigurationModal } from "./AlarmConfigurationModal";
import styles from "./AlarmsPage.module.scss";

export function AlarmsPage({ alarms, stations, onAcknowledgeAlarm, onConfigureAlarm }: PageData) {
  const [configuring, setConfiguring] = useState(false);
  const acknowledge = async (alarm: Alarm) => {
    const responsible = window.prompt("Informe o responsável pelo reconhecimento:");
    if (responsible?.trim()) await onAcknowledgeAlarm(alarm.id, responsible.trim());
  };
  return (
    <>
      <PageSection
        title="Alarmes"
        description="Visualize eventos não conformes e alertas que exigem atenção."
        action={
          <button className={styles.configure} type="button" onClick={() => setConfiguring(true)}>
            Adicionar alarme
          </button>
        }
      >
        <div className={styles.list}>
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
                <button className={styles.acknowledge} type="button" onClick={() => void acknowledge(alarm)}>
                  Reconhecer
                </button>
              )}
            </article>
          ))}
        </div>
      </PageSection>
      {configuring && <AlarmConfigurationModal onClose={() => setConfiguring(false)} onSave={onConfigureAlarm} />}
    </>
  );
}
