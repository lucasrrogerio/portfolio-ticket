## 1. Configuração de Logs e Estado

- [x] 1.1 Configurar o módulo `logging` no arquivo `graph_agent.py`
- [x] 1.2 Atualizar o `AgentState` no `graph_agent.py` para incluir o campo `ticket_id: str`

## 2. Injeção do Correlation ID nos Nós

- [x] 2.1 Adicionar logs de entrada e saída no nó `no_analisar_intencao`, lendo o `ticket_id` do estado
- [x] 2.2 Adicionar logs de entrada e saída no nó `no_buscar_documentos`, incluindo a quantidade de resultados trazidos se aplicável
- [x] 2.3 Adicionar logs de entrada e saída no nó `no_gerar_resposta`, marcando o fim do fluxo

## 3. Adaptação da API e Teste

- [x] 3.1 Atualizar a função `processar_ticket` no `graph_agent.py` para receber o `ticket_id` e repassá-lo para o `estado_inicial`
- [x] 3.2 Atualizar o endpoint em `main.py` para enviar o `request.ticket_id` na chamada de `processar_ticket`
- [x] 3.3 Testar a aplicação localmente acompanhando os logs via terminal
