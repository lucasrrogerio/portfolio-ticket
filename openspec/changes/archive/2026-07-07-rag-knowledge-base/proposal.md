## Why

O suporte de nível 1 gasta a maior parte do tempo em trabalho mecânico: ler o chamado, buscar a resposta na documentação interna e reformular para o cliente. Isso é repetitivo, lento e inconsistente entre atendentes.

Este change implementa a base do sistema de triagem inteligente: um microsserviço que recebe chamados em texto livre, busca contexto relevante numa base de conhecimento via busca semântica (RAG) e usa uma LLM para formular respostas naturais — eliminando keyword matching frágil e templates rígidos.

## What Changes

- Criação de um banco vetorial (ChromaDB) com documentos de política da empresa (reembolso, acesso, SLA)
- Implementação de um modelo de embeddings multilíngue local (SentenceTransformers) para busca semântica em português
- Construção de um fluxo de agentes com LangGraph (Bibliotecário → Atendente) para orquestrar busca e geração de resposta
- Exposição via API FastAPI com endpoint de processamento de tickets (`POST /api/v1/tickets/process`)
- Integração com LLM Minimax-M3 via SDK compatível com OpenAI

## Capabilities

### New Capabilities
- `ticket-processing`: Recebimento de chamados em texto livre, busca semântica na base de conhecimento e geração de resposta contextualizada via LLM
- `rag-pipeline`: Pipeline de RAG com ChromaDB para indexação e busca vetorial de documentos de política da empresa

### Modified Capabilities

_(nenhuma — é o change inicial do projeto)_

## Impact

- **Novos arquivos**: `main.py`, `graph_agent.py`, `requirements.txt`, `data/policies/*.md`
- **Dependências**: FastAPI, LangGraph, ChromaDB, SentenceTransformers, langchain-openai
- **APIs expostas**: `POST /api/v1/tickets/process`, `GET /`
- **Infra**: Requer variável de ambiente `MINIMAX_API_KEY` para chamadas à LLM
