"""Evaluation and error analysis module for recruitment ad performance models.

Evaluates on test split:
- Regression: Dummy vs Ridge vs LightGBM (RMSE, MAE, R², Pearson r)
- Classification: Dummy vs Logistic vs LightGBM (ROC-AUC, PR-AUC, F1, Precision, Recall)
- Slice-based Error Analysis: Residuals, worst errors, and performance across slices.
"""

from __future__ import annotations
import os
import json
import joblib
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    roc_auc_score, average_precision_score, f1_score,
    precision_score, recall_score, accuracy_score
)
from scipy.stats import pearsonr

try:
    from src.data.loader import load_and_preprocess_data
except ImportError:
    from loader import load_and_preprocess_data

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def evaluate_models() -> Dict[str, Any]:
    """Evaluate trained models on the test set and generate error analysis."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    data = load_and_preprocess_data()
    X_test = data["X_test"]
    y_test_reg = data["y_test_reg"]
    y_test_clf = data["y_test_clf"]
    df_test_meta = data["df_test_meta"]

    # Load models
    dummy_reg = joblib.load(os.path.join(MODELS_DIR, "dummy_regressor.joblib"))
    linear_reg = joblib.load(os.path.join(MODELS_DIR, "linear_regressor.joblib"))
    lgbm_reg = joblib.load(os.path.join(MODELS_DIR, "lightgbm_regressor.joblib"))

    dummy_clf = joblib.load(os.path.join(MODELS_DIR, "dummy_classifier.joblib"))
    logistic_clf = joblib.load(os.path.join(MODELS_DIR, "logistic_classifier.joblib"))
    lgbm_clf = joblib.load(os.path.join(MODELS_DIR, "lightgbm_classifier.joblib"))

    # 1. Regression Predictions
    pred_dummy_reg = dummy_reg.predict(X_test)
    pred_linear_reg = linear_reg.predict(X_test)
    pred_lgbm_reg = lgbm_reg.predict(X_test)

    def calc_reg_metrics(y_true, y_pred, name):
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))
        r2 = float(r2_score(y_true, y_pred))
        pr, _ = pearsonr(y_true, y_pred) if np.std(y_pred) > 1e-6 else (0.0, 1.0)
        return {
            "model": name,
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "r2": round(r2, 4),
            "pearson_r": round(float(pr), 4)
        }

    reg_metrics = {
        "dummy_baseline": calc_reg_metrics(y_test_reg, pred_dummy_reg, "Dummy Baseline (Median)"),
        "linear_ridge": calc_reg_metrics(y_test_reg, pred_linear_reg, "Ridge Regression"),
        "lightgbm": calc_reg_metrics(y_test_reg, pred_lgbm_reg, "LightGBM Regressor")
    }

    # 2. Classification Predictions
    pred_dummy_prob = dummy_clf.predict_proba(X_test)[:, 1] if hasattr(dummy_clf, "predict_proba") else np.zeros(len(X_test))
    pred_logistic_prob = logistic_clf.predict_proba(X_test)[:, 1]
    pred_lgbm_prob = lgbm_clf.predict_proba(X_test)[:, 1]

    pred_dummy_class = dummy_clf.predict(X_test)
    pred_logistic_class = logistic_clf.predict(X_test)
    pred_lgbm_class = (pred_lgbm_prob >= 0.5).astype(int)

    def calc_clf_metrics(y_true, y_prob, y_pred, name):
        try:
            auc = float(roc_auc_score(y_true, y_prob))
        except Exception:
            auc = 0.5
        try:
            pr_auc = float(average_precision_score(y_true, y_prob))
        except Exception:
            pr_auc = float(np.mean(y_true))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        acc = float(accuracy_score(y_true, y_pred))
        return {
            "model": name,
            "roc_auc": round(auc, 4),
            "pr_auc": round(pr_auc, 4),
            "f1_score": round(f1, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "accuracy": round(acc, 4)
        }

    clf_metrics = {
        "dummy_baseline": calc_clf_metrics(y_test_clf, pred_dummy_prob, pred_dummy_class, "Dummy Baseline"),
        "logistic_regression": calc_clf_metrics(y_test_clf, pred_logistic_prob, pred_logistic_class, "Logistic Regression"),
        "lightgbm": calc_clf_metrics(y_test_clf, pred_lgbm_prob, pred_lgbm_class, "LightGBM Classifier")
    }

    # Improvement summary
    reg_rmse_reduction_pct = (
        (reg_metrics["dummy_baseline"]["rmse"] - reg_metrics["lightgbm"]["rmse"])
        / reg_metrics["dummy_baseline"]["rmse"] * 100.0
    )
    clf_auc_improvement_pct = (
        (clf_metrics["lightgbm"]["roc_auc"] - clf_metrics["dummy_baseline"]["roc_auc"])
        / clf_metrics["dummy_baseline"]["roc_auc"] * 100.0
    )

    comparison_summary = {
        "regression": reg_metrics,
        "classification": clf_metrics,
        "improvements": {
            "rmse_reduction_vs_baseline_pct": round(reg_rmse_reduction_pct, 2),
            "r2_jump": round(reg_metrics["lightgbm"]["r2"] - reg_metrics["dummy_baseline"]["r2"], 4),
            "roc_auc_lift_pct": round(clf_auc_improvement_pct, 2),
            "roc_auc_lightgbm": clf_metrics["lightgbm"]["roc_auc"],
            "roc_auc_logistic": clf_metrics["logistic_regression"]["roc_auc"]
        }
    }

    with open(os.path.join(REPORTS_DIR, "model_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(comparison_summary, f, indent=2)

    with open(os.path.join(REPORTS_DIR, "baseline_comparison.json"), "w", encoding="utf-8") as f:
        json.dump(comparison_summary, f, indent=2)

    # 3. Error Analysis
    res_vals = (y_test_reg.values - pred_lgbm_reg)
    abs_errors = np.abs(res_vals)

    # Worst over-predictions (predicted much higher than actual)
    worst_over_idx = np.argsort(res_vals)[:5]
    worst_over = []
    for idx in worst_over_idx:
        meta_row = df_test_meta.iloc[idx]
        worst_over.append({
            "title": str(meta_row.get("title", "")),
            "company": str(meta_row.get("company_name", "")),
            "views": int(meta_row.get("views", 0)),
            "applies": int(meta_row.get("applies", 0)),
            "actual_apply_rate": round(float(y_test_reg.iloc[idx]), 4),
            "predicted_apply_rate": round(float(pred_lgbm_reg[idx]), 4),
            "residual": round(float(res_vals[idx]), 4)
        })

    # Worst under-predictions (predicted much lower than actual)
    worst_under_idx = np.argsort(res_vals)[-5:]
    worst_under = []
    for idx in reversed(worst_under_idx):
        meta_row = df_test_meta.iloc[idx]
        worst_under.append({
            "title": str(meta_row.get("title", "")),
            "company": str(meta_row.get("company_name", "")),
            "views": int(meta_row.get("views", 0)),
            "applies": int(meta_row.get("applies", 0)),
            "actual_apply_rate": round(float(y_test_reg.iloc[idx]), 4),
            "predicted_apply_rate": round(float(pred_lgbm_reg[idx]), 4),
            "residual": round(float(res_vals[idx]), 4)
        })

    # Subgroup/Slice Evaluation
    slices = {}

    # Slice by salary
    mask_sal = (X_test["has_salary"].values == 1)
    slices["salary_specified"] = {
        "sample_count": int(np.sum(mask_sal)),
        "mae": round(float(mean_absolute_error(y_test_reg.values[mask_sal], pred_lgbm_reg[mask_sal])), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test_reg.values[mask_sal], pred_lgbm_reg[mask_sal]))), 4)
    }
    slices["salary_omitted"] = {
        "sample_count": int(np.sum(~mask_sal)),
        "mae": round(float(mean_absolute_error(y_test_reg.values[~mask_sal], pred_lgbm_reg[~mask_sal])), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test_reg.values[~mask_sal], pred_lgbm_reg[~mask_sal]))), 4)
    }

    # Slice by remote
    mask_remote = (X_test["is_remote"].values == 1)
    slices["remote_roles"] = {
        "sample_count": int(np.sum(mask_remote)),
        "mae": round(float(mean_absolute_error(y_test_reg.values[mask_remote], pred_lgbm_reg[mask_remote])), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test_reg.values[mask_remote], pred_lgbm_reg[mask_remote]))), 4)
    }
    slices["onsite_roles"] = {
        "sample_count": int(np.sum(~mask_remote)),
        "mae": round(float(mean_absolute_error(y_test_reg.values[~mask_remote], pred_lgbm_reg[~mask_remote])), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test_reg.values[~mask_remote], pred_lgbm_reg[~mask_remote]))), 4)
    }

    error_analysis = {
        "residual_summary": {
            "mean_residual": round(float(np.mean(res_vals)), 5),
            "std_residual": round(float(np.std(res_vals)), 4),
            "median_abs_error": round(float(np.median(abs_errors)), 4),
            "max_abs_error": round(float(np.max(abs_errors)), 4)
        },
        "slice_performance": slices,
        "worst_over_predictions": worst_over,
        "worst_under_predictions": worst_under
    }

    with open(os.path.join(REPORTS_DIR, "error_analysis.json"), "w", encoding="utf-8") as f:
        json.dump(error_analysis, f, indent=2)

    print("[Evaluation] Successfully generated model evaluation & error analysis!")
    print(f"[Evaluation] LightGBM RMSE: {reg_metrics['lightgbm']['rmse']} (vs Dummy {reg_metrics['dummy_baseline']['rmse']})")
    print(f"[Evaluation] LightGBM R²: {reg_metrics['lightgbm']['r2']} (vs Linear {reg_metrics['linear_ridge']['r2']})")
    print(f"[Evaluation] LightGBM ROC-AUC: {clf_metrics['lightgbm']['roc_auc']} (vs Logistic {clf_metrics['logistic_regression']['roc_auc']})")
    return comparison_summary


if __name__ == "__main__":
    evaluate_models()
