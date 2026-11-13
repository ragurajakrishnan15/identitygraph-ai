# Evaluation Summary

Model version: `0.1.0-202611130301` (primary: `graph_gradient_boosting`)

**All data is synthetic.** Chronological split; thresholds chosen on validation only; scores are uncalibrated.

Test positives: see table. Train end: 2025-05-25 03:18:03.116360818

| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 | Recall@1%FPR |
|---|---|---|---|---|---|---|
| logistic_regression | 0.755 | 0.897 | 0.759 | 0.692 | 0.724 | 0.509 |
| random_forest | 0.819 | 0.913 | 0.942 | 0.729 | 0.822 | 0.753 |
| gradient_boosting | 0.830 | 0.924 | 0.964 | 0.714 | 0.820 | 0.732 |
| graph_gradient_boosting | 0.845 | 0.923 | 0.912 | 0.767 | 0.833 | 0.772 |
| xgboost | 0.829 | 0.917 | 0.911 | 0.732 | 0.812 | 0.743 |
| graph_xgboost | 0.845 | 0.921 | 0.950 | 0.761 | 0.845 | 0.777 |
| lightgbm | 0.828 | 0.919 | 0.923 | 0.729 | 0.815 | 0.743 |
| graph_lightgbm | 0.844 | 0.920 | 0.934 | 0.756 | 0.836 | 0.775 |

Graph-enhanced model improved PR-AUC over the same-family baseline (0.845 vs 0.830). Reported as measured.