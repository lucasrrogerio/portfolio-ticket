# 🏗 Decisões de Arquitetura

Este documento descreve as decisões técnicas do projeto,  trade-offs e alternativas consideradas.

---

## 📋 Índice

- [Por que IA e não regras determinísticas?](#-por-que-ia-e-não-regras-determinísticas)
- [Por que não usar só a busca vetorial, sem a LLM?](#-por-que-não-usar-só-a-busca-vetorial-sem-a-llm)
- [Por que usar busca híbrida (Vetorial + BM25)?](#-por-que-busca-híbrida-vetorial--bm25)
- [Trade-offs assumidos](#️-trade-offs-assumidos)
- [Visão geral da arquitetura](#-visão-geral-da-arquitetura)
- [Fluxo do LangGraph](#fluxo-do-langgraph)
- [Stack tecnológica e justificativas](#-stack-tecnológica-e-justificativas)
- [Separação de responsabilidades](#-separação-de-responsabilidades)

---

## 🤔 Por que IA e não regras determinísticas?


### Alternativas determinísticas e seus limites

| Abordagem | Como funciona | Onde falha |
|---|---|---|
| **Keyword matching** | Busca por palavras-chave ("reembolso", "senha", "SLA") e retorna a resposta mapeada. | Sinônimos, erros de digitação e linguagem informal quebram o sistema. Ex: O cliente escreve "quero meu dinheiro de volta" e nenhuma keyword bate. |
| **Árvore de decisão / Fluxo fixo** | Chatbot com menus ("Selecione: 1-Financeiro, 2-Técnico, 3-Outro"). | Funciona para fluxos simples, mas não lida com texto livre. Quando o cliente não acha a opção desejada, o fluxo trava. |
| **Regex + NLP clássico** | Classificadores treinados (ex: Naive Bayes, SVM) para categorizar o ticket e retornar templates. | Exige dataset de treinamento rotulado, retreino constante quando surgem novos tipos de chamado, e as respostas são templates rígidos que não se adaptam ao tom/contexto do cliente. |

### Onde a IA generativa + RAG se justifica

A combinação de **busca vetorial (RAG)** + **LLM** resolve os pontos fracos acima:

- **Busca semântica**: "quero meu dinheiro de volta" é matematicamente similar a "política de reembolso" no espaço vetorial, eliminando a fragilidade do keyword matching.
- **Resposta contextualizada**: A LLM não devolve um template fixo. Ela formula uma resposta natural, adaptada ao tom e aos detalhes específicos da pergunta do cliente.
- **Zero retreino**: Novos documentos de política são adicionados via upload (endpoint POST). Não é necessário retreinar nenhum modelo, basta indexar o novo `.md`.

---

## 🔍 Por que não usar só a busca vetorial, sem a LLM?

A busca semântica por si só **já resolve o problema de encontrar a informação certa**. O cliente pergunta *"minha conta travou"* e o ChromaDB retorna o documento sobre bloqueio de conta — sem precisar de keyword matching exato. Então por que adicionar o custo de uma LLM no topo?

**Exemplo concreto — só busca vetorial:**
> Pergunta: *"Errei a senha várias vezes e minha conta travou, preciso acessar URGENTE pra uma reunião!"*
>
> Resposta (trecho cru do documento): *"A conta é bloqueada automaticamente após 5 tentativas incorretas de login. O desbloqueio ocorre automaticamente após 30 minutos."*

Funciona. O cliente recebe a informação correta, com custo zero de LLM e resposta determinística.

**Mesmo cenário — busca vetorial + LLM:**
> Resposta reformulada: *"Entendo a urgência! Sua conta foi bloqueada por segurança após as tentativas incorretas. Ela será desbloqueada automaticamente em 30 minutos. Enquanto isso, recomendo redefinir sua senha clicando em 'Esqueci minha senha' na tela de login assim que desbloquear."*

Mas a LLM neste projeto vai **muito além de apenas reescrever textos**. O verdadeiro motivo de não usarmos apenas uma busca vetorial é a capacidade de criar um **Agente Autônomo**.

Ao acoplar a LLM a ferramentas e integrações externas (através de Tool Calling ou padrões como o MCP - Model Context Protocol), transformamos um sistema estático de *Perguntas e Respostas* em um sistema ativo de *Resolução de Problemas*:

1. **Compreensão de Intenção e Contexto:** A LLM consegue ler o histórico do ticket, entender o tom do usuário e deduzir se a situação exige ação imediata ou escalonamento, coisa que a busca vetorial sozinha jamais faria.
2. **Execução Ativa:** O agente não precisa apenas responder "você precisa acessar o sistema e redefinir a senha". Tendo acesso às ferramentas certas, a IA entende a política via RAG, bate na API do sistema para verificar o status do usuário e, de forma autônoma, toma a ação de disparar o e-mail de redefinição **sem nenhuma intervenção humana**.
3. **Autonomia de Fluxo:** Diferente de um chatbot engessado, a LLM atua orquestrando o fluxo: "Primeiro consulto as políticas da empresa. Depois chamo a API de billing. Se a fatura estiver atrasada de fato, executo a ação de estorno e aviso o cliente".

Em resumo: A busca híbrida e o RAG são **a memória** do sistema. O LangGraph e a LLM formam **o cérebro e as mãos**, garantindo uma automação inteligente e resolução ponta a ponta para o cliente.

---

## 🔀 Por que Busca Híbrida (Vetorial + BM25)?

A busca semântica (vetorial) é excelente para entender o contexto. Se o usuário digitar "quero cancelar", ela encontra o documento de "reembolso". Porém, **ela falha em buscas exatas**.

Se um usuário digita o jargão *"vantagens do plano Enterprise"* ou *"Erro XPT-99"*, a busca semântica pode diluir o peso dessas palavras raras e focar apenas no conceito geral da frase, trazendo documentos incorretos. 

Para resolver esse gap (muito comum em RAGs de produção), adotamos a **Busca Híbrida**:
- **Busca Semântica:** Para entender sinônimos e intenções.
- **Busca Lexical (BM25):** Para "cravar" palavras-chave exatas e raras.
- **RRF (Reciprocal Rank Fusion):** Um algoritmo que funde os rankings das duas buscas para garantir que o melhor documento de ambos os mundos suba para o topo.

---

## ⚖️ Trade-offs assumidos

> Nenhuma decisão técnica é de graça. Aqui estão os custos conscientes:

- **Latência**: Uma chamada à LLM leva ~1-3s. Para triagem assíncrona (o cliente não espera em tempo real), isso é aceitável. Para chat ao vivo, precisaria de cache ou streaming.
- **Custo por chamada**: Cada ticket consome tokens da API. Em volume alto, isso precisa ser monitorado. A escolha do modelo Minimax-M3 foi intencional — é significativamente mais barato que GPT-4 para tarefas de suporte.
- **Não-determinismo**: A mesma pergunta pode gerar respostas ligeiramente diferentes. A "Regra de Ouro" no prompt (responder apenas com base no contexto) mitiga isso, mas não elimina 100%. Por isso, a arquitetura prevê revisão humana antes do envio.

**Resumo**: Para um cenário com texto livre do cliente, base de conhecimento que muda com frequência e necessidade de respostas naturais (não templates), IA + RAG é a escolha correta. Se os chamados fossem categorizados via formulário com campos fixos, um sistema de regras seria mais barato e mais previsível.

---

## 🗺 Visão geral da arquitetura

```
┌─────────────────┐       HTTP        ┌──────────────────────────────┐
│  Spring Boot    │ ──────────────▶   │  FastAPI (este serviço)      │
│  (Backend)      │  POST /tickets    │                              │
└─────────────────┘                   │  main.py (API)               │
                                      │    ├── graph_agent.py        │
                                      │    │    └── LangGraph         │
                                      │    │         ├─ Analista      │ ─▶ Otimiza Intenção
                                      │    │         ├─ Bibliotecário │ ─▶ ChromaDB + BM25
                                      │    │         ├─ Atendente     │ ─▶ LLM (Minimax)
                                      │    │         └─ Tools         │ ─▶ APIs / Mocks
                                      │    └── rag_service.py        │
                                      │         └── ChromaDB + Embeddings
                                      └──────────────────────────────┘
```

### Fluxo do LangGraph (Orquestração de Agentes)

O fluxo reflete uma arquitetura real de **Agente Autônomo** com tomada de decisão (Tool Calling) e rotas condicionais:

```text
[START] ──▶ [Analista] ──▶ [Bibliotecário] ──▶ [Atendente] ──(Fim)──▶ [END]
                 │                │                 │  ▲
                 ▼                ▼                 ▼  │
             Otimiza a      Busca Híbrida     Decide se usa
             pergunta       (Chroma + BM25)   ferramentas
                                                    │  │
                                            (Usa)   ▼  │ (Retorna Resultado)
                                                 [Tools]
```

**Como o ciclo funciona:**
1. **Analista:** Recebe o texto livre do cliente, analisa a intenção e extrai as palavras-chave vitais (gerando um JSON estruturado).
2. **Bibliotecário:** Usa esse JSON para realizar a Busca Híbrida e resgatar as políticas corretas do banco vetorial e do índice.
3. **Atendente (O Cérebro):** Recebe a política e a pergunta. Aqui acontece a mágica do *Tool Calling*. Se a política exigir uma ação no sistema (ex: "destravar conta"), o Atendente decide interromper a resposta e chamar a ferramenta correspondente.
4. **Tools Node (Ação):** Um nó condicional. Se o Atendente pedir o uso de ferramentas, o grafo desvia para este nó, executa a função Python (API mockada em `tools.py`) e devolve o resultado para a LLM. O ciclo se repete até o Atendente dar a resposta final e seguir para o `END`.

Essa estrutura com loop condicional prova que não estamos apenas gerando texto, mas criando um fluxo de raciocínio lógico e execução ativa (baseado no padrão `ReAct`), totalmente orquestrado pelo LangGraph.

---

## 🛠 Stack tecnológica e justificativas

| Tecnologia | Papel | Por que essa e não outra? |
|---|---|---|
| **FastAPI** | API REST | Async nativo, documentação automática (Swagger), validação via Pydantic. Ideal para microsserviços Python. |
| **LangGraph / AgentScope** | Orquestração de agentes | Iniciei com o LangGraph pois ele modela o fluxo como um grafo de estados, facilitando integrações. Porém, também estruturei testes com o **AgentScope** por ser um framework muito promissor para orquestração de múltiplos agentes com maior autonomia. Manter os dois no radar (e no código) demonstra versatilidade e pensamento em escalabilidade futura. |
| **ChromaDB + BM25** | Banco e Busca | ChromaDB para persistência e vetores locais (ideal para portfólio), complementado com algoritmo BM25 em memória para viabilizar a arquitetura de **Busca Híbrida**. |
| **SentenceTransformers** | Geração de embeddings | Modelo multilíngue (`paraphrase-multilingual-MiniLM-L12-v2`) que roda localmente, sem custo por chamada. Essencial para suporte em português. |
| **Minimax-M3 (via OpenAI SDK)** | LLM para geração de texto | Compatível com o SDK da OpenAI (troca de provider sem alterar código), custo acessível, e desempenho adequado para tarefas de suporte N1. |

---

## 📐 Separação de responsabilidades

```
Portfolio-Ticket/
├── main.py            → Camada HTTP (entrada/saída)
├── graph_agent.py     → Orquestração (fluxo dos agentes)
└── rag_service.py     → Dados (ChromaDB + embeddings)
```

- **`main.py`** — Camada HTTP. Não contém lógica de negócio; apenas recebe requests, chama os serviços e devolve responses.
- **`graph_agent.py`** — Orquestração. Define *como* os agentes interagem (ordem, fluxo, estado). Não sabe como o banco vetorial funciona internamente.
- **`rag_service.py`** — Dados. Encapsula toda interação com o ChromaDB e o modelo de embeddings. Pode ser substituído por outro provider (ex: Pinecone) sem afetar o restante.

Essa separação garante que cada módulo pode evoluir de forma independente. Trocar o ChromaDB por Pinecone? Só muda `rag_service.py`. Adicionar um novo nó de classificação no fluxo? Só muda `graph_agent.py`. Expor um novo endpoint? Só muda `main.py`.
