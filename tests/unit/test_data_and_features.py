import numpy as np
import pandas as pd

from identitygraph.config import load_config
from identitygraph.data.generator import generate
from identitygraph.data.schemas import APPLICATION_COLUMNS
from identitygraph.data.validation import validate
from identitygraph.evaluation.splits import chronological_split
from identitygraph.features.graph_features import graph_features
from identitygraph.features.pipeline import build_features


def test_generator_reproducible_and_schema():
    a, b = generate(n=600, seed=1), generate(n=600, seed=1)
    pd.testing.assert_frame_equal(a, b)
    assert not a.equals(generate(n=600, seed=2))
    assert set(APPLICATION_COLUMNS).issubset(a.columns)
    assert validate(a)["ok"]
    assert a.fraud_scenario.nunique() >= 6 and 0.03 < a.fraud_label.mean() < 0.12


def _toy(rows):
    base = dict(applicant_id="A", full_name="Al Bo", email="al.bo@x.test", phone="p", address="a", device_id="d",
                ip_address="i", employment_status="employed", annual_income=1e5, requested_credit=1e4,
                application_channel="web", date_of_birth="1990-01-01", fraud_label=0)
    df = pd.DataFrame([{**base, **r} for r in rows])
    df["application_timestamp"] = pd.to_datetime(df["application_timestamp"])
    return df


def test_velocity_windows_count_only_prior_rows():
    df = _toy([
        dict(application_id="1", application_timestamp="2025-01-01 00:00", applicant_id="A1"),
        dict(application_id="2", application_timestamp="2025-01-01 00:30", applicant_id="A2"),
        dict(application_id="3", application_timestamp="2025-01-01 05:00", applicant_id="A3"),
        dict(application_id="4", application_timestamp="2025-01-05 00:00", applicant_id="A4"),
    ])
    f = build_features(df)
    assert list(f.device_id_apps_1h) == [0, 1, 0, 0]
    assert list(f.device_id_apps_24h) == [0, 1, 2, 0]
    assert list(f.device_id_apps_7d) == [0, 1, 2, 3]
    assert list(f.device_id_prior_distinct_applicants) == [0, 1, 2, 3]


def test_features_are_point_in_time():
    """A row's features must not change when LATER rows are appended."""
    df = generate(n=800, seed=3)
    cut = df.application_timestamp.iloc[500]
    full = build_features(df, train_end=cut)
    part = build_features(df.iloc[:500], train_end=cut)
    cols = [c for c in full.columns if c not in ("split",)]
    num = [c for c in cols if full[c].dtype.kind in "if"]
    np.testing.assert_allclose(full[num].iloc[:500].to_numpy(), part[num].to_numpy())


def test_neighbor_fraud_ratio_ignores_labels_after_train_end_and_immature():
    df = _toy([
        dict(application_id="1", application_timestamp="2025-01-01", applicant_id="A1", fraud_label=1),
        dict(application_id="2", application_timestamp="2025-01-10", applicant_id="A2"),   # label of #1 immature (<30d)
        dict(application_id="3", application_timestamp="2025-03-01", applicant_id="A3"),   # #1 matured, in train
        dict(application_id="4", application_timestamp="2025-06-01", applicant_id="A4"),
    ])
    cols = ["device_id", "ip_address", "email", "phone", "address"]
    g = graph_features(df, cols, train_end=pd.Timestamp("2025-02-01"), maturity_days=30)
    assert g.neighbor_fraud_ratio.iloc[1] == 0          # immature
    assert g.neighbor_fraud_ratio.iloc[2] > 0           # matured + in train
    # same data but #1 after train_end => label must be unusable
    g2 = graph_features(df, cols, train_end=pd.Timestamp("2024-12-31"), maturity_days=30)
    assert (g2.neighbor_fraud_ratio == 0).all()


def test_changing_future_labels_does_not_change_features():
    """Strict mode (label_scope=train): labels after train_end never influence any feature."""
    cfg = {**load_config("features"), "label_scope": "train"}
    df = generate(n=800, seed=5)
    split_t = df.application_timestamp.iloc[480]
    a = build_features(df, train_end=split_t, cfg=cfg)
    df2 = df.copy()
    df2.loc[df2.application_timestamp > split_t, "fraud_label"] = 1 - df2.fraud_label
    b = build_features(df2, train_end=split_t, cfg=cfg)
    pd.testing.assert_frame_equal(a.drop(columns="fraud_label"), b.drop(columns="fraud_label"))


def test_immature_labels_never_leak_in_all_matured_mode():
    """Default mode: a label becomes usable only after the maturity lag, so flipping every label
    younger than the lag (relative to the last application) must not change any feature."""
    cfg = load_config("features")
    df = generate(n=800, seed=5)
    last = df.application_timestamp.max()
    young = df.application_timestamp > last - pd.Timedelta(days=cfg["label_maturity_days"])
    assert young.sum() > 0
    a = build_features(df, cfg=cfg)
    df2 = df.copy()
    df2.loc[young, "fraud_label"] = 1 - df2.loc[young, "fraud_label"]
    b = build_features(df2, cfg=cfg)
    pd.testing.assert_frame_equal(a.drop(columns="fraud_label"), b.drop(columns="fraud_label"))


def test_chronological_split_no_overlap():
    df = generate(n=500, seed=4)
    tr, va, te, end = chronological_split(df)
    assert tr.application_timestamp.max() <= va.application_timestamp.min()
    assert va.application_timestamp.max() <= te.application_timestamp.min()
    assert end == tr.application_timestamp.max() and len(tr) + len(va) + len(te) == len(df)


def test_component_size_grows_with_shared_device():
    df = _toy([dict(application_id=str(i), application_timestamp=f"2025-01-0{i + 1}", applicant_id=f"A{i}",
                    phone=f"p{i}", address=f"a{i}", email=f"e{i}@x.test", ip_address=f"i{i}") for i in range(4)])
    f = build_features(df)
    assert list(f.component_size) == [1, 2, 3, 4]


def test_unknown_labels_are_excluded_from_neighbor_fraud_ratio():
    """Online applications have no label (NaN). They must not count as known non-fraud once matured."""
    cols = ["device_id", "ip_address", "email", "phone", "address"]
    rows = [
        dict(application_id="1", application_timestamp="2025-01-01", applicant_id="A1", fraud_label=1),
        dict(application_id="2", application_timestamp="2025-01-02", applicant_id="A2", fraud_label=float("nan")),
        dict(application_id="3", application_timestamp="2025-01-03", applicant_id="A3", fraud_label=float("nan")),
        dict(application_id="4", application_timestamp="2025-03-01", applicant_id="A4"),
    ]
    g = graph_features(_toy(rows), cols, maturity_days=7)
    assert g.neighbor_fraud_ratio.iloc[3] == 1.0   # 1 known fraud / 1 known; NaNs ignored, not diluted to 1/3
