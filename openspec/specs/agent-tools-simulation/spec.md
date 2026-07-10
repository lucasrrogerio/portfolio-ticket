# agent-tools-simulation Specification

## Purpose
TBD - created by archiving change agent-mock-tools. Update Purpose after archive.
## Requirements
### Requirement: Ferramentas simuladas de serviços corporativos
O sistema SHALL disponibilizar funções em Python decoradas como ferramentas (`@tool`) que simulam operações de negócios em sistemas externos (ex: `get_user_status`, `unlock_account`, `escalate_to_human`, etc.).

#### Scenario: Invocação de ferramenta
- **WHEN** a ferramenta é invocada
- **THEN** ela suspende a execução assincronamente (via `asyncio.sleep`) por um período aleatório e configurável (entre 2 a 12 segundos) e retorna um dicionário estático contendo o status da simulação.

