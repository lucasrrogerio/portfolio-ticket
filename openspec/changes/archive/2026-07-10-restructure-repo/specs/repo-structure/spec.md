## ADDED Requirements

### Requirement: Application structure shall follow FastAPI idiomatic design
The system SHALL organize all internal logic within an `app/` folder to segregate business logic from environment configurations and root-level files.

#### Scenario: Running the FastAPI server
- **WHEN** the developer wants to start the web service
- **THEN** the developer executes `uvicorn app.main:app` from the project root

### Requirement: Documentation shall be segregated
The system SHALL move all in-depth documentation and technical evaluations to a dedicated `docs/` directory, leaving only the `README.md` at the project root for onboarding.

#### Scenario: Navigating the repository documentation
- **WHEN** a new contributor explores the repository
- **THEN** the contributor accesses architectural details under `docs/architecture.md`
