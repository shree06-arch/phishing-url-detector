"""
train.py
Trains a RandomForest classifier on URL features extracted from
data/urls.csv, evaluates it, and saves the trained model + feature
list to models/model.joblib.
"""

import csv
import json
import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

from features import extract_features, FEATURE_NAMES

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "urls.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.joblib")


def load_dataset(path):
    urls, labels = [], []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            urls.append(row["url"])
            labels.append(int(row["label"]))
    return urls, labels


def featurize(urls):
    rows = [extract_features(u) for u in urls]
    X = np.array([[r[name] for name in FEATURE_NAMES] for r in rows], dtype=float)
    return X


def main():
    urls, labels = load_dataset(DATA_PATH)
    X = featurize(urls)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    print("=== Classification report ===")
    print(classification_report(y_test, y_pred, target_names=["legitimate", "phishing"]))

    print("=== Confusion matrix ===")
    print(confusion_matrix(y_test, y_pred))

    print(f"ROC AUC: {roc_auc_score(y_test, y_proba):.4f}")

    importances = sorted(
        zip(FEATURE_NAMES, clf.feature_importances_), key=lambda x: -x[1]
    )
    print("\n=== Top 10 feature importances ===")
    for name, imp in importances[:10]:
        print(f"{name:30s} {imp:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump({"model": clf, "feature_names": FEATURE_NAMES}, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()
