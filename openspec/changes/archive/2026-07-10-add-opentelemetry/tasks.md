## 1. Infraestrutura Local e Dependências

- [x] 1.1 Adicionar pacotes `opentelemetry-*` no `requirements.txt`.
- [x] 1.2 Criar arquivo `Dockerfile` para conteinerizar a aplicação Python.
- [x] 1.3 Criar `docker-compose.yml` contendo os serviços `app`, `tempo`, `prometheus` e `grafana`.
- [x] 1.4 Adicionar pasta `infra/` com `datasources.yml` para pré-configuração do Grafana.

## 2. Refatoração do Triage API (Toggle)

- [x] 2.1 Alterar `TicketRequest` no `main.py` para incluir o campo opcional `motor`.
- [x] 2.2 Refatorar rota `/api/v1/tickets/process` para `async def` e adicionar a lógica condicional de importação (LangGraph vs AgentScope).

## 3. Instrumentação OpenTelemetry

- [x] 3.1 Configurar TracerProvider, OTLPSpanExporter e inicializar `FastAPIInstrumentor` no topo do `main.py`.
- [x] 3.2 Importar o OpenTelemetry no `graph_agent.py` e criar os spans (`tracer.start_as_current_span`) dentro das funções dos nós LangGraph.

## 4. Testes e Validação

- [x] 4.1 Executar a stack local via Docker Compose e validar o envio de traces do `motor=langgraph`.
- [x] 4.2 Validar o envio de traces e correta execução usando o `motor=agentscope`.
