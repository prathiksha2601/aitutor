"""
tests/ml/test_ml_pipeline.py
Tests for the MobileNetV2 ML pipeline components.
Runs without requiring the trained model artifact or dataset download.
"""

import json
from pathlib import Path
import numpy as np
import pytest

from ml.predict import ExpressionPredictor

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_labels_json_structure():
    labels_file = PROJECT_ROOT / "ml" / "artifacts" / "labels.json"
    assert labels_file.exists(), "labels.json should exist in ml/artifacts"

    with open(labels_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "classes" in data
    assert "num_classes" in data
    assert data["num_classes"] == 7
    expected_classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
    assert sorted(data["classes"]) == sorted(expected_classes)


def test_predictor_unavailable_when_model_missing():
    """Predictor reports status 'unavailable' honestly rather than guessing."""
    predictor = ExpressionPredictor(
        model_path="nonexistent_model.keras",
        labels_path=str(PROJECT_ROOT / "ml" / "artifacts" / "labels.json"),
    )
    assert not predictor.is_available()

    dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
    result = predictor.predict_image(dummy_image)

    assert result["status"] == "unavailable"
    assert "timestamp" in result


def test_preprocess_image_shape_and_range():
    predictor = ExpressionPredictor(
        model_path="nonexistent_model.keras",
        labels_path=str(PROJECT_ROOT / "ml" / "artifacts" / "labels.json"),
    )
    dummy_image = np.ones((100, 150, 3), dtype=np.uint8) * 128
    tensor = predictor.preprocess(dummy_image)

    assert tensor is not None
    # MobileNetV2 input shape: (1, 224, 224, 3)
    assert tensor.shape == (1, 224, 224, 3)
    # Normalized to [0, 1]
    assert tensor.min() >= 0.0
    assert tensor.max() <= 1.0


def test_predict_missing_model_no_exception():
    predictor = ExpressionPredictor(
        model_path="missing_path.keras",
        labels_path="missing_labels.json",
    )
    # Must not raise an unhandled exception
    res = predictor.predict_image(b"invalid_bytes")
    assert res["status"] in ("unavailable", "error")
