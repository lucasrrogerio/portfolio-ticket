## ADDED Requirements

### Requirement: OTLP Auto-Instrumentation
A aplicação SHALL instrumentar o framework FastAPI para coletar automaticamente métricas e traces de todas as rotas de entrada via protocolo OTLP.

#### Scenario: Rota process_ticket é chamada
- **WHEN** um cliente faz uma requisição POST para `/api/v1/tickets/process`
- **THEN** um span raiz é gerado e enviado para o exportador OTLP configurado capturando latência, status code e endpoint.

### Requirement: LangGraph Manual Tracing
A aplicação SHALL criar Spans customizados (OpenTelemetry) para os nós individuais do LangGraph (`no_analisar_intencao`, `no_buscar_documentos`, `no_gerar_resposta`) garantindo que o gráfico de cascata represente a execução da IA.

#### Scenario: AgentGraph processa o ticket
- **WHEN** o orquestrador aciona a execução do `no_analisar_intencao`
- **THEN** um novo child-span nomeado `Analista_LLM` é criado com atributos contendo o `ticket_id`.
