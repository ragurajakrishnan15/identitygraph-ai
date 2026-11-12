"use client";
import { ArrowDown, ArrowUp, ExternalLink, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { CaseView } from "@/components/applications/CaseView";
import { Card, PageHeader, State, TierBadge } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import { fmtDate, money } from "@/lib/utils";

const SORTS = [["timestamp", "Date"], ["score", "Score"], ["income", "Income"], ["credit", "Requested"]] as const;

export default function Applications() {
  const [q, setQ] = useState("");
  const [dq, setDq] = useState("");
  const [tier, setTier] = useState("");
  const [channel, setChannel] = useState("");
  const [sort, setSort] = useState<string>("score");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(1);
  const [open, setOpen] = useState<string | null>(null);
  const size = 15;

  useEffect(() => { const t = setTimeout(() => { setDq(q); setPage(1); }, 300); return () => clearTimeout(t); }, [q]);
  const s = useApi(() => api.applications({ q: dq, tier, channel, sort, order, page, page_size: size }), [dq, tier, channel, sort, order, page]);

  return (
    <>
      <PageHeader title="Application Explorer" subtitle="Search, filter and sort scored synthetic applications" />
      <Card className="mb-4">
        <div className="grid gap-3 md:grid-cols-5">
          <input className="input md:col-span-2" placeholder="Search id, name, email, device, phone…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search" />
          <select className="input" value={tier} onChange={(e) => { setTier(e.target.value); setPage(1); }} aria-label="Tier">
            <option value="">All tiers</option>{["Low", "Medium", "High"].map((t) => <option key={t}>{t}</option>)}
          </select>
          <select className="input" value={channel} onChange={(e) => { setChannel(e.target.value); setPage(1); }} aria-label="Channel">
            <option value="">All channels</option>{["web", "mobile", "branch", "partner"].map((t) => <option key={t}>{t}</option>)}
          </select>
          <div className="flex gap-2">
            <select className="input" value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Sort by">
              {SORTS.map(([k, l]) => <option key={k} value={k}>{l}</option>)}
            </select>
            <button className="btn-ghost" onClick={() => setOrder(order === "desc" ? "asc" : "desc")} aria-label="Toggle sort order">
              {order === "desc" ? <ArrowDown size={14} /> : <ArrowUp size={14} />}
            </button>
          </div>
        </div>
      </Card>
      <State s={s}>
        {(p) => {
          const pages = Math.max(1, Math.ceil(p.total / size));
          return (
            <Card>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead><tr>{["Application", "Name", "Channel", "Income", "Requested", "Submitted", "Score", "Tier"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
                  <tbody>
                    {p.items.map((a) => (
                      <tr key={a.application_id} className="cursor-pointer border-t border-navy-700 hover:bg-navy-700/50" onClick={() => setOpen(a.application_id)}>
                        <td className="td text-accent-soft">{a.application_id}</td>
                        <td className="td">{a.full_name}</td>
                        <td className="td">{a.application_channel}</td>
                        <td className="td">{money(a.annual_income)}</td>
                        <td className="td">{money(a.requested_credit)}</td>
                        <td className="td whitespace-nowrap">{fmtDate(a.application_timestamp)}</td>
                        <td className="td">{a.score?.display_score ?? "-"}</td>
                        <td className="td">{a.score && <TierBadge tier={a.score.tier} />}</td>
                      </tr>
                    ))}
                    {p.items.length === 0 && <tr><td className="td text-slate-500" colSpan={8}>No applications match.</td></tr>}
                  </tbody>
                </table>
              </div>
              <div className="mt-3 flex items-center justify-between text-sm text-slate-400">
                <span>{p.total.toLocaleString()} results</span>
                <div className="flex items-center gap-2">
                  <button className="btn-ghost" disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</button>
                  <span>Page {page} / {pages}</span>
                  <button className="btn-ghost" disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</button>
                </div>
              </div>
            </Card>
          );
        }}
      </State>

      {open && (
        <div className="fixed inset-0 z-40 flex justify-end bg-black/60" onClick={() => setOpen(null)}>
          <aside className="h-full w-full max-w-2xl overflow-y-auto border-l border-navy-600 bg-navy-900 p-5" onClick={(e) => e.stopPropagation()}>
            <div className="mb-3 flex justify-between">
              <Link href={`/applications/${open}`} className="btn-ghost"><ExternalLink size={14} /> Open full page</Link>
              <button className="btn-ghost" onClick={() => setOpen(null)} aria-label="Close"><X size={14} /></button>
            </div>
            <CaseView id={open} />
          </aside>
        </div>
      )}
    </>
  );
}
