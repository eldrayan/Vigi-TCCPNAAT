/**
 * Descrição: Permite definir a estação fixa e o lote ativo da operação.
 * Autor: Leôncio Ferreira
 */

import { Accessibility, CheckCircle2, Save, Settings } from "lucide-react";
import { FormEvent, useState } from "react";

import type { PageData } from "../../app/page-types";
import { PageSection } from "../layout/PageSection";
import styles from "./SettingsPage.module.scss";

type SettingsPageProps = Pick<PageData, "stations" | "onConfigureContext"> & {
  fontScale: number;
  onFontScaleChange: (scale: number) => void;
};

export function SettingsPage({
  stations,
  onConfigureContext,
  fontScale,
  onFontScaleChange,
}: SettingsPageProps) {
  const station = stations[0];
  const [batchCode, setBatchCode] = useState("");
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [failure, setFailure] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const code = batchCode.trim();
    if (!code || !station) return;
    setSaving(true);
    setFeedback(null);
    setFailure(null);
    try {
      await onConfigureContext(station.code, code);
      setFeedback(`Lote salvo com sucesso: ${code}.`);
    } catch (cause) {
      setFailure(cause instanceof Error ? cause.message : "Não foi possível salvar a configuração.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <PageSection title="Configurações" description="Defina a estação e o lote em operação.">
      <div className={styles.stack}>
        <section className={styles.card} aria-labelledby="operational-context-title">
          <div className={styles.heading}>
            <span className={styles.icon} aria-hidden="true"><Settings size={18} /></span>
            <div>
              <h2 id="operational-context-title">Configuração operacional</h2>
              <p>A configuração será enviada ao dispositivo da estação.</p>
            </div>
          </div>
          <form className={styles.form} onSubmit={handleSubmit} aria-busy={saving}>
            <label htmlFor="active-station">
              Estação ativa
              <input
                id="active-station"
                value={station?.name ?? "Nenhuma estação cadastrada"}
                readOnly
              />
              <small>{station ? `${station.code} · ${station.device_id}` : "Cadastre uma estação pela API."}</small>
            </label>
            <label htmlFor="batch-code">
              Nome do lote
              <input
                id="batch-code"
                value={batchCode}
                onChange={(event) => setBatchCode(event.target.value)}
                placeholder="Ex.: LOTE_01"
                maxLength={100}
                required
              />
            </label>
            <button type="submit" disabled={saving || !station}>
              <Save size={16} />
              {saving ? "Salvando…" : "Salvar configuração"}
            </button>
          </form>
          {feedback && (
            <p className={styles.success} role="status" aria-live="polite" aria-atomic="true">
              <CheckCircle2 size={16} aria-hidden="true" />
              {feedback}
            </p>
          )}
          {failure && <p className={styles.failure} role="alert">{failure}</p>}
        </section>

        <section className={styles.card} aria-labelledby="accessibility-title">
          <div className={styles.heading}>
            <span className={styles.icon} aria-hidden="true"><Accessibility size={18} /></span>
            <div>
              <h2 id="accessibility-title">Acessibilidade</h2>
              <p>Personalize a leitura do dashboard conforme sua necessidade.</p>
            </div>
          </div>
          <div className={styles.fontSize}>
          <div>
              <h3 id="font-size-title">Tamanho da fonte</h3>
              <p>Use os botões ou a barra para diminuir ou aumentar os textos.</p>
            </div>
            <div className={styles.fontControls} aria-labelledby="font-size-title">
              <button
                type="button"
                className={styles.fontLabelSmall}
                onClick={() => onFontScaleChange(Math.max(1, fontScale - 0.1))}
                disabled={fontScale === 1}
                aria-label="Diminuir tamanho da fonte"
              >
                A−
              </button>
              <div className={styles.sliderWrap}>
                <output aria-live="polite">{Math.round(fontScale * 100)}%</output>
                <input
                  type="range"
                  min="1"
                  max="1.2"
                  step="0.1"
                  value={fontScale}
                  onChange={(event) => onFontScaleChange(Number(event.target.value))}
                  aria-label="Tamanho da fonte"
                  aria-valuetext={`${Math.round(fontScale * 100)} por cento`}
                />
              </div>
              <button
                type="button"
                className={styles.fontLabelLarge}
                onClick={() => onFontScaleChange(Math.min(1.2, fontScale + 0.1))}
                disabled={fontScale === 1.2}
                aria-label="Aumentar tamanho da fonte"
              >
                A+
              </button>
            </div>
          </div>
        </section>
      </div>
    </PageSection>
  );
}
