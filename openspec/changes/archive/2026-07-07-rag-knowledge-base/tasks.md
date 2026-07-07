## 1. Setup e Dependências

- [x] 1.1 Criar `requirements.txt` com FastAPI, uvicorn, pydantic, langgraph, langchain-openai, chromadb e sentence-transformers
- [x] 1.2 Criar e configurar ambiente virtual Python (`.venv`)

## 2. Base de Conhecimento (RAG Pipeline)

- [x] 2.1 Criar documentos mock de política da empresa em `data/policies/` (reembolso, acesso, SLA)
- [x] 2.2 Inicializar ChromaDB com `PersistentClient` e coleção `politicas_empresa`
- [x] 2.3 Configurar modelo de embeddings SentenceTransformers (`paraphrase-multilingual-MiniLM-L12-v2`)
- [x] 2.4 Implementar indexação dos documentos no ChromaDB com embeddings vetoriais

## 3. Fluxo de Agentes (LangGraph)

- [x] 3.1 Definir `AgentState` com campos `pergunta`, `contexto_encontrado` e `resposta_final`
- [x] 3.2 Implementar nó `bibliotecario` (busca semântica no ChromaDB)
- [x] 3.3 Implementar nó `atendente` (geração de resposta via LLM Minimax-M3 com Regra de Ouro)
- [x] 3.4 Construir o grafo `StateGraph` com fluxo START → bibliotecario → atendente → END
- [x] 3.5 Expor função `processar_ticket()` para consumo pela API

## 4. API FastAPI

- [x] 4.1 Criar `main.py` com instância FastAPI e modelos Pydantic (`TicketRequest`, `TicketResponse`)
- [x] 4.2 Implementar endpoint `GET /` (health check)
- [x] 4.3 Implementar endpoint `POST /api/v1/tickets/process` que recebe chamado e retorna resposta da IA
