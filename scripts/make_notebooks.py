"""Generate and execute the three analysis notebooks (outputs come from the real artifacts, nothing is invented).

Run after generate_data / train / evaluate:  python scripts/make_notebooks.py
Needs: pip install nbformat nbconvert matplotlib ipykernel
"""
from pathlib import Path

import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"

SETUP = """import sys, json
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({"figure.figsize": (8, 3.5), "axes.grid": True, "axes.spines.top": False, "axes.spines.right": False})
pd.set_option("display.width", 140)"""


def nb(cells):
    n = nbf.v4.new_notebook()
    n.cells = [nbf.v4.new_markdown_cell(c) if k == "md" else nbf.v4.new_code_cell(c) for k, c in cells]
    n.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    return n


NOTEBOOKS = {
    "01_data_exploration.ipynb": [
        ("md", "# 01 Data exploration\n**All data here is synthetic** (`src/identitygraph/data/generator.py`). `fraud_label` / `fraud_scenario` are training-only."),
        ("code", SETUP + "\nfrom identitygraph.data.ingestion import load_applications\nfrom identitygraph.data.validation import validate\ndf = load_applications()\nprint(df.shape)\ndf.head(3).T"),
        ("code", "v = validate(df)\n{k: v[k] for k in ('ok', 'errors', 'n_rows', 'fraud_rate')}"),
        ("md", "## Fraud scenarios\nFraud is generated as clusters (rings, bursts, shared contacts) plus individual anomalies, so rates vary over time."),
        ("code", "sc = df.groupby('fraud_scenario').agg(rows=('application_id', 'count'), fraud_rate=('fraud_label', 'mean'))\nprint(sc)\nsc['rows'].plot.barh(title='Rows per scenario');"),
        ("code", "m = df.set_index('application_timestamp').resample('W')['fraud_label'].agg(['mean', 'size'])\nax = m['mean'].plot(title='Weekly fraud rate (synthetic)'); ax.set_ylabel('rate');"),
        ("md", "## Income vs requested credit"),
        ("code", "df['ratio'] = df.requested_credit / df.annual_income\ndf.groupby('fraud_label')['ratio'].describe()"),
        ("code", "fig, ax = plt.subplots()\nfor lab, g in df.groupby('fraud_label'):\n    ax.hist(g.ratio.clip(upper=2.5), bins=40, alpha=.6, density=True, label=f'fraud={lab}')\nax.set_xlabel('requested / income'); ax.legend();"),
        ("code", "# Entity reuse in the raw data\nfor c in ['device_id', 'ip_address', 'email', 'phone', 'address']:\n    vc = df[c].value_counts()\n    print(f'{c:12s} distinct={len(vc):6d}  max reuse={vc.iloc[0]:3d}  values used >1x={(vc > 1).sum()}')"),
    ],
    "02_feature_analysis.ipynb": [
        ("md", "# 02 Feature analysis\nPoint-in-time features from `data/processed/features.parquet` (built by `scripts/train.py` / `build_features.py`). Splits are chronological."),
        ("code", SETUP + "\nfrom identitygraph.config import PROCESSED_DIR\nfrom identitygraph.features.pipeline import BASE_FEATURES, GRAPH_FEATURES\nf = pd.read_parquet(PROCESSED_DIR / 'features.parquet')\nprint(f.shape); f['split'].value_counts()"),
        ("md", "## Univariate signal (train period only)\nMean of each feature for fraud vs legitimate, and AUC of the raw feature as a score (train split only, so no test leakage)."),
        ("code", "from sklearn.metrics import roc_auc_score\ntr = f[f.split == 'train']\nrows = []\nfor c in BASE_FEATURES + GRAPH_FEATURES:\n    rows.append((c, tr[c].mean(), tr.loc[tr.fraud_label == 1, c].mean(), tr.loc[tr.fraud_label == 0, c].mean(), roc_auc_score(tr.fraud_label, tr[c])))\nt = pd.DataFrame(rows, columns=['feature', 'mean', 'mean_fraud', 'mean_legit', 'auc']).set_index('feature')\nt['auc_strength'] = (t.auc - .5).abs()\nt.sort_values('auc_strength', ascending=False).head(15).round(3)"),
        ("code", "top = t.sort_values('auc_strength', ascending=False).head(12)\n(top['auc'] - .5).plot.barh(title='|Univariate AUC - 0.5| (train)').invert_yaxis();"),
        ("md", "## Graph features\n`component_size` and `neighbor_fraud_ratio` are computed chronologically (union-find); labels are only used once matured (see `label_maturity_days` / `label_scope` in configs/features.yaml)."),
        ("code", "g = tr.groupby(pd.cut(tr.component_size, [0, 1, 2, 4, 8, 16, 1e9]), observed=True)['fraud_label'].agg(['mean', 'size'])\nprint(g)\ng['mean'].plot.bar(title='Fraud rate by component size at application time (train)');"),
        ("code", "print('Test-period neighbor_fraud_ratio > 0:', (f[f.split == 'test'].neighbor_fraud_ratio > 0).mean().round(3))\nprint('Val  -period neighbor_fraud_ratio > 0:', (f[f.split == 'val'].neighbor_fraud_ratio > 0).mean().round(3))"),
        ("md", "Leakage protections are asserted in `tests/unit/test_data_and_features.py` (point-in-time, future labels do not change features)."),
    ],
    "03_model_experiments.ipynb": [
        ("md", "# 03 Model experiments\nReads `artifacts/metrics.json` written by `scripts/train.py`. Test period is a chronological hold-out; thresholds were chosen on validation only. **Synthetic data, so results are optimistic.**"),
        ("code", SETUP + "\nfrom identitygraph.models.registry import load_json\nrep = load_json('metrics.json')\nprint(rep['version'], rep['primary_model'], rep['data'])"),
        ("code", "rows = []\nfor name, r in rep['models'].items():\n    for split in ('validation', 'test'):\n        m = r[split]\n        rows.append(dict(model=name, split=split, pr_auc=m['pr_auc'], roc_auc=m['roc_auc'], precision=m['precision'], recall=m['recall'], f1=m['f1'], recall_at_1pct_fpr=m['recall_at_1pct_fpr']))\ntab = pd.DataFrame(rows)\ntab[tab.split == 'test'].drop(columns='split').set_index('model').round(3)"),
        ("code", "piv = tab.pivot(index='model', columns='split', values='pr_auc')\nprint(piv.round(3))\npiv.plot.bar(title='PR-AUC: validation vs test'); plt.ylim(0, 1);"),
        ("md", "## Does the graph help?\nCompare each graph-enhanced model with its same-family baseline."),
        ("code", "pairs = [(a, 'graph_' + a) for a in ('gradient_boosting', 'xgboost', 'lightgbm') if 'graph_' + a in rep['models']]\nout = pd.DataFrame({a: [rep['models'][a]['test']['pr_auc'], rep['models'][g]['test']['pr_auc']] for a, g in pairs}, index=['baseline', 'with graph features'])\nout.loc['lift'] = out.loc['with graph features'] - out.loc['baseline']\nout.round(3)"),
        ("code", "fig, axs = plt.subplots(1, 2, figsize=(11, 3.6))\nfor n, r in rep['models'].items():\n    p = np.array(r['curves_test']['pr']); axs[0].plot(p[:, 0], p[:, 1], label=n)\n    c = np.array(r['curves_test']['roc']); axs[1].plot(c[:, 0], c[:, 1], label=n)\naxs[0].set(title='Precision-Recall (test)', xlabel='recall', ylabel='precision'); axs[1].set(title='ROC (test)', xlabel='FPR', ylabel='TPR'); axs[0].legend(fontsize=7);"),
        ("code", "fi = pd.DataFrame(rep['models']['graph_gradient_boosting']['feature_importance']).set_index('feature')\nfi.head(12).plot.barh(legend=False, title='Top features: graph gradient boosting').invert_yaxis();"),
        ("code", "cm = rep['models'][rep['primary_model']]['test']['confusion_matrix']; print(rep['primary_model'], cm)\nprint('thresholds (validation-selected):', rep['models'][rep['primary_model']]['thresholds'])"),
        ("md", "**Caveats:** single seed, no confidence intervals, uncalibrated scores, synthetic fraud patterns with explicit signals."),
    ],
}

if __name__ == "__main__":
    NB_DIR.mkdir(exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        n = nb(cells)
        ExecutePreprocessor(timeout=300, kernel_name="python3").preprocess(n, {"metadata": {"path": str(NB_DIR)}})
        nbf.write(n, NB_DIR / name)
        print("executed", name)
