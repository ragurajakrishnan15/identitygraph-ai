/**
 * SIMULATED FALLBACK DATA — used ONLY when the backend API is unreachable.
 * Every value here is illustrative, not a model result. The UI shows a banner whenever it is used.
 */
import type { Application, Overview, Page, Tier } from "@/types/application";
import type { NetworkResponse } from "@/types/graph";
import type { FeatureCatalog, ModelMetrics, ModelReport, Monitoring } from "@/types/metrics";
import type { ScoreRequest, ScoreResponse } from "@/types/scoring";

const tiers: Tier[] = ["Low", "Low", "Medium", "High", "Low", "Medium"];
const channels = ["web", "mobile", "branch", "partner"];

const mockApps: Application[] = Array.from({ length: 30 }, (_, i) => {
  const tier = tiers[i % tiers.length];
  const score = tier === "High" ? 0.82 : tier === "Medium" ? 0.45 : 0.06;
  return {
    application_id: `MOCK${String(i + 1).padStart(5, "0")}`,
    applicant_id: `MOCK-APL-${i + 1}`,
    application_timestamp: new Date(Date.UTC(2025, 5, 1 + i)).toISOString(),
    full_name: ["Alex Smith", "Priya Patel", "Wei Lee", "Maria Garcia"][i % 4],
    date_of_birth: "1988-04-12",
    email: `mock${i}@mail.test`,
    phone: `+1-555-000${String(i).padStart(4, "0")}`,
    address: `${100 + i} Oak St`,
    device_id: `dev-mock-${i % 7}`,
    ip_address: `10.0.${i % 5}.${i + 1}`,
    employment_status: "employed",
    annual_income: 60000 + i * 1500,
    requested_credit: 8000 + i * 400,
    application_channel: channels[i % 4],
    fraud_label: null,
    fraud_scenario: null,
    source: "mock",
    split: null,
    score: {
      application_id: `MOCK${String(i + 1).padStart(5, "0")}`,
      score, display_score: Math.round(score * 100), tier,
      recommendation: `${tier} (simulated mock)`, model_version: "mock", scored_at: new Date().toISOString(),
      factors: [{ feature: "device_id_prior_distinct_applicants", description: "Mock factor: device shared by other applicants", contribution: 0.4, direction: "increases risk" }],
    },
    linked_entities: [{ entity_id: "device:dev-mock-1", kind: "device", label: "dev-mock-1", shared_with_other_applications: 3 }],
    notes: [],
    timeline: [{ event: "Application submitted (mock)", at: new Date().toISOString() }],
  };
});

export const mock = {
  applications(params: URLSearchParams): Page<Application> {
    const q = (params.get("q") ?? "").toLowerCase();
    const tier = params.get("tier");
    const channel = params.get("channel");
    let items = mockApps.filter((a) => (!q || a.full_name.toLowerCase().includes(q) || a.application_id.toLowerCase().includes(q))
      && (!tier || a.score?.tier === tier) && (!channel || a.application_channel === channel));
    const page = Number(params.get("page") ?? 1), size = Number(params.get("page_size") ?? 25);
    const total = items.length;
    items = items.slice((page - 1) * size, page * size);
    return { items, total, page, page_size: size };
  },
  application: (id: string) => mockApps.find((a) => a.application_id === id) ?? mockApps[0],
  overview(): Overview {
    return {
      total: mockApps.length, tiers: { Low: 18, Medium: 7, High: 5 }, avg_score: 0.22,
      channels: channels.flatMap((c) => (["Low", "Medium", "High"] as Tier[]).map((t) => ({ channel: c, tier: t, count: t === "Low" ? 5 : 2 }))),
      trend: ["2025-01", "2025-02", "2025-03", "2025-04"].map((p, i) => ({ period: p, applications: 100 + i * 10, avg_score: 0.15 + i * 0.02 })),
      top_cases: mockApps.filter((a) => a.score?.tier === "High").slice(0, 8),
    };
  },
  score(r: ScoreRequest): ScoreResponse {
    const ratio = r.requested_credit / r.annual_income;
    const score = Math.min(0.95, 0.05 + ratio * 0.5);
    const tier: Tier = score > 0.6 ? "High" : score > 0.3 ? "Medium" : "Low";
    return {
      application_id: "MOCK-SCORE", score, display_score: Math.round(score * 100), tier,
      recommendation: `${tier} (simulated mock; backend unreachable)`, model_version: "mock", scored_at: new Date().toISOString(),
      top_factors: [{ feature: "income_to_credit_ratio", description: `Requested credit is ${(ratio * 100).toFixed(0)}% of income (mock heuristic)`, contribution: ratio, direction: "increases risk" }],
      linked_entities: [], is_simulated: true, note: "MOCK result: backend unreachable.",
    };
  },
  network(id: string): NetworkResponse {
    const nodes = [
      { id, type: "device", label: "dev-mock-1", is_focus: true, flagged: true, degree: 3 },
      ...[1, 2, 3].map((i) => ({ id: `application:M${i}`, type: "application", label: `MOCK${i}`, is_focus: false, flagged: false, degree: 2 })),
    ];
    return { nodes, edges: [1, 2, 3].map((i) => ({ id: `e${i}`, source: id, target: `application:M${i}`, relation: "used" })),
      summary: { entity_id: id, kind: "device", label: "dev-mock-1", degree: 3, linked_applications: 3, component_size: 4 },
      note: "MOCK graph. Connections are investigation signals, not proof of fraud." };
  },
  entities: () => ({ items: [{ entity_id: "device:dev-mock-1", kind: "device", label: "dev-mock-1", degree: 3 }] }),
  modelReport(): ModelReport {
    const m: ModelMetrics = { pr_auc: 0, roc_auc: 0, precision: 0, recall: 0, f1: 0, recall_at_1pct_fpr: 0, precision_at_1pct_review_budget: 0,
      threshold: 0.5, confusion_matrix: { tn: 0, fp: 0, fn: 0, tp: 0 }, n: 0, positives: 0 };
    return { version: "mock", primary_model: "mock", trained_at: new Date().toISOString(),
      data: { n_total: 0, n_train: 0, n_val: 0, n_test: 0, train_end: "", fraud_rate_test: 0, synthetic: true },
      models: { mock: { validation: m, test: m, thresholds: { medium: 0.3, high: 0.6 }, curves_test: { pr: [[0, 1], [1, 0]], roc: [[0, 0], [1, 1]] }, feature_importance: [], n_features: 0 } },
      note: "MOCK: no real metrics available because the backend is unreachable." };
  },
  monitoring(): Monitoring {
    return { generated_at: new Date().toISOString(), mode: "MOCK", model_version: "mock",
      quality: { status: "unknown", schema_ok: false, errors: [], n_rows: 0, missingness: {} },
      feature_drift: [], score_psi: { psi: 0, status: "unknown" }, score_distribution: [], tier_distribution: {},
      label_performance: { available: false, note: "MOCK", pr_auc_test: null } };
  },
  features: (): FeatureCatalog => ({ groups: [] }),
};
