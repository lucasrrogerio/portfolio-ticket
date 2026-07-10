## ADDED Requirements

### Requirement: Automated execution of unit and integration tests
The system SHALL support executing automated tests locally using `pytest` to verify RAG queries, FastAPI routing, and agent flows.

#### Scenario: Running the test suite
- **WHEN** the developer runs `pytest` from the root directory
- **THEN** all tests execute successfully and print the test results report

### Requirement: Mocked LLM and database connections in tests
The test suite SHALL mock external API endpoints (specifically Minimax and local persistent ChromaDB) to guarantee that tests run fast, locally, and without cost or network dependencies.

#### Scenario: Running tests offline
- **WHEN** the developer runs `pytest` in an environment without internet access or valid API keys
- **THEN** the test suite executes successfully without making actual HTTP calls to the Minimax API
