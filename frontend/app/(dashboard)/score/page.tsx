"use client";
import Link from "next/link";
import { useState } from "react";
import { Card, ErrorBox, PageHeader, SimulatedBanner, TierBadge } from "@/components/ui";
import { api } from "@/lib/api-client";
import { cn, TIER_COLOR } from "@/lib/utils";
import { validateScoreRequest, type FormErrors } from "@/lib/validators";
import type { ScoreRequest, ScoreResponse } from "@/types/scoring";

const EMPTY: ScoreRequest = {
  full_name: "", date_of_birth: "1990-01-01", email: "", phone: "", address: "", device_id: "", ip_address: "",
  employment_status: "employed", annual_income: 70000, requested_credit: 10000, application_channel: "web",
};
const SAMPLE: ScoreRequest = {
  full_name: "Jordan Reed", date_of_birth: "2003-02-14", email: "j.r.99@mail.test", phone: "+1-555-0100100",
  address: "12 Pine St, Unit 4", device_id: "dev-demo-001", ip_address: "203.0.113.7",
  employment_status: "unemployed", annual_income: 18000, requested_credit: 22000, application_channel: "web",
};
/** A real system captures device and IP from the request itself. In this demo they are generated per submission
 *  (documentation IP ranges, random device id) unless the user opens "Advanced" to reuse values on purpose. */
const autoIdentity = () => {
  const r = () => Math.random().toString(36).slice(2, 10);
  return { device_id: `dev-auto-${r()}`, ip_address: `203.0.113.${1 + Math.floor(Math.random() * 254)}` };
};
const STAGES = ["Validating input", "Building point-in-time features", "Scoring model", "Explaining result"];

const Field = ({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) => (
  <label className="block text-xs text-muted">{label}{children}{error && <span className="text-danger">{error}</span>}</label>
);

export default function ScorePage() {
  const [v, setV] = useState<ScoreRequest>(EMPTY);
  const [errs, setErrs] = useState<FormErrors>({});
  const [stage, setStage] = useState(-1);
  const [res, setRes] = useState<ScoreResponse | null>(null);
  const [sim, setSim] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [slow, setSlow] = useState(false);
  const [advanced, setAdvanced] = useState(false);

  const set = <K extends keyof ScoreRequest>(k: K, val: ScoreRequest[K]) => setV((p) => ({ ...p, [k]: val }));
  const txt = (k: keyof ScoreRequest, ph?: string) => (
    <input className="input mt-1" placeholder={ph} value={String(v[k])} onChange={(e) => set(k, e.target.value as never)} />
  );
  const num = (k: "annual_income" | "requested_credit") => (
    <input type="number" className="input mt-1" value={v[k]} onChange={(e) => set(k, Number(e.target.value))} />
  );

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const payload: ScoreRequest = advanced ? v : { ...v, ...autoIdentity() };
    const found = validateScoreRequest(payload);
    setErrs(found);
    if (Object.keys(found).length) return;
    setErr(null); setRes(null); setStage(0);
    const timer = setInterval(() => setStage((s) => Math.min(s + 1, STAGES.length - 1)), 900);
    // The hosted API runs on a small free instance: the first score after idle can take a while.
    const slowTimer = setTimeout(() => setSlow(true), 6000);
    try {
      const r = await api.score(payload);
      setRes(r.data); setSim(r.simulated);
    } catch (x) {
      setErr((x as Error).message);
    } finally {
      clearInterval(timer); clearTimeout(slowTimer); setSlow(false); setStage(-1);
    }
  }

  return (
    <>
      <PageHeader title="Score Application" subtitle="Submit a synthetic application. Labels are never accepted. Result is a simulated recommendation."
        action={<button type="button" className="btn-ghost" onClick={() => { setV(SAMPLE); setErrs({}); setAdvanced(true); }}>Fill suspicious sample</button>} />
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Application">
          <form onSubmit={submit} className="grid grid-cols-2 gap-3" noValidate>
            <Field label="Full name" error={errs.full_name}>{txt("full_name")}</Field>
            <Field label="Date of birth" error={errs.date_of_birth}>{txt("date_of_birth", "YYYY-MM-DD")}</Field>
            <Field label="Email" error={errs.email}>{txt("email")}</Field>
            <Field label="Phone" error={errs.phone}>{txt("phone")}</Field>
            <div className="col-span-2"><Field label="Address" error={errs.address}>{txt("address")}</Field></div>
            <Field label="Employment">
              <select className="input mt-1" value={v.employment_status} onChange={(e) => set("employment_status", e.target.value)}>
                {["employed", "self_employed", "unemployed", "student", "retired"].map((o) => <option key={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="Channel">
              <select className="input mt-1" value={v.application_channel} onChange={(e) => set("application_channel", e.target.value)}>
                {["web", "mobile", "branch", "partner"].map((o) => <option key={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="Annual income ($)" error={errs.annual_income}>{num("annual_income")}</Field>
            <Field label="Requested credit ($)" error={errs.requested_credit}>{num("requested_credit")}</Field>
            <div className="col-span-2">
              <button type="button" className="text-xs text-accent underline-offset-2 hover:underline" aria-expanded={advanced}
                onClick={() => setAdvanced((a) => !a)}>
                {advanced ? "Hide" : "Show"} advanced: device and network
              </button>
              {!advanced && (
                <p className="mt-1 text-xs text-subtle">
                  Device ID and IP address are filled in automatically, as a real website would capture them. Open Advanced to reuse a value from an earlier application and see how links form.
                </p>
              )}
            </div>
            {advanced && (
              <>
                <Field label="Device ID" error={errs.device_id}>{txt("device_id")}</Field>
                <Field label="IP address" error={errs.ip_address}>{txt("ip_address", "1.2.3.4")}</Field>
              </>
            )}
            <div className="col-span-2"><button className="btn w-full justify-center" disabled={stage >= 0}>{stage >= 0 ? STAGES[stage] + "…" : "Score application"}</button></div>
          </form>
          <details className="mt-4 text-xs text-muted">
            <summary className="cursor-pointer text-ink">Why does this form ask for these details?</summary>
            <ul className="mt-2 list-disc space-y-1 pl-4">
              <li><b>Device, IP, phone, email, address</b> link applications to each other. Many applications sharing one of these is a typical fraud-ring pattern, and it is the model&apos;s strongest signal.</li>
              <li><b>Name and date of birth</b> are checked for consistency, for example an email that does not resemble the name.</li>
              <li><b>Income, requested credit, employment, channel</b> feed ratio and risk checks.</li>
              <li>Everything here is synthetic. Nothing you enter is real data, and the result is a simulated recommendation.</li>
            </ul>
          </details>
        </Card>

        <div className="space-y-4">
          {err && <ErrorBox message={err} />}
          {sim && <SimulatedBanner />}
          {stage >= 0 && (
            <Card title="Scoring">
              <ol className="space-y-2 text-sm">
                {STAGES.map((s, i) => (
                  <li key={s} className={cn("flex items-center gap-2", i <= stage ? "text-ink" : "text-subtle")}>
                    <span className={cn("h-2 w-2 rounded-full", i < stage ? "bg-safe" : i === stage ? "animate-pulse bg-accent" : "bg-line")} /> {s}
                  </li>
                ))}
              </ol>
              {slow && (
                <p role="status" className="mt-3 text-xs text-muted">
                  Still working. The demo API runs on a small free server, so the first score after a quiet period can take up to a minute. Please keep this page open.
                </p>
              )}
            </Card>
          )}
          {!res && stage < 0 && !err && <Card><p className="text-sm text-muted">Submit the form to see a score, tier, contributing factors and linked entities.</p></Card>}
          {res && (
            <>
              <Card title="Risk assessment">
                <div className="flex items-center gap-6">
                  <div className="flex h-28 w-28 flex-col items-center justify-center rounded-full border-4" style={{ borderColor: TIER_COLOR[res.tier] }}>
                    <div className="text-3xl font-semibold text-ink">{res.display_score}</div>
                    <div className="text-[10px] text-muted">/ 100</div>
                  </div>
                  <div className="space-y-1 text-sm">
                    <div><TierBadge tier={res.tier} /></div>
                    <div className="text-ink">{res.recommendation}</div>
                    <div className="text-xs text-subtle">Model {res.model_version}. Uncalibrated score {res.score.toFixed(3)} (not a probability).</div>
                    <Link className="text-xs text-accent" href={`/applications/${res.application_id}`}>Open case {res.application_id}</Link>
                  </div>
                </div>
                <p className="mt-3 text-xs text-subtle">{res.note}</p>
              </Card>
              <Card title="Top contributing factors">
                <ul className="space-y-2 text-sm">
                  {res.top_factors.map((f) => (
                    <li key={f.feature} className="flex items-start justify-between gap-3">
                      <span>{f.description}</span>
                      <span className={cn("shrink-0 text-xs", f.contribution > 0 ? "text-danger" : "text-safe")}>{f.direction}</span>
                    </li>
                  ))}
                </ul>
                <p className="mt-3 text-xs text-subtle">Factors are model associations, not proof or causation.</p>
              </Card>
              <Card title="Network preview">
                {res.linked_entities.length === 0 ? <p className="text-sm text-muted">No linked entities.</p> : (
                  <ul className="space-y-1 text-sm">
                    {res.linked_entities.map((l) => (
                      <li key={l.entity_id} className="flex justify-between">
                        <Link href={`/network?focus=${encodeURIComponent(l.entity_id)}`} className="text-accent">{l.kind}: {l.label}</Link>
                        <span className={l.shared_with_other_applications > 0 ? "text-warn" : "text-subtle"}>shared with {l.shared_with_other_applications} other app(s)</span>
                      </li>
                    ))}
                  </ul>
                )}
                <p className="mt-3 text-xs text-subtle">Connections are investigation signals, not proof of fraud.</p>
              </Card>
            </>
          )}
        </div>
      </div>
    </>
  );
}
