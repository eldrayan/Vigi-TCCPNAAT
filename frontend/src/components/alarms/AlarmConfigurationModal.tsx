/**
 * Descrição: Configura o nome e o limite percentual de um alarme do lote ativo.
 * Autor: Leôncio Ferreira
 */

import { useState, type FormEvent } from "react";

import type { Station } from "../../lib/api";
import styles from "./AlarmModal.module.scss";

interface AlarmConfigurationModalProps {
  stations: Station[];
  onClose: () => void;
  onSave: (name: string, limit: number, stationId: number) => Promise<void>;
}

export function AlarmConfigurationModal({ stations, onClose, onSave }: AlarmConfigurationModalProps) {
  const [name, setName] = useState("Alarme de qualidade");
  const [limit, setLimit] = useState("20");
  const [stationId, setStationId] = useState(() => String(stations[0]?.id ?? ""));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const value = Number(limit);
    const selectedStationId = Number(stationId);
    if (!name.trim() || !Number.isFinite(value) || value < 0 || value > 100 || !selectedStationId) return;
    setSubmitting(true);
    setError(null);
    try {
      await onSave(name.trim(), value, selectedStationId);
      onClose();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Não foi possível configurar o alarme.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.backdrop} role="presentation" onMouseDown={onClose}>
      <section
        className={styles.configModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="alarm-config-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div>
          <p>LOTE ATIVO · ESTAÇÃO SELECIONADA</p>
          <h2 id="alarm-config-title">Configurar alarme</h2>
        </div>
        <form onSubmit={(event) => void submit(event)} aria-busy={submitting}>
          <label>
            Estação
            <select value={stationId} onChange={(event) => setStationId(event.target.value)} required>
              {stations.map((station) => (
                <option key={station.id} value={station.id}>
                  {station.name} · {station.code}
                </option>
              ))}
            </select>
            <small>O alarme será associado ao lote ativo dessa estação.</small>
          </label>
          <label>
            Nome do alarme
            <input value={name} maxLength={100} onChange={(event) => setName(event.target.value)} required />
          </label>
          <label>
            Limite de não conformidade (%)
            <input
              type="number"
              value={limit}
              min="0"
              max="100"
              step="0.1"
              onChange={(event) => setLimit(event.target.value)}
              required
            />
          </label>
          {error && (
            <p className={styles.failure} role="alert">
              {error}
            </p>
          )}
          <div className={styles.actions}>
            <button type="button" onClick={onClose} disabled={submitting}>
              Cancelar
            </button>
            <button type="submit" disabled={submitting || stations.length === 0}>
              {submitting ? "Salvando…" : "Salvar regra"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
