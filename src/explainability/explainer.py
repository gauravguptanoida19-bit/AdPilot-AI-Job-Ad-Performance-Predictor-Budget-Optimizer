"""TreeSHAP explainer and actionable recommendation engine for Recruitment Ad Predictor.

Uses native LightGBM TreeSHAP implementation (`pred_contrib=True`) which computes
exact TreeSHAP values for all features plus base value without external binary overhead.
"""

from __future__ import annotations
import os
import json
import joblib
from typing import Dict, Any, List
import numpy as np
import pandas as pd

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


class AdPerformanceExplainer:
    """Computes global and local TreeSHAP explanations and actionable optimizations."""

    def __init__(self, model_path: str | None = None, metadata_path: str | None = None):
        if model_path is None:
            model_path = os.path.join(MODELS_DIR, "lightgbm_regressor.joblib")
        if metadata_path is None:
            metadata_path = os.path.join(MODELS_DIR, "metadata.json")

        self.model = joblib.load(model_path)
        with open(metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.feature_names = self.metadata["feature_names"]

    def _compute_shap_matrix(self, X_df: pd.DataFrame) -> Tuple[np.ndarray, float]:
        """Compute exact TreeSHAP values using LightGBM's native C++ TreeSHAP engine.

        Returns (shap_values_matrix, base_expected_value).
        """
        # Ensure column order matches training feature_names
        X_aligned = X_df[self.feature_names]
        contribs = self.model.predict(X_aligned, pred_contrib=True)
        # Last column is the expected base value
        base_value = float(contribs[0, -1])
        shap_values = contribs[:, :-1]
        return shap_values, base_value

    def explain_global(self, X_sample: pd.DataFrame, top_n: int = 15) -> Dict[str, Any]:
        """Compute global feature importance using mean absolute SHAP values."""
        shap_values, base_value = self._compute_shap_matrix(X_sample)
        mean_abs_shap = np.mean(np.abs(shap_values), axis=0)

        rankings = []
        for name, val in zip(self.feature_names, mean_abs_shap):
            rankings.append({
                "feature": name,
                "importance": round(float(val), 5),
                "importance_pct": 0.0
            })

        # Calculate percentages
        total_imp = sum(r["importance"] for r in rankings)
        for r in rankings:
            r["importance_pct"] = round((r["importance"] / max(total_imp, 1e-6)) * 100.0, 2)

        rankings.sort(key=lambda x: x["importance"], reverse=True)

        result = {
            "base_expected_value": round(base_value, 4),
            "top_features": rankings[:top_n],
            "all_features": rankings
        }

        # Save to reports
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(os.path.join(REPORTS_DIR, "shap_global_importance.json"), "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        return result

    def explain_instance(self, features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Compute local SHAP explanation and actionable suggestions for a single ad."""
        # Convert to 1-row DataFrame aligned with feature_names
        row_df = pd.DataFrame([{f: features_dict.get(f, 0) for f in self.feature_names}])
        shap_values, base_value = self._compute_shap_matrix(row_df)
        shap_val = shap_values[0]
        predicted_val = float(self.model.predict(row_df)[0])

        contributions = []
        for feat, val, s in zip(self.feature_names, row_df.iloc[0], shap_val):
            contributions.append({
                "feature": feat,
                "value": float(val) if isinstance(val, (int, float, np.number)) else str(val),
                "shap_impact": round(float(s), 5),
                "direction": "positive" if s >= 0 else "negative"
            })

        contributions.sort(key=lambda x: abs(x["shap_impact"]), reverse=True)

        recommendations = self.generate_recommendations(features_dict, contributions)

        return {
            "predicted_apply_rate": round(max(0.001, min(1.0, predicted_val)), 4),
            "baseline_apply_rate": round(base_value, 4),
            "total_impact": round(predicted_val - base_value, 4),
            "top_positive_drivers": [c for c in contributions if c["direction"] == "positive"][:5],
            "top_negative_drivers": [c for c in contributions if c["direction"] == "negative"][:5],
            "all_contributions": contributions,
            "actionable_recommendations": recommendations
        }

    def generate_recommendations(
        self,
        features: Dict[str, Any],
        contributions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate concrete, actionable recruiting suggestions based on SHAP drivers."""
        recs = []
        shap_map = {c["feature"]: c["shap_impact"] for c in contributions}

        # 1. Salary presence
        if features.get("has_salary", 0) == 0 or shap_map.get("has_salary", 0) < 0:
            recs.append({
                "category": "Salary Transparency",
                "severity": "HIGH",
                "impact": "Boosts candidate application rate by +35% to +50%",
                "recommendation": "Disclose a clear salary or hourly range. Postings without transparent salary suffer significantly lower applicant conversion.",
                "shap_drag": abs(shap_map.get("has_salary", -0.018))
            })

        # 2. Description length
        char_len = features.get("desc_char_length", 0)
        if char_len > 2200:
            recs.append({
                "category": "Content Optimization",
                "severity": "MEDIUM",
                "impact": "Reduces candidate abandonment",
                "recommendation": f"Description is overly verbose ({char_len} chars). Candidates experience cognitive fatigue on mobile. Shorten text to 800-1,800 characters.",
                "shap_drag": abs(shap_map.get("desc_char_length", -0.005))
            })
        elif char_len < 500 and char_len > 0:
            recs.append({
                "category": "Content Optimization",
                "severity": "MEDIUM",
                "impact": "Increases role credibility and clarity",
                "recommendation": f"Description is very brief ({char_len} chars). Include detailed day-to-day responsibilities and project scope to reassure candidates.",
                "shap_drag": abs(shap_map.get("desc_char_length", -0.005))
            })

        # 3. Bullet points formatting
        bullets = features.get("desc_bullet_points", 0)
        if bullets < 3:
            recs.append({
                "category": "Formatting & Readability",
                "severity": "MEDIUM",
                "impact": "Improves mobile skim-readability",
                "recommendation": f"Found only {bullets} bullet point markers. Restructure qualifications and responsibilities into 4-7 structured bullet points.",
                "shap_drag": abs(shap_map.get("desc_bullet_points", -0.003))
            })

        # 4. Explicit skills
        skills_cnt = features.get("skills_count", 0)
        if skills_cnt < 3:
            recs.append({
                "category": "Skills Specificity",
                "severity": "LOW",
                "impact": "Improves search matching and candidate self-selection",
                "recommendation": f"Only {skills_cnt} explicit skills detected. Tag 4 to 8 specific core competencies.",
                "shap_drag": 0.004
            })

        # 5. Remote / Location flexibility
        if features.get("is_remote", 0) == 0:
            recs.append({
                "category": "Workplace Flexibility",
                "severity": "INFO",
                "impact": "Expands talent pool reach by 25%+",
                "recommendation": "If feasible, offering hybrid or remote options substantially expands candidate reach and elevates apply-per-view metrics.",
                "shap_drag": abs(shap_map.get("is_remote", -0.012))
            })

        # Sort recommendations by highest potential impact
        recs.sort(key=lambda x: x.get("shap_drag", 0), reverse=True)
        return recs


def compute_and_save_global_shap():
    """Utility to compute and persist global SHAP values using the test dataset."""
    from src.data.loader import load_and_preprocess_data
    data = load_and_preprocess_data()
    X_test = data["X_test"].iloc[:500]

    explainer = AdPerformanceExplainer()
    res = explainer.explain_global(X_test)
    print(f"[SHAP] Successfully computed global TreeSHAP values for {len(res['top_features'])} features.")
    for feat in res["top_features"][:6]:
        print(f"  - {feat['feature']}: {feat['importance']:.5f} ({feat['importance_pct']}%)")
    return res


if __name__ == "__main__":
    compute_and_save_global_shap()
