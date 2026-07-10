import asyncio
import os
import logging
import json

from agentscope.agent import Agent
from agentscope.message import UserMsg, AssistantMsg, SystemMsg
from agentscope.model import OpenAIChatModel
from agentscope.credential import OpenAICredential

from app.services.rag_service import busca_hibrida
from app.agents.prompts import ANALISTA_PROMPT, ATENDENTE_SYSTEM_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ==========================================
# 1. Configurações Iniciais e Carregamento
# ==========================================

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "SUA_CHAVE_AQUI")
MINIMAX_BASE_URL = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.io/v1")

# No AgentScope 2.0, os modelos e credenciais são instanciados e passados diretamente.
# Como o Minimax é compatível com OpenAI, usamos a abstração do OpenAI.
model = OpenAIChatModel(
    credential=OpenAICredential(
        api_key=MINIMAX_API_KEY,
        base_url=MINIMAX_BASE_URL,
    ),
    model="Minimax-M2.7",
)

def extract_text(content):
    """Extrai o texto do conteúdo da mensagem do AgentScope 2.0 (lista de blocos ou string)."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list) and len(content) > 0:
        return content[0].text
    return str(content)

# ==========================================
# 2. Definição dos Agentes (AgentScope 2.0)
# ==========================================

class AnalistaAgent(Agent):
    """Agente responsável por extrair a intenção e palavras-chave da pergunta."""
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
        
        # Chama a resposta padrão do agente (que usa o system_prompt acima + prompt_msg)
        response = await super().reply(prompt_msg)
        
        logger.info(f"[Nó: {self.name}] Pergunta otimizada gerada com sucesso.")
        
        # Repassamos o conteúdo customizado para o próximo agente (como JSON string, pois content deve ser texto/blocos)
        content_dict = {
            "pergunta_original": pergunta,
            "resultado_analise": extract_text(response.content)
        }
        return AssistantMsg(name=self.name, content=json.dumps(content_dict))


class BibliotecarioAgent(Agent):
    """Agente responsável por buscar documentos no banco de dados vetorial e BM25."""
    def __init__(self, name: str, model: OpenAIChatModel):
        super().__init__(
            name=name,
            system_prompt="Você busca documentos.",
            model=model
        )

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
        
        contexto = busca_hibrida(intencao, keyword, n_results=3)
        logger.info(f"[Nó: {self.name}] Documentos recuperados com sucesso (Híbrida).")
        
        content_dict = {
            "pergunta_original": pergunta_original,
            "contexto": contexto
        }
        return AssistantMsg(name=self.name, content=json.dumps(content_dict))


class AtendenteAgent(Agent):
    """Agente responsável por gerar a resposta final com base no contexto."""
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
        # O Agente vai gerar a resposta final baseada no contexto do sistema
        response = await super().reply(prompt_msg)
        
        logger.info(f"[Nó: {self.name}] Resposta gerada. Fim do fluxo.")
        return response


# ==========================================
# 3. Instanciação e Função Principal
# ==========================================

analista = AnalistaAgent(name="Analista", model=model)
bibliotecario = BibliotecarioAgent(name="Bibliotecario", model=model)
atendente = AtendenteAgent(name="Atendente", model=model)

async def processar_ticket(ticket_id: str, texto_do_ticket: str) -> str:
    """
    Processa um ticket utilizando a nova arquitetura do AgentScope 2.0 de forma assíncrona.
    """
    logger.info(f"[Ticket: {ticket_id}] Iniciando processamento do ticket.")
    
    # Em AgentScope 2.0 as mensagens iniciais usam UserMsg
    msg_inicial = UserMsg(name="user", content=texto_do_ticket)
    
    # As execuções são assíncronas (await)
    msg_analise = await analista.reply(msg_inicial)
    msg_contexto = await bibliotecario.reply(msg_analise)
    msg_resposta = await atendente.reply(msg_contexto)
    
    logger.info(f"[Ticket: {ticket_id}] Processamento concluído.")
    
    # O conteúdo da última mensagem é a resposta final do Atendente
    return extract_text(msg_resposta.content)

# ==========================================
# Exemplo de execução direta (opcional)
# ==========================================
if __name__ == "__main__":
    async def main():
        resultado = await processar_ticket("TICKET-123", "Quais as vantagens de ser enterprise?")
        print("\n[Resposta Final]\n", resultado)
    
    asyncio.run(main())
