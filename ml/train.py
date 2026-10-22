"""
train.py
MobileNetV2 transfer learning training script for facial expression classification.
Freezes pretrained base, trains custom classification head, and saves model artifacts.
"""

import argparse
import json
from pathlib import Path
import sys
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks, optimizers


def build_model(num_classes: int, img_size: int = 224, learning_rate: float = 0.001):
    """
    Build MobileNetV2 with frozen ImageNet base and new classification head.
    Note: ImageNet weights provide generic visual features, NOT facial expression classification.
    The new classification head must be trained on facial expression data.
    """
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(img_size, img_size, 3),
        include_top=False,
        weights="imagenet",
    )
    # Freeze the base model
    base_model.trainable = False

    model = models.Sequential([
        layers.Input(shape=(img_size, img_size, 3)),
        # Data augmentation
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        # Preprocessing scaling [0, 1] -> [-1, 1] for MobileNetV2
        layers.Rescaling(scale=1.0 / 127.5, offset=-1.0),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation="relu"),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation="softmax", dtype="float32"),
    ])

    model.compile(
        optimizer=optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base_model


def main():
    parser = argparse.ArgumentParser(description="Train MobileNetV2 on facial expressions")
    parser.add_argument("--data_dir", type=str, default="./data/processed", help="Processed dataset directory")
    parser.add_argument("--output_dir", type=str, default="./artifacts", help="Artifacts directory")
    parser.add_argument("--epochs", type=int, default=20, help="Training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--img_size", type=int, default=224, help="Image size")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    train_dir = data_dir / "train"
    val_dir = data_dir / "val"

    if not train_dir.exists() or not val_dir.exists():
        print(f"[ERROR] Processed data directories not found at {data_dir}.")
        print("Please run prepare_dataset.py first.")
        sys.exit(1)

    print("=== Training MobileNetV2 for Facial Expression Classification ===")
    print(f"Train dir: {train_dir}")
    print(f"Val dir:   {val_dir}")

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        shuffle=True,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        shuffle=False,
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"Classes ({num_classes}): {class_names}")

    # Save labels.json
    labels_path = output_dir / "labels.json"
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump({"classes": class_names, "num_classes": num_classes}, f, indent=2)

    # Prefetch
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)

    model, _ = build_model(num_classes, args.img_size, args.learning_rate)
    model.summary()

    model_path = output_dir / "expression_model.keras"
    cb_list = [
        callbacks.ModelCheckpoint(
            filepath=str(model_path),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=5,
            restore_best_weights=True,
            verbose=1,
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.2,
            patience=3,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    print(f"\nStarting training for {args.epochs} epochs...")
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=cb_list,
    )

    # Save training history
    history_path = output_dir / "training_history.json"
    clean_history = {k: [float(v) for v in vals] for k, vals in history.history.items()}
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(clean_history, f, indent=2)

    print(f"\n[SUCCESS] Model saved to: {model_path}")
    print(f"[SUCCESS] History saved to: {history_path}")


if __name__ == "__main__":
    main()
