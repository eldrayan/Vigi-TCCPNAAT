/**
 * Descrição: Solicita o reconhecimento explícito de um alarme crítico aberto.
 * Autor: Leôncio Ferreira
 */

import { ShieldAlert } from "lucide-react";
import { useState } from "react";

import type { Alarm } from "../../lib/api";
import styles from "./AlarmModal.module.scss";

interface ActiveAlarmModalProps {
  alarm: Alarm;
  onConfirm: (alarmId: number, responsible: string) => Promise<void>;
  onClose?: () => void;
}

export function ActiveAlarmModal({ alarm, onConfirm, onClose }: ActiveAlarmModalProps) {
  const [responsible, setResponsible] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const confirm = async () => {
    if (!responsible.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await onConfirm(alarm.id, responsible.trim());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Falha ao reconhecer o alarme.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.backdrop} role="presentation" onMouseDown={onClose}>
      <section
        className={styles.alertModal}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="active-alarm-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <ShieldAlert size={28} />
        <p>Alarme ativo</p>
        <h2 id="active-alarm-title">{alarm.name}</h2>
        <span>
          Taxa atual: {alarm.rate.toLocaleString("pt-BR")}% · Limite: {alarm.threshold.toLocaleString("pt-BR")}%
        </span>
        <label>
          Responsável pelo reconhecimento
          <input
            autoFocus
            value={responsible}
            onChange={(event) => setResponsible(event.target.value)}
            placeholder="Seu nome"
          />
        </label>
        {error && <p className={styles.failure} role="alert">{error}</p>}
        <button type="button" disabled={!responsible.trim() || submitting} onClick={() => void confirm()}>
          {submitting ? "Confirmando…" : "Reconhecer e confirmar"}
        </button>
        {onClose && (
          <button type="button" className={styles.cancelBtn} disabled={submitting} onClick={onClose}>
            Cancelar
          </button>
        )}
      </section>
    </div>
  );
}
