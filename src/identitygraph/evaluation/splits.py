from __future__ import annotations

import pandas as pd


def chronological_split(df: pd.DataFrame, train_frac: float = 0.6, val_frac: float = 0.2):
    """Return (train, val, test) by application_timestamp order, plus the train_end timestamp."""
    df = df.sort_values("application_timestamp", kind="stable").reset_index(drop=True)
    n = len(df)
    i1, i2 = int(n * train_frac), int(n * (train_frac + val_frac))
    train, val, test = df.iloc[:i1], df.iloc[i1:i2], df.iloc[i2:]
    train_end = train["application_timestamp"].iloc[-1]
    assert train["application_timestamp"].max() <= val["application_timestamp"].min()
    assert val["application_timestamp"].max() <= test["application_timestamp"].min()
    return train, val, test, train_end
