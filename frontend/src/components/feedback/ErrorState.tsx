import { AlertCircle, RefreshCw } from "lucide-react";

import styles from "./ErrorState.module.scss";

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

/** Estado visual padronizado para falhas de carregamento ou comunicação. */
export function ErrorState({
  title = "Não foi possível carregar os dados",
  message = "Ocorreu um erro inesperado. Tente novamente em alguns instantes.",
  onRetry,
}: ErrorStateProps) {
  return (
    <section className={styles.container} role="alert" aria-live="polite">
      <div className={styles.icon} aria-hidden="true">
        <AlertCircle size={28} strokeWidth={1.8} />
      </div>
      <h2>{title}</h2>
      <p>{message}</p>
      {onRetry && (
        <button className={styles.retry} type="button" onClick={onRetry}>
          <RefreshCw size={15} aria-hidden="true" />
          Tentar novamente
        </button>
      )}
    </section>
  );
}
