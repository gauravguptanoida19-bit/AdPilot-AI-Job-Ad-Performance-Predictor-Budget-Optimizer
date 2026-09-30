# FastAPI REST API Documentation

The AdPilot server exposes a high-throughput REST API for ad scoring, factor attribution, and bandit simulation.

Interactive Swagger documentation is available at:  
👉 `http://127.0.0.1:8000/docs`

---

## Endpoints Overview

### 1. Health & Readiness
`GET /health`
- **Response**:
```json
{
  "status": "healthy",
  "service": "recruitment-ad-optimizer-api",
  "version": "1.0.0",
  "models_loaded": true,
  "reports_available": true
}
```

### 2. Ad Performance Predictor & TreeSHAP
`POST /api/v1/predict`
- **Request Body**:
```json
{
  "title": "Senior Systems Engineer",
  "company_name": "Apex Tech Systems",
  "description": "Responsibilities: Build cloud systems...",
  "min_salary": 150000.0,
  "max_salary": 180000.0,
  "pay_period": "YEARLY",
  "location": "Remote",
  "formatted_work_type": "Full-time",
  "formatted_experience_level": "Mid-Senior level",
  "skills": "Python, Kubernetes, AWS",
  "sponsored": true
}
```
- **Response**:
```json
{
  "predicted_apply_rate": 0.1185,
  "predicted_apply_rate_pct": 11.85,
  "expected_applications_per_100_views": 11.9,
  "high_conversion_probability": 0.812,
  "is_high_converting": true,
  "baseline_apply_rate": 0.0978,
  "total_shap_impact": 0.0207,
  "top_positive_drivers": [
    { "feature": "has_salary", "value": 1, "shap_impact": 0.0163, "direction": "positive" },
    { "feature": "is_remote", "value": 1, "shap_impact": 0.0115, "direction": "positive" }
  ],
  "top_negative_drivers": [],
  "actionable_recommendations": []
}
```

### 3. Multi-Armed Bandit Simulation
`POST /api/v1/simulate`
- **Request Body**:
```json
{
  "total_budget": 10000.0,
  "days": 30,
  "seed": 42
}
```
- **Response**: Contains trajectory comparisons between Thompson Sampling, Equal Split, Epsilon-Greedy, and UCB1.

### 4. Authentication
`POST /api/v1/auth/login`
- **Request Body**:
```json
{
  "email": "recruiter@joveo.com",
  "password": "password123"
}
```
- **Response**: Returns JWT/Bearer token and authenticated user profile.
