## ADDED Requirements

### Requirement: Indexação de documentos via embeddings
O sistema SHALL converter documentos de texto em vetores numéricos usando um modelo de embeddings multilíngue e armazená-los num banco vetorial persistente (ChromaDB).

#### Scenario: Indexação de documento de política
- **WHEN** um documento Markdown de política é processado pelo pipeline de ingestão
- **THEN** o sistema gera um embedding vetorial e armazena o documento com seu vetor e metadados no ChromaDB

### Requirement: Busca semântica por similaridade
O sistema SHALL encontrar o documento mais relevante para uma query de texto livre usando busca por similaridade vetorial, sem depender de correspondência exata de palavras-chave.

#### Scenario: Busca com linguagem informal
- **WHEN** o usuário escreve "quero meu dinheiro de volta"
- **THEN** o sistema retorna o documento sobre "Política de Reembolso e Cancelamento" (semanticamente similar), mesmo sem compartilhar palavras-chave

#### Scenario: Busca sem resultados relevantes
- **WHEN** a query não tem correspondência semântica com nenhum documento indexado
- **THEN** o sistema retorna "Sem resultados."

### Requirement: Persistência do banco vetorial
O sistema SHALL persistir os dados do ChromaDB em disco, garantindo que os documentos indexados sobrevivam a reinicializações do serviço.

#### Scenario: Reinicialização do serviço
- **WHEN** o serviço é reiniciado
- **THEN** os documentos previamente indexados continuam disponíveis para busca (diretório `meu_banco_vetorial/`)
