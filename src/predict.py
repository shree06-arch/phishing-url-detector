"""
predict.py
CLI tool to classify a URL as phishing or legitimate using the trained
model in models/model.joblib.

Usage:
    python src/predict.py "http://paypal-verify.tk/login"
"""

import os
import sys

import joblib
import numpy as np

from features import extract_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.joblib")


def load_model(path=MODEL_PATH):
    bundle = joblib.load(path)
    return bundle["model"], bundle["feature_names"]


def predict_url(url, model=None, feature_names=None):
    if model is None or feature_names is None:
        model, feature_names = load_model()
    feats = extract_features(url)
    X = np.array([[feats[name] for name in feature_names]], dtype=float)
    proba = model.predict_proba(X)[0, 1]
    label = "phishing" if proba >= 0.5 else "legitimate"
    return {
        "url": url,
        "prediction": label,
        "phishing_probability": round(float(proba), 4),
        "features": feats,
    }


def main():
    if len(sys.argv) < 2:
        print('Usage: python src/predict.py "<url>"')
        sys.exit(1)

    url = sys.argv[1]
    result = predict_url(url)
    print(f"URL:        {result['url']}")
    print(f"Prediction: {result['prediction'].upper()}")
    print(f"Confidence: {result['phishing_probability'] * 100:.2f}% phishing")


if __name__ == "__main__":
    main()
