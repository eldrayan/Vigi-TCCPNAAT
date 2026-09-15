/**
 * Descrição: Exibe a navegação principal e a identidade visual do dashboard.
 * Autor: Leôncio Ferreira
 */

import type { LucideIcon } from "lucide-react";

import logo from "../assets/vigi-symbol.svg";
import styles from "./Sidebar.module.scss";

interface NavigationItem {
  label: string;
  icon: LucideIcon;
}
interface SidebarProps {
  activePage: string;
  items: NavigationItem[];
  onNavigate: (page: string) => void;
}

export function Sidebar({ activePage, items, onNavigate }: SidebarProps) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <div className={styles.brandMark}>
          <img src={logo} alt="" />
          <strong>VIGI</strong>
        </div>
        <span>VISÃO INTELIGENTE PARA GARANTIA DE INSPEÇÃO</span>
      </div>
      <nav aria-label="Navegação principal">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <a
              className={activePage === item.label ? styles.activeLink : ""}
              href={`#${item.label.toLowerCase()}`}
              key={item.label}
              onClick={(event) => {
                event.preventDefault();
                onNavigate(item.label);
              }}
            >
              <span aria-hidden="true">
                <Icon size={18} strokeWidth={1.7} />
              </span>
              {item.label}
            </a>
          );
        })}
      </nav>
    </aside>
  );
}
