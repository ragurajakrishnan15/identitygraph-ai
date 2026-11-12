"use client";
import { Download } from "lucide-react";
import { useState } from "react";
import { Card, ErrorBox, PageHeader, State, TierBadge } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import { downloadCsv, money } from "@/lib/utils";

export default function Reports() {
  const [tier, setTier] = useState("High");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const s = useApi(() => api.applications({ tier, sort: "score", order: "desc", page: 1, page_size: 10 }), [tier]);

  async function exportCsv() {
    setBusy(true); setErr(null);
    try {
      const r = await api.applications({ tier, sort: "score", order: "desc", page: 1, page_size: 100 });
      downloadCsv(`identitygraph_${tier.toLowerCase()}_risk_cases.csv`, r.data.items.map((a) => ({
        application_id: a.application_id, name: a.full_name, channel: a.application_channel, income: a.annual_income,
        requested_credit: a.requested_credit, score: a.score?.score, tier: a.score?.tier, recommendation: a.score?.recommendation,
        model_version: a.score?.model_version, simulated: true,
      })));
    } catch (e) { setErr((e as Error).message); } finally { setBusy(false); }
  }

  return (
    <>
      <PageHeader title="Reports & Insights" subtitle="Preview and export the highest-scoring cases (top 100 per export). All simulated."
        action={<button className="btn" onClick={exportCsv} disabled={busy}><Download size={14} /> Export CSV</button>} />
      {err && <ErrorBox message={err} />}
      <div className="mb-4 flex gap-2">
        {["High", "Medium", "Low"].map((t) => <button key={t} className={t === tier ? "btn" : "btn-ghost"} onClick={() => setTier(t)}>{t}</button>)}
      </div>
      <State s={s}>
        {(p) => (
          <Card title={`${tier}-tier cases: preview (${p.total.toLocaleString()} total)`}>
            <table className="w-full">
              <thead><tr>{["Application", "Name", "Requested", "Score", "Tier", "Simulated recommendation"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
              <tbody>{p.items.map((a) => (
                <tr key={a.application_id} className="border-t border-navy-700">
                  <td className="td">{a.application_id}</td><td className="td">{a.full_name}</td><td className="td">{money(a.requested_credit)}</td>
                  <td className="td">{a.score?.display_score}</td><td className="td">{a.score && <TierBadge tier={a.score.tier} />}</td><td className="td">{a.score?.recommendation}</td>
                </tr>))}</tbody>
            </table>
          </Card>
        )}
      </State>
      <p className="mt-4 text-xs text-slate-500">The full model card and evaluation summary live in <code>reports/</code>. Data is synthetic; nothing here is a real credit decision.</p>
    </>
  );
}
