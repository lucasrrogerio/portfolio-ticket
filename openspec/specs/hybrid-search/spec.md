# Hybrid Search

## Purpose
Especificação do mecanismo de busca híbrida combinando busca lexical e busca semântica para recuperação de contexto no RAG.

## Requirements

### Requirement: Busca Híbrida de Documentos
O sistema SHALL executar duas buscas independentes no RAG (Semântica e Lexical) e combinar os resultados utilizando o algoritmo de pontuação Reciprocal Rank Fusion (RRF).

#### Scenario: Roteamento Híbrido com Sucesso
- **WHEN** o Analista extrai a intenção e a keyword (ex: "vantagens", "Enterprise")
- **THEN** o Bibliotecário deve executar a busca semântica para "vantagens" e a busca lexical para "Enterprise"
- **AND** os documentos recuperados devem ser re-ranqueados e limitados aos `n` melhores resultados conjuntos.
