# EIT REST API Reference

All requests and responses use JSON. State-changing requests accept `Content-Type: application/json`.
Standard response envelope:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional human message"
}
```

---

## 1. Health

### `GET /api/health`
Checks server health, MongoDB connectivity, and configured sub-services.
- **Response 200 OK**:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "1.0.0",
    "db_connected": true,
    "services": {
      "model_configured": true,
      "openai_configured": false
    },
    "timestamp": "2026-10-11T13:28:09Z"
  }
}
```

---

## 2. Topics & Lessons

### `GET /api/topics?page=1&per_page=20`
Returns paginated active topics.

### `GET /api/lessons?topic_id=<id>&page=1&per_page=50`
Returns lessons, optionally filtered by `topic_id`, sorted by sequence number.

### `GET /api/lessons/<lesson_id>`
Returns metadata for a single lesson.

---

## 3. Learning Sessions

### `POST /api/sessions`
Start a learning session.
- **Headers**: `X-Session-ID: <anonymous_id>` or `Authorization: Bearer <token>`
- **Body**:
```json
{
  "lesson_id": "6acb8ed4e6ab5a1e4da48cfd",
  "topic_id": "6acb8ed4e6ab5a1e4da48ceb"
}
```

### `GET /api/sessions/<session_id>`
Get active session details. Enforces session ownership (returns `403` if identity mismatch).

### `PATCH /api/sessions/<session_id>`
Update last playback position and status (`active`, `paused`, `completed`).

### `POST /api/sessions/<session_id>/end`
Marks session status as `completed` and records `ended_at`.

---

## 4. Progress

### `GET /api/progress`
Returns progress records for the requesting student identity.

### `POST /api/progress`
Upserts a progress record.
- **Body**:
```json
{
  "lesson_id": "6acb8ed4e6ab5a1e4da48cfd",
  "topic_id": "6acb8ed4e6ab5a1e4da48ceb",
  "last_position_seconds": 340.5,
  "completion_status": "in_progress"
}
```

---

## 5. AI Tutor

### `POST /api/tutor/chat`
Ask the AI Tutor a question with selected teaching mode.
- **Body**:
```json
{
  "session_id": "<session_id>",
  "message": "What is polymorphism?",
  "response_mode": "simple | step_by_step | example | programming | quiz | feedback | summary | revision",
  "lesson_id": "<lesson_id>",
  "topic_id": "<topic_id>",
  "expression_context": { ... }
}
```

### `POST /api/tutor/quiz`
Generate an interactive multiple-choice quiz question.

### `POST /api/tutor/feedback`
Submit an answer and receive supportive, model-evaluated feedback.

---

## 6. Computer Vision

### `POST /api/expression/analyze`
Submit a webcam frame for MobileNetV2 facial-expression and gaze inference.
- **STRICT REQUIREMENT**: `"consent": true`. Requests without consent receive `403 FORBIDDEN`.
- **Body**:
```json
{
  "image_b64": "data:image/jpeg;base64,...",
  "consent": true
}
```

### `POST /api/expression/session`
Save aggregated session summary (consent-gated, 7-day TTL).
