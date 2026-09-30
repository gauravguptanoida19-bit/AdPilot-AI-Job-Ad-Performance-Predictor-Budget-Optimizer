"""API integration tests using FastAPI TestClient."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_healthcheck():
    """Verify health endpoint returns 200 and readiness status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True
    assert data["reports_available"] is True


def test_get_metrics():
    """Verify metrics route returns evaluation, error analysis and EDA summary."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "evaluation" in data
    assert "error_analysis" in data
    assert "eda_summary" in data
    assert "lightgbm" in data["evaluation"]["regression"]


def test_get_global_shap():
    """Verify global TreeSHAP endpoint returns feature rankings."""
    response = client.get("/api/v1/shap/global")
    assert response.status_code == 200
    data = response.json()
    assert "top_features" in data
    assert len(data["top_features"]) > 0


def test_get_sample_jobs():
    """Verify sample jobs endpoint returns preset templates."""
    response = client.get("/api/v1/sample-jobs")
    assert response.status_code == 200
    samples = response.json()
    assert isinstance(samples, list)
    assert len(samples) >= 3


def test_predict_endpoint():
    """Verify prediction endpoint returns apply rate, high-converting probability and SHAP."""
    payload = {
        "title": "Senior Backend Engineer",
        "company_name": "Apex Tech Systems",
        "description": "About the Role:\nWe need a Senior Backend Engineer.\n\nResponsibilities:\n- Design scalable APIs\n- Work with databases\n\nRequirements:\n- 4+ years Python experience\n- Strong SQL skills",
        "min_salary": 140000.0,
        "max_salary": 170000.0,
        "pay_period": "YEARLY",
        "location": "Remote",
        "formatted_work_type": "Full-time",
        "formatted_experience_level": "Mid-Senior level",
        "skills": "Python, SQL, Docker",
        "sponsored": True
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_apply_rate" in data
    assert 0.0 < data["predicted_apply_rate"] <= 1.0
    assert "high_conversion_probability" in data
    assert "actionable_recommendations" in data
    assert "top_positive_drivers" in data


def test_channels_endpoint():
    """Verify default channels list."""
    response = client.get("/api/v1/channels")
    assert response.status_code == 200
    channels = response.json()
    assert len(channels) >= 5
    assert any(c["id"] == "linkedin_jobs" for c in channels)


def test_login_endpoint():
    """Verify login authentication endpoint with demo user."""
    payload = {
        "email": "recruiter@joveo.com",
        "password": "password123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["email"] == "recruiter@joveo.com"
    assert data["user"]["name"] == "Sarah Chen"


def test_simulate_endpoint():
    """Verify running budget simulation returns expected comparative metrics."""
    payload = {
        "total_budget": 5000.0,
        "days": 14,
        "seed": 42
    }
    response = client.post("/api/v1/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "business_impact" in data
    assert "strategy_comparisons" in data
    assert "thompson_sampling" in data["strategy_comparisons"]
    assert "equal_split" in data["strategy_comparisons"]
    assert data["business_impact"]["application_lift_pct"] > 0
