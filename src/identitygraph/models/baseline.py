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


def model_specs(random_state: int = 42) -> dict:
    """name -> (estimator, numeric feature list, scale?)."""
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
