## Why

A base de conhecimento (RAG) estava sendo inicializada com documentos mockados localmente, sem uma maneira dinâmica de adicionar ou remover políticas no banco vetorial. Precisamos de uma interface para que o sistema maior (Spring Boot) possa gerenciar os documentos indexados. Além disso, a lógica de gerenciamento do banco vetorial estava misturada no grafo de agentes, violando a separação de responsabilidades.

## What Changes

- Extração de toda a lógica do ChromaDB e embeddings para um novo serviço isolado (`rag_service.py`)
- Adição do pacote `python-multipart` para suportar upload de arquivos na API
- Criação do endpoint `POST /api/v1/documents` para upload e indexação de novos arquivos Markdown
- Criação do endpoint `GET /api/v1/documents` para listar todos os documentos indexados
- Criação do endpoint `DELETE /api/v1/documents/{doc_id}` para remover documentos do banco vetorial

## Capabilities

### New Capabilities
- `document-management`: Endpoints HTTP para listar, adicionar e remover documentos da base de conhecimento (RAG) dinamicamente via API.

### Modified Capabilities
_(nenhuma — o `ticket-processing` e o `rag-pipeline` mantêm seus requisitos comportamentais, apenas a implementação do RAG foi refatorada)_

## Impact

- **Novos arquivos**: `rag_service.py`
- **Arquivos modificados**: `main.py`, `graph_agent.py`, `requirements.txt`
- **Dependências**: Adição de `python-multipart`
- **APIs expostas**: Novos endpoints de gerenciamento em `/api/v1/documents`
