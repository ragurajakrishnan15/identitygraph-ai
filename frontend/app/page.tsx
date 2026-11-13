import { Activity, ArrowRight, ArrowUpRight, Network, ScanSearch, ShieldCheck, TestTube2 } from "lucide-react";
import Link from "next/link";
import { HeroGraph } from "@/components/marketing/HeroGraph";
import { Reveal } from "@/components/marketing/Reveal";
import { Brand, REPO_URL } from "@/components/shell/TopNav";

// Measured on the chronological hold-out (4,000 synthetic applications). Re-check after retraining.
const STATS = [
  { v: "0.845", l: "PR-AUC, graph model", s: "vs 0.830 without graph features" },
  { v: "77%", l: "fraud caught at 1% false positives", s: "chronological test period" },
  { v: "8", l: "models compared", s: "linear, forest, 3 boosters, 3 graph variants" },
  { v: "22", l: "automated tests", s: "including label-leakage checks" },
];

const FEATURES = [
  { icon: Network, t: "See the network, not just the row", d: "Applications are linked by shared devices, IPs, phones, emails and addresses. Rings that look unremarkable one application at a time show up as connected components." },
  { icon: ScanSearch, t: "Every score explained", d: "SHAP-based factors list what pushed each score up or down, in plain language. They describe associations and never claim proof." },
  { icon: Activity, t: "Watches itself", d: "Population stability index, data-quality checks and score-distribution shifts show when the model's inputs stop looking like its training data." },
  { icon: TestTube2, t: "Built not to cheat", d: "Chronological splits, point-in-time features, labels used only after a maturity lag, thresholds picked on validation only, and tests that fail on leakage." },
];

const LIMITS = [
  ["Synthetic data", "Fraud patterns are generated, so metrics are optimistic and say nothing about a real portfolio."],
  ["Simulated decisions", "Tiers and recommendations show how a policy would route cases. Nothing here approves or declines credit."],
  ["Uncalibrated scores", "A 0.80 is a ranking signal, not an 80% chance of fraud. Thresholds are chosen on validation data only."],
];

export default function Landing() {
  return (
    <>
      <header className="glass sticky top-0 z-40">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-5 md:px-8">
          <Brand />
          <nav aria-label="Site" className="flex items-center gap-5 text-[13px] text-muted">
            <a href="#features" className="hidden hover:text-ink sm:inline">Features</a>
            <a href="#results" className="hidden hover:text-ink sm:inline">Results</a>
            <a href="#honest" className="hidden hover:text-ink sm:inline">Limits</a>
            <Link href="/overview" className="rounded-full bg-accent px-3.5 py-1.5 font-medium text-white hover:brightness-110">Open dashboard</Link>
          </nav>
        </div>
      </header>

      <main>
        <section className="mx-auto grid max-w-6xl items-center gap-10 px-5 pb-20 pt-16 md:px-8 md:pt-24 lg:grid-cols-[1.1fr_1fr]">
          <Reveal>
            <p className="mb-5 inline-flex items-center gap-2 rounded-full bg-fill px-3 py-1 text-xs font-medium text-muted">
              <ShieldCheck size={13} className="text-accent" /> Identity-graph fraud risk · portfolio project
            </p>
            <h1 className="text-5xl font-semibold leading-[1.02] tracking-tightest text-ink md:text-7xl">
              Catch fraud rings <span className="bg-gradient-to-r from-accent to-[#af52de] bg-clip-text text-transparent">before they pay out.</span>
            </h1>
            <p className="mt-6 max-w-xl text-xl leading-relaxed text-muted">
              A credit-application risk platform that scores each applicant on what they say <em>and</em> who they are connected to, with an explanation for every decision.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-3">
              <Link href="/overview" className="btn px-6 py-3 text-base">Explore the dashboard <ArrowRight size={16} /></Link>
              <Link href="/score" className="btn-ghost px-6 py-3 text-base">Score an application</Link>
            </div>
            <p className="mt-5 text-xs text-subtle">Built on synthetic data. Decisions are simulated; scores are uncalibrated and are not probabilities.</p>
          </Reveal>
          <Reveal delay={0.15}>
            <div className="rounded-[2rem] border border-line/70 bg-surface p-4 shadow-lift">
              <HeroGraph />
              <div className="mx-2 mb-2 flex items-center justify-between rounded-2xl bg-fill px-4 py-3 text-sm">
                <span className="text-muted">7 applications · 1 shared device</span>
                <span className="rounded-full bg-danger/10 px-2.5 py-0.5 text-xs font-medium text-danger">High risk · investigate</span>
              </div>
            </div>
          </Reveal>
        </section>

        <section id="results" className="border-y border-line/60 bg-fill/60">
          <div className="mx-auto max-w-6xl px-5 py-16 md:px-8">
            <Reveal>
              <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
                {STATS.map((s) => (
                  <div key={s.l}>
                    <div className="text-5xl font-semibold tracking-tightest text-ink md:text-6xl">{s.v}</div>
                    <div className="mt-2 text-sm font-medium text-ink">{s.l}</div>
                    <div className="mt-1 text-xs text-subtle">{s.s}</div>
                  </div>
                ))}
              </div>
              <p className="mt-10 text-xs text-subtle">Measured on a chronological hold-out of synthetic data, which is optimistic. See the model card for protocol and caveats.</p>
            </Reveal>
          </div>
        </section>

        <section id="features" className="mx-auto max-w-6xl px-5 py-24 md:px-8">
          <Reveal>
            <h2 className="max-w-2xl text-4xl font-semibold tracking-tightest text-ink md:text-6xl">Built to be trusted, not just accurate.</h2>
          </Reveal>
          <div className="mt-14 grid gap-6 md:grid-cols-2">
            {FEATURES.map(({ icon: Icon, t, d }, i) => (
              <Reveal key={t} delay={(i % 2) * 0.08}>
                <article className="h-full rounded-[2rem] border border-line/70 bg-surface p-8 shadow-card transition hover:shadow-lift md:p-10">
                  <span className="grid h-11 w-11 place-items-center rounded-2xl bg-accent/10 text-accent"><Icon size={22} /></span>
                  <h3 className="mt-6 text-2xl font-semibold tracking-tight text-ink">{t}</h3>
                  <p className="mt-3 leading-relaxed text-muted">{d}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </section>

        <section id="honest" className="bg-ink text-bg">
          <div className="mx-auto max-w-6xl px-5 py-24 md:px-8">
            <Reveal>
              <h2 className="max-w-3xl text-4xl font-semibold tracking-tightest md:text-6xl">Honest about what it is.</h2>
              <div className="mt-12 grid gap-10 md:grid-cols-3">
                {LIMITS.map(([h, p]) => (
                  <div key={h}><h3 className="text-xl font-semibold">{h}</h3><p className="mt-2 leading-relaxed opacity-70">{p}</p></div>
                ))}
              </div>
            </Reveal>
          </div>
        </section>

        <section className="mx-auto max-w-6xl px-5 py-24 text-center md:px-8">
          <Reveal>
            <h2 className="mx-auto max-w-3xl text-4xl font-semibold tracking-tightest text-ink md:text-6xl">See it work on a suspicious application.</h2>
            <p className="mx-auto mt-5 max-w-xl text-lg text-muted">Fill the sample form, score it, then follow the shared device through the identity network.</p>
            <div className="mt-9 flex flex-wrap justify-center gap-3">
              <Link href="/score" className="btn px-6 py-3 text-base">Try the scorer <ArrowRight size={16} /></Link>
              <a href={REPO_URL} target="_blank" rel="noreferrer" className="btn-ghost px-6 py-3 text-base">View source <ArrowUpRight size={16} /></a>
            </div>
          </Reveal>
        </section>
      </main>

      <footer className="border-t border-line/60">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-5 py-8 text-xs text-subtle md:px-8">
          <span>IdentityGraph AI · portfolio project on synthetic data. Not for real credit decisions.</span>
          <span>Python · scikit-learn · XGBoost · NetworkX · SHAP · FastAPI · Next.js</span>
        </div>
      </footer>
    </>
  );
}
