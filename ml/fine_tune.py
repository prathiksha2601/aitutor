"""
fine_tune.py
Fine-tunes top layers of the pretrained MobileNetV2 base with a low learning rate.
"""

import argparse
import json
from pathlib import Path
import sys
import tensorflow as tf
from tensorflow.keras import callbacks, optimizers


def main():
    parser = argparse.ArgumentParser(description="Fine-tune trained MobileNetV2 expression model")
    parser.add_argument("--model_path", type=str, default="./artifacts/expression_model.keras", help="Base model")
    parser.add_argument("--data_dir", type=str, default="./data/processed", help="Dataset directory")
    parser.add_argument("--output_dir", type=str, default="./artifacts", help="Artifacts directory")
    parser.add_argument("--epochs", type=int, default=10, help="Fine-tuning epochs")
    parser.add_argument("--learning_rate", type=float, default=1e-4, help="Lower learning rate")
    parser.add_argument("--unfreeze_layers", type=int, default=30, help="Number of base layers to unfreeze")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--img_size", type=int, default=224, help="Image size")
    args = parser.parse_args()

    model_file = Path(args.model_path)
    if not model_file.exists():
        print(f"[ERROR] Trained base model not found at: {model_file}")
        print("Please run train.py first to obtain the initial model.")
        sys.exit(1)

    data_dir = Path(args.data_dir)
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    if not train_dir.exists() or not val_dir.exists():
        print(f"[ERROR] Dataset splits not found in: {data_dir}")
        sys.exit(1)

    print("=== Fine-Tuning MobileNetV2 Model ===")
    print(f"Loading base model: {model_file}")
    model = tf.keras.models.load_model(str(model_file))

    # Find the MobileNetV2 base layer inside the sequential model
    mobilenet_base = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            mobilenet_base = layer
            break

    if mobilenet_base is not None:
        mobilenet_base.trainable = True
        # Freeze all layers except the last `unfreeze_layers`
        for layer in mobilenet_base.layers[:-args.unfreeze_layers]:
            layer.trainable = False
        print(f"Unfroze last {args.unfreeze_layers} layers of MobileNetV2 base.")
    else:
        # Fallback: unfreeze layers in model directly
        model.trainable = True
        for layer in model.layers[:-args.unfreeze_layers]:
            layer.trainable = False
        print(f"Unfroze top {args.unfreeze_layers} layers.")

    model.compile(
        optimizer=optimizers.Adam(learning_rate=args.learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        shuffle=True,
    ).prefetch(buffer_size=tf.data.AUTOTUNE)

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        shuffle=False,
    ).prefetch(buffer_size=tf.data.AUTOTUNE)

    output_dir = Path(args.output_dir)
    finetuned_path = output_dir / "expression_model_finetuned.keras"

    cb_list = [
        callbacks.ModelCheckpoint(
            filepath=str(finetuned_path),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        callbacks.EarlyStopping(
            monitor="val_accuracy",
            patience=4,
            restore_best_weights=True,
            verbose=1,
        ),
    ]

    print(f"Starting fine-tuning for {args.epochs} epochs with LR={args.learning_rate}...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=cb_list,
    )

    print(f"[SUCCESS] Fine-tuned model saved to: {finetuned_path}")


if __name__ == "__main__":
    main()
