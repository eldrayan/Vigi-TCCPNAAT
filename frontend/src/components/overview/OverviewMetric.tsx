/**
 * Descrição: Exibe um indicador resumido da operação.
 * Autor: Leôncio Ferreira
 */

import type { ClipboardCheck } from "lucide-react";

import styles from "./OverviewMetrics.module.scss";

interface OverviewMetricProps {
  icon: typeof ClipboardCheck;
  label: string;
  value: string;
  detail: string;
}

export function OverviewMetric({ icon: Icon, label, value, detail }: OverviewMetricProps) {
  return (
    <article className={styles.metric}>
      <Icon size={18} />
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}
