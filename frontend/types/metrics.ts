export interface ModelMetrics {
  pr_auc: number;
  roc_auc: number;
  precision: number;
  recall: number;
  f1: number;
  recall_at_1pct_fpr: number;
  precision_at_1pct_review_budget: number;
  threshold: number;
  confusion_matrix: { tn: number; fp: number; fn: number; tp: number };
  n: number;
  positives: number;
}
export interface ModelResult {
  validation: ModelMetrics;
  test: ModelMetrics;
  thresholds: { medium: number; high: number };
  curves_test: { pr: number[][]; roc: number[][] };
  feature_importance: { feature: string; importance: number }[];
  n_features: number;
}
export interface ModelReport {
  version: string;
  primary_model: string;
  trained_at: string;
  data: { n_total: number; n_train: number; n_val: number; n_test: number; train_end: string; fraud_rate_test: number; synthetic: boolean };
  models: Record<string, ModelResult>;
  note: string;
}
export interface Monitoring {
  generated_at: string;
  mode: string;
  model_version: string;
  quality: { status: string; schema_ok: boolean; errors: string[]; n_rows: number; missingness: Record<string, number> };
  feature_drift: { feature: string; psi: number; status: string }[];
  score_psi: { psi: number; status: string };
  score_distribution: { bin: string; count: number }[];
  tier_distribution: Record<string, number>;
  label_performance: { available: boolean; note: string; pr_auc_test: number | null };
}
export interface FeatureCatalog {
  groups: { group: string; features: { name: string; importance: number | null }[] }[];
}
