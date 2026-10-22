# EIT Security Architecture & Safeguards

This document describes the security controls, authentication mechanisms, and safeguards implemented across the AI-Driven Emotional Intelligence Tutor (EIT).

---

## 1. Authentication & Password Security

- **Argon2id Hashing**: Password hashing uses Argon2id (`time_cost=2`, `memory_cost=19456`, `parallelism=1`). Plaintext passwords are never stored or logged.
- **JWT (JSON Web Tokens)**: Cryptographically signed with `HS256` and an environment-configurable secret key (`JWT_SECRET_KEY`). Tokens expire after `SESSION_TIMEOUT_HOURS` (default: 24h).
- **Minimum Password Complexity**: Enforced on registration (minimum 8 characters).

---

## 2. Authorization & Ownership Enforcements

- **Session Ownership Guard**: The API verifies ownership on every session-related operation (`GET /api/sessions/<id>`, `PATCH /api/sessions/<id>`, `POST /api/sessions/<id>/end`). Users cannot view or modify another student's session.
- **Anonymous Session Protection**: Guest students receive a random UUID v4 stored in localStorage and passed via the `X-Session-ID` header, scoped strictly to their session records.

---

## 3. Network & API Protection

- **CORS Restriction**: Configured via Flask-CORS with a strict origin allowlist matching `FRONTEND_ORIGIN` (default: `http://localhost:5173`). Unapproved origins are rejected.
- **Rate Limiting**: Configured using `Flask-Limiter` with an in-memory sliding window (default: 60 requests/minute per client IP) to protect against brute-force attacks and denial-of-service.
- **Payload Limits**: Image payloads for webcam inference are strictly capped (< 1MB base64 / 500KB decoded).

---

## 4. AI & Agent Guardrails

- **Strict Tool Allowlist**: The EIT Learning Agent can only invoke explicitly allowlisted tools (`get_lesson`, `get_topic`, `get_conversation`, `get_progress`). Attempting to invoke unapproved functions raises a `PermissionError`.
- **Zero Arbitrary Execution**: The LLM is never given tools to execute arbitrary Python, shell commands, or raw database queries.
- **Prompt Injection Defense**: User messages are passed strictly in the user content block of the chat completion API and never interpolated directly into administrative system instructions.
- **Image Isolation**: Raw webcam images and biometric data are never forwarded to the OpenAI API or any external text LLM provider.

---

## 5. Audit Logging

- **Audit Collection**: Security-critical actions (logins, session mutations, consent grants) trigger records in the `audit_logs` collection.
- **Non-Throwing Logging**: Audit failures never disrupt legitimate student interactions.
