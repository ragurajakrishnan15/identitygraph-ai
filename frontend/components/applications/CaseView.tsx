"use client";
import Link from "next/link";
import { useState } from "react";
import { Card, State, TierBadge } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import { cn, fmtDate, money } from "@/lib/utils";

export function CaseView({ id }: { id: string }) {
  const s = useApi(() => api.application(id), [id]);
  const [note, setNote] = useState("");
  const [extra, setExtra] = useState<{ id: number; note: string; created_at: string }[] | null>(null);
  const [saving, setSaving] = useState(false);
  const [noteErr, setNoteErr] = useState<string | null>(null);

  async function addNote() {
    if (!note.trim()) return;
    setSaving(true); setNoteErr(null);
    try {
      const r = await api.addNote(id, note.trim());
      setExtra(r.notes); setNote("");
    } catch (e) {
      setNoteErr((e as Error).message || "Could not save note (is the API running?)");
    } finally { setSaving(false); }
  }

  return (
    <State s={s}>
      {(a) => {
        const notes = extra ?? a.notes ?? [];
        return (
          <div className="space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <h2 className="text-xl font-semibold text-ink">{a.application_id}</h2>
              {a.score && <TierBadge tier={a.score.tier} />}
              {a.score && <span className="text-sm text-muted">score {a.score.display_score}/100</span>}
              {a.source === "online" && <span className="rounded border border-accent/40 px-2 text-xs text-accent">online-scored</span>}
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <Card title="Profile">
                <dl className="grid grid-cols-[110px_1fr] gap-y-1 text-sm">
                  {([["Name", a.full_name], ["DOB", a.date_of_birth], ["Email", a.email], ["Phone", a.phone], ["Address", a.address],
                    ["Device", a.device_id], ["IP", a.ip_address], ["Employment", a.employment_status],
                    ["Income", money(a.annual_income)], ["Requested", money(a.requested_credit)], ["Channel", a.application_channel],
                    ["Submitted", fmtDate(a.application_timestamp)]] as const).map(([k, v]) => (
                    <div key={k} className="contents"><dt className="text-subtle">{k}</dt><dd className="break-all">{v}</dd></div>
                  ))}
                </dl>
                {a.fraud_scenario && (
                  <p className="mt-3 text-xs text-subtle">Synthetic ground truth (training only): {a.fraud_scenario} / label {a.fraud_label}</p>
                )}
              </Card>
              <Card title="Risk assessment">
                {a.score ? (
                  <>
                    <p className="text-sm">{a.score.recommendation}</p>
                    <p className="mt-1 text-xs text-subtle">Model {a.score.model_version}; uncalibrated score {a.score.score.toFixed(3)}. Simulated output.</p>
                    <ul className="mt-3 space-y-2 text-sm">
                      {a.score.factors.map((f) => (
                        <li key={f.feature} className="flex justify-between gap-3">
                          <span>{f.description}</span>
                          <span className={cn("shrink-0 text-xs", f.contribution > 0 ? "text-danger" : "text-safe")}>{f.direction}</span>
                        </li>
                      ))}
                    </ul>
                    <p className="mt-3 text-xs text-subtle">Factors are associations, not proof.</p>
                  </>
                ) : <p className="text-sm text-muted">Not scored.</p>}
              </Card>
              <Card title="Linked entities (graph links)">
                <ul className="space-y-1 text-sm">
                  {(a.linked_entities ?? []).map((l) => (
                    <li key={l.entity_id} className="flex justify-between gap-2">
                      <Link className="text-accent" href={`/network?focus=${encodeURIComponent(l.entity_id)}`}>{l.kind}: {l.label}</Link>
                      <span className={l.shared_with_other_applications > 0 ? "text-warn" : "text-subtle"}>{l.shared_with_other_applications} other app(s)</span>
                    </li>
                  ))}
                </ul>
                <p className="mt-3 text-xs text-subtle">Connections are investigation signals, not proof of fraud.</p>
              </Card>
              <Card title="Activity timeline">
                <ol className="space-y-2 border-l border-line pl-4 text-sm">
                  {(a.timeline ?? []).map((t, i) => (
                    <li key={i}><div>{t.event}</div><div className="text-xs text-subtle">{fmtDate(t.at)}</div></li>
                  ))}
                </ol>
              </Card>
            </div>
            <Card title="Investigation notes">
              <div className="flex gap-2">
                <input className="input" placeholder="Add a note…" value={note} onChange={(e) => setNote(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && addNote()} />
                <button className="btn" onClick={addNote} disabled={saving || !note.trim()}>Add</button>
              </div>
              {noteErr && <p className="mt-2 text-xs text-danger">{noteErr}</p>}
              <ul className="mt-3 space-y-2 text-sm">
                {notes.map((n) => <li key={n.id} className="rounded border border-line p-2">{n.note}<div className="text-xs text-subtle">{fmtDate(n.created_at)}</div></li>)}
                {notes.length === 0 && <li className="text-subtle">No notes yet.</li>}
              </ul>
            </Card>
          </div>
        );
      }}
    </State>
  );
}
