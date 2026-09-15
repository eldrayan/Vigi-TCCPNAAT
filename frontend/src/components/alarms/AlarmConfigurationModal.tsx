/**
 * Descrição: Configura o nome e o limite percentual de um alarme do lote ativo.
 * Autor: Leôncio Ferreira
 */

import { useState, type FormEvent } from "react";

import styles from "./AlarmModal.module.scss";

interface AlarmConfigurationModalProps {
  onClose: () => void;
  onSave: (name: string, limit: number) => Promise<void>;
}

export function AlarmConfigurationModal({ onClose, onSave }: AlarmConfigurationModalProps) {
  const [name, setName] = useState("Alarme de qualidade");
  const [limit, setLimit] = useState("20");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    const value = Number(limit);
    if (!name.trim() || !Number.isFinite(value) || value < 0 || value > 100) return;
    setSubmitting(true);
    try {
      await onSave(name.trim(), value);
      onClose();
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
          <p>LOTE ATIVO · ESTAÇÃO 01</p>
          <h2 id="alarm-config-title">Configurar alarme</h2>
        </div>
        <form onSubmit={(event) => void submit(event)}>
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
          <div className={styles.actions}>
            <button type="button" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" disabled={submitting}>
              {submitting ? "Salvando…" : "Salvar limite"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
