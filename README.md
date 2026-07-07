# 🎫 Portfolio-Ticket — Triagem Inteligente de Chamados

Microsserviço de IA que recebe chamados de suporte, busca contexto relevante numa base de conhecimento interna e sugere respostas automaticamente. Projetado para funcionar como backend de um sistema maior (ex: uma aplicação Spring Boot que gerencia os tickets).

---

## 📋 Índice

- [Motivação](#-motivação)
- [Por que IA para triagem?](#-por-que-ia-para-triagem)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Endpoints da API](#-endpoints-da-api)
- [Como Rodar](#-como-rodar)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)

---

## 💡 Motivação

Em operações de suporte real, a maior parte do tempo de um analista de nível 1 é gasta lendo o chamado, buscando a resposta na documentação interna e reformulando essa resposta para o cliente. Isso é repetitivo, lento e sujeito a inconsistências entre atendentes.

A proposta deste projeto é automatizar exatamente esse fluxo:

1. O cliente abre um chamado com texto livre.
2. A IA busca o trecho mais relevante da base de conhecimento da empresa.
3. A IA formula uma resposta baseada **exclusivamente** nesse contexto (sem inventar).
4. O sistema devolve a sugestão, que pode ser enviada ao cliente ou revisada por um humano.

O objetivo **não é substituir o atendente**, mas eliminar o trabalho mecânico de busca e redação, permitindo que o humano foque em casos que realmente exigem julgamento.

---

## 🤔 Por que IA para triagem?

Em vez de usar keyword matching ou árvores de decisão (que quebram com texto livre e linguagem informal), este projeto combina **busca vetorial semântica (RAG)** com uma **LLM** para encontrar a informação certa e reformulá-la numa resposta natural para o cliente.

> Para a análise completa de trade-offs — incluindo por que não usar só a busca vetorial sem LLM, alternativas determinísticas consideradas e custos assumidos — veja o [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🏗 Arquitetura

```
┌─────────────────┐       HTTP        ┌──────────────────────────────┐
│  Spring Boot    │ ──────────────▶   │  FastAPI (este serviço)      │
│  (Backend)      │  POST /tickets    │                              │
└─────────────────┘                   │  main.py (API)               │
                                      │    ├── graph_agent.py        │
                                      │    │    └── LangGraph         │
                                      │    │         ├─ Bibliotecário │ ─▶ ChromaDB (busca vetorial)
                                      │    │         └─ Atendente     │ ─▶ LLM (Minimax-M3)
                                      │    └── rag_service.py        │
                                      │         └── ChromaDB + Embeddings
                                      └──────────────────────────────┘
```

> Para detalhes sobre a stack, fluxo do LangGraph e separação de responsabilidades, veja o [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 📁 Estrutura do Projeto

```
Portfolio-Ticket/
├── main.py                  # API FastAPI — endpoints HTTP
├── graph_agent.py           # Orquestração LangGraph — fluxo dos agentes
├── rag_service.py           # Serviço de RAG — ChromaDB + embeddings
├── rag_knowledge_base.md    # Documentação sobre o design da base de conhecimento
├── requirements.txt         # Dependências Python
├── ARCHITECTURE.md          # Decisões arquiteturais e trade-offs
├── data/
│   └── policies/            # Documentos de política da empresa (mock)
│       ├── acesso_conta.md
│       ├── politica_reembolso.md
│       └── politica_sla.md
└── meu_banco_vetorial/      # Dados persistidos do ChromaDB (gerado automaticamente)
```

---

## 📡 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/tickets/process` | Processa um chamado e retorna a sugestão da IA |
| `POST` | `/api/v1/documents` | Upload de arquivo `.md` para indexar no RAG |
| `GET` | `/api/v1/documents` | Lista todos os documentos indexados |
| `DELETE` | `/api/v1/documents/{doc_id}` | Remove um documento do RAG pelo ID |

### Exemplos

**Processar um ticket:**
```bash
curl -X POST http://localhost:8000/api/v1/tickets/process \
  -H "Content-Type: application/json" \
  -d '{"ticket_id": "TK-001", "texto": "Minha conta foi bloqueada depois de errar a senha"}'
```

**Upload de documento para o RAG:**
```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@data/policies/acesso_conta.md"
```

**Listar documentos indexados:**
```bash
curl http://localhost:8000/api/v1/documents
```

**Remover documento:**
```bash
curl -X DELETE http://localhost:8000/api/v1/documents/acesso_conta.md
```

---

## 🚀 Como Rodar

```bash
# 1. Criar e ativar o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar a chave da API (ver seção abaixo)
export MINIMAX_API_KEY="sua-chave-aqui"

# 4. Iniciar o servidor
uvicorn main:app --reload
```

A documentação interativa (Swagger) estará disponível em `http://localhost:8000/docs`.

---

## 🔑 Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `MINIMAX_API_KEY` | Sim | Chave de API do Minimax para chamadas à LLM |
