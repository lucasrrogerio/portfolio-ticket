## Why

As the application grew, we restructured the code into `app/`, separated observability, and unified prompts. To prevent regressions when making future updates (like modifying the agent flows, updating retrieval strategies, or altering tools), we need a robust suite of unit and integration tests. Currently, we only have a script to test RAG manually (`tests/teste_busca.py`), but no automated tests using standard test runners like `pytest`.

## What Changes

- Add a unit testing suite under the `tests/` directory.
- Test cases for:
  - RAG services (mocking ChromaDB or using temporary databases).
  - FastAPI endpoints (using `fastapi.testclient.TestClient`).
  - LangGraph agent flow (mocking ChatOpenAI and tools to check the routing and state transitions).
  - Observability telemetry setup.
- Add `pytest` and its dependencies to `requirements.txt`.
- Set up a GitHub Actions workflow or a local test script to run tests easily.

## Capabilities

### New Capabilities
- `unit-testing`: Automatic test cases for the FastAPI application and LangGraph agents.

### Modified Capabilities


## Impact

- All developers can run `pytest` locally to ensure code changes do not break existing functionality.
- Requires adding `pytest` and `pytest-asyncio` to the dependencies.
