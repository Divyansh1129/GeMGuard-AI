"""
train_model.py
----------------
Run this ONCE (or whenever you regenerate the dataset) to train the risk
classifier. Not called by the API at request time — training happens offline,
the API just loads the saved model file (risk_model.pkl).

Usage:
    python app/ml/train_model.py

Input:  gem_bidder_compliance_dataset.csv (place in project root)
Output: app/ml/risk_model.pkl  (trained model, loaded by ml_service.py)
        app/ml/feature_importance.png (for your presentation/demo)
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt

DATA_PATH = "gem_bidder_compliance_dataset.csv"
MODEL_OUT = "app/ml/risk_model.pkl"

FEATURES = [
    "udyam_valid", "udyam_expired", "gst_registered", "gst_status_active",
    "gst_returns_filed_pct", "pan_valid", "itr_filed_last_year", "income_tax_defaulter",
    "epfo_applicable", "epfo_compliant", "esic_applicable", "esic_compliant",
    "make_in_india_local_content_pct", "make_in_india_required_threshold",
    "startup_india_claimed", "startup_india_verified", "nsic_claimed", "nsic_verified",
    "oem_authorization_required", "oem_authorization_provided", "blacklisted_flag",
    "debarment_active", "documents_missing_count", "name_mismatch_across_docs",
    "document_authenticity_score", "turnover_consistency_ratio",
    "years_since_registration", "past_disputes_count"
]
TARGET = "risk_level"


def main():
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURES]
    y = df[TARGET]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)  # Low/Medium/High -> 0/1/2

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=10, random_state=42, class_weight="balanced"
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("=== Classification Report ===")
    print(classification_report(y_test, preds, target_names=le.classes_))
    print("=== Confusion Matrix ===")
    print(confusion_matrix(y_test, preds))

    importances = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
    plt.figure(figsize=(8, 10))
    importances.plot(kind="barh")
    plt.title("Feature Importance — Bidder Risk Classifier")
    plt.tight_layout()
    plt.savefig("app/ml/feature_importance.png")

    joblib.dump({"model": model, "label_encoder": le, "features": FEATURES}, MODEL_OUT)
    print(f"\nModel saved to {MODEL_OUT}")


if __name__ == "__main__":
    main()