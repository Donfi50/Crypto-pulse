import json
from pathlib import Path

import numpy as np


def build_feature_vector(prices, window=20):
    """Create a simple feature vector from price history."""
    if len(prices) < window:
        raise ValueError("Not enough data to build a feature vector.")

    recent = np.asarray(prices[-window:], dtype=float)
    normalized = recent / recent[0]
    return normalized.tolist()


def train_dummy_model(prices):
    """Return a lightweight pseudo-model using price momentum."""
    if len(prices) < 5:
        return {"status": "insufficient_data"}

    current = float(prices[-1])
    previous = float(prices[-2])
    momentum = (current - previous) / previous

    prediction = {
        "momentum": momentum,
        "expected_direction": "BUY" if momentum > 0 else "SELL" if momentum < 0 else "HOLD",
        "confidence": min(max(abs(momentum) * 100, 0), 99),
    }
    return prediction


def save_prediction_report(report, filename="prediction_report.json"):
    """Persist model prediction output to disk."""
    path = Path(filename)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return str(path)
