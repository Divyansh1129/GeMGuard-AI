"""
ml_service.py
---------------
Loads the trained risk_model.pkl ONCE at server startup (not per-request —
that would be slow). Exposes predict_risk() which the compliance router calls.
"""

import joblib
import pandas as pd
import os
from app.config import settings

_model_bundle = None


def load_model():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(settings.RISK_MODEL_PATH):
            raise FileNotFoundError(
                f"No trained model at {settings.RISK_MODEL_PATH}. "
                f"Run `python app/ml/train_model.py` first."
            )
        _model_bundle = joblib.load(settings.RISK_MODEL_PATH)
    return _model_bundle


def predict_risk(feature_dict: dict) -> dict:
    """
    feature_dict: values for every column in FEATURES (see train_model.py),
                   built from the rule-engine / portal-check results.
    Returns: {"risk_level": "Low"/"Medium"/"High", "high_risk_probability": float}
    """
    bundle = load_model()
    model, le, features = bundle["model"], bundle["label_encoder"], bundle["features"]

    row = pd.DataFrame([{f: feature_dict.get(f, 0) for f in features}])
    pred_class = model.predict(row)[0]
    pred_proba = model.predict_proba(row)[0]

    risk_level = le.inverse_transform([pred_class])[0]
    high_idx = list(le.classes_).index("High") if "High" in le.classes_ else None
    high_prob = float(pred_proba[high_idx]) if high_idx is not None else float(max(pred_proba))

    return {"risk_level": risk_level, "high_risk_probability": round(high_prob, 3)}