from pydantic import BaseModel
from typing import Optional

class TicketRequest(BaseModel):
    ticket_id: str
    texto: str
    motor: Optional[str] = "langgraph"

class TicketResponse(BaseModel):
    ticket_id: str
    status: str
    resposta_ia: str
    erro: Optional[str] = None
