## Why

The project has grown significantly with the addition of AgentScope, LangGraph, Prometheus, Grafana, Loki, Tempo, and hybrid search. Currently, all core modules and markdown files are placed in the root directory, which is causing clutter and making the repository disorganized. Moving to a structured `app/` folder (the FastAPI gold standard) and segregating documentation into a `docs/` folder will vastly improve maintainability, onboarding, and separation of concerns.

## What Changes

- Segregate source code into an `app/` directory (`main.py`, `core/`, `agents/`, `services/`).
- Segregate large documentation markdown files into a `docs/` directory.
- Refactor `main.py` by extracting observability configuration (Loki, OTel, Prometheus) into `app/core/observability.py` to achieve Separation of Concerns.
- Rewrite `README.md` to be an executive summary and quick-start guide, pointing to the new `docs/` files.
- Ensure all relative paths (like the ChromaDB persistent path) continue working perfectly from the project root.

## Capabilities

### New Capabilities
- `repo-structure`: Structural definitions for the application's layout and documentation.

### Modified Capabilities


## Impact

- All developers will now need to use `uvicorn app.main:app` to start the server.
- The `docker-compose.yml` and `requirements.txt` remain unaffected.
- The repository root will be significantly cleaner.
