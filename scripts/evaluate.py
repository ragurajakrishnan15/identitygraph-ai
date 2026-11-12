"""Write monitoring snapshot and evaluation report from saved artifacts (no metrics are invented)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.config import PROCESSED_DIR, REPORT_DIR  # noqa: E402
from identitygraph.models.registry import load_bundle, load_json, save_json  # noqa: E402
from identitygraph.monitoring.snapshot import build_snapshot  # noqa: E402

if __name__ == "__main__":
    rep = load_json("metrics.json")
    bundle = load_bundle()
    feats = pd.read_parquet(PROCESSED_DIR / "features.parquet")
    save_json(build_snapshot(bundle, feats), "monitoring.json")
    REPORT_DIR.mkdir(exist_ok=True)
    lines = ["# Evaluation Summary\n", f"Model version: `{rep['version']}` (primary: `{rep['primary_model']}`)\n",
             "**All data is synthetic.** Chronological split; thresholds chosen on validation only; "
             "scores are uncalibrated.\n",
             f"Test positives: see table. Train end: {rep['data']['train_end']}\n",
             "| Model | PR-AUC | ROC-AUC | Precision | Recall | F1 | Recall@1%FPR |", "|---|---|---|---|---|---|---|"]
    for k, v in rep["models"].items():
        t = v["test"]
        lines.append(f"| {k} | {t['pr_auc']:.3f} | {t['roc_auc']:.3f} | {t['precision']:.3f} | {t['recall']:.3f} | "
                     f"{t['f1']:.3f} | {t['recall_at_1pct_fpr']:.3f} |")
    base, graph = rep["models"]["gradient_boosting"]["test"]["pr_auc"], rep["models"]["graph_gradient_boosting"]["test"]["pr_auc"]
    verdict = "improved" if graph > base else "did not improve"
    lines.append(f"\nGraph-enhanced model {verdict} PR-AUC over the same-family baseline "
                 f"({graph:.3f} vs {base:.3f}). Reported as measured.")
    (REPORT_DIR / "evaluation_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote artifacts/monitoring.json and reports/evaluation_summary.md")
