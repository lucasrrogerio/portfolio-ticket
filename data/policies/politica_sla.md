# Acordo de Nível de Serviço (SLA) e Estabilidade

## 1. Promessa de Disponibilidade (Uptime)
Nós garantimos que os nossos serviços estarão disponíveis e operacionais por **99.9%** do tempo durante cada mês civil (Aproximadamente, permite cerca de 43 minutos de downtime por mês).

## 2. Manutenção Programada
- Manutenções de rotina, atualizações de infraestrutura e deploys sistêmicos ocorrem durante a nossa "Janela de Manutenção".
- **Horário:** Todos os domingos, entre **02h00 e 04h00 da manhã (Horário Padrão de Brasília - BRT)**.
- Qualquer indisponibilidade durante esta janela **NÃO** é contabilizada como violação de SLA.

## 3. Quedas Não Programadas (Downtime)
Qualquer instabilidade crítica (quando o sistema fica totalmente inacessível) fora da janela de manutenção conta como downtime.

### Regras de Compensação Financeira
A compensação só é aplicável mediante solicitação do cliente em até 10 dias após o incidente, seguindo as regras:
- Se o uptime do mês ficar **entre 99.0% e 99.8%**: O cliente recebe **10% de desconto** na fatura do mês seguinte (para planos mensais) ou um crédito equivalente (para anuais).
- Se o uptime for **inferior a 99.0%** (mais de 7 horas fora do ar no mês): O cliente recebe **25% de desconto** na fatura do mês seguinte.
- *Nota:* Contas gratuitas ou em período de testes (trial) não são elegíveis para créditos de compensação por SLA.

## 4. Escalada de Incidentes (War Room)
Se um cliente relatar que o "sistema está totalmente fora do ar", o agente de atendimento (IA ou Humano) deve primeiramente checar o painel de *Status Page* público.
- Se houver indisponibilidade confirmada: Informar o cliente que estamos cientes e trabalhando na solução.
- Se a Status Page estiver verde, mas o cliente provar que está fora do ar para ele (e outros começarem a relatar o mesmo), o chamado deve ser encaminhado com urgência (Tag: `CRÍTICO`) para a equipe de **Engenharia de Confiabilidade (SRE)**.
