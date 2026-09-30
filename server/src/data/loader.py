"""Data loading, cleaning, and feature engineering pipeline.

Prepares features for LightGBM and baseline models.
Handles both real LinkedIn postings dataset (Kaggle) and bootstrap dataset.
"""

from __future__ import annotations
import os
import re
from typing import Dict, Tuple, List, Any
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

try:
    from src.data.bootstrap_data import ensure_dataset
except ImportError:
    from bootstrap_data import ensure_dataset

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "postings.csv")
PROCESSED_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")

EXP_LEVEL_MAP = {
    "internship": 0,
    "entry level": 1,
    "associate": 2,
    "mid-senior level": 3,
    "director": 4,
    "executive": 5
}

JOB_CATEGORY_KEYWORDS = {
    "Software Engineering": ["software", "developer", "backend", "frontend", "full stack", "systems", "devops", "cloud", "infrastructure", "mobile", "ios", "android"],
    "Data & AI": ["data", "machine learning", "ml", "ai", "scientist", "analyst", "analytics", "bi", "quantitative", "research"],
    "Product & Design": ["product", "design", "ux", "ui", "designer", "roadmap", "wireframe"],
    "Sales & BD": ["sales", "account executive", "business development", "sdr", "partnerships", "pipeline"],
    "Marketing & Growth": ["marketing", "seo", "growth", "content", "brand", "social media", "copywriting"],
    "Operations & HR": ["hr", "human resources", "talent", "recruiting", "operations", "people", "coordinator", "admin"],
    "Customer Support": ["support", "success", "client", "service", "customer"]
}


def infer_category(title: str) -> str:
    """Infer job category from title."""
    t_lower = str(title).lower()
    for cat, keywords in JOB_CATEGORY_KEYWORDS.items():
        if any(kw in t_lower for kw in keywords):
            return cat
    return "Other"


def infer_seniority_score(title: str, exp_level_str: str | None = None) -> int:
    """Extract numeric seniority level from title and experience level."""
    t_lower = str(title).lower()
    if "intern" in t_lower:
        return 0
    if "junior" in t_lower or "associate" in t_lower or "entry" in t_lower:
        return 1
    if "director" in t_lower or "head" in t_lower:
        return 4
    if "vp" in t_lower or "vice president" in t_lower or "chief" in t_lower or "executive" in t_lower:
        return 5
    if "lead" in t_lower or "principal" in t_lower or "staff" in t_lower:
        return 4
    if "senior" in t_lower or "sr" in t_lower:
        return 3

    if exp_level_str and str(exp_level_str).lower() in EXP_LEVEL_MAP:
        return EXP_LEVEL_MAP[str(exp_level_str).lower()]
    return 2  # Default to Mid/Associate


def count_bullet_points(text: str) -> int:
    """Count bullet points or list markers in description."""
    if not isinstance(text, str):
        return 0
    return len(re.findall(r"(?:^|\n)\s*[-*•–]\s+", text))


def process_features(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features from raw postings dataframe."""
    processed = pd.DataFrame(index=df.index)

    # 1. Salary normalizations
    min_sal_col = df.get("min_salary", pd.Series(np.nan, index=df.index))
    max_sal_col = df.get("max_salary", pd.Series(np.nan, index=df.index))
    med_sal_col = df.get("med_salary", pd.Series(np.nan, index=df.index))

    has_salary = (min_sal_col.notna() | max_sal_col.notna() | med_sal_col.notna()).astype(int)
    processed["has_salary"] = has_salary

    # Compute annualized salary estimate
    def annualize_salary(row):
        pay_period = str(row.get("pay_period", "")).upper()
        med = row.get("med_salary")
        min_s = row.get("min_salary")
        max_s = row.get("max_salary")

        val = med if pd.notna(med) else (
            (min_s + max_s) / 2.0 if (pd.notna(min_s) and pd.notna(max_s)) else (
                min_s if pd.notna(min_s) else max_s
            )
        )
        if pd.isna(val):
            return np.nan
        if pay_period == "HOURLY":
            return val * 2080.0
        elif pay_period == "MONTHLY":
            return val * 12.0
        elif pay_period == "WEEKLY":
            return val * 52.0
        return val

    annual_salary = df.apply(annualize_salary, axis=1)
    median_sal = annual_salary.median() if not annual_salary.dropna().empty else 105000.0
    processed["normalized_salary_annual"] = annual_salary.fillna(median_sal)

    # Salary spread
    def calc_spread(row):
        min_s = row.get("min_salary")
        max_s = row.get("max_salary")
        if pd.notna(min_s) and pd.notna(max_s) and max_s > 0:
            return min(1.0, max(0.0, (max_s - min_s) / max_s))
        return 0.0

    processed["salary_spread"] = df.apply(calc_spread, axis=1)

    # 2. Text description characteristics
    descriptions = df["description"].fillna("").astype(str)
    processed["desc_char_length"] = descriptions.str.len()
    processed["desc_word_count"] = descriptions.str.split().str.len()
    processed["desc_bullet_points"] = descriptions.apply(count_bullet_points)
    # Optimal description length penalty/indicator (600 - 2000 chars is standard sweetspot)
    processed["desc_is_optimal_length"] = (
        (processed["desc_char_length"] >= 600) & (processed["desc_char_length"] <= 2000)
    ).astype(int)

    # 3. Job title & seniority
    titles = df["title"].fillna("").astype(str)
    processed["title_length"] = titles.str.len()
    exp_levels = df.get("formatted_experience_level", pd.Series(index=df.index, dtype=str))
    processed["seniority_level"] = [
        infer_seniority_score(t, e) for t, e in zip(titles, exp_levels)
    ]

    # Category encoding (one-hot)
    categories = [infer_category(t) for t in titles]
    for cat in JOB_CATEGORY_KEYWORDS.keys():
        col_name = f"cat_{cat.lower().replace(' ', '_').replace('&', 'and')}"
        processed[col_name] = [1 if c == cat else 0 for c in categories]

    # 4. Location & Remote
    remote_flag = df.get("remote_allowed", pd.Series(0, index=df.index)).fillna(0).astype(int)
    loc_remote = df["location"].fillna("").str.lower().str.contains("remote").astype(int)
    processed["is_remote"] = ((remote_flag == 1) | (loc_remote == 1)).astype(int)

    # Metro tier
    loc_tier_1 = df["location"].fillna("").str.lower().str.contains("san francisco|new york|seattle|boston").astype(int)
    loc_tier_2 = df["location"].fillna("").str.lower().str.contains("austin|chicago|denver|atlanta|dallas").astype(int)
    processed["loc_tier_1"] = loc_tier_1
    processed["loc_tier_2"] = loc_tier_2

    # 5. Work type
    work_type = df.get("formatted_work_type", pd.Series("", index=df.index)).fillna("").str.lower()
    processed["is_fulltime"] = (work_type == "full-time").astype(int)
    processed["is_contract"] = (work_type == "contract").astype(int)

    # 6. Skills count
    def extract_skills_count(val):
        if pd.isna(val) or not str(val).strip():
            return 0
        return len([s for s in str(val).split(",") if s.strip()])

    skills = df.get("skills_desc", pd.Series("", index=df.index))
    processed["skills_count"] = skills.apply(extract_skills_count)

    # 7. Sponsorship
    processed["sponsored"] = df.get("sponsored", pd.Series(0, index=df.index)).fillna(0).astype(int)

    # 8. Posting time signals
    listed_time = df.get("listed_time", pd.Series(0, index=df.index)).fillna(0)
    timestamps = pd.to_datetime(listed_time, unit="ms", errors="coerce")
    processed["posting_dayofweek"] = timestamps.dt.dayofweek.fillna(2).astype(int)
    processed["posting_hour"] = timestamps.dt.hour.fillna(12).astype(int)
    processed["is_weekend_posting"] = (processed["posting_dayofweek"] >= 5).astype(int)

    return processed


def load_and_preprocess_data(
    raw_path: str = RAW_DATA_PATH,
    test_size: float = 0.2,
    random_state: int = 42
) -> Dict[str, Any]:
    """Load raw dataset, clean, engineer features, and return train/test splits."""
    ensure_dataset(raw_path)
    df = pd.read_csv(raw_path)

    # Basic data validation
    df = df[df["views"].notna() & (df["views"] > 0)].copy()
    df["applies"] = df["applies"].fillna(0).clip(lower=0)

    # Calculate targets
    # Continuous apply rate: applies per view
    df["apply_rate"] = (df["applies"] / df["views"]).clip(lower=0.0, upper=1.0)

    # Classification target: high performing posting (above 60th percentile)
    threshold = df["apply_rate"].quantile(0.60)
    df["is_high_converting"] = (df["apply_rate"] >= threshold).astype(int)

    # Extract engineered feature matrix
    X = process_features(df)
    y_reg = df["apply_rate"]
    y_clf = df["is_high_converting"]

    feature_names = list(X.columns)

    X_train, X_test, y_train_reg, y_test_reg, y_train_clf, y_test_clf, df_train_meta, df_test_meta = train_test_split(
        X, y_reg, y_clf, df, test_size=test_size, random_state=random_state, stratify=y_clf
    )

    # Save processed datasets
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    train_save = X_train.copy()
    train_save["apply_rate"] = y_train_reg
    train_save["is_high_converting"] = y_train_clf
    train_save.to_csv(os.path.join(PROCESSED_DATA_DIR, "train.csv"), index=False)

    test_save = X_test.copy()
    test_save["apply_rate"] = y_test_reg
    test_save["is_high_converting"] = y_test_clf
    test_save.to_csv(os.path.join(PROCESSED_DATA_DIR, "test.csv"), index=False)

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train_reg": y_train_reg,
        "y_test_reg": y_test_reg,
        "y_train_clf": y_train_clf,
        "y_test_clf": y_test_clf,
        "df_train_meta": df_train_meta,
        "df_test_meta": df_test_meta,
        "feature_names": feature_names,
        "threshold": float(threshold)
    }


if __name__ == "__main__":
    data = load_and_preprocess_data()
    print(f"Loaded successfully. Train shape: {data['X_train'].shape}, Test shape: {data['X_test'].shape}")
    print(f"Features ({len(data['feature_names'])}): {data['feature_names']}")
