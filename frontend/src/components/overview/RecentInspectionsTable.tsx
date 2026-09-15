/**
 * Descrição: Exibe as últimas inspeções e permite abrir seus detalhes.
 * Autor: Leôncio Ferreira
 */

import { CheckCircle2, Eye, XCircle } from "lucide-react";

import type { Inspection } from "../../lib/api";
import { formatDate, labelType } from "../../lib/formatters";
import styles from "./OverviewPage.module.scss";

interface RecentInspectionsTableProps {
  inspections: Inspection[];
  onSelect: (inspection: Inspection) => void;
}

export function RecentInspectionsTable({ inspections, onSelect }: RecentInspectionsTableProps) {
  return (
    <div className={styles.recentTableWrap}>
      <table className={styles.recentTable}>
        <thead>
          <tr>
            <th>Hora</th>
            <th>Estação</th>
            <th>Conformidade</th>
            <th>Tipo</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {inspections.length === 0 ? (
            <tr>
              <td className={styles.emptyRow} colSpan={5}>
                Nenhuma inspeção encontrada no filtro selecionado.
              </td>
            </tr>
          ) : (
            inspections.map((inspection) => {
              const compliant = inspection.result === "CONFORME";
              return (
                <tr key={inspection.inspection_id}>
                  <td>{formatDate(inspection.timestamp).split(", ")[1]}</td>
                  <td>{inspection.station_code ?? "—"}</td>
                  <td>
                    <span className={compliant ? styles.badgeOk : styles.badgeDanger}>
                      {compliant ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                      {compliant ? "Conforme" : "Não conforme"}
                    </span>
                  </td>
                  <td>
                    {compliant ? "—" : labelType(inspection.nonconformity_type ?? inspection.technical_failure_type)}
                  </td>
                  <td>
                    <button type="button" onClick={() => onSelect(inspection)}>
                      <Eye size={13} />
                      Ver detalhes
                    </button>
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );
}
