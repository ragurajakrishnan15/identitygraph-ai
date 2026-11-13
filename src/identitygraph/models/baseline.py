from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ..features.pipeline import BASE_FEATURES, CATEGORICAL, GRAPH_FEATURES


def make_preprocessor(numeric: list[str], scale: bool) -> ColumnTransformer:
    num = StandardScaler() if scale else "passthrough"
    return ColumnTransformer([
        ("num", num, numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])


def _boosters(random_state: int) -> dict:
    """XGBoost / LightGBM variants (skipped gracefully if the libraries are not installed)."""
    out: dict = {}
    try:
        from xgboost import XGBClassifier
        mk = lambda: XGBClassifier(n_estimators=300, max_depth=4, learning_rate=0.05, subsample=0.8,  # noqa: E731
                                   colsample_bytree=0.8, eval_metric="logloss", n_jobs=2, random_state=random_state)
        out["xgboost"] = (mk(), BASE_FEATURES, False)
        out["graph_xgboost"] = (mk(), BASE_FEATURES + GRAPH_FEATURES, False)
    except ImportError:  # pragma: no cover
        pass
    try:
        from lightgbm import LGBMClassifier
        mk = lambda: LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=15, subsample=0.8,  # noqa: E731
                                    colsample_bytree=0.8, n_jobs=2, random_state=random_state, verbose=-1)
        out["lightgbm"] = (mk(), BASE_FEATURES, False)
        out["graph_lightgbm"] = (mk(), BASE_FEATURES + GRAPH_FEATURES, False)
    except ImportError:  # pragma: no cover
        pass
    return out


def model_specs(random_state: int = 42) -> dict:
    """name -> (estimator, numeric feature list, scale?)."""
    return {**_core_specs(random_state), **_boosters(random_state)}


def _core_specs(random_state: int) -> dict:
    return {
        "logistic_regression": (LogisticRegression(max_iter=2000, class_weight="balanced"), BASE_FEATURES, True),
        "random_forest": (RandomForestClassifier(n_estimators=200, min_samples_leaf=3, class_weight="balanced_subsample",
                                                 n_jobs=-1, random_state=random_state), BASE_FEATURES, False),
        "gradient_boosting": (GradientBoostingClassifier(random_state=random_state), BASE_FEATURES, False),
        "graph_gradient_boosting": (GradientBoostingClassifier(random_state=random_state),
                                    BASE_FEATURES + GRAPH_FEATURES, False),
    }


def build_pipeline(name: str, random_state: int = 42) -> tuple[Pipeline, list[str]]:
    est, feats, scale = model_specs(random_state)[name]
    return Pipeline([("prep", make_preprocessor(feats, scale)), ("clf", est)]), feats
