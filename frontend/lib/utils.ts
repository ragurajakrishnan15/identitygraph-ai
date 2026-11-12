import clsx, { type ClassValue } from "clsx";
import type { Tier } from "@/types/application";

export const cn = (...a: ClassValue[]) => clsx(a);
export const money = (n: number) => `$${Math.round(n).toLocaleString()}`;
export const pct = (n: number, d = 1) => `${(n * 100).toFixed(d)}%`;
export const fmtDate = (s: string) => new Date(s).toLocaleString();

export const TIER_STYLE: Record<Tier, string> = {
  Low: "bg-safe/15 text-safe border-safe/30",
  Medium: "bg-warn/15 text-warn border-warn/30",
  High: "bg-danger/15 text-danger border-danger/30",
};
export const TIER_COLOR: Record<Tier, string> = { Low: "#2dd4bf", Medium: "#fbbf24", High: "#fb7185" };

export function downloadCsv(filename: string, rows: Record<string, unknown>[]) {
  if (!rows.length) return;
  const cols = Object.keys(rows[0]);
  const esc = (v: unknown) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\n");
  const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
