"""Per-case factor explanations. SHAP (TreeExplainer) when available, otherwise a global-importance
fallback scaled by how unusual the value is. Factors are associations, not causal proof."""
from __future__ import annotations

import numpy as np
import pandas as pd

TEXT = {
    "device_id_prior_distinct_applicants": "Device previously used by {v:.0f} other applicant(s)",
    "ip_address_prior_distinct_applicants": "IP address previously used by {v:.0f} other applicant(s)",
    "email_prior_distinct_applicants": "Email previously seen on {v:.0f} other applicant(s)",
    "phone_prior_distinct_applicants": "Phone previously seen on {v:.0f} other applicant(s)",
    "address_prior_distinct_applicants": "Address previously seen on {v:.0f} other applicant(s)",
    "device_id_prior_apps": "Device appeared in {v:.0f} earlier application(s)",
    "ip_address_prior_apps": "IP appeared in {v:.0f} earlier application(s)",
    "email_prior_apps": "Email appeared in {v:.0f} earlier application(s)",
    "phone_prior_apps": "Phone appeared in {v:.0f} earlier application(s)",
    "address_prior_apps": "Address appeared in {v:.0f} earlier application(s)",
    "device_id_apps_1h": "{v:.0f} application(s) from this device in the last hour",
    "device_id_apps_24h": "{v:.0f} application(s) from this device in 24h",
    "device_id_apps_7d": "{v:.0f} application(s) from this device in 7 days",
    "ip_address_apps_1h": "{v:.0f} application(s) from this IP in the last hour",
    "ip_address_apps_24h": "{v:.0f} application(s) from this IP in 24h",
    "ip_address_apps_7d": "{v:.0f} application(s) from this IP in 7 days",
    "income_to_credit_ratio": "Income-to-requested-credit ratio is {v:.2f}",
    "email_name_mismatch": "Email address does not resemble the applicant's name",
    "young_high_credit": "Young applicant requesting a large share of income",
    "age": "Applicant age is {v:.0f}",
    "is_night": "Application submitted at night",
    "hour": "Submitted at hour {v:.0f}",
    "component_size": "Part of a linked cluster of {v:.0f} application(s)",
    "component_distinct_applicants": "Linked cluster spans {v:.0f} applicant(s)",
    "max_entity_degree": "Shares an identifier with up to {v:.0f} earlier application(s)",
    "neighbor_fraud_ratio": "{v:.0%} of linked earlier cases (with matured labels) were fraud",
}


def _describe(feat: str, value: float) -> str:
    t = TEXT.get(feat)
    return t.format(v=value) if t else f"{feat.replace('_', ' ')} = {value:.2f}"


def explain_rows(bundle: dict, X: pd.DataFrame, background: pd.DataFrame | None = None, top_k: int = 5):
    """Return list (per row) of [{feature, description, contribution, direction}] sorted by |contribution|."""
    pipe = bundle["pipeline"]
    prep, clf = pipe.named_steps["prep"], pipe.named_steps["clf"]
    names = [n.split("__", 1)[-1] for n in prep.get_feature_names_out()]
    Z = prep.transform(X[bundle["features"]])
    Z = Z.toarray() if hasattr(Z, "toarray") else np.asarray(Z)
    contrib = None
    try:
        import shap

        if hasattr(clf, "feature_importances_"):
            vals = shap.TreeExplainer(clf).shap_values(Z)
            if isinstance(vals, list):
                vals = vals[-1]
            vals = np.asarray(vals)
            contrib = vals[..., 1] if vals.ndim == 3 else vals
        else:
            contrib = Z * clf.coef_[0]
    except Exception:  # fallback: importance-weighted standardised deviation
        imp = getattr(clf, "feature_importances_", None)
        if imp is None:
            imp = np.abs(getattr(clf, "coef_", np.ones((1, Z.shape[1]))))[0]
        mu, sd = Z.mean(0), Z.std(0) + 1e-9
        contrib = imp * (Z - mu) / sd
    out = []
    for i in range(len(X)):
        order = np.argsort(-np.abs(contrib[i]))[:top_k]
        factors = []
        for j in order:
            f = names[j]
            if f.startswith(("employment_status_", "application_channel_")):
                continue
            raw = X.iloc[i].get(f, Z[i, j])
            factors.append({
                "feature": f, "description": _describe(f, float(raw)),
                "contribution": float(contrib[i, j]),
                "direction": "increases risk" if contrib[i, j] > 0 else "decreases risk",
            })
        out.append(factors)
    return out
