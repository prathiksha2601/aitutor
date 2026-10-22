"""
predict.py
Stand-alone predictor for facial expression classification.
Can be imported as a Python module or executed from CLI.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import numpy as np


class ExpressionPredictor:
    """Predicts facial expressions from images using trained MobileNetV2 model."""

    def __init__(
        self,
        model_path: str = "./artifacts/expression_model.keras",
        labels_path: str = "./artifacts/labels.json",
    ):
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        self.model = None
        self.classes = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]
        self.available = False
        self._load()

    def _load(self) -> None:
        if self.labels_path.exists():
            try:
                with open(self.labels_path, "r", encoding="utf-8") as f:
                    self.classes = json.load(f).get("classes", self.classes)
            except Exception:
                pass

        if self.model_path.exists():
            try:
                import tensorflow as tf
                self.model = tf.keras.models.load_model(str(self.model_path))
                self.available = True
            except Exception:
                self.available = False
        else:
            self.available = False

    def is_available(self) -> bool:
        return self.available and self.model is not None

    def preprocess(self, image_input) -> np.ndarray | None:
        """Load and resize image to (1, 224, 224, 3) normalized to [0, 1]."""
        try:
            import cv2
            if isinstance(image_input, (str, Path)):
                img = cv2.imread(str(image_input))
            elif isinstance(image_input, bytes):
                nparr = np.frombuffer(image_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            elif isinstance(image_input, np.ndarray):
                img = image_input
            else:
                return None

            if img is None:
                return None

            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            elif img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            resized = cv2.resize(img, (224, 224))
            normalized = resized.astype(np.float32) / 255.0
            return np.expand_dims(normalized, axis=0)
        except Exception:
            return None

    def predict_image(self, image_input) -> dict:
        """
        Predict facial expression.
        Returns a structured prediction dict.
        Never substitutes fake or random numbers when the model is unavailable.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        if not self.is_available():
            return {
                "status": "unavailable",
                "message": "Model not loaded. Train the model first by running: python ml/train.py",
                "timestamp": timestamp,
                "model_version": "1.0.0",
            }

        tensor = self.preprocess(image_input)
        if tensor is None:
            return {
                "status": "error",
                "message": "Could not read or process image.",
                "timestamp": timestamp,
                "model_version": "1.0.0",
            }

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


def main():
    parser = argparse.ArgumentParser(description="Predict facial expression from an image file")
    parser.add_argument("--image", type=str, required=True, help="Path to face image")
    parser.add_argument("--model", type=str, default="./artifacts/expression_model.keras", help="Model path")
    parser.add_argument("--labels", type=str, default="./artifacts/labels.json", help="Labels path")
    args = parser.parse_args()

    predictor = ExpressionPredictor(args.model, args.labels)
    result = predictor.predict_image(args.image)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
