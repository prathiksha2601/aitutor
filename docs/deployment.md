# EIT Production Deployment Guide

## 1. Production Architecture

In production, run the application using Docker Compose with an Nginx reverse proxy providing HTTPS termination:

```
[ Internet / HTTPS (443) ]
             │
             ▼
      [ Nginx Reverse Proxy ]
       ├── /api/  ──> [ Gunicorn / Flask (Port 5000) ]
       └── /      ──> [ Vite Static Files (Nginx) ]
                               │
                               ▼
                   [ MongoDB 8.0 (Internal Network) ]
```

---

## 2. Environment Variables Checklist

Ensure the following variables are configured in production:

```env
FLASK_ENV=production
FLASK_SECRET_KEY=<generate_with_secrets_token_hex_32>
JWT_SECRET_KEY=<generate_with_secrets_token_hex_32>
MONGODB_URI=mongodb://user:password@mongodb:27017/eit_database?authSource=admin
MONGODB_DATABASE=eit_database
OPENAI_API_KEY=<your_production_openai_api_key>
OPENAI_MODEL=gpt-4o-mini
FRONTEND_ORIGIN=https://your-domain.com
RATE_LIMIT_PER_MINUTE=60
MODEL_PATH=/app/ml/artifacts/expression_model.keras
MODEL_LABELS_PATH=/app/ml/artifacts/labels.json
```

---

## 3. Docker Compose Deployment

Build and launch all services:

```bash
docker compose up -d --build
```

Verify service status:

```bash
docker compose ps
docker compose logs -f backend
```

---

## 4. Production Database Initialization

Run seed data and create MongoDB indexes:

```bash
docker compose exec backend python scripts/seed_demo_data.py
```
