/**
 * Descrição: Exibe os detalhes técnicos de uma inspeção selecionada.
 * Autor: Leôncio Ferreira
 */

import type { Inspection } from "../../lib/api";
import { formatDate, labelType } from "../../lib/formatters";

import badgeStyles from "./OverviewPage.module.scss";
import styles from "./InspectionDetailModal.module.scss";

interface InspectionDetailModalProps {
  inspection: Inspection;
  onClose: () => void;
}

export function InspectionDetailModal({ inspection, onClose }: InspectionDetailModalProps) {
  const compliant = inspection.result === "CONFORME";
  return (
    <div className={styles.modalBackdrop} role="presentation" onClick={onClose}>
      <section
        className={styles.detailModal}
        role="dialog"
        aria-modal="true"
        aria-labelledby="inspection-detail-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className={styles.sectionHeading}>
          <h2 id="inspection-detail-title">Detalhes da inspeção</h2>
          <button type="button" onClick={onClose} aria-label="Fechar">
            ×
          </button>
        </header>
        <dl className={styles.detailList}>
          <div>
            <dt>Estação</dt>
            <dd>{inspection.station_code ?? "—"}</dd>
          </div>
          <div>
            <dt>Horário</dt>
            <dd>{formatDate(inspection.timestamp)}</dd>
          </div>
          <div>
            <dt>Resultado</dt>
            <dd>
              <span className={compliant ? badgeStyles.badgeOk : badgeStyles.badgeDanger}>
                {inspection.result.replaceAll("_", " ")}
              </span>
            </dd>
          </div>
          <div>
            <dt>Confiança do modelo</dt>
            <dd>{inspection.confidence ? `${Math.round(inspection.confidence * 100)}%` : "—"}</dd>
          </div>
          {inspection.nonconformity_type && (
            <div>
              <dt>Tipo de não conformidade</dt>
              <dd>{labelType(inspection.nonconformity_type)}</dd>
            </div>
          )}
          {inspection.technical_failure_type && (
            <div>
              <dt>Falha técnica</dt>
              <dd>{labelType(inspection.technical_failure_type)}</dd>
            </div>
          )}
        </dl>
      </section>
    </div>
  );
}
