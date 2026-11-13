# Model Card: IdentityGraph AI

**Intended use:** portfolio demonstration of fraud-risk triage on synthetic data. Not for real credit decisions.

## Models
Logistic Regression (balanced), Random Forest, and three gradient-boosting families (scikit-learn, XGBoost, LightGBM), each with a baseline and a
graph-enhanced variant that adds `component_size`, `component_distinct_applicants`, `max_entity_degree`, `neighbor_fraud_ratio`.
Configured primary: `graph_gradient_boosting`. Preprocessing (scaler for LR, one-hot for employment/channel) is fit on the train split only and
saved with the model in `artifacts/model.joblib`.

## Evaluation protocol
Chronological 60/20/20 split (12,000 / 4,000 / 4,000). Primary metric PR-AUC. Thresholds chosen on validation only:
`high` = validation-F1-optimal score; `medium` = lowest score keeping validation recall >= 0.90, capped so that at most 15% of
applications are flagged (review-capacity cap).

## Test results (4,000 rows, 377 positives; measured, from `artifacts/metrics.json`)
| Model | PR-AUC | ROC-AUC | Precision | Recall | Recall@1% FPR |
|---|---|---|---|---|---|
| logistic_regression | 0.755 | 0.897 | 0.759 | 0.692 | 0.509 |
| random_forest | 0.819 | 0.913 | 0.942 | 0.729 | 0.753 |
| gradient_boosting | 0.830 | 0.924 | 0.964 | 0.714 | 0.732 |
| graph_gradient_boosting | 0.845 | 0.923 | 0.912 | 0.767 | 0.772 |
| xgboost | 0.829 | 0.917 | 0.911 | 0.732 | 0.743 |
| graph_xgboost | 0.845 | 0.921 | 0.950 | 0.761 | 0.777 |
| lightgbm | 0.828 | 0.919 | 0.923 | 0.729 | 0.743 |
| graph_lightgbm | 0.844 | 0.920 | 0.934 | 0.756 | 0.775 |

Graph features lift PR-AUC by about +0.015 in all three boosting families (0.830 -> 0.845, 0.829 -> 0.845, 0.828 -> 0.844). Precision/recall use each model's
validation-selected `high` threshold. Re-running training regenerates these numbers; this table is a snapshot.

## Finding: neighbour-fraud feature and the label-maturity lag
`neighbor_fraud_ratio` = share of *earlier* applications sharing an entity that were fraud, using only labels old enough to be known (maturity lag).
- First attempt (30-day lag, train-period labels only): the feature was non-zero for ~0% of validation/test rows, and the graph model did **not** beat the baseline
  (PR-AUC 0.827 vs 0.830). My first explanation, train/serve skew from the train-only label rule, was incomplete: switching to "all labels matured before the application"
  (valid in production as delayed feedback) changed nothing, because the true cause was that synthetic fraud clusters live shorter than 30 days, so neighbour labels were never
  known in time.
- With a 7-day lag (`configs/features.yaml`), the feature is non-zero for 1-3% of rows and the graph variants improve over their baselines.
- **Caveat:** the 7-day value was chosen after seeing test-period results of the 30-day run, with a single alternative tried. Treat the improvement as indicative, not a clean
  held-out estimate. Single seed, no confidence intervals. The leakage tests (`tests/unit`) pass in both label modes.

## Review tiers
Policy output only (simulated). With the review-capacity cap, roughly 15% of applications fall in Medium or High.

## Explainability
SHAP TreeExplainer (log-odds contributions) with a fallback to importance-weighted deviations. Factors are associations, not causal proof.

## Limitations
Synthetic, optimistic data; scores uncalibrated (do not read as probabilities); no fairness analysis (synthetic data has no protected attributes);
rows from the train period are scored in-sample when shown in the dashboard; single random seed, no confidence intervals.
