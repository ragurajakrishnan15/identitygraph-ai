# Model Card: IdentityGraph AI

**Intended use:** portfolio demonstration of fraud-risk triage on synthetic data. Not for real credit decisions.

## Models
Logistic Regression (balanced), Random Forest, sklearn Gradient Boosting, and a graph-enhanced Gradient Boosting that adds
`component_size`, `component_distinct_applicants`, `max_entity_degree`, `neighbor_fraud_ratio`. Configured primary: `graph_gradient_boosting`.
Preprocessing (scaler for LR, one-hot for employment/channel) is fit on the train split only and saved with the model in `artifacts/model.joblib`.

## Evaluation protocol
Chronological 60/20/20 split (12,000 / 4,000 / 4,000). Primary metric PR-AUC. Thresholds chosen on validation:
`high` = validation-F1-optimal score; `medium` = lowest score keeping validation recall >= 0.90.

## Test results (4,000 rows, 377 positives; measured, from `artifacts/metrics.json`)
| Model | PR-AUC | ROC-AUC | Precision | Recall | Recall@1% FPR |
|---|---|---|---|---|---|
| logistic_regression | 0.755 | 0.897 | 0.759 | 0.692 | 0.509 |
| random_forest | 0.819 | 0.913 | 0.942 | 0.729 | 0.753 |
| gradient_boosting | 0.830 | 0.924 | 0.964 | 0.714 | 0.732 |
| graph_gradient_boosting | 0.827 | 0.919 | 0.889 | 0.740 | 0.745 |

The graph-enhanced model has slightly higher recall but marginally lower PR-AUC than the baseline: **no PR-AUC improvement from graph features** in this run.
Precision/recall use each model's validation-selected `high` threshold. Re-running training regenerates these numbers; this table is a snapshot.

## Explainability
SHAP TreeExplainer (log-odds contributions) with a fallback to importance-weighted deviations. Factors are associations, not causal proof.

## Limitations
Synthetic, optimistic data; scores uncalibrated (do not read as probabilities); no fairness analysis (synthetic data has no protected attributes);
rows from the train period are scored in-sample when shown in the dashboard; single random seed, no confidence intervals.
