## 1. Setup

- [x] 1.1 Atualizar `requirements.txt` adicionando a dependência `python-multipart`

## 2. Refatoração (rag_service.py)

- [x] 2.1 Criar o arquivo `rag_service.py`
- [x] 2.2 Mover a inicialização do `ChromaDB` (PersistentClient) e `SentenceTransformer` para o `rag_service.py`
- [x] 2.3 Implementar a função `buscar_documentos_similares` no `rag_service.py`
- [x] 2.4 Atualizar `graph_agent.py` para usar a função de busca do novo serviço, removendo a lógica de banco de dados interna ao grafo

## 3. Endpoints de Gerenciamento de Documentos

- [x] 3.1 Implementar a função `adicionar_documento(doc_id, texto)` no `rag_service.py`
- [x] 3.2 Implementar a função `remover_documento(doc_id)` no `rag_service.py`
- [x] 3.3 Implementar a função `listar_documentos()` no `rag_service.py`
- [x] 3.4 Criar endpoint `POST /api/v1/documents` em `main.py` para receber um `UploadFile`, ler o conteúdo e enviá-lo ao `rag_service` usando o nome do arquivo como ID
- [x] 3.5 Criar endpoint `GET /api/v1/documents` em `main.py`
- [x] 3.6 Criar endpoint `DELETE /api/v1/documents/{doc_id}` em `main.py`
