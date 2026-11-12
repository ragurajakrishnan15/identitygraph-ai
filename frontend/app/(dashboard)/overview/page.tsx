"use client";
import Link from "next/link";
import { ChannelBars, TierPie, TrendChart } from "@/components/charts";
import { Card, PageHeader, State, Stat, TierBadge } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import { pct } from "@/lib/utils";

export default function Overview() {
  const s = useApi(() => api.overview(), []);
  return (
    <>
      <PageHeader title="Overview" subtitle="Synthetic applications scored by the IdentityGraph model (simulated decisions)" />
      <State s={s}>
        {(o) => {
          const hi = o.tiers.High ?? 0, med = o.tiers.Medium ?? 0;
          return (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <Stat label="Applications" value={o.total.toLocaleString()} />
                <Stat label="High risk" value={hi.toLocaleString()} tone="danger" hint={pct(hi / Math.max(o.total, 1)) + " of total"} />
                <Stat label="Medium risk" value={med.toLocaleString()} tone="warn" hint={pct(med / Math.max(o.total, 1)) + " of total"} />
                <Stat label="Avg score" value={o.avg_score.toFixed(3)} hint="uncalibrated, not a probability" />
              </div>
              <div className="grid gap-4 lg:grid-cols-3">
                <Card title="Volume & average score by month" className="lg:col-span-2"><TrendChart data={o.trend} /></Card>
                <Card title="Risk tier distribution"><TierPie tiers={o.tiers} /></Card>
              </div>
              <div className="grid gap-4 lg:grid-cols-3">
                <Card title="Tiers by channel"><ChannelBars rows={o.channels} /></Card>
                <Card title="Highest-scoring cases" className="lg:col-span-2" action={<Link href="/applications" className="text-xs text-accent-soft">View all</Link>}>
                  <table className="w-full">
                    <thead><tr><th className="th">Application</th><th className="th">Name</th><th className="th">Score</th><th className="th">Tier</th></tr></thead>
                    <tbody>
                      {o.top_cases.map((a) => (
                        <tr key={a.application_id} className="border-t border-navy-700">
                          <td className="td"><Link className="text-accent-soft" href={`/applications/${a.application_id}`}>{a.application_id}</Link></td>
                          <td className="td">{a.full_name}</td>
                          <td className="td">{a.score?.display_score}</td>
                          <td className="td">{a.score && <TierBadge tier={a.score.tier} />}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </Card>
              </div>
              <p className="text-xs text-slate-500">Scores are in-sample for train-period rows; see Model Performance for chronological held-out results.</p>
            </div>
          );
        }}
      </State>
    </>
  );
}
