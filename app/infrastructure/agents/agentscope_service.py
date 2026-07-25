import asyncio
import os
import logging
import json

from agentscope.agent import Agent
from agentscope.message import UserMsg, AssistantMsg, SystemMsg
from agentscope.model import OpenAIChatModel
from agentscope.credential import OpenAICredential

from app.infrastructure.agents.prompts import ANALISTA_PROMPT, ATENDENTE_SYSTEM_PROMPT
from app.domain.interfaces.rag_repository import RAGRepository
from app.domain.interfaces.agent_service import AgentService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def extract_text(content):
    if isinstance(content, str):
        return content
    elif isinstance(content, list) and len(content) > 0:
        return content[0].text
    return str(content)

class AnalistaAgent(Agent):
    def __init__(self, name: str, model: OpenAIChatModel):
        super().__init__(
            name=name,
            model=model,
            system_prompt=ANALISTA_PROMPT
        )

    async def reply(self, x: UserMsg | SystemMsg | AssistantMsg) -> AssistantMsg:
        pergunta = extract_text(x.content)
        logger.info(f"[Nó: {self.name}] Analisando intenção da pergunta.")
        prompt_msg = UserMsg(name="user", content=f"Pergunta original do cliente: {pergunta}\nJSON:")
        response = await super().reply(prompt_msg)
        logger.info(f"[Nó: {self.name}] Pergunta otimizada gerada com sucesso.")
        
        content_dict = {
            "pergunta_original": pergunta,
            "resultado_analise": extract_text(response.content)
        }
        return AssistantMsg(name=self.name, content=json.dumps(content_dict))


class BibliotecarioAgent(Agent):
    def __init__(self, name: str, model: OpenAIChatModel, rag_repository: RAGRepository):
        super().__init__(
            name=name,
            system_prompt="Você busca documentos.",
            model=model
        )
        self.rag_repository = rag_repository

    async def reply(self, x: AssistantMsg) -> AssistantMsg:
        logger.info(f"[Nó: {self.name}] Buscando documentos no banco vetorial e BM25.")
        
        json_str = extract_text(x.content)
        try:
            dados = json.loads(json_str)
        except Exception:
            dados = {}
            
        pergunta_original = dados.get("pergunta_original", "")
        pergunta_busca_str = dados.get("resultado_analise", "{}")
        
        intencao = pergunta_original
        keyword = ""
        try:
            dados_busca = json.loads(pergunta_busca_str)
            intencao = dados_busca.get("intencao", pergunta_original)
            keyword = dados_busca.get("keyword", "")
        except Exception as e:
            logger.warning(f"Erro ao dar parse no JSON do Analista: {e}. Usando texto puro.")
        
        contexto = self.rag_repository.busca_hibrida(intencao, keyword, n_results=3)
        logger.info(f"[Nó: {self.name}] Documentos recuperados com sucesso (Híbrida).")
        
        content_dict = {
            "pergunta_original": pergunta_original,
            "contexto": contexto
        }
        return AssistantMsg(name=self.name, content=json.dumps(content_dict))


class AtendenteAgent(Agent):
    def __init__(self, name: str, model: OpenAIChatModel):
        super().__init__(
            name=name,
            system_prompt="Você é um agente de suporte de nível 1.",
            model=model
        )

    async def reply(self, x: AssistantMsg) -> AssistantMsg:
        logger.info(f"[Nó: {self.name}] Gerando resposta final baseada no contexto.")
        
        json_str = extract_text(x.content)
        try:
            dados = json.loads(json_str)
        except Exception:
            dados = {}
            
        pergunta = dados.get("pergunta_original", "")
        contexto = dados.get("contexto", "")

        prompt = f"""{ATENDENTE_SYSTEM_PROMPT.format(contexto=contexto)}

[PERGUNTA DO CLIENTE]
{pergunta}"""
        prompt_msg = UserMsg(name="user", content=prompt)
        response = await super().reply(prompt_msg)
        
        logger.info(f"[Nó: {self.name}] Resposta gerada. Fim do fluxo.")
        return response


class AgentScopeAgentService(AgentService):
    def __init__(self, rag_repository: RAGRepository):
        self.rag_repository = rag_repository
        
        MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "SUA_CHAVE_AQUI")
        MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")

        self.model = OpenAIChatModel(
            credential=OpenAICredential(
                api_key=MINIMAX_API_KEY,
                base_url=MINIMAX_BASE_URL,
            ),
            model="Minimax-M2.7",
        )
        
        self.analista = AnalistaAgent(name="Analista", model=self.model)
        self.bibliotecario = BibliotecarioAgent(name="Bibliotecario", model=self.model, rag_repository=self.rag_repository)
        self.atendente = AtendenteAgent(name="Atendente", model=self.model)

    async def processar_ticket(self, ticket_id: str, texto_do_ticket: str) -> str:
        logger.info(f"[Ticket: {ticket_id}] Iniciando processamento do ticket (AgentScope).")
        
        msg_inicial = UserMsg(name="user", content=texto_do_ticket)
        
        msg_analise = await self.analista.reply(msg_inicial)
        msg_contexto = await self.bibliotecario.reply(msg_analise)
        msg_resposta = await self.atendente.reply(msg_contexto)
        
        logger.info(f"[Ticket: {ticket_id}] Processamento concluído.")
        return extract_text(msg_resposta.content)
