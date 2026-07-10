## Context

A aplicação atual de Triage AI utiliza o `graph_agent` (LangGraph) para responder a chamados através de uma busca híbrida em documentos e chamadas ao LLM Minimax. Para fins de portfólio e produção na Vercel, o usuário deseja ter instrumentação detalhada de tempo de execução e métricas usando OpenTelemetry, enviando dados para uma stack Grafana, além de uma chave seletora para testar um agente alternativo feito com AgentScope.

## Goals / Non-Goals

**Goals:**
- Instrumentar o backend (FastAPI) para gerar traces OTLP automaticamente.
- Instrumentar nós específicos do LangGraph (Analista, Bibliotecário, Atendente) manualmente usando Spans.
- Suportar a exportação dinâmica de telemetria baseada em variáveis de ambiente (`OTEL_EXPORTER_OTLP_ENDPOINT`).
- Permitir a escolha do motor do agente (`langgraph` ou `agentscope`) via o payload da API.
- Fornecer um `docker-compose.yml` local com Grafana, Prometheus e Tempo para demonstração do portfólio.

**Non-Goals:**
- Alterar as lógicas, prompts ou fluxo conversacional dos agentes atuais.
- Subir a stack do Grafana em produção (A recomendação para produção na Vercel é utilizar o Grafana Cloud SaaS).

## Decisions

1. **Uso de OTLP Padrão:** Utilizar a biblioteca oficial `opentelemetry-exporter-otlp` do Python para garantir que a aplicação possa enviar dados tanto para o Tempo local (no docker-compose) quanto para o Grafana Cloud mudando apenas o endpoint na Vercel.
2. **Instrumentação Híbrida:** 
   - A biblioteca `opentelemetry-instrumentation-fastapi` fará o rastreamento automático do endpoint.
   - Chamadas a `tracer.start_as_current_span` envolverão as funções no `graph_agent.py` para visualizar o gráfico de cascata de quanto tempo cada passo do LangGraph consumiu.
3. **Toggle de Agente Dinâmico:** A importação dos arquivos `graph_agent.py` e `agentscope_agent.py` dentro do `main.py` será condicionada pela propriedade `motor` na requisição web, protegendo contra erros de dependência global se algum dos frameworks quebrar isoladamente.
4. **Infraestrutura Local Isolada:** O `docker-compose.yml` subirá o `app` (FastAPI construído via Dockerfile) ao lado dos containers `tempo`, `prometheus` e `grafana`, e arquivos `datasource.yml` farão a auto-configuração do Grafana.

## Risks / Trade-offs

- **[Risk] Aumento do tempo de startup do FastAPI devido aos imports de LLMs duplicados no toggle.** → **Mitigation:** Importar os agentes apenas dentro da rota (lazy loading) ou manter inicialização assíncrona onde possível.
- **[Risk] Vercel congelar instâncias e interromper o envio do exportador OTLP em background.** → **Mitigation:** Usar o exportador síncrono ou com envio imediato via HTTP (em vez de gRPC assíncrono batchado) se estiver operando em modo function. No contexto local (Docker), o padrão Batch gRPC funciona perfeitamente.
