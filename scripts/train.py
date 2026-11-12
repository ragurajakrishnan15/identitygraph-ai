import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.data.ingestion import load_applications  # noqa: E402
from identitygraph.models.train import train_all  # noqa: E402

if __name__ == "__main__":
    rep = train_all(load_applications())
    print(f"version {rep['version']} primary={rep['primary_model']}")
    print(f"{'model':28s} {'PR-AUC':>7s} {'ROC':>6s} {'prec':>6s} {'rec':>6s} {'R@1%FPR':>8s}")
    for k, v in rep["models"].items():
        t = v["test"]
        print(f"{k:28s} {t['pr_auc']:7.3f} {t['roc_auc']:6.3f} {t['precision']:6.3f} {t['recall']:6.3f} "
              f"{t['recall_at_1pct_fpr']:8.3f}")
