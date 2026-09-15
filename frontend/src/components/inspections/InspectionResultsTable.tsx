/**
 * Descrição: Exibe a tabela paginada do histórico de inspeções.
 * Autor: Leôncio Ferreira
 */

import { CheckCircle2, XCircle } from "lucide-react";

import type { Inspection } from "../../lib/api";
import { formatDate, labelType } from "../../lib/formatters";
import { Pagination } from "./Pagination";
import styles from "./InspectionsPage.module.scss";

interface InspectionResultsTableProps {
  inspections: Inspection[];
  total: number;
  limit: number;
  offset: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

export function InspectionResultsTable({
  inspections,
  total,
  limit,
  offset,
  onPageChange,
  onPageSizeChange,
}: InspectionResultsTableProps) {
  return (
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
        total={total}
        limit={limit}
        offset={offset}
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
      />
    </div>
  );
}
