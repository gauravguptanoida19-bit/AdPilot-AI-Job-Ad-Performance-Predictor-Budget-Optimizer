"""FastAPI Application Entrypoint for Recruitment Ad Performance & Budget Optimizer."""

from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.metrics import router as metrics_router
from backend.routes.predict import router as predict_router
from backend.routes.simulate import router as simulate_router
from backend.routes.auth import router as auth_router

app = FastAPI(
    title="Recruitment Ad Performance Predictor & Budget Optimizer API",
    description="Classical ML (LightGBM) ad performance prediction, TreeSHAP explainability, and Thompson Sampling multi-armed bandit budget optimizer.",
    version="1.0.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(metrics_router)
app.include_router(predict_router)
app.include_router(simulate_router)


@app.get("/health")
def healthcheck():
    """Service health and readiness check."""
    models_ready = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "models", "lightgbm_regressor.joblib"))
    reports_ready = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "reports", "model_metrics.json"))
    return {
        "status": "healthy",
        "service": "recruitment-ad-optimizer-api",
        "version": "1.0.0",
        "models_loaded": models_ready,
        "reports_available": reports_ready
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
