# Deployment Guide (Self-hosted)

## Single-server setup

1. Run backend with Uvicorn/Gunicorn.
2. Build frontend static files and serve via Nginx/Caddy.
3. Reverse proxy:
   - `/api` -> backend
   - `/ws` -> backend (WebSocket upgrade)
   - `/` -> frontend static files

## Docker Compose example

```yaml
services:
  webfactory:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
```

Use SQLite on persistent volume (`/app/data/webfactory.db`).

## Production hardening checklist

- Set `secret_key` via environment variable.
- Enable HTTPS.
- Add backup strategy for SQLite.
- Add process manager + health checks.
- Consider PostgreSQL if you outgrow SQLite write throughput.
