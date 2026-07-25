import asyncio
import random
import logging
from langchain_core.tools import tool
from app.core.observability import instrument_tool, set_span_attribute

logger = logging.getLogger(__name__)

@tool
@instrument_tool
async def get_user_status(email: str) -> dict:
    """Verifica o status da conta do usuário no Active Directory / Okta. 
    Retorna o status atual (ex: LOCKED, ACTIVE) e informações do último login.
    """
    delay = random.uniform(2.0, 4.5)
    set_span_attribute("tool.delay", delay)
    logger.info(f"[Tool] Iniciando get_user_status para {email} com delay de {delay:.2f}s...")
    await asyncio.sleep(delay)
    
    # Simula que a conta está bloqueada se for para resetar senha / acesso
    status = "LOCKED"
    logger.info(f"[Tool] Finalizado get_user_status para {email}: {status}")
    return {
        "email": email,
        "status": status,
        "last_login": "2026-07-10T08:30:00-03:00"
    }

@tool
@instrument_tool
async def unlock_account(email: str) -> dict:
    """Desbloqueia a conta do usuário no Active Directory / Okta e gera uma senha temporária."""
    delay = random.uniform(3.5, 6.0)
    set_span_attribute("tool.delay", delay)
    logger.info(f"[Tool] Iniciando unlock_account para {email} com delay de {delay:.2f}s...")
    await asyncio.sleep(delay)
    
    temp_pwd = f"Temp@{random.randint(1000, 9999)}!"
    logger.info(f"[Tool] Finalizado unlock_account para {email}. Nova senha temporária gerada.")
    return {
        "email": email,
        "status": "ACTIVE",
        "message": "Conta desbloqueada com sucesso.",
        "temp_password": temp_pwd
    }

@tool
@instrument_tool
async def escalate_to_human(issue_summary: str, urgency: str) -> dict:
    """Escala o problema para um atendente humano abrindo um ticket de Nível 2 no Jira / ServiceNow.
    Parâmetros:
      - issue_summary: Resumo do problema
      - urgency: Nível de urgência ('HIGH', 'MEDIUM', 'LOW')
    """
    delay = random.uniform(3.0, 5.0)
    set_span_attribute("tool.delay", delay)
    logger.info(f"[Tool] Iniciando escalate_to_human com delay de {delay:.2f}s...")
    await asyncio.sleep(delay)
    
    ticket_id = f"ITSM-{random.randint(10000, 99999)}"
    logger.info(f"[Tool] Finalizado escalate_to_human. Ticket {ticket_id} criado no ServiceNow.")
    return {
        "ticket_id": ticket_id,
        "status": "OPENED",
        "assigned_team": "L2_Support",
        "message": f"Chamado escalado com sucesso. ID do ticket: {ticket_id}."
    }

@tool
@instrument_tool
async def get_billing_history(customer_id: str) -> dict:
    """Consulta o histórico de faturamento e últimas faturas do cliente no CRM / Stripe."""
    delay = random.uniform(4.0, 8.5)
    set_span_attribute("tool.delay", delay)
    logger.info(f"[Tool] Iniciando get_billing_history para {customer_id} com delay de {delay:.2f}s...")
    await asyncio.sleep(delay)
    
    logger.info(f"[Tool] Finalizado get_billing_history para {customer_id}.")
    return {
        "customer_id": customer_id,
        "invoices": [
            {
                "invoice_id": "INV-2026-001",
                "amount": 99.90,
                "status": "PAID",
                "date": "2026-06-01",
                "transaction_id": "TX_A123"
            },
            {
                "invoice_id": "INV-2026-002",
                "amount": 99.90,
                "status": "PAID",
                "date": "2026-07-01",
                "transaction_id": "TX_B456" # Transação duplicada de teste
            }
        ]
    }

@tool
@instrument_tool
async def process_refund(transaction_id: str, amount: float) -> dict:
    """Processa o estorno/reembolso de uma transação duplicada ou cobrada indevidamente no Stripe."""
    delay = random.uniform(6.0, 12.0)
    set_span_attribute("tool.delay", delay)
    logger.info(f"[Tool] Iniciando process_refund para {transaction_id} no valor de R$ {amount} com delay de {delay:.2f}s...")
    await asyncio.sleep(delay)
    
    logger.info(f"[Tool] Finalizado process_refund para {transaction_id}.")
    return {
        "transaction_id": transaction_id,
        "amount_refunded": amount,
        "status": "REFUNDED",
        "message": "Reembolso processado com sucesso no gateway de pagamento."
    }
