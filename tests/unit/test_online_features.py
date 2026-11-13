"""OnlineFeaturizer must reproduce build_features exactly for newly arriving applications."""
import numpy as np
import pandas as pd
import pytest

from identitygraph.data.generator import generate
from identitygraph.features.online import OnlineFallback, OnlineFeaturizer
from identitygraph.features.pipeline import BASE_FEATURES, GRAPH_FEATURES, build_features

FEATS = BASE_FEATURES + GRAPH_FEATURES
RAW_DROP = ["fraud_label", "fraud_scenario"]


def _history_and_new(n_new=6, seed=11, offsets_h=None):
    df = generate(n=1500, seed=seed).sort_values("application_timestamp").reset_index(drop=True)
    # a few unknown (online-style) labels in the history
    df.loc[df.index % 17 == 0, "fraud_label"] = np.nan
    last = df.application_timestamp.max()
    fraud = df[df.fraud_label == 1]
    # new applications reuse entities of known-fraud cases, of each other, and of ordinary rows
    recent = fraud[fraud.application_timestamp > last - pd.Timedelta(days=4)]
    assert len(recent) >= 1  # labels still immature (7-day lag) for the early new rows
    src = pd.concat([fraud.iloc[:2], recent.iloc[-2:], df.iloc[[5, 600]]]).iloc[:n_new].copy()
    src = pd.concat([src, src.iloc[[0]]]).iloc[:n_new + 1].copy()  # last row shares everything with the first
    src["application_id"] = [f"NEW-{i}" for i in range(len(src))]
    src["applicant_id"] = [f"APL-NEW-{i}" for i in range(len(src))]
    offsets = offsets_h or [1, 2, 30, 31, 24 * 9, 24 * 9 + 1, 24 * 9 + 2]
    src["application_timestamp"] = [last + pd.Timedelta(hours=o) for o in offsets[:len(src)]]
    return df, src.drop(columns=RAW_DROP).reset_index(drop=True)


def _full(df, new):
    n = new.copy()
    n["fraud_label"] = np.nan
    both = pd.concat([df.drop(columns=["fraud_scenario"]), n], ignore_index=True)
    out = build_features(both)
    return out[out.application_id.isin(new.application_id)].set_index("application_id")


@pytest.mark.parametrize("seed", [11, 12])
def test_online_matches_full_recompute(seed):
    df, new = _history_and_new(seed=seed)
    expect = _full(df, new)
    got = OnlineFeaturizer(df).features(new).set_index("application_id")
    for c in FEATS:
        np.testing.assert_allclose(got.loc[expect.index, c].astype(float), expect[c].astype(float),
                                   err_msg=c, rtol=1e-9, atol=1e-9)
    # the comparison must exercise the interesting features, not just zeros
    assert expect["neighbor_fraud_ratio"].gt(0).any()
    assert expect["component_size"].gt(1).any() and expect["device_id_prior_apps"].gt(0).any()


def test_online_batch_equals_one_by_one():
    df, new = _history_and_new()
    batch = OnlineFeaturizer(df).features(new)
    fz = OnlineFeaturizer(df)
    single = pd.concat([fz.features(new.iloc[[i]]) for i in range(len(new))], ignore_index=True)
    for c in FEATS:
        np.testing.assert_allclose(batch[c].astype(float), single[c].astype(float), err_msg=c)


def test_commit_false_does_not_change_state():
    df, new = _history_and_new()
    fz = OnlineFeaturizer(df)
    a = fz.features(new.iloc[[0]], commit=False)
    b = fz.features(new.iloc[[0]], commit=False)
    for c in FEATS:
        assert a[c].iloc[0] == b[c].iloc[0], c


def test_old_timestamp_or_unsorted_batch_falls_back_without_mutating():
    df, new = _history_and_new()
    fz = OnlineFeaturizer(df)
    old = new.iloc[[0]].copy()
    old["application_timestamp"] = df.application_timestamp.iloc[100]
    with pytest.raises(OnlineFallback):
        fz.features(old)
    unsorted = new.iloc[[1, 0]].copy()  # second row older than the first
    with pytest.raises(OnlineFallback):
        fz.features(unsorted)
    # state untouched: the in-order batch still matches the full recompute
    expect = _full(df, new)
    got = fz.features(new).set_index("application_id")
    for c in FEATS:
        np.testing.assert_allclose(got.loc[expect.index, c].astype(float), expect[c].astype(float), err_msg=c)


def test_strict_label_scope_is_unsupported():
    df, new = _history_and_new()
    from identitygraph.config import load_config
    fz = OnlineFeaturizer(df, cfg={**load_config("features"), "label_scope": "train"})
    with pytest.raises(OnlineFallback):
        fz.features(new)
