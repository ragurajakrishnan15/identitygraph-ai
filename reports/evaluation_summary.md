# Evaluation Summary

Model version: `0.1.0-202611122325` (primary: `graph_gradient_boosting`)

**All data is synthetic.** Chronological split; thresholds chosen on validation only; scores are uncalibrated.

Test positives: see table. Train end: 2025-05-25 03:18:03.116360818

| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 | Recall@1%FPR |
|---|---|---|---|---|---|---|
| logistic_regression | 0.755 | 0.897 | 0.759 | 0.692 | 0.724 | 0.509 |
| random_forest | 0.819 | 0.913 | 0.942 | 0.729 | 0.822 | 0.753 |
| gradient_boosting | 0.830 | 0.924 | 0.964 | 0.714 | 0.820 | 0.732 |
| graph_gradient_boosting | 0.827 | 0.919 | 0.889 | 0.740 | 0.808 | 0.745 |

Graph-enhanced model did not improve PR-AUC over the same-family baseline (0.827 vs 0.830). Reported as measured.