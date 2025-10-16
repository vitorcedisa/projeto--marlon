import json
import logging
import os
from models.order import Order
from utils.response import success_response, error_response, get_path_parameter

# Configurar o logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Função Lambda para marcar um pedido como entregue.
    
    Parameters:
    - event: dict, dados recebidos pela Lambda (API Gateway)
    - context: objeto com informações sobre a execução
    
    Returns:
    - dict: resposta compatível com API Gateway
    """
    logger.info("Evento recebido para marcar como entregue: %s", json.dumps(event))
    
    try:
        # Extrair ID do pedido do path parameter
        order_id = get_path_parameter(event, 'id')
        
        if not order_id:
            return error_response("ID do pedido é obrigatório", 400)
        
        # Buscar o pedido no DynamoDB
        try:
            order = Order.get(order_id)
        except Order.DoesNotExist:
            return error_response("Pedido não encontrado", 404)
        
        # Atualizar status de entregue
        order.entregue = True
        order.save()
        
        logger.info(f"Pedido [{order.id}] marcado como entregue")
        
        return success_response({
            'mensagem': 'Pedido marcado como entregue',
            'pedido': order.to_dict()
        })
        
    except Exception as e:
        logger.error("Erro na execução da Lambda delivered: %s", str(e))
        return error_response("Erro interno ao atualizar status do pedido")