## 1. Create Core Application Directories

- [x] 1.1 Create `app/` directory and its subdirectories: `app/core/`, `app/agents/`, `app/services/`
- [x] 1.2 Add `__init__.py` files to each of the created directories

## 2. Refactor Documentation

- [x] 2.1 Create `docs/` directory
- [x] 2.2 Move `ARCHITECTURE.md` to `docs/architecture.md`
- [x] 2.3 Move `AVALIACAO_RAG.md` to `docs/evaluation.md`
- [x] 2.4 Move `rag_knowledge_base.md` to `docs/rag_knowledge_base.md`
- [x] 2.5 Create `docs/observability.md` with instructions on Grafana, Tempo, and Loki
- [x] 2.6 Rewrite the project root `README.md` to be a concise executive summary

## 3. Relocate Core Python Files

- [x] 3.1 Move `rag_service.py` to `app/services/rag_service.py`
- [x] 3.2 Move `tools.py` to `app/agents/tools.py`
- [x] 3.3 Move `graph_agent.py` to `app/agents/graph_agent.py`
- [x] 3.4 Move `agentscope_agent.py` to `app/agents/agentscope_agent.py`

## 4. Extract Observability & Main

- [x] 4.1 Create `app/core/observability.py` and move the OTel/Prometheus/Loki setup into a `setup_observability` function
- [x] 4.2 Move `main.py` to `app/main.py`
- [x] 4.3 Refactor `app/main.py` to remove inline observability config, importing `setup_observability` instead
- [x] 4.4 Update all internal imports in `app/main.py`, `graph_agent.py`, and `agentscope_agent.py` to reflect the new `app.*` namespaces

## 5. Clean up Root Folder

- [x] 5.1 Move `teste_busca.py` and `rag.ipynb` to a new `tests/` or `notebooks/` directory (create if necessary)
- [x] 5.2 Remove outdated `server_logs.txt` from root

## 6. Unify Prompts

- [x] 6.1 Create `app/agents/prompts.py` with unified system prompts
- [x] 6.2 Refactor `app/agents/graph_agent.py` to import prompts from `app.agents.prompts`
- [x] 6.3 Refactor `app/agents/agentscope_agent.py` to import prompts from `app.agents.prompts`

## 7. Verification

- [x] 7.1 Start server using `uvicorn app.main:app` and verify it starts correctly
- [x] 7.2 Test the `/api/v1/tickets/process` endpoint to confirm RAG and Agent logic still function properly with unified prompts
