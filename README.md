# Digital Shield

One React + Vite browser frontend and one shared FastAPI backend. The target
engine uses one lightweight verification agent with scam checker, URL checker,
claim verifier, and vision tool. WhatsApp is a future integration vision shown
only through pitch animation.

The backend currently validates input and returns an explicit placeholder. The
frontend is an existing Vite starter; product UI and API connection are pending.

## Repository

```text
frontend/          Browser app (existing starter)
  src/components/ Planned UI components
  src/pages/      Planned pages
  src/services/   Planned API service
backend/           FastAPI foundation and empty agent/tool modules
docs/              Architecture, context, development, demo, pitch, coding guides
requirements.txt   Minimal backend dependencies
.env.example       Example backend environment variable
```

Root `public/` preserves legacy material outside the active app; see
[legacy material notes](public/README.md). It is not a second frontend target.

## Backend

Use standard Windows CPython 3.10+ (tested on 3.13), from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open http://127.0.0.1:8000/docs. `/` redirects there and `/health` reports health.
See [project context](docs/project_context.md) for the current `/verify` contract.

## Existing frontend starter

```powershell
cd frontend
npm ci
npm run dev
```

This launches the existing starter, not a completed verification interface.

## Project guides

- [Architecture](docs/architecture.md)
- [Current implementation](docs/project_context.md)
- [Development plan](docs/development_plan.md)
- [Demo plan](docs/demo_plan.md)
- [Pitch notes](docs/pitch_notes.md)
- [Coding agent guide](docs/coding_agent_guide.md)
