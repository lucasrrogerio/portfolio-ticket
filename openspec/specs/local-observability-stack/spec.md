# Local Observability Stack

## Purpose
Provisionamento local de contêineres para stack de observabilidade.

## Requirements

### Requirement: Local Docker Stack
O repositório SHALL fornecer um arquivo `docker-compose.yml` pré-configurado contendo serviços para a aplicação principal e para a stack de observabilidade LGTM-lite (Grafana, Tempo e Prometheus).

#### Scenario: Subindo o ambiente local
- **WHEN** o desenvolvedor executa `docker-compose up`
- **THEN** a aplicação é exposta com sua instrumentação OpenTelemetry apontando para o contêiner interno do `Tempo`, e o Grafana (na porta 3000) inicia com as datasources já provisionadas automaticamente.
