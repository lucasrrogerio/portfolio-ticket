# Agent Engine Toggle

## Purpose
Permite selecionar dinamicamente o motor do agente a ser usado para processar os tickets.

## Requirements

### Requirement: Request-Based Engine Selection
A aplicação SHALL aceitar um campo `motor` no payload de requisição e instanciar/invocar o framework correspondente baseado no seu valor, protegendo contra dependências cruzadas (crash de um framework não deve derrubar o outro se não foi invocado).

#### Scenario: Uso do Motor LangGraph (Padrão)
- **WHEN** o cliente envia um POST para `/api/v1/tickets/process` sem o parâmetro motor ou com motor="langgraph"
- **THEN** a aplicação invoca a função `processar_ticket` de `graph_agent.py` e retorna a resposta.

#### Scenario: Uso do Motor AgentScope
- **WHEN** o cliente envia um POST para `/api/v1/tickets/process` com o parâmetro motor="agentscope"
- **THEN** a aplicação invoca a função assíncrona `processar_ticket` de `agentscope_agent.py` e retorna a resposta.
