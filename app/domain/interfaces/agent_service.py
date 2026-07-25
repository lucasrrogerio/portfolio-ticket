from typing import Protocol

class AgentService(Protocol):
    async def processar_ticket(self, ticket_id: str, texto_do_ticket: str) -> str:
        """Processa um ticket e retorna a resposta da IA."""
        ...
