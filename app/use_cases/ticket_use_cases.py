from typing import Dict, Any
from app.domain.interfaces.agent_service import AgentService

class ProcessTicketUseCase:
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service

    async def execute(self, ticket_id: str, texto_do_ticket: str) -> Dict[str, Any]:
        """
        Executa a regra de negócio para processar um ticket usando o motor de IA injetado.
        """
        if not ticket_id or not texto_do_ticket:
            raise ValueError("O ID do ticket e o texto não podem estar vazios.")
            
        resposta_final = await self.agent_service.processar_ticket(ticket_id, texto_do_ticket)
        
        return {
            "ticket_id": ticket_id,
            "status": "RESPONDIDO_PELA_IA",
            "resposta_ia": resposta_final
        }
