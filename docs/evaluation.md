# Plano de Avaliação de RAG (RAG Evaluation)

Este documento descreve a metodologia para quantificar matematicamente o desempenho do sistema de IA (RAG) atual em comparação com novas abordagens arquiteturais (como a adição de um Nó de Roteamento/Intenção no LangGraph).

## 1. Construção do Dataset de Teste (Ground Truth)
Para termos uma linha de base, é necessário criar um arquivo (ex: `dataset_teste.json`) com 30 a 50 perguntas reais ou simuladas de clientes, mapeadas para a resposta ou documento esperado.

**Exemplo de estrutura do Dataset:**
```json
[
  {
    "pergunta": "fatura veio alta esse mes me ajuda",
    "dificuldade": "dificil",
    "documento_esperado": "politica_reembolso.md",
    "tipo_de_erro_comum": "falta de contexto semântico"
  },
  {
    "pergunta": "quais as vantagens do plano enterprise?",
    "dificuldade": "media",
    "documento_esperado": "limites_api.md",
    "tipo_de_erro_comum": "diluição de palavra-chave"
  }
]
```

## 2. Métricas de Avaliação

O teste deve medir três dimensões principais em cada execução:

### A. Recuperação (Retrieval)
Mede a capacidade do ChromaDB de achar o texto certo ANTES de mandar para a LLM.
- **Hit Rate (Taxa de Acerto):** O documento correto (`documento_esperado`) apareceu no top K (`n_results=3`)?
- **MRR (Mean Reciprocal Rank):** Avalia a posição do documento correto. Se ele foi o 1º da lista, nota 1. Se foi o 2º, nota 0.5. Se foi o 3º, nota 0.33.

### B. Geração (Generation)
Usando frameworks como **Ragas** ou **LangSmith**, uma LLM atuará como "juíza" para dar notas de 0 a 1 para as respostas geradas:
- **Fidelidade (Faithfulness):** A resposta gerada é baseada APENAS nos documentos encontrados ou a IA "alucinou"?
- **Relevância da Resposta (Answer Relevance):** A resposta respondeu diretamente à pergunta do usuário?

### C. Eficiência e Custo
- **Latência (Tempo de Resposta):** Tempo total (em segundos) desde o recebimento do JSON até o envio da resposta.
- **Consumo de Tokens:** Custo estimado de tokens de entrada e saída por requisição.

## 3. Estrutura do Teste A/B Offline

O fluxo do script de teste (`test_rag_pipeline.py`) deve seguir estes passos:

1. Carregar o `dataset_teste.json`.
2. Para cada pergunta no dataset:
   - Executar na **Abordagem A** (Pipeline Atual - RAG Simples).
   - Executar na **Abordagem B** (Pipeline Novo - Agentic RAG com Nó de Intenção).
3. Coletar os documentos recuperados, a resposta gerada, o tempo e os tokens de cada execução.
4. Calcular o Hit Rate e MRR comparando os documentos retornados com os documentos esperados.
5. Rodar a avaliação da LLM Juíza (Ragas) sobre as respostas geradas.
6. Exportar os resultados consolidados (tabela CSV/Markdown).

## 4. Critério de Decisão

A decisão de promover a nova arquitetura para produção deve basear-se na seguinte matriz:

- Se a **Abordagem B** aumentar o *Hit Rate* e a *Relevância* significativamente (ex: > 15%), o custo extra de tokens geralmente **vale a pena**, pois reduz o transbordo para o atendimento humano (que é exponencialmente mais caro).
- A **Latência** só será um impeditivo se a Abordagem B violar um possível SLA de resposta (ex: se o sistema deve responder em menos de 5 segundos e a nova abordagem está levando 10 segundos). Em canais assíncronos (ex: tickets, e-mail), a precisão é muito mais valiosa do que a latência.
