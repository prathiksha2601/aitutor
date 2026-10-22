# EIT System Architecture

## 1. High-Level Architecture

The AI-Driven Emotional Intelligence Tutor (EIT) follows a decoupled, three-tier architecture:

```
[ React + Vite Frontend (SPA) ]
          │
          │  HTTPS / JSON REST API
          ▼
[ Flask Application Server ]
    ├── Authentication & Authorization (JWT + Argon2id)
    ├── Input Validation (Pydantic & Sanitisers)
    ├── Topic & Lesson Service
    ├── Learning Session Service
    ├── Progress Tracking Service
    ├── AI Tutor Service & EIT Learning Agent (7-step workflow)
    ├── Computer Vision Service (MobileNetV2 Inference + Temporal Aggregator)
    ├── Security & Audit Service
    └── PyMongo Repositories
          │
          │  PyMongo Driver (UTC BSON)
          ▼
[ MongoDB Database (eit_database) ]
    ├── users
    ├── topics
    ├── lessons
    ├── learning_sessions
    ├── progress
    ├── conversations
    ├── quiz_attempts
    ├── expression_summaries (TTL indexed)
    └── audit_logs
```

---

## 2. Component Descriptions

### Frontend (React + Vite)
- **Vite 6** dev server and production bundler.
- **React 18** functional components using hooks (`useState`, `useEffect`, `useCallback`, `useRef`).
- **React Router v6** for client-side routing.
- **Native Fetch API** client with centralized session and token header injection.
- **HTML5 Video Player** supporting local video sources and responsive YouTube embeds.
- **Hardware-Isolated Webcam Hook** (`useWebcam`) with explicit user consent, real-time preview, and guaranteed track cleanup.

### Backend (Python / Flask)
- **Application Factory Pattern** (`create_app`) with modular Blueprints.
- **PyMongo Repositories** separating database access logic from controllers.
- **Strict CORS Policy** locked to `FRONTEND_ORIGIN`.
- **Flask-Limiter** rate limiting (default 60 requests/minute per IP).
- **Graceful Error Handling** with structured JSON envelopes (`{"success": bool, "data": ..., "error": ...}`).

### Database (MongoDB 8.0)
- Single source of truth for application records.
- Indexed for lookup performance and uniqueness.
- TTL expiration index on `expression_summaries` (7-day automatic purge).

### Machine Learning & Computer Vision
- **TensorFlow / Keras MobileNetV2** transfer learning for 7-class facial expression classification.
- **OpenCV** image decoding, RGB color space conversion, and (224, 224, 3) normalization.
- **Temporal Aggregation**: Sliding window (10 observations) smoothing noisy frame outputs before suggesting help.
- **MediaPipe FaceMesh** optional approximate gaze estimator.
