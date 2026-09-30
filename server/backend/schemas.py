"""Pydantic schemas for FastAPI endpoints."""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class JobPostingInput(BaseModel):
    title: str = Field(..., json_schema_extra={"example": "Senior Full Stack Engineer"})
    company_name: Optional[str] = Field("Acme Inc", json_schema_extra={"example": "TechCorp"})
    description: str = Field(..., json_schema_extra={"example": "We are looking for a Senior Full Stack Engineer with 5+ years of experience..."})
    min_salary: Optional[float] = Field(None, json_schema_extra={"example": 130000.0})
    max_salary: Optional[float] = Field(None, json_schema_extra={"example": 170000.0})
    pay_period: Optional[str] = Field("YEARLY", json_schema_extra={"example": "YEARLY"})
    location: str = Field("San Francisco, CA", json_schema_extra={"example": "San Francisco, CA"})
    formatted_work_type: str = Field("Full-time", json_schema_extra={"example": "Full-time"})
    formatted_experience_level: str = Field("Mid-Senior level", json_schema_extra={"example": "Mid-Senior level"})
    skills: Optional[str] = Field("", json_schema_extra={"example": "Python, React, Docker, AWS, PostgreSQL"})
    sponsored: Optional[bool] = Field(False, json_schema_extra={"example": False})


class FeatureContribution(BaseModel):
    feature: str
    value: Any
    shap_impact: float
    direction: str


class OptimizationRecommendation(BaseModel):
    category: str
    severity: str
    impact: str
    recommendation: str
    shap_drag: float


class PredictionResponse(BaseModel):
    predicted_apply_rate: float
    predicted_apply_rate_pct: float
    expected_applications_per_100_views: float
    high_conversion_probability: float
    is_high_converting: bool
    baseline_apply_rate: float
    total_shap_impact: float
    top_positive_drivers: List[FeatureContribution]
    top_negative_drivers: List[FeatureContribution]
    actionable_recommendations: List[OptimizationRecommendation]
    engineered_features: Dict[str, Any]


class ChannelConfig(BaseModel):
    id: str
    name: str
    cpc: float
    true_cvr: float
    daily_capacity: int
    description: str


class SimulationRequest(BaseModel):
    total_budget: float = Field(10000.0, ge=500.0, le=500000.0)
    days: int = Field(30, ge=7, le=90)
    channels: Optional[List[ChannelConfig]] = None
    seed: Optional[int] = 42


class BusinessImpact(BaseModel):
    application_lift_pct: float
    additional_applications: int
    cpa_savings_per_app: float
    cpa_savings_pct: float
    headline: str


class SimulationResponse(BaseModel):
    simulation_parameters: Dict[str, Any]
    business_impact: BusinessImpact
    strategy_comparisons: Dict[str, Any]
    detailed_trajectories: Dict[str, Any]
