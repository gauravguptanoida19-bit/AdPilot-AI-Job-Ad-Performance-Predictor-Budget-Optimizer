"""Metrics and metadata API routes."""

from __future__ import annotations
import os
import json
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["Metrics & Analysis"])
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _read_json_file(filename: str) -> Dict[str, Any]:
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Report file {filename} not found.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/metrics")
def get_model_metrics() -> Dict[str, Any]:
    """Retrieve full model evaluation metrics, baseline comparison, and slice error analysis."""
    metrics = _read_json_file("model_metrics.json")
    error_analysis = _read_json_file("error_analysis.json")
    eda_summary = _read_json_file("eda_summary.json")

    return {
        "evaluation": metrics,
        "error_analysis": error_analysis,
        "eda_summary": eda_summary
    }


@router.get("/shap/global")
def get_global_shap() -> Dict[str, Any]:
    """Retrieve global TreeSHAP feature importance rankings."""
    return _read_json_file("shap_global_importance.json")


@router.get("/sample-jobs")
def get_sample_jobs() -> List[Dict[str, Any]]:
    """Return pre-configured job posting templates for instant testing in the UI."""
    return [
        {
            "id": "tech_lead_full",
            "label": "Senior Tech Lead (Full Transparency & Remote)",
            "title": "Lead Systems Engineer",
            "company_name": "Apex Tech Systems",
            "description": "About the Role:\nWe are looking for a Lead Systems Engineer to architect next-generation cloud infrastructure.\n\nResponsibilities:\n- Design scalable distributed systems\n- Champion reliability and DevOps CI/CD automation\n- Mentor mid-level developers\n- Partner with product managers on release schedules\n\nRequirements:\n- 6+ years engineering experience\n- Proficiency in Python, Kubernetes, AWS, Go\n- Experience with high-availability systems\n\nBenefits:\n- Comprehensive health insurance\n- 401(k) matching up to 5%\n- Unlimited PTO and home office budget",
            "min_salary": 160000.0,
            "max_salary": 200000.0,
            "pay_period": "YEARLY",
            "location": "Remote",
            "formatted_work_type": "Full-time",
            "formatted_experience_level": "Mid-Senior level",
            "skills": "Python, Kubernetes, AWS, Docker, Microservices, Git",
            "sponsored": True
        },
        {
            "id": "missing_salary_vague",
            "label": "Account Executive (Missing Salary & Brief Desc)",
            "title": "Account Executive",
            "company_name": "Nexus Digital Partners",
            "description": "We are seeking a hunter to close B2B enterprise deals. Must be energetic and self-driven. Fast-paced environment with unlimited potential.",
            "min_salary": None,
            "max_salary": None,
            "pay_period": "YEARLY",
            "location": "New York, NY",
            "formatted_work_type": "Full-time",
            "formatted_experience_level": "Associate",
            "skills": "B2B Sales, Cold Outreach",
            "sponsored": False
        },
        {
            "id": "data_scientist_onsite",
            "label": "Data Scientist (On-site, Moderate Salary)",
            "title": "Data Scientist",
            "company_name": "Vanguard Financial Analytics",
            "description": "Position: Data Scientist\nLocation: Boston, MA\n\nResponsibilities:\n- Build predictive credit scoring algorithms\n- Deploy ML models to production pipelines\n- Present analytical findings to executive stakeholders\n\nRequirements:\n- Master's in Computer Science, Statistics, or related discipline\n- Strong experience in Python, Scikit-Learn, SQL, LightGBM\n- Familiarity with financial regulations",
            "min_salary": 115000.0,
            "max_salary": 140000.0,
            "pay_period": "YEARLY",
            "location": "Boston, MA",
            "formatted_work_type": "Full-time",
            "formatted_experience_level": "Mid-Senior level",
            "skills": "Python, SQL, Machine Learning, Scikit-Learn, Statistics",
            "sponsored": False
        },
        {
            "id": "entry_support",
            "label": "Customer Support Representative (Hourly)",
            "title": "Customer Support Representative",
            "company_name": "BlueSky Retail Group",
            "description": "Join our team providing world-class assistance to customers via email and live chat.\n\nWhat you'll do:\n- Resolve inquiries with empathy and accuracy\n- Track issues in ticketing systems\n- Meet resolution SLAs\n\nWhat you bring:\n- Excellent written communication\n- Patience and problem-solving mentality\n- Availability for flexible shifts",
            "min_salary": 24.0,
            "max_salary": 28.0,
            "pay_period": "HOURLY",
            "location": "Austin, TX",
            "formatted_work_type": "Full-time",
            "formatted_experience_level": "Entry level",
            "skills": "Zendesk, Intercom, Customer Support",
            "sponsored": True
        }
    ]
