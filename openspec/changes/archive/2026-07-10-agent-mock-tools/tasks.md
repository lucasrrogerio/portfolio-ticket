## 1. Criação do Módulo de Ferramentas (Tools)

- [x] 1.1 Criar arquivo `tools.py` na raiz do projeto
- [x] 1.2 Implementar a ferramenta `get_user_status(email)` simulando consulta ao AD/IAM com delay de 2.0s a 4.5s (`asyncio.sleep`)
- [x] 1.3 Implementar a ferramenta `unlock_account(email)` simulando reset de senha no IAM com delay de 3.5s a 6.0s
- [x] 1.4 Implementar a ferramenta `escalate_to_human(issue_summary, urgency)` simulando criação de ticket no ITSM com delay de 3.0s a 5.0s
- [x] 1.5 Implementar a ferramenta `get_billing_history(customer_id)` simulando consulta ao CRM com delay de 4.0s a 8.5s
- [x] 1.6 Implementar a ferramenta `process_refund(transaction_id, amount)` simulando estorno no CRM com delay de 6.0s a 12.0s

## 2. Adaptação do Agente LangGraph

- [x] 2.1 Modificar `graph_agent.py` para importar as funções do `tools.py` e criar uma lista `tools = [...]`
- [x] 2.2 Vincular as ferramentas à LLM usando `llm.bind_tools(tools)`
- [x] 2.3 Instanciar um `ToolNode` do `langgraph.prebuilt` passando a lista de `tools`
- [x] 2.4 Ajustar o fluxo (StateGraph) para incluir o `ToolNode` e criar uma transição condicional (routing) após o LLM avaliar se deve chamar uma ferramenta ou responder diretamente
- [x] 2.5 Atualizar o prompt do LLM no nó principal para explicar que ele possui ferramentas corporativas para resolver o ticket

## 3. Testes e Validação de Observabilidade

- [x] 3.1 Executar a aplicação e disparar um ticket de teste focado em TI (ex: "Desbloqueie minha conta") para validar se a ferramenta é invocada
- [x] 3.2 Conferir a duração total da resposta e verificar os rastreamentos (Traces) no Loki/Grafana Tempo para confirmar se o *waterfall* está capturando o delay simulado
