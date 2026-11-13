"use client";
import { AlertTriangle, FlaskConical, Loader2 } from "lucide-react";
import type { ReactNode } from "react";
import type { Tier } from "@/types/application";
import { cn, TIER_STYLE } from "@/lib/utils";

export function TierBadge({ tier }: { tier: Tier }) {
  return <span className={cn("inline-block rounded-full border px-2 py-0.5 text-xs font-medium", TIER_STYLE[tier])}>{tier}</span>;
}

export function Card({ title, children, className, action }: { title?: string; children: ReactNode; className?: string; action?: ReactNode }) {
  return (
    <section className={cn("card", className)}>
      {(title || action) && (
        <header className="mb-4 flex items-center justify-between">
          {title && <h3 className="text-[15px] font-semibold tracking-tight text-ink">{title}</h3>}
          {action}
        </header>
      )}
      {children}
    </section>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-10 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-4xl font-semibold tracking-tightest text-ink md:text-5xl">{title}</h1>
        {subtitle && <p className="mt-3 max-w-2xl text-base text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}

export function Stat({ label, value, hint, tone }: { label: string; value: ReactNode; hint?: string; tone?: "safe" | "warn" | "danger" }) {
  const color = tone === "safe" ? "text-safe" : tone === "warn" ? "text-warn" : tone === "danger" ? "text-danger" : "text-ink";
  return (
    <div className="card">
      <div className="text-xs font-medium text-muted">{label}</div>
      <div className={cn("mt-2 text-4xl font-semibold tracking-tightest", color)}>{value}</div>
      {hint && <div className="mt-1 text-xs text-subtle">{hint}</div>}
    </div>
  );
}

export function SimulatedBanner() {
  return (
    <div role="status" className="mb-4 flex items-center gap-2 rounded-2xl border border-warn/30 bg-warn/10 px-4 py-3 text-sm text-warn">
      <FlaskConical size={16} /> Backend unreachable: showing SIMULATED mock data, not model results. Start the API (see README).
    </div>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 py-10 text-sm text-muted">
      <Loader2 className="animate-spin" size={16} /> {label}
    </div>
  );
}

export function ErrorBox({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex items-center justify-between gap-3 rounded-2xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
      <span className="flex items-center gap-2"><AlertTriangle size={16} /> {message}</span>
      {onRetry && <button className="btn-ghost" onClick={onRetry}>Retry</button>}
    </div>
  );
}

/** Standard loading / error / simulated wrapper for an useApi() result. */
export function State<T>({ s, children }: { s: { data: T | null; loading: boolean; error: string | null; simulated: boolean; reload: () => void }; children: (d: T) => ReactNode }) {
  if (s.loading && !s.data) return <Loading />;
  if (s.error) return <ErrorBox message={s.error} onRetry={s.reload} />;
  if (!s.data) return null;
  return (
    <>
      {s.simulated && <SimulatedBanner />}
      {children(s.data)}
    </>
  );
}

export const SimulatedNote = ({ children }: { children: ReactNode }) => (
  <p className="mt-3 text-xs text-subtle">{children}</p>
);
