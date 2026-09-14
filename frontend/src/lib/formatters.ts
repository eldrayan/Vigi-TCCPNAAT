/**
 * Descrição: Reúne formatações reutilizadas na exibição de dados do dashboard.
 * Autor: Leôncio Ferreira
 */

export function labelType(type: string | null): string {
  return type?.replaceAll("_", " ") ?? "—";
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}
