## Context

The repository has accumulated several core components in its root directory: two agent implementations (LangGraph, AgentScope), an embedding/RAG service, simulated corporate tools, observability setups, and FastAPI endpoint definitions. In addition, extensive documentation markdown files reside alongside code and configuration files. This flat structure makes the codebase hard to navigate and violates common FastAPI structure patterns.

## Goals / Non-Goals

**Goals:**
- Implement a standard FastAPI `app/` structure.
- Clean up the project root to only contain essential config (`docker-compose.yml`, `requirements.txt`) and high-level docs (`README.md`).
- Organize internal documentation under a dedicated `docs/` folder.
- Extract tracing/logging/metrics setup from `main.py` into a dedicated `app/core/observability.py`.

**Non-Goals:**
- Do not refactor the logic within the agents, RAG service, or tools.
- Do not change how the infrastructure (Docker, Grafana, Loki) operates.

## Decisions

**1. FastAPI `app/` Layout:**
- **Why?** It is the standard structure for FastAPI applications. It inherently separates configuration, endpoints, and business logic.
- **Alternative:** Keep everything in root or group by feature (e.g. `domain/`). Given the current scale, `app/` with functional directories (`agents/`, `services/`, `core/`) is simpler and sufficient.

**2. Extracting Observability Setup:**
- **Why?** `main.py` should only be responsible for registering routers/endpoints. The OpenTelemetry, Loki, and Prometheus initialization is noisy. Moving it to `app/core/observability.py` abstracts this complexity.
- **Alternative:** Keep it in `main.py` but collapse it. This is harder to maintain.

**3. Segregation of Docs:**
- **Why?** Moving architecture and RAG evaluation docs to `docs/` makes the repo instantly more welcoming to newcomers. The root `README.md` will focus solely on how to run the project.

**4. Prompt Unification:**
- **Why?** Keeping separate duplicate prompts in LangGraph and AgentScope implementations invites divergence and violates DRY. Storing system prompts in a central `app/agents/prompts.py` ensures both runner engines share the same persona, policies, and autonomy guidelines.

## Risks / Trade-offs

- **[Risk] Relative paths breaking** → Mitigation: All scripts will still be run from the repository root (e.g., `uvicorn app.main:app`), meaning relative paths to `data/` and `meu_banco_vetorial/` will continue to function flawlessly.
- **[Risk] Python import paths breaking** → Mitigation: We will systematically update all local imports across `.py` files (e.g., `import rag_service` -> `from app.services import rag_service`).
