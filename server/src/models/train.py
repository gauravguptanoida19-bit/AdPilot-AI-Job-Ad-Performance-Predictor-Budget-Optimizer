"""Training pipeline for Recruitment Ad Performance Predictor models.

Trains:
- Regressors: Baseline Dummy, Ridge/Linear, LightGBM Regressor (predicting apply_rate)
- Classifiers: Baseline Dummy, Logistic Regression, LightGBM Classifier (predicting high-converting ad)
"""

from __future__ import annotations
import os
import json
import joblib
from typing import Dict, Any
import numpy as np
from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import lightgbm as lgb

try:
    from src.data.loader import load_and_preprocess_data
except ImportError:
    from loader import load_and_preprocess_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")


def train_models() -> Dict[str, Any]:
    """Train all baseline and LightGBM models, saving artifacts to disk."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    print("[Training] Loading preprocessed data...")
    data = load_and_preprocess_data()

    X_train = data["X_train"]
    y_train_reg = data["y_train_reg"]
    y_train_clf = data["y_train_clf"]
    feature_names = data["feature_names"]

    print(f"[Training] Features count: {len(feature_names)}. Training samples: {len(X_train)}")

    # 1. Regressors
    print("[Training] Training Baseline Dummy Regressor...")
    dummy_reg = DummyRegressor(strategy="median")
    dummy_reg.fit(X_train, y_train_reg)

    print("[Training] Training Linear/Ridge Regressor...")
    linear_reg = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", Ridge(alpha=10.0, random_state=42))
    ])
    linear_reg.fit(X_train, y_train_reg)

    print("[Training] Training LightGBM Regressor...")
    lgbm_reg = lgb.LGBMRegressor(
        n_estimators=350,
        learning_rate=0.035,
        num_leaves=31,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_samples=25,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgbm_reg.fit(X_train, y_train_reg)

    # 2. Classifiers
    print("[Training] Training Baseline Dummy Classifier...")
    dummy_clf = DummyClassifier(strategy="most_frequent")
    dummy_clf.fit(X_train, y_train_clf)

    print("[Training] Training Logistic Regression Classifier...")
    logistic_clf = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42))
    ])
    logistic_clf.fit(X_train, y_train_clf)

    print("[Training] Training LightGBM Classifier...")
    lgbm_clf = lgb.LGBMClassifier(
        n_estimators=350,
        learning_rate=0.035,
        num_leaves=31,
        max_depth=6,
        subsample=0.85,
        colsample_bytree=0.85,
        min_child_samples=25,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgbm_clf.fit(X_train, y_train_clf)

    # Save artifacts
    artifacts = {
        "dummy_regressor.joblib": dummy_reg,
        "linear_regressor.joblib": linear_reg,
        "lightgbm_regressor.joblib": lgbm_reg,
        "dummy_classifier.joblib": dummy_clf,
        "logistic_classifier.joblib": logistic_clf,
        "lightgbm_classifier.joblib": lgbm_clf,
    }

    for filename, model_obj in artifacts.items():
        save_path = os.path.join(MODELS_DIR, filename)
        joblib.dump(model_obj, save_path)
        print(f"[Training] Saved model artifact to: {save_path}")

    metadata = {
        "feature_names": feature_names,
        "num_features": len(feature_names),
        "target_reg": "apply_rate (applications / views)",
        "target_clf": "is_high_converting (apply_rate >= 60th percentile)",
        "threshold": data["threshold"],
        "train_samples": len(X_train),
        "test_samples": len(data["X_test"])
    }
    with open(os.path.join(MODELS_DIR, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("[Training] All models trained and saved successfully.")
    return {
        "artifacts": artifacts,
        "metadata": metadata,
        "data": data
    }


if __name__ == "__main__":
    train_models()
