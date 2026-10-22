"""
prepare_dataset.py
Dataset preparation script for FER-2013 facial expression classification.
Splits data into train, val, and test splits and creates labels.json.
"""

import argparse
import json
import os
from pathlib import Path
import random
import shutil
import sys

CLASSES = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]


def validate_source(data_dir: Path) -> dict[str, list[Path]]:
    """Inspect dataset directory and collect image files per class."""
    if not data_dir.exists():
        print(f"[ERROR] Source dataset directory does not exist: {data_dir}")
        print("Please download the FER-2013 dataset from Kaggle and extract to ml/data/raw/fer2013/")
        sys.exit(1)

    class_files = {cls_name: [] for cls_name in CLASSES}

    # FER-2013 commonly has train/ and test/ folders, or class folders directly
    for cls_name in CLASSES:
        # Check direct class folder
        cls_dir = data_dir / cls_name
        if cls_dir.is_dir():
            for ext in ("*.jpg", "*.jpeg", "*.png"):
                class_files[cls_name].extend(list(cls_dir.glob(ext)))

        # Check subdirectories (e.g. train/angry, test/angry)
        for sub in ("train", "test", "val"):
            sub_cls_dir = data_dir / sub / cls_name
            if sub_cls_dir.is_dir():
                for ext in ("*.jpg", "*.jpeg", "*.png"):
                    class_files[cls_name].extend(list(sub_cls_dir.glob(ext)))

    total_images = sum(len(f) for f in class_files.values())
    if total_images == 0:
        print(f"[ERROR] No images found for classes {CLASSES} in {data_dir}")
        sys.exit(1)

    print(f"[INFO] Found {total_images} total images across {len(CLASSES)} classes:")
    for cls_name, files in class_files.items():
        print(f"  - {cls_name:10s}: {len(files)} images")

    return class_files


def prepare_splits(
    class_files: dict[str, list[Path]],
    output_dir: Path,
    val_split: float = 0.15,
    test_split: float = 0.15,
    seed: int = 42,
) -> None:
    random.seed(seed)

    for split in ("train", "val", "test"):
        for cls_name in CLASSES:
            (output_dir / split / cls_name).mkdir(parents=True, exist_ok=True)

    split_counts = {"train": 0, "val": 0, "test": 0}

    for cls_name, files in class_files.items():
        shuffled = list(files)
        random.shuffle(shuffled)

        n_total = len(shuffled)
        n_test = int(n_total * test_split)
        n_val = int(n_total * val_split)

        test_files = shuffled[:n_test]
        val_files = shuffled[n_test : n_test + n_val]
        train_files = shuffled[n_test + n_val :]

        for f in train_files:
            dest = output_dir / "train" / cls_name / f.name
            shutil.copy2(f, dest)
            split_counts["train"] += 1

        for f in val_files:
            dest = output_dir / "val" / cls_name / f.name
            shutil.copy2(f, dest)
            split_counts["val"] += 1

        for f in test_files:
            dest = output_dir / "test" / cls_name / f.name
            shutil.copy2(f, dest)
            split_counts["test"] += 1

    print("\n[INFO] Split complete:")
    print(f"  Train: {split_counts['train']} images")
    print(f"  Val:   {split_counts['val']} images")
    print(f"  Test:  {split_counts['test']} images")

    # Save labels.json in artifacts
    artifacts_dir = output_dir.parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    labels_file = artifacts_dir / "labels.json"
    with open(labels_file, "w", encoding="utf-8") as f:
        json.dump({"classes": CLASSES, "num_classes": len(CLASSES)}, f, indent=2)
    print(f"[INFO] Saved labels mapping to {labels_file}")


def main():
    parser = argparse.ArgumentParser(description="Prepare FER-2013 dataset for MobileNetV2")
    parser.add_argument("--data_dir", type=str, default="./data/raw/fer2013", help="Raw dataset directory")
    parser.add_argument("--output_dir", type=str, default="./data/processed", help="Processed output directory")
    parser.add_argument("--val_split", type=float, default=0.15, help="Validation fraction")
    parser.add_argument("--test_split", type=float, default=0.15, help="Test fraction")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)

    print("=== EIT Dataset Preparation ===")
    class_files = validate_source(data_dir)
    prepare_splits(class_files, output_dir, args.val_split, args.test_split, args.seed)
    print("[SUCCESS] Dataset ready for training.")


if __name__ == "__main__":
    main()
