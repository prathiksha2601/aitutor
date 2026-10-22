# EIT Machine Learning Pipeline: Facial Expression Classification

This module implements a transfer learning pipeline using **MobileNetV2** for classifying facial expressions.

> **Important Disclaimer**: Facial expression analysis produces **uncertain, optional signals**. It does NOT reliably prove student emotion, comprehension, attention, or mental state. These signals must never be used to evaluate, grade, diagnose, or penalize students.

---

## 1. Dataset: FER-2013

We use the public **FER-2013 (Facial Expression Recognition 2013)** dataset, which contains 48x48 pixel grayscale images categorized into 7 emotion classes:
- `angry`
- `disgust`
- `fear`
- `happy`
- `neutral`
- `sad`
- `surprise`

### Download Instructions

1. Go to Kaggle: [FER-2013 Dataset on Kaggle](https://www.kaggle.com/datasets/msambare/fer2013)
2. Download the archive (`fer2013.zip`).
3. Extract the contents so the folder structure looks like:
```
ml/data/raw/fer2013/
├── train/
│   ├── angry/
│   ├── disgust/
│   ├── fear/
│   ├── happy/
│   ├── neutral/
│   ├── sad/
│   └── surprise/
└── test/
    ├── angry/
    ├── ...
```

---

## 2. Step-by-Step Training Pipeline

### Step 1: Prepare and Split Dataset

Organize and split the dataset into `train`, `val`, and `test` splits:

```bash
cd ml
python prepare_dataset.py --data_dir ./data/raw/fer2013 --output_dir ./data/processed
```

### Step 2: Train MobileNetV2 Base Model

Train the custom classification head with frozen MobileNetV2 ImageNet weights:

```bash
python train.py --epochs 20 --batch_size 32 --learning_rate 0.001
```

- Input images are resized to `224x224x3`.
- Model checkpointing saves the best model to `artifacts/expression_model.keras`.
- Training history is saved to `artifacts/training_history.json`.

### Step 3: Fine-Tune Top Layers (Optional)

Unfreeze the top 30 layers and train with a lower learning rate (`1e-4`):

```bash
python fine_tune.py --epochs 10 --learning_rate 0.0001
```

Saves to `artifacts/expression_model_finetuned.keras`.

### Step 4: Evaluate on Test Set

Evaluate on held-out test data:

```bash
python evaluate.py --data_dir ./data/processed/test
```

Saves test loss and accuracy to `artifacts/evaluation_results.json`.

### Step 5: Test Stand-Alone Prediction

Run inference on an arbitrary image:

```bash
python predict.py --image path/to/face_photo.jpg
```

---

## 3. Important Implementation Notes

1. **Why Transfer Learning?**: MobileNetV2 provides lightweight, fast feature extraction suitable for near real-time inference on educational devices.
2. **ImageNet Limitation**: Pretrained ImageNet weights learn general object representations, NOT facial emotion labels. Training the classification head on facial expression data is required.
3. **Graceful Degradation**: If no model file exists at `ml/artifacts/expression_model.keras`, the backend inference service honestly reports `status: "unavailable"` and the EIT web app continues to function seamlessly without webcam analysis.
