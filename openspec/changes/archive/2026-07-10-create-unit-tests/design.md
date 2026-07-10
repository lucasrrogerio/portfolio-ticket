## Context

The application contains custom Python modules for RAG search, corporate agent tools, LangGraph orchestrations, and FastAPI endpoints. However, there are no unit tests verifying the correctness of these components. Without automated testing, modifications to the codebase (such as altering prompt structures or refactoring agents) pose a high regression risk.

## Goals / Non-Goals

**Goals:**
- Set up a standard testing harness using `pytest` and `pytest-asyncio`.
- Implement unit tests for individual functions (e.g., retrieval logic, tool definitions).
- Implement integration tests for FastAPI endpoints using `TestClient`.
- Implement unit tests for LangGraph agent nodes and state transitions, mocking the LLM to avoid external API calls.

**Non-Goals:**
- We will not run end-to-end tests that make live calls to the Minimax API or other real corporate endpoints.
- We will not perform UI/browser-based testing.

## Decisions

**1. Testing Framework:**
- **Why?** `pytest` is the industry standard for Python testing due to its rich ecosystem, simple syntax, and native async support via `pytest-asyncio`.
- **Alternative:** Python's built-in `unittest` library. `pytest` is preferred because writing test fixtures and dealing with async tests is cleaner and more declarative.

**2. Mocking Strategy:**
- **Why?** Since tests must run quickly and deterministically, we must mock all external calls:
  - Mock `SentenceTransformer` embedding generation using `unittest.mock`.
  - Mock the ChromaDB persistent client.
  - Mock `llm` and `llm_with_tools` calls in LangGraph to avoid Minimax API charges and timeouts.
- **Alternative:** Spin up a real ChromaDB instance. This adds overhead and makes local execution slower.

**3. Test Structure:**
- Group tests logically under `tests/`:
  - `tests/test_rag.py`: Verifies RAG hybrid retrieval logic.
  - `tests/test_api.py`: Verifies FastAPI routes.
  - `tests/test_agents.py`: Verifies LangGraph agent decisions and tool routing.

## Risks / Trade-offs

- **[Risk] Test fragility due to LLM mock complexity** → Mitigation: Keep mocks simple (e.g., make LLM mock return pre-defined ToolCalls or simple answers based on the prompt content).
- **[Risk] Syncing db state in tests** → Mitigation: Use a fresh, temporary/in-memory database instance or mock ChromaDB's responses completely.
