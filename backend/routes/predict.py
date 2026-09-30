"""Prediction and local SHAP explanation API routes."""

from __future__ import annotations
import os
import joblib
import pandas as pd
import numpy as np
from fastapi import APIRouter, HTTPException

from backend.schemas import JobPostingInput, PredictionResponse
from src.data.loader import process_features
from src.explainability.explainer import AdPerformanceExplainer

router = APIRouter(prefix="/api/v1", tags=["Prediction & Explanations"])
MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")

# Cached instances
_explainer = None
_clf_model = None


def get_explainer() -> AdPerformanceExplainer:
    global _explainer
    if _explainer is None:
        _explainer = AdPerformanceExplainer()
    return _explainer


def get_clf_model():
    global _clf_model
    if _clf_model is None:
        clf_path = os.path.join(MODELS_DIR, "lightgbm_classifier.joblib")
        if not os.path.exists(clf_path):
            raise HTTPException(status_code=500, detail="Classifier model not found.")
        _clf_model = joblib.load(clf_path)
    return _clf_model


@router.post("/predict", response_model=PredictionResponse)
def predict_ad_performance(job: JobPostingInput) -> PredictionResponse:
    """Predict application conversion rate, high-performing likelihood, and generate SHAP breakdown."""
    explainer = get_explainer()
    clf_model = get_clf_model()

    # Convert input schema into single-row DataFrame matching loader expectations
    row = {
        "title": job.title,
        "company_name": job.company_name,
        "description": job.description,
        "min_salary": job.min_salary,
        "max_salary": job.max_salary,
        "med_salary": (job.min_salary + job.max_salary) / 2.0 if (job.min_salary and job.max_salary) else None,
        "pay_period": job.pay_period,
        "location": job.location,
        "formatted_work_type": job.formatted_work_type,
        "formatted_experience_level": job.formatted_experience_level,
        "skills_desc": job.skills,
        "remote_allowed": 1 if "remote" in job.location.lower() else 0,
        "sponsored": 1 if job.sponsored else 0,
        "listed_time": int(pd.Timestamp.now().timestamp() * 1000)
    }

    df_raw = pd.DataFrame([row])
    features_df = process_features(df_raw)
    feat_dict = features_df.iloc[0].to_dict()

    # 1. Regression & SHAP explainability
    explanation = explainer.explain_instance(feat_dict)
    predicted_apply_rate = explanation["predicted_apply_rate"]

    # 2. Classification: High conversion likelihood
    X_aligned = features_df[explainer.feature_names]
    clf_prob = float(clf_model.predict_proba(X_aligned)[0, 1])
    is_high = clf_prob >= 0.50

    return PredictionResponse(
        predicted_apply_rate=predicted_apply_rate,
        predicted_apply_rate_pct=round(predicted_apply_rate * 100.0, 2),
        expected_applications_per_100_views=round(predicted_apply_rate * 100.0, 1),
        high_conversion_probability=round(clf_prob, 3),
        is_high_converting=is_high,
        baseline_apply_rate=explanation["baseline_apply_rate"],
        total_shap_impact=explanation["total_impact"],
        top_positive_drivers=explanation["top_positive_drivers"],
        top_negative_drivers=explanation["top_negative_drivers"],
        actionable_recommendations=explanation["actionable_recommendations"],
        engineered_features={k: round(v, 2) if isinstance(v, float) else v for k, v in feat_dict.items()}
    )
