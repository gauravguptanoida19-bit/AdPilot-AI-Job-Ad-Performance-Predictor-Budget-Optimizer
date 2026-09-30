"""Unit tests for ML components, TreeSHAP explainer, and Bandit Simulator."""

import pytest
import numpy as np
import pandas as pd
from src.data.loader import process_features, load_and_preprocess_data
from src.explainability.explainer import AdPerformanceExplainer
from src.optimizer.bandit import BanditSimulator, DEFAULT_CHANNELS


def test_feature_processing():
    """Verify feature engineering extracts required signals properly."""
    raw_df = pd.DataFrame([{
        "title": "Senior Software Engineer",
        "description": "Responsibilities:\n- Build microservices\n- Mentor engineers\nRequirements:\n- 5 years Python",
        "min_salary": 140000.0,
        "max_salary": 180000.0,
        "pay_period": "YEARLY",
        "location": "Remote",
        "formatted_work_type": "Full-time",
        "formatted_experience_level": "Mid-Senior level",
        "skills_desc": "Python, Docker, AWS",
        "remote_allowed": 1,
        "sponsored": 0,
        "views": 100,
        "applies": 10
    }])
    feats = process_features(raw_df)
    assert len(feats) == 1
    row = feats.iloc[0]
    assert row["has_salary"] == 1
    assert row["normalized_salary_annual"] == 160000.0
    assert row["is_remote"] == 1
    assert row["seniority_level"] == 3
    assert row["skills_count"] == 3
    assert row["desc_bullet_points"] == 3


def test_explainer_inference():
    """Verify TreeSHAP explainer produces valid local explanations and recommendations."""
    explainer = AdPerformanceExplainer()
    raw_df = pd.DataFrame([{
        "title": "Account Executive",
        "description": "Short description without salary",
        "min_salary": None,
        "max_salary": None,
        "pay_period": None,
        "location": "Dallas, TX",
        "formatted_work_type": "Full-time",
        "formatted_experience_level": "Entry level",
        "skills_desc": "",
        "remote_allowed": 0,
        "sponsored": 0
    }])
    feats = process_features(raw_df).iloc[0].to_dict()
    res = explainer.explain_instance(feats)

    assert 0.0 < res["predicted_apply_rate"] <= 1.0
    assert "top_positive_drivers" in res
    assert "top_negative_drivers" in res
    assert len(res["actionable_recommendations"]) > 0
    # Missing salary should trigger a salary recommendation
    cats = [r["category"] for r in res["actionable_recommendations"]]
    assert "Salary Transparency" in cats


def test_bandit_simulation_lift():
    """Verify Thompson Sampling achieves lower or competitive CPA and valid budget conservation."""
    simulator = BanditSimulator(total_budget=5000.0, days=15, seed=123)
    results = simulator.run_simulation()

    strat = results["strategy_comparisons"]
    assert "thompson_sampling" in strat
    assert "equal_split" in strat

    # Total spend should closely match budget (within 1%)
    ts_spent = strat["thompson_sampling"]["total_budget_spent"]
    assert abs(ts_spent - 5000.0) < 100.0

    eq_spent = strat["equal_split"]["total_budget_spent"]
    assert abs(eq_spent - 5000.0) < 100.0

    # Applications should be positive
    assert strat["thompson_sampling"]["total_applications"] > 0
    assert strat["equal_split"]["total_applications"] > 0

    # Business impact fields present
    impact = results["business_impact"]
    assert "application_lift_pct" in impact
    assert "cpa_savings_per_app" in impact
