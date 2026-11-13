"use client";
import { HBars, HistBars } from "@/components/charts";
import { Card, PageHeader, State, Stat } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import { cn, fmtDate } from "@/lib/utils";

const tone = (s: string) => (s === "stable" || s === "pass" ? "text-safe" : s === "moderate" ? "text-warn" : "text-danger");

export default function Monitoring() {
  const s = useApi(() => api.monitoring(), []);
  return (
    <>
      <PageHeader title="Monitoring" subtitle="Data quality, drift (PSI) and score distribution" />
      <State s={s}>
        {(m) => {
          const miss = Object.entries(m.quality.missingness).map(([k, v]) => ({ field: k, missing: v })).filter((x) => x.missing > 0);
          return (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <Stat label="Data quality" value={m.quality.status.toUpperCase()} tone={m.quality.status === "pass" ? "safe" : "danger"} hint={`${m.quality.n_rows.toLocaleString()} rows checked`} />
                <Stat label="Score PSI" value={m.score_psi.psi.toFixed(3)} tone={m.score_psi.status === "stable" ? "safe" : m.score_psi.status === "moderate" ? "warn" : "danger"} hint={m.score_psi.status} />
                <Stat label="Drifted features" value={m.feature_drift.filter((d) => d.status !== "stable").length} hint="PSI ≥ 0.10" />
                <Stat label="Held-out PR-AUC" value={m.label_performance.pr_auc_test?.toFixed(3) ?? "n/a"} hint="labels matured (synthetic)" />
              </div>
              <p className="text-xs text-subtle">Generated {fmtDate(m.generated_at)} · model {m.model_version} · mode: {m.mode}. {m.label_performance.note}</p>
              <div className="grid gap-4 lg:grid-cols-2">
                <Card title="Feature drift (PSI, train → test)">
                  <HBars data={m.feature_drift.slice(0, 14)} xKey="psi" yKey="feature" color="#ff9f0a" />
                  <p className="mt-2 text-xs text-subtle">&lt;0.10 stable · 0.10–0.25 moderate · &gt;0.25 significant</p>
                </Card>
                <div className="space-y-4">
                  <Card title="Score distribution (test)"><HistBars data={m.score_distribution} xKey="bin" yKey="count" /></Card>
                  <Card title="Tier distribution">
                    <div className="flex gap-6 text-sm">{Object.entries(m.tier_distribution).map(([k, v]) => <div key={k}><div className="text-xl font-semibold text-ink">{v.toLocaleString()}</div><div className="text-xs text-muted">{k}</div></div>)}</div>
                  </Card>
                </div>
              </div>
              <Card title="Missingness">
                {miss.length === 0 ? <p className="text-sm text-safe">No missing values in monitored fields.</p> : (
                  <ul className="text-sm">{miss.map((x) => <li key={x.field} className={cn(tone(x.missing > 0.05 ? "fail" : "moderate"))}>{x.field}: {(x.missing * 100).toFixed(2)}%</li>)}</ul>
                )}
              </Card>
              <Card title="Drift table">
                <table className="w-full"><thead><tr><th className="th">Feature</th><th className="th">PSI</th><th className="th">Status</th></tr></thead>
                  <tbody>{m.feature_drift.map((d) => <tr key={d.feature} className="border-t border-line"><td className="td">{d.feature}</td><td className="td">{d.psi.toFixed(3)}</td><td className={cn("td", tone(d.status))}>{d.status}</td></tr>)}</tbody></table>
              </Card>
            </div>
          );
        }}
      </State>
    </>
  );
}
