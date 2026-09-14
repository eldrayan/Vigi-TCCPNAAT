/**
 * Descrição: Exibe os controles de paginação do histórico de inspeções.
 * Autor: Leôncio Ferreira
 */

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from "lucide-react";

import styles from "./Pagination.module.scss";

interface PaginationProps {
  total: number;
  limit: number;
  offset: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
}

function visiblePages(current: number, total: number): number[] {
  const start = Math.max(1, Math.min(current - 2, total - 4));
  const end = Math.min(total, start + 4);
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}

export function Pagination({ total, limit, offset, onPageChange, onPageSizeChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const currentPage = Math.floor(offset / limit) + 1;
  const start = total === 0 ? 0 : offset + 1;
  const end = Math.min(offset + limit, total);
  const change = (page: number) => onPageChange(page);

  return (
    <nav className={styles.container} aria-label="Paginação das inspeções">
      <button type="button" aria-label="Primeira página" disabled={currentPage === 1} onClick={() => change(1)}>
        <ChevronsLeft size={16} />
      </button>
      <button
        type="button"
        aria-label="Página anterior"
        disabled={currentPage === 1}
        onClick={() => change(currentPage - 1)}
      >
        <ChevronLeft size={16} />
      </button>
      {visiblePages(currentPage, totalPages).map((page) => (
        <button
          className={page === currentPage ? styles.selected : ""}
          key={page}
          type="button"
          aria-current={page === currentPage ? "page" : undefined}
          onClick={() => change(page)}
        >
          {page}
        </button>
      ))}
      <button
        type="button"
        aria-label="Próxima página"
        disabled={currentPage === totalPages}
        onClick={() => change(currentPage + 1)}
      >
        <ChevronRight size={16} />
      </button>
      <button
        type="button"
        aria-label="Última página"
        disabled={currentPage === totalPages}
        onClick={() => change(totalPages)}
      >
        <ChevronsRight size={16} />
      </button>
      <span>
        {start} - {end} de {total}
      </span>
      <select
        aria-label="Itens por página"
        value={limit}
        onChange={(event) => onPageSizeChange(Number(event.target.value))}
      >
        <option value={10}>10</option>
        <option value={20}>20</option>
        <option value={50}>50</option>
        <option value={100}>100</option>
      </select>
    </nav>
  );
}
