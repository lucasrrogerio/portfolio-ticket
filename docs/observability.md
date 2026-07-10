# Observabilidade (Tempo, Loki e Prometheus)

Este documento detalha o funcionamento e a configuração da pilha de observabilidade híbrida (Localhost + Docker) do nosso serviço de triagem de tickets.

---

## 🛠️ Visão Geral da Arquitetura Híbrida

Para otimizar o tempo de desenvolvimento e o uso de recursos de hardware, a pilha de observabilidade roda de forma híbrida:

1. **Aplicação Python (FastAPI + LangGraph)**: Executada diretamente no `localhost` (fora do Docker).
2. **Serviços de Telemetria (Grafana Stack)**: Executados via Docker Compose.

```mermaid
graph TD
    subgraph Localhost
        FastAPI[FastAPI App]
        LangGraph[LangGraph Engine]
        Chroma[ChromaDB]
    end

    subgraph Docker Containers
        Tempo[Grafana Tempo (Traces)]
        Prometheus[Prometheus (Métricas)]
        Loki[Grafana Loki (Logs)]
        Grafana[Grafana Dashboard]
    end

    FastAPI -->|Spans via gRPC 4317| Tempo
    FastAPI -->|Logs via HTTP 3100| Loki
    Prometheus -->|Scrape HTTP 8000/metrics| FastAPI
    Grafana -->|Query| Tempo
    Grafana -->|Query| Loki
    Grafana -->|Query| Prometheus
```

---

## 📈 Coleta de Dados

### 1. Rastreamento (Traces) - Grafana Tempo
- O `TracerProvider` do OpenTelemetry é configurado no arquivo [observability.py](file:///Users/lucasrogerio/Projetos/Portfolio-Ticket/app/core/observability.py) e exporta dados no protocolo gRPC (OTLP/gRPC) para o Tempo no endereço `http://localhost:4317`.
- **Instrumentação Automática**: O FastAPI é instrumentado automaticamente usando `FastAPIInstrumentor`.
- **Instrumentação Manual**: Cada ferramenta corporativa simulada (AD, CRM, ITSM) no arquivo [tools.py](file:///Users/lucasrogerio/Projetos/Portfolio-Ticket/app/agents/tools.py) cria spans manuais para mapear a latência simulada (de 2s a 12s).

### 2. Métricas - Prometheus
- O Prometheus monitora a saúde e performance HTTP da aplicação acessando periodicamente o endpoint `/metrics` gerado pelo `prometheus-fastapi-instrumentator`.

### 3. Registro (Logs) - Grafana Loki
- Os logs da aplicação são injetados diretamente no Grafana Loki usando o driver `logging-loki`. O endpoint configurado é o `http://localhost:3100/loki/api/v1/push`.

---

## 🚀 Como Visualizar Traces e Logs no Grafana

1. Com o docker compose ativo (`docker compose up -d`), acesse o Grafana no seu navegador:
   * **URL**: [http://localhost:3000](http://localhost:3000)
   * **Usuário / Senha**: `admin` / `admin` (ou sem autenticação dependendo da imagem)
2. Vá até o menu lateral esquerdo e clique em **Explore** (ícone de bússola).
3. Selecione a fonte de dados (Data Source):
   * Escolha **Tempo** para investigar Traces de execução dos agentes.
   * Escolha **Loki** para inspecionar os logs do sistema.
4. No buscador do Tempo, filtre por:
   * **Service Name**: `ticket-triage-service`
5. Clique em **Run Query** e selecione um trace na lista.

### Mapeamento de Latência (Waterfall)
Como as ferramentas corporativas possuem delays simulados realistas para simular chamadas de rede externas, o waterfall do trace ilustra com precisão o tempo gasto em cada etapa:

* **AD Lock status**: ~2.5s
* **CRM Account info**: ~4.0s
* **ITSM ticket creation**: ~5.0s

Ao olhar o trace no Grafana, você verá claramente a execução sequencial assíncrona do LangGraph chamando as ferramentas e aguardando suas respostas antes de devolver a conclusão ao usuário.
