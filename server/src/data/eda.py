"""Exploratory Data Analysis (EDA) module for recruitment ad performance."""

from __future__ import annotations
import os
import json
from typing import Dict, Any
import numpy as np
import pandas as pd

try:
    from src.data.loader import load_and_preprocess_data, RAW_DATA_PATH
except ImportError:
    from loader import load_and_preprocess_data, RAW_DATA_PATH

REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


def run_eda(raw_path: str = RAW_DATA_PATH) -> Dict[str, Any]:
    """Run comprehensive EDA on raw and processed recruitment ad data."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    df_raw = pd.read_csv(raw_path)
    df_raw["applies"] = df_raw["applies"].fillna(0)
    df_raw["apply_rate"] = (df_raw["applies"] / df_raw["views"].clip(lower=1)).clip(lower=0.0, upper=1.0)
    df_raw["has_salary"] = (df_raw["max_salary"].notna() | df_raw["min_salary"].notna() | df_raw["med_salary"].notna()).astype(int)

    # 1. Overall volume statistics
    total_postings = len(df_raw)
    total_views = int(df_raw["views"].sum())
    total_applies = int(df_raw["applies"].sum())
    overall_cvr = float(total_applies / max(1, total_views))

    apply_rate_stats = {
        "mean": float(df_raw["apply_rate"].mean()),
        "median": float(df_raw["apply_rate"].median()),
        "std": float(df_raw["apply_rate"].std()),
        "q25": float(df_raw["apply_rate"].quantile(0.25)),
        "q75": float(df_raw["apply_rate"].quantile(0.75)),
        "q95": float(df_raw["apply_rate"].quantile(0.95))
    }

    # 2. Impact of Salary Transparency
    salary_group = df_raw.groupby("has_salary")["apply_rate"].agg(["count", "mean", "median"]).to_dict(orient="index")
    salary_lift_pct = (
        (salary_group[1]["mean"] - salary_group[0]["mean"]) / salary_group[0]["mean"] * 100.0
        if 0 in salary_group and 1 in salary_group and salary_group[0]["mean"] > 0 else 0.0
    )

    # 3. Impact of Remote Flexibility
    remote_flag = (df_raw["remote_allowed"] == 1) | df_raw["location"].fillna("").str.lower().str.contains("remote")
    df_raw["is_remote_calc"] = remote_flag.astype(int)
    remote_group = df_raw.groupby("is_remote_calc")["apply_rate"].agg(["count", "mean", "median"]).to_dict(orient="index")
    remote_lift_pct = (
        (remote_group[1]["mean"] - remote_group[0]["mean"]) / remote_group[0]["mean"] * 100.0
        if 0 in remote_group and 1 in remote_group and remote_group[0]["mean"] > 0 else 0.0
    )

    # 4. Conversion by Experience Level
    exp_cvr = df_raw.groupby("formatted_experience_level")["apply_rate"].mean().to_dict()

    # 5. Conversion by Work Type
    work_cvr = df_raw.groupby("formatted_work_type")["apply_rate"].mean().to_dict()

    # 6. Feature Correlation with Apply Rate
    data_bundle = load_and_preprocess_data(raw_path)
    X_train = data_bundle["X_train"]
    y_train = data_bundle["y_train_reg"]
    corr_series = X_train.apply(lambda col: np.corrcoef(col, y_train)[0, 1] if col.std() > 1e-6 else 0.0)
    top_correlations = corr_series.sort_values(ascending=False).to_dict()

    summary = {
        "dataset_summary": {
            "total_postings": total_postings,
            "total_views": total_views,
            "total_applies": total_applies,
            "overall_cvr": round(overall_cvr, 4)
        },
        "apply_rate_distribution": {k: round(v, 4) for k, v in apply_rate_stats.items()},
        "salary_transparency_analysis": {
            "with_salary_mean_cvr": round(salary_group.get(1, {}).get("mean", 0.0), 4),
            "without_salary_mean_cvr": round(salary_group.get(0, {}).get("mean", 0.0), 4),
            "measured_lift_pct": round(salary_lift_pct, 2),
            "postings_with_salary_count": salary_group.get(1, {}).get("count", 0),
            "postings_without_salary_count": salary_group.get(0, {}).get("count", 0)
        },
        "remote_work_analysis": {
            "remote_mean_cvr": round(remote_group.get(1, {}).get("mean", 0.0), 4),
            "onsite_mean_cvr": round(remote_group.get(0, {}).get("mean", 0.0), 4),
            "measured_lift_pct": round(remote_lift_pct, 2)
        },
        "experience_level_cvr": {k: round(v, 4) for k, v in exp_cvr.items()},
        "work_type_cvr": {k: round(v, 4) for k, v in work_cvr.items()},
        "feature_correlations": {k: round(float(v), 4) for k, v in top_correlations.items()}
    }

    report_path = os.path.join(REPORT_DIR, "eda_summary.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[EDA] Successfully generated EDA report at: {report_path}")
    print(f"[EDA] Total Postings: {total_postings} | Overall CVR: {overall_cvr:.2%}")
    print(f"[EDA] Salary transparency lift: +{salary_lift_pct:.1f}%")
    print(f"[EDA] Remote work lift: +{remote_lift_pct:.1f}%")
    return summary


if __name__ == "__main__":
    run_eda()
