"""generate small fixture -> validate -> features -> train -> evaluate -> save/load -> score."""
import pandas as pd

from identitygraph.data.validation import validate
from identitygraph.models.predict import score_frame, score_new_applications
from identitygraph.models.registry import load_bundle


def test_pipeline(small_df, trained):
    assert validate(small_df)["ok"]
    assert set(trained["models"]) == {"logistic_regression", "random_forest", "gradient_boosting", "graph_gradient_boosting"}
    for m in trained["models"].values():
        assert 0 <= m["test"]["pr_auc"] <= 1 and m["thresholds"]["selected_on"] == "validation"
    # primary model beats a random baseline on the held-out period (fraud rate ~7%)
    assert trained["models"]["gradient_boosting"]["test"]["pr_auc"] > 0.2

    bundle = load_bundle()  # save/load round trip
    assert bundle["calibrated"] is False and bundle["train_end"] is not None
    feats = pd.read_parquet(__import__("identitygraph.config", fromlist=["x"]).PROCESSED_DIR / "features.parquet")
    s = score_frame(bundle, feats.head(50))
    assert ((s >= 0) & (s <= 1)).all()

    new = small_df.tail(3).drop(columns=["fraud_label", "fraud_scenario"]).copy()
    new["application_id"] = ["N1", "N2", "N3"]
    new["application_timestamp"] = pd.Timestamp("2030-01-01")
    out = score_new_applications(bundle, small_df.head(len(small_df) - 3), new)
    assert len(out) == 3 and "score" in out
