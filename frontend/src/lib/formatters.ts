/**
 * Descrição: Reúne formatações reutilizadas na exibição de dados do dashboard.
 * Autor: Leôncio Ferreira
 */

export function labelType(type: string | null | undefined): string {
  return type?.replaceAll("_", " ") ?? "—";
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(date);
  } catch {
    return "—";
  }
}

export function formatTime(value: string | null | undefined): string {
  if (!value) return "—";
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return new Intl.DateTimeFormat("pt-BR", {
      timeStyle: "short",
    }).format(date);
  } catch {
    return "—";
  }
}
