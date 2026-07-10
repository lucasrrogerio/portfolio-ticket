## 1. Setup Dependencies

- [x] 1.1 Add `pytest`, `pytest-asyncio`, and `httpx` to `requirements.txt`
- [x] 1.2 Install new dependencies in the virtual environment

## 2. Implement RAG Unit Tests

- [x] 2.1 Create `tests/test_rag.py`
- [x] 2.2 Add unit tests for `busca_hibrida` and `adicionar_documento`, mocking ChromaDB and SentenceTransformer

## 3. Implement Agent Unit Tests

- [x] 3.1 Create `tests/test_agents.py`
- [x] 3.2 Add unit tests for `LangGraph` agent nodes (`no_analisar_intencao`, `no_gerar_resposta`), mocking `ChatOpenAI` calls and verifying `StateGraph` logic

## 4. Implement API Integration Tests

- [x] 4.1 Create `tests/test_api.py`
- [x] 4.2 Add integration tests using `TestClient` to verify endpoints (`GET /`, `POST /api/v1/tickets/process`, `POST /api/v1/documents`, `DELETE /api/v1/documents/{doc_id}`)

## 5. Verification

- [x] 5.1 Run `pytest` to ensure all tests pass locally
- [x] 5.2 Validate that the test suite runs fully mock-based (no internet or Minimax API key required)
