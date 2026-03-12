# WebFactory Framework

A self-hostable, multiplayer-first framework for building a top-down 2D factory game in the browser.

## What this provides

- **Python backend (FastAPI + WebSocket)** with SQLite persistence.
- **Username/password auth** with token-based sessions.
- **Persistent worlds** identified by custom world codes.
- **16-player target** per world.
- **Framework abstractions** for:
  - item definitions and stacks,
  - inventory and transfer utilities,
  - building definitions and ticking behavior,
  - world state, expansion, and settings ("gamerules").
- **React frontend** to create/join worlds and interact with a live world canvas.
- **Docs focused on extending content** so you can add your own smelters/crafters/etc.

## Quick start

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

Visit `http://localhost:5173`.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Content Authoring Guide](docs/content-authoring.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)

## License

MIT.
