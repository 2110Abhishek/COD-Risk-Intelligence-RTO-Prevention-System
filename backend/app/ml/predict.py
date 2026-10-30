import os
import joblib
from typing import Dict, Any, Tuple
import pandas as pd
from app.core.settings import settings
from app.ml.features import extract_order_features

_cached_model = None
_cached_version = None


def load_model_pipeline():
    global _cached_model, _cached_version
    artifact_path = settings.model_artifact_path
    if os.path.exists(artifact_path):
        try:
            artifact = joblib.load(artifact_path)
            _cached_model = artifact["model_pipeline"]
            _cached_version = artifact.get("model_version", "rto-v1.0")
            return _cached_model, _cached_version
        except Exception as e:
            print(f"Error loading model artifact: {e}")
    return None, "fallback-heuristic-v1.0"


def predict_rto_risk(order_data: Dict[str, Any]) -> Tuple[float, str, Dict[str, Any]]:
    """
    Predicts calibrated RTO probability for an incoming order.
    Returns: (probability: float, model_version: str, feature_snapshot: Dict)
    """
    features = extract_order_features(order_data)
    model, version = load_model_pipeline()

    if model is not None:
        try:
            feat_df = pd.DataFrame([features])
            prob = float(model.predict_proba(feat_df)[0, 1])
            return round(prob, 4), version, features
        except Exception as e:
            print(f"Model prediction failed: {e}; using calibrated fallback")

    # Safe heuristic fallback
    prior_orders = features["customer_prior_orders"]
    prior_rto = features["customer_prior_rto"]
    prior_rto_rate = features["prior_rto_rate"]
    
    # Base prior probability (~28% COD baseline)
    prob = 0.28

    if features["is_first_time"]:
        prob = 0.26  # First-time customer baseline
    elif prior_orders > 0:
        if prior_rto == 0:
            prob = max(0.08, 0.20 - 0.04 * prior_orders)
        else:
            prob = min(0.85, 0.35 + 0.30 * prior_rto_rate)

    if features["name_is_suspicious"]:
        prob = min(0.95, prob + 0.35)
    if not features["phone_is_valid"]:
        prob = min(0.95, prob + 0.30)
    if not features["pincode_is_valid"]:
        prob = min(0.90, prob + 0.15)
    if features["has_landmark"]:
        prob = max(0.05, prob - 0.06)

    return round(float(prob), 4), version, features
