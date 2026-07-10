## Why

Instrumentar a aplicação com OpenTelemetry é crucial para monitorar e debugar orquestradores de IA, identificando gargalos em chamadas de LLM ou buscas no banco vetorial. Adicionalmente, esta mudança irá destacar habilidades em Observabilidade e engenharia de software modernas (stack Grafana) para a apresentação do portfólio, enquanto suportará execução na nuvem (ex: Grafana Cloud + Vercel).

## What Changes

- Adição de dependências do ecossistema OpenTelemetry no `requirements.txt`.
- Instrumentação automática do FastAPI para capturar tempos de requisições.
- Instrumentação manual via "Spans" no `graph_agent.py` para medir o tempo gasto em cada nó do LangGraph (Analista, Bibliotecário, Atendente).
- Adição de uma "chave seletora" (toggle) no endpoint principal para permitir a alternância de orquestrador entre `langgraph` e `agentscope`.
- Criação de um ambiente local orquestrado por `docker-compose.yml` que provê a aplicação rodando junto com uma stack completa do Grafana (Grafana, Prometheus e Tempo).

## Capabilities

### New Capabilities
- `observability-telemetry`: Geração e exportação de traces via protocolo OTLP para monitoramento da aplicação Python e seus agentes de IA.
- `agent-engine-toggle`: Capacidade de selecionar o motor de execução (LangGraph vs AgentScope) dinamicamente via payload da requisição.
- `local-observability-stack`: Ambiente em contêineres locais para visualização de métricas e rastreamentos de forma plug-and-play.

### Modified Capabilities
<!-- Nenhuma existente a ser alterada a nível de especificação -->

## Impact

- `main.py`: Refatorado para `async` e adicionado instrumento OTel.
- `graph_agent.py`: Receberá os blocos de spans para Tracing.
- `requirements.txt`: Novas dependências.
- Novos arquivos de infraestrutura (Dockerfile, docker-compose.yml, prometheus.yml, etc).
