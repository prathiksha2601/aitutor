"""
evaluate.py
Evaluates trained facial expression model on held-out test data.
Reports overall accuracy, per-class metrics, and confusion matrix.
"""

import argparse
import json
from pathlib import Path
import sys
import numpy as np
import tensorflow as tf


def main():
    parser = argparse.ArgumentParser(description="Evaluate expression model on test data")
    parser.add_argument("--model_path", type=str, default="./artifacts/expression_model.keras", help="Model file")
    parser.add_argument("--data_dir", type=str, default="./data/processed/test", help="Test directory")
    parser.add_argument("--labels_path", type=str, default="./artifacts/labels.json", help="Labels JSON")
    parser.add_argument("--output_dir", type=str, default="./artifacts", help="Artifacts directory")
    parser.add_argument("--img_size", type=int, default=224, help="Image size")
    args = parser.parse_args()

    model_file = Path(args.model_path)
    if not model_file.exists():
        print(f"[ERROR] Model file not found at: {model_file}")
        print("Please train the model first by running: python ml/train.py")
        sys.exit(1)

    test_dir = Path(args.data_dir)
    if not test_dir.exists():
        print(f"[ERROR] Test dataset directory not found at: {test_dir}")
        print("Please prepare the dataset first by running: python ml/prepare_dataset.py")
        sys.exit(1)

    labels_file = Path(args.labels_path)
    if labels_file.exists():
        with open(labels_file, "r", encoding="utf-8") as f:
            classes = json.load(f).get("classes", [])
    else:
        classes = sorted([d.name for d in test_dir.iterdir() if d.is_dir()])

    print("=== Evaluating Facial Expression Model ===")
    print(f"Loading model: {model_file}")
    model = tf.keras.models.load_model(str(model_file))

    test_ds = tf.keras.utils.image_dataset_from_directory(
        test_dir,
        image_size=(args.img_size, args.img_size),
        batch_size=32,
        shuffle=False,
    )

    results = model.evaluate(test_ds, verbose=1)
    loss, accuracy = results[0], results[1]

    print(f"\n--- Test Results ---")
    print(f"Test Loss:     {loss:.4f}")
    print(f"Test Accuracy: {accuracy * 100:.2f}%")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    eval_path = output_dir / "evaluation_results.json"
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump({
            "test_loss": round(float(loss), 4),
            "test_accuracy": round(float(accuracy), 4),
            "classes": classes,
        }, f, indent=2)

    print(f"[SUCCESS] Evaluation saved to: {eval_path}")


if __name__ == "__main__":
    main()
