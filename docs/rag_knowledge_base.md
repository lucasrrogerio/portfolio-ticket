# Design da Base de Conhecimento (RAG)

Para que nosso **Agente Solucionador** consiga responder perguntas com precisão e não invente coisas (alucinação), precisamos alimentá-lo com dados reais da nossa empresa fictícia. 

Esta é a base do padrão **RAG (Retrieval-Augmented Generation)**.

## 1. O Fluxo de Ingestão de Dados

Antes mesmo do cliente abrir um chamado, precisamos ter a nossa base pronta. O fluxo para você implementar depois no Python será:

1. **Documentos Brutos:** Arquivos em Markdown (`.md`), PDF ou TXT contendo as regras da empresa.
2. **Document Loaders:** Usar o `TextLoader` ou `DirectoryLoader` do LangChain para ler esses arquivos.
3. **Text Splitter:** Quebrar o texto em pedaços menores (chunks) de, por exemplo, 500 tokens. Isso é necessário porque não podemos jogar a base inteira na LLM de uma vez.
4. **Embeddings:** Converter esses "chunks" de texto em vetores numéricos usando um modelo de embedding (ex: `text-embedding-3-small` da OpenAI ou um modelo open-source do HuggingFace).
5. **Vector Store:** Salvar esses vetores em um banco de dados vetorial. Para começar localmente, recomendo o **ChromaDB** ou **FAISS**, pois rodam em memória/arquivo local sem precisar de infraestrutura extra.

---

## 1.1 A Estratégia de Busca Híbrida (Hybrid Search)

A busca semântica tradicional (por vetores) entende sinônimos e contexto, o que é ótimo para a maioria das perguntas. Porém, ela **falha em encontrar palavras-chave específicas**, como siglas, IDs de erro, ou jargões corporativos (ex: "plano enterprise", "Erro XPT-99"). Nessas horas, o modelo vetorial pode "diluir" o peso da palavra exata no contexto geral da frase, trazendo documentos errados.

Para evitar alucinações nesses cenários críticos e trazer resultados de nível de produção, adotamos a **Busca Híbrida**:
- **Busca Semântica (ChromaDB + SentenceTransformers):** Transforma frases em vetores para procurar pelo *significado* geral da pergunta.
- **Busca Lexical (BM25):** Atua como um "Control+F Inteligente", focando em "Match Exato". Ele ignora palavras muito comuns e dá uma pontuação altíssima para documentos que contenham palavras-chave raras ou exatas solicitadas pelo usuário.

### Como unimos os resultados? (Reciprocal Rank Fusion - RRF)
Como a Busca Semântica e a Busca Lexical avaliam os textos de formas completamente diferentes, usamos o algoritmo **RRF** para combinar os dois mundos. 
O RRF não tenta cruzar as "notas" dos algoritmos; ele avalia apenas o **ranking (a posição)** em que cada documento ficou nas duas listas. Através de uma fórmula de fusão matemática, ele gera uma lista final unificada, jogando para o topo o documento perfeito que pontuou bem em ambas as estratégias.

---

## 2. Mock de Dados (Textos para a Base)

Aqui estão três exemplos de políticas que você pode salvar como arquivos `.txt` ou `.md` na sua máquina para alimentar o Vector Store depois. Vamos usar um cenário de uma **empresa de Software/SaaS**.

### Documento 1: Política de Reembolso e Cancelamento (`politica_reembolso.md`)
```markdown
# Política de Reembolso e Cancelamento
- **Prazo de Arrependimento:** Clientes novos têm o direito de solicitar reembolso integral em até 7 dias corridos após a primeira compra, sem necessidade de justificativa.
- **Assinaturas Anuais:** Cancelamentos de assinaturas anuais após os 7 dias iniciais não garantem reembolso do valor já pago. O serviço continuará ativo até o fim do ciclo vigente.
- **Processamento:** O estorno é realizado diretamente no cartão de crédito usado na compra e pode levar de 5 a 10 dias úteis para aparecer na fatura.
- **Como solicitar:** A solicitação de estorno dentro do prazo de 7 dias pode ser feita via painel de controle (Configurações > Faturamento > Cancelar Assinatura) ou abrindo um chamado de Suporte Financeiro.
```

### Documento 2: Problemas de Acesso e Senha (`acesso_conta.md`)
```markdown
# Problemas de Acesso à Conta
- **Esqueci minha senha:** O cliente pode redefinir a senha clicando em "Esqueci minha senha" na tela de login. Um link com validade de 15 minutos será enviado ao e-mail cadastrado.
- **Conta Bloqueada:** A conta é bloqueada automaticamente após 5 tentativas incorretas de login. O desbloqueio ocorre automaticamente após 30 minutos.
- **Autenticação em Dois Fatores (2FA):** Caso o cliente perca o acesso ao seu aplicativo de 2FA (como Google Authenticator), ele deverá usar os "Códigos de Recuperação" gerados no momento da ativação do 2FA. Se perdeu os códigos, o ticket deve ser escalado para a Equipe de Segurança e um analista humano precisará verificar a identidade via documento com foto.
```

### Documento 3: Política de Instabilidade (SLA) (`politica_sla.md`)
```markdown
# Política de Nível de Serviço (SLA)
- **Disponibilidade:** Garantimos 99.9% de uptime mensal.
- **Compensação por Queda:** Caso o sistema fique indisponível por mais de 4 horas seguidas, clientes do plano "Enterprise" têm direito a um desconto de 10% na próxima fatura.
- **Manutenção Programada:** Manutenções são realizadas aos domingos, entre 02h00 e 04h00 da manhã (horário de Brasília) e não contam como "downtime" ou quebra de SLA.
```

---

## 3. Como o Agente vai usar isso na prática?

Quando um cliente enviar o seguinte chamado:
> *"Tentei logar várias vezes com a senha antiga, errei tudo e minha conta foi bloqueada. Como faço pra voltar a usar agora? Preciso urgente!"*

1. O LangGraph recebe a mensagem e a passa para o **Retrieval QA**.
2. O banco vetorial é consultado e retorna o **Documento 2**.
3. A LLM recebe a pergunta original + o texto do Documento 2 e formula a resposta:
   > *"Sua conta foi bloqueada por segurança após as tentativas falhas. Ela será desbloqueada automaticamente em 30 minutos. Após esse período, você pode acessar a tela de login e clicar em 'Esqueci minha senha' para cadastrar uma nova."*
4. Como o nível de confiança dessa resposta será alto, o Agente de Decisão pode enviar a resposta ao cliente e marcar o ticket como `RESOLVIDO`.

## Próximo Passo Sugerido
O que acha desses dados fictícios? 
Se quiser, podemos brincar um pouco com a ideia de **Prompt Engineering**: escrever o *System Prompt* exato que esse Agente de RAG usará para saber como deve se comportar (tom de voz, regras de atendimento, etc).
