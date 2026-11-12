"use client";
import { useState } from "react";
import { CurveChart, HBars } from "@/components/charts";
import { Card, PageHeader, State } from "@/components/ui";
import { useApi } from "@/hooks/useApi";
import { api } from "@/lib/api-client";
import { cn, pct } from "@/lib/utils";

const COLORS = ["#7c6cf6", "#2dd4bf", "#fbbf24", "#fb7185"];

export default function Models() {
  const s = useApi(() => api.modelMetrics(), []);
  const [sel, setSel] = useState<string | null>(null);
  return (
    <>
      <PageHeader title="Model Performance" subtitle="Chronological held-out TEST period; thresholds selected on validation only; synthetic data" />
      <State s={s}>
        {(r) => {
          const names = Object.keys(r.models);
          const cur = sel ?? r.primary_model;
          const m = r.models[cur] ?? r.models[names[0]];
          const cm = m.test.confusion_matrix;
          const best = Math.max(...names.map((n) => r.models[n].test.pr_auc));
          return (
            <div className="space-y-4">
              <Card title="Model comparison (test)">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead><tr>{["Model", "PR-AUC ★", "ROC-AUC", "Precision", "Recall", "F1", "Recall @1% FPR", "Prec @1% budget"].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
                    <tbody>
                      {names.map((n) => {
                        const t = r.models[n].test;
                        return (
                          <tr key={n} className={cn("cursor-pointer border-t border-navy-700 hover:bg-navy-700/50", n === cur && "bg-accent/10")} onClick={() => setSel(n)}>
                            <td className="td">{n}{n === r.primary_model && <span className="ml-2 text-xs text-accent-soft">primary</span>}</td>
                            <td className={cn("td", t.pr_auc === best && "font-semibold text-safe")}>{t.pr_auc.toFixed(3)}</td>
                            <td className="td">{t.roc_auc.toFixed(3)}</td><td className="td">{t.precision.toFixed(3)}</td>
                            <td className="td">{t.recall.toFixed(3)}</td><td className="td">{t.f1.toFixed(3)}</td>
                            <td className="td">{t.recall_at_1pct_fpr.toFixed(3)}</td><td className="td">{t.precision_at_1pct_review_budget.toFixed(3)}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                <p className="mt-2 text-xs text-slate-500">
                  {r.data.n_test.toLocaleString()} test rows, fraud rate {pct(r.data.fraud_rate_test)}. Train ends {r.data.train_end}. Click a row to inspect it. {r.note}
                </p>
              </Card>
              <div className="grid gap-4 lg:grid-cols-2">
                <Card title="Precision-Recall (test)"><CurveChart xLabel="Recall" yLabel="Precision" series={names.map((n, i) => ({ name: n, color: COLORS[i % 4], points: r.models[n].curves_test.pr }))} /></Card>
                <Card title="ROC (test)"><CurveChart xLabel="FPR" yLabel="TPR" series={names.map((n, i) => ({ name: n, color: COLORS[i % 4], points: r.models[n].curves_test.roc }))} /></Card>
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <Card title={`Confusion matrix: ${cur} @ threshold ${m.test.threshold.toFixed(3)}`}>
                  <div className="grid max-w-sm grid-cols-2 gap-2 text-center">
                    {[["True negative", cm.tn, "text-safe"], ["False positive", cm.fp, "text-warn"], ["False negative", cm.fn, "text-danger"], ["True positive", cm.tp, "text-safe"]].map(([l, v, c]) => (
                      <div key={l as string} className="rounded-lg border border-navy-600 bg-navy-900 p-3"><div className={cn("text-xl font-semibold", c as string)}>{(v as number).toLocaleString()}</div><div className="text-xs text-slate-400">{l}</div></div>
                    ))}
                  </div>
                </Card>
                <Card title={`Feature importance: ${cur}`}>
                  <HBars data={m.feature_importance.slice(0, 12)} xKey="importance" yKey="feature" />
                </Card>
              </div>
            </div>
          );
        }}
      </State>
    </>
  );
}
