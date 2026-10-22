"""
app/computer_vision/inference.py
Facial-expression inference using MobileNetV2 and OpenCV.
Treats predictions as uncertain, optional signals.
Returns clearly labeled 'unavailable' status when model artifacts are missing.
"""

import base64
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

# Fallback default classes for FER-2013 if labels.json not yet generated
DEFAULT_CLASSES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]


class ExpressionInference:
    """Facial-expression inference service using trained MobileNetV2 model."""

    def __init__(self, model_path: str, labels_path: str):
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        self.model = None
        self.classes = DEFAULT_CLASSES
        self.status = "unavailable"
        self._load_model()

    def _load_model(self) -> None:
        """Load Keras model and label mapping if files exist."""
        # Load labels
        if self.labels_path.exists():
            try:
                with open(self.labels_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.classes = data.get("classes", DEFAULT_CLASSES)
            except Exception as exc:
                logger.warning("Could not read labels from %s: %s", self.labels_path, exc)

        # Load Keras model
        if self.model_path.exists():
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(str(self.model_path))
                self.status = "ok"
                logger.info("MobileNetV2 expression model loaded successfully from %s", self.model_path)
            except Exception as exc:
                logger.warning("Failed to load model from %s: %s", self.model_path, exc)
                self.status = "unavailable"
        else:
            self.status = "unavailable"
            logger.info("Expression model file not found at %s. Inference service is marked unavailable.", self.model_path)

    def is_available(self) -> bool:
        return self.status == "ok" and self.model is not None

    @staticmethod
    def decode_base64(image_b64: str) -> bytes:
        """Strip data URI header if present and decode base64."""
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        return base64.b64decode(image_b64)

    def preprocess_image(self, image_bytes: bytes) -> np.ndarray | None:
        """
        Decode raw image bytes with OpenCV, resize to (224, 224, 3),
        and scale pixels to [0, 1].
        """
        try:
            import cv2
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return None
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Resize to MobileNetV2 input dimensions
            resized = cv2.resize(img_rgb, (224, 224))
            # Normalise to [0, 1]
            normalized = resized.astype(np.float32) / 255.0
            # Add batch dimension
            return np.expand_dims(normalized, axis=0)
        except Exception as exc:
            logger.warning("Image preprocessing failed: %s", exc)
            return None

    def predict(self, image_bytes: bytes) -> dict:
        """
        Run inference on image bytes.
        Returns a structured prediction dict.
        Never substitutes fake/random predictions when the model is unavailable.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        if not self.is_available():
            return {
                "status": "unavailable",
                "message": (
                    "Expression model artifact not found. "
                    "Run 'python ml/train.py' to train and save the model."
                ),
                "timestamp": timestamp,
                "model_version": "1.0.0",
            }

        tensor = self.preprocess_image(image_bytes)
        if tensor is None:
            return {
                "status": "error",
                "message": "Invalid or unreadable image data.",
                "timestamp": timestamp,
                "model_version": "1.0.0",
            }

        try:
            preds = self.model.predict(tensor, verbose=0)[0]
            top_idx = int(np.argmax(preds))
            confidence = float(preds[top_idx])
            probabilities = {
                cls_name: round(float(prob), 4)
                for cls_name, prob in zip(self.classes, preds)
            }

            return {
                "status": "ok",
                "category": self.classes[top_idx],
                "confidence": round(confidence, 4),
                "probabilities": probabilities,
                "timestamp": timestamp,
                "model_version": "1.0.0",
                "uncertain_signal": True,
            }
        except Exception as exc:
            logger.error("Inference prediction error: %s", exc)
            return {
                "status": "error",
                "message": str(exc),
                "timestamp": timestamp,
                "model_version": "1.0.0",
            }
