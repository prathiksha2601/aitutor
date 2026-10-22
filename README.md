# AI-Driven Emotional Intelligence Tutor (EIT)

> An intelligent educational platform with AI tutoring, interactive video lessons, optional webcam-based facial-expression signals, and real-time learning progress tracking.

---

## ⚡ Quick Start (Development)

### Prerequisites
- **Python 3.13+**
- **Node.js 22+**
- **MongoDB 8.0+** running locally (`mongod`)
- **Git**

### 1. Clone and set up

```bash
git clone <your-repo-url>
cd eit-project
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env — set FLASK_SECRET_KEY, JWT_SECRET_KEY, and optionally OPENAI_API_KEY
```

### 3. Seed Demo Data

```bash
# From project root
python scripts/seed_demo_data.py
```

### 4. Start Backend

```bash
cd backend
python run.py
# Flask starts at http://localhost:5000
# Test: curl http://localhost:5000/api/health
```

### 5. Frontend Setup

```bash
cd frontend
npm install

# Configure environment
copy .env.example .env
# Default VITE_API_BASE_URL=http://localhost:5000/api is fine for development

npm run dev
# React starts at http://localhost:5173
```

---

## 🔑 External Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_SECRET_KEY` | ✅ Yes | Flask session secret (generate with `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `JWT_SECRET_KEY` | ✅ Yes | JWT signing key (generate same way) |
| `MONGODB_URI` | ✅ Yes | MongoDB connection URI (default: `mongodb://localhost:27017/`) |
| `OPENAI_API_KEY` | ⚠️ Optional | Required for AI tutor. App works without it with a clear message. |
| `OPENAI_MODEL` | ⚠️ Optional | Default: `gpt-4o-mini` |
| `MODEL_PATH` | ⚠️ Optional | Path to trained `.keras` model file |
| `MODEL_LABELS_PATH` | ⚠️ Optional | Path to `labels.json` class mapping |

---

## 🤖 ML Pipeline (Facial Expression Classification)

The ML pipeline uses MobileNetV2 transfer learning trained on FER-2013.
The model artifact is **not included** in this repository and must be trained.

See [`ml/README.md`](ml/README.md) for complete instructions.

**Quick summary:**
1. Download FER-2013 from Kaggle → `ml/data/raw/fer2013/`
2. `python ml/prepare_dataset.py --data_dir ./ml/data/raw/fer2013`
3. `python ml/train.py --epochs 20`
4. `python ml/evaluate.py`

The app runs fully without the ML model (expression analysis shows "unavailable").

---

## 🏗️ Architecture

```
React Frontend (Vite)
       │
       │  JSON / REST API
       ▼
Flask Application
  ├── Auth & Security (JWT + argon2id)
  ├── Topics & Lessons Service
  ├── AI Tutor Service (OpenAI SDK)
  │     └── EIT Learning Agent (7-step controlled workflow)
  ├── Computer Vision Service (TF/Keras + OpenCV)
  │     ├── Expression Inference (MobileNetV2)
  │     ├── Gaze Estimation (MediaPipe)
  │     └── Temporal Aggregator
  ├── Learning Progress Service
  └── PyMongo Repositories
         ▼
      MongoDB
  ├── users
  ├── topics
  ├── lessons
  ├── learning_sessions
  ├── progress
  ├── conversations
  ├── quiz_attempts
  ├── expression_summaries
  └── audit_logs
```

---

## 🔒 Security

- **Passwords**: argon2id hashing (never plaintext)
- **Auth**: JWT tokens (24h expiry)
- **CORS**: Strict origin allowlist
- **Ownership checks**: All session/progress endpoints verify ownership
- **Input validation**: Pydantic models on all POST endpoints
- **Rate limiting**: Flask-Limiter on all routes
- **Secrets**: Environment variables only, never in source code
- **Webcam**: Requires explicit consent, no raw image storage by default
- **AI Agent**: Allowlisted tools only, no arbitrary code execution

---

## 📁 Project Structure

```
eit-project/
├── frontend/          # React + Vite frontend
├── backend/           # Flask backend
│   ├── app/
│   │   ├── agents/    # EIT Learning Agent workflow
│   │   ├── computer_vision/  # Expression inference + gaze
│   │   ├── repositories/     # PyMongo data access
│   │   ├── routes/           # Flask blueprints
│   │   ├── security/         # Auth + audit
│   │   └── tutoring/         # AI tutor service
│   └── tests/
├── ml/                # MobileNetV2 training pipeline
├── scripts/           # Seed data scripts
├── tests/             # All automated tests
└── docs/              # Architecture + API documentation
```

---

## 🧪 Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# ML tests (no trained model required)
python -m pytest ../tests/ml/ -v

# Frontend tests
cd frontend
npm test
```

---

## 📚 Documentation

| Doc | Description |
|-----|-------------|
| [`docs/architecture.md`](docs/architecture.md) | System architecture |
| [`docs/api.md`](docs/api.md) | REST API reference |
| [`docs/database-schema.md`](docs/database-schema.md) | MongoDB collections |
| [`docs/security.md`](docs/security.md) | Security design |
| [`docs/privacy.md`](docs/privacy.md) | Privacy policy |
| [`docs/agent-workflow.md`](docs/agent-workflow.md) | AI agent workflow |
| [`docs/deployment.md`](docs/deployment.md) | Production deployment |
| [`ml/README.md`](ml/README.md) | ML pipeline guide |

---

## ⚠️ Important Disclaimers

- Facial expression and gaze predictions are **uncertain, optional signals**. They are never used to diagnose students, penalize outcomes, or make definitive claims about emotional states or comprehension.
- The application is **fully functional** without webcam, ML model, or OpenAI API key.
- FER-2013 dataset has known limitations. Expected test accuracy: 60–70%.
- Always obtain informed consent before enabling webcam features.

---

## 📄 License

MIT License — see LICENSE file.
