/**
 * Descrição: Fornece a estrutura comum de título e conteúdo das páginas internas.
 * Autor: Leôncio Ferreira
 */

import type { ReactNode } from "react";

import styles from "./PageSection.module.scss";

interface PageSectionProps {
  title: string;
  description: string;
  children: ReactNode;
  action?: ReactNode;
}

export function PageSection({ title, description, children, action }: PageSectionProps) {
  return (
    <section className={styles.pageSection}>
      <header className={styles.pageIntro}>
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        {action && <div className={styles.pageActions}>{action}</div>}
      </header>
      {children}
    </section>
  );
}
