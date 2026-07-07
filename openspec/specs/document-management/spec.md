# Document Management

## Purpose
TBD

## Requirements

### Requirement: Upload e indexação de documentos
O sistema SHALL fornecer um endpoint para receber arquivos Markdown (`.md`) via requisição multipart e indexá-los no banco vetorial.

#### Scenario: Upload bem-sucedido
- **WHEN** um cliente faz `POST /api/v1/documents` enviando um arquivo `.md` válido
- **THEN** o sistema salva o conteúdo do arquivo, gera seus embeddings, indexa no ChromaDB usando o nome do arquivo como ID e retorna status 200 com os metadados do documento indexado

### Requirement: Listagem de documentos
O sistema SHALL fornecer um endpoint para listar todos os documentos atualmente indexados na base de conhecimento.

#### Scenario: Listagem de documentos indexados
- **WHEN** um cliente faz `GET /api/v1/documents`
- **THEN** o sistema retorna status 200 com uma lista de nomes de arquivos correspondentes aos IDs dos documentos armazenados no ChromaDB

### Requirement: Remoção de documentos
O sistema SHALL fornecer um endpoint para remover um documento específico da base de conhecimento usando seu ID (nome do arquivo).

#### Scenario: Remoção bem-sucedida
- **WHEN** um cliente faz `DELETE /api/v1/documents/{doc_id}` com um ID existente
- **THEN** o sistema remove o documento correspondente do ChromaDB e retorna status 200 confirmando a deleção

#### Scenario: Tentativa de remoção de documento inexistente
- **WHEN** um cliente faz `DELETE /api/v1/documents/{doc_id}` com um ID que não existe na base
- **THEN** o sistema não altera o estado do banco e retorna uma mensagem adequada (ex: informando que não encontrou ou apenas confirmando a deleção idempotente)
