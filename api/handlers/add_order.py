import json
import logging
import os
from models.order import Order
from utils.response import success_response, error_response, parse_body

# Configurar o logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Função Lambda para adicionar um novo pedido de farmácia.
    
    Parameters:
    - event: dict, dados recebidos pela Lambda (API Gateway)
    - context: objeto com informações sobre a execução
    
    Returns:
    - dict: resposta compatível com API Gateway
    """
    logger.info("Evento recebido para adicionar pedido: %s", json.dumps(event))
    
    try:
        # Extrair dados do corpo da requisição
        body = parse_body(event)
        
        # Validar dados obrigatórios
        medicamentos = body.get('medicamentos', [])
        cliente = body.get('cliente', '').strip()
        total = body.get('total', 0)
        
        if not medicamentos:
            return error_response("Lista de medicamentos é obrigatória", 400)
        
        if not cliente:
            return error_response("Nome do cliente é obrigatório", 400)
        
        if total <= 0:
            return error_response("Total deve ser maior que zero", 400)
        
        # Criar novo pedido
        novo_pedido = Order.create_order(
            medicamentos=medicamentos,
            cliente=cliente,
            total=total
        )
        
        logger.info(f"Pedido [{novo_pedido.id}] criado com sucesso para cliente {cliente}")
        
        return success_response({
            'mensagem': 'Pedido criado com sucesso',
            'pedido': novo_pedido.to_dict()
        })
        
    except Exception as e:
        logger.error("Erro na execução da Lambda add_order: %s", str(e))
        return error_response("Erro interno na criação do pedido")