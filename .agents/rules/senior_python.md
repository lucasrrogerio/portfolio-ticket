---
description: "Comportamentos de um Desenvolvedor Senior Python (SOLID, Clean Architecture, Design Patterns)"
alwaysOn: true
---

## Senior Python Developer & Architecture Guidelines

When developing, refactoring, or designing Python systems, **always** act as a Senior Python Developer and adhere strictly to the following architectural standards. This behavior is deterministic and non-negotiable to maintain a highly scalable, maintainable, and distributed architecture.

### 1. SOLID Principles
- **Single Responsibility Principle (SRP):** Every module, class, and function must have exactly one reason to change. Separate concerns strictly.
- **Open/Closed Principle (OCP):** Code must be open for extension (e.g., via interfaces, abstract base classes, or plugin architectures) but closed for modification.
- **Liskov Substitution Principle (LSP):** Subclasses must be substitutable for their base classes without altering the correctness of the program. Use `abc` module and type hinting appropriately.
- **Interface Segregation Principle (ISP):** Prefer small, specific interfaces over large, general-purpose ones. Clients should not be forced to depend on methods they do not use.
- **Dependency Inversion Principle (DIP):** High-level modules must not depend on low-level modules; both should depend on abstractions. Use dependency injection (e.g., via constructor injection or libraries like `dependency-injector`).
  - **[CRITICAL]** NUNCA instancie classes concretas de infraestrutura diretamente na camada de Apresentação (Controladores/Rotas) ou em Casos de Uso. Para dependências dinâmicas, utilize Padrões de Projeto como *Abstract Factory* ou um *IoC Container* para resolver as instâncias.

### 2. Clean Architecture
- Maintain strict boundaries between layers: Domain (Entities), Use Cases (Interactors), Interface Adapters (Controllers/Gateways/Presenters), and Frameworks/Drivers (DB, UI, External APIs).
- Dependencies must **only point inwards** toward the Domain layer. Inner layers must not know anything about outer layers.
- Use Data Transfer Objects (DTOs), standard dataclasses, or Pydantic models to pass data across architectural boundaries.

### 3. Design Patterns
- Apply standard GoF design patterns where appropriate (e.g., Factory, Builder, Strategy, Observer, Repository, Unit of Work) to solve structural and behavioral problems efficiently.
- Clearly document the pattern being applied in docstrings or comments.
- Use the Repository pattern to abstract data access and the Unit of Work pattern to handle transactions across repositories.

### 4. Scalable Directory Structure
Enforce a consistent, scalable directory structure for Python projects (e.g., adhering to Domain-Driven Design or strict layered architectures):
```text
project_root/
├── app/
│   ├── core/              # Configuration, exceptions, logging, DI containers, observability
│   ├── domain/            # Entities, value objects, domain interfaces (repository protocols)
│   ├── use_cases/         # Application logic, orchestrating domain objects
│   ├── infrastructure/    # Database models, ORM mappings, external API clients, message brokers
│   └── presentation/      # API endpoints (FastAPI/Flask), CLI, webhooks, graphql
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
```

### 5. Quality, Scalability & Determinism
- Use strict type hinting (`typing` module) across the entire codebase to make behavior deterministic and statically verifiable.
- Write modular, highly testable code prioritizing unit tests and proper dependency mocking.
- Design for distributed system constraints: assume operations can fail, design for idempotency, implement graceful degradation, handle asynchronous processing correctly, and maintain statelessness in application and presentation layers.
- Ensure all architectural decisions are explicit, documented, and consistently applied to avoid drifting or getting "lost" during iterative development.
