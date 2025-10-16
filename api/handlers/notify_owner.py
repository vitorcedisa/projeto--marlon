import json
import logging
import os
import boto3
from botocore.exceptions import ClientError

# Configurar o logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente SNS
sns_client = boto3.client('sns')

def lambda_handler(event, context):
    """
    Função Lambda event-driven para notificar o dono da farmácia sobre mudanças nos pedidos.
    Esta função é acionada pelo DynamoDB Stream.
    
    Parameters:
    - event: dict, dados do DynamoDB Stream
    - context: objeto com informações sobre a execução
    
    Returns:
    - None (função event-driven)
    """
    logger.info("Evento recebido do DynamoDB Stream: %s", json.dumps(event))
    
    try:
        # Processar cada record do stream
        for record in event.get('Records', []):
            process_record(record)
            
    except Exception as e:
        logger.error("Erro na execução da Lambda notify_owner: %s", str(e))
        raise e

def process_record(record):
    """
    Processa um record individual do DynamoDB Stream
    """
    try:
        event_name = record.get('eventName')
        dynamodb_data = record.get('dynamodb', {})
        
        # Filtrar apenas eventos INSERT e MODIFY
        if event_name not in ['INSERT', 'MODIFY']:
            logger.info(f"Ignorando evento {event_name}")
            return
        
        # Extrair dados das imagens
        new_image = dynamodb_data.get('NewImage', {})
        old_image = dynamodb_data.get('OldImage', {})
        
        # Determinar tipo de notificação
        notification_data = determine_notification_type(new_image, old_image, event_name)
        
        if notification_data:
            send_notification(notification_data)
            
    except Exception as e:
        logger.error(f"Erro ao processar record: {str(e)}")
        raise e

def determine_notification_type(new_image, old_image, event_name):
    """
    Determina o tipo de notificação baseado nas mudanças no pedido
    """
    try:
        # Converter dados do DynamoDB para formato mais legível
        new_data = convert_dynamodb_item(new_image)
        old_data = convert_dynamodb_item(old_image) if old_image else None
        
        cliente = new_data.get('cliente', 'Cliente')
        
        # Novo pedido
        if event_name == 'INSERT':
            return {
                'tipo': 'novo_pedido',
                'titulo': 'Novo Pedido Recebido!',
                'mensagem': f'Novo pedido de {cliente}',
                'detalhes': {
                    'cliente': cliente,
                    'medicamentos': new_data.get('medicamentos', []),
                    'total': new_data.get('total', 0)
                }
            }
        
        # Pedido modificado
        elif event_name == 'MODIFY' and old_data:
            # Verificar se foi marcado como entregue
            if not old_data.get('entregue', False) and new_data.get('entregue', False):
                return {
                    'tipo': 'entregue',
                    'titulo': 'Pedido Entregue!',
                    'mensagem': f'Pedido de {cliente} foi entregue',
                    'detalhes': {
                        'cliente': cliente,
                        'id_pedido': new_data.get('id')
                    }
                }
            
            # Verificar se foi marcado como recebido
            if not old_data.get('recebido', False) and new_data.get('recebido', False):
                return {
                    'tipo': 'recebido',
                    'titulo': 'Pedido Confirmado!',
                    'mensagem': f'{cliente} confirmou o recebimento do pedido',
                    'detalhes': {
                        'cliente': cliente,
                        'id_pedido': new_data.get('id')
                    }
                }
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao determinar tipo de notificação: {str(e)}")
        return None

def convert_dynamodb_item(item):
    """
    Converte item do DynamoDB para formato Python padrão
    """
    converted = {}
    
    for key, value in item.items():
        if 'S' in value:  # String
            converted[key] = value['S']
        elif 'N' in value:  # Number
            converted[key] = float(value['N'])
        elif 'BOOL' in value:  # Boolean
            converted[key] = value['BOOL']
        elif 'L' in value:  # List
            converted[key] = [convert_dynamodb_item({'item': v})['item'] for v in value['L']]
        elif 'SS' in value:  # String Set
            converted[key] = value['SS']
    
    return converted

def send_notification(notification_data):
    """
    Envia notificação via SNS
    """
    try:
        topic_arn = os.environ.get('SNS_TOPIC_ARN')
        
        if not topic_arn:
            logger.error("SNS_TOPIC_ARN não configurado")
            return
        
        # Criar mensagem para SNS
        message = {
            'default': notification_data['mensagem'],
            'sms': f"{notification_data['titulo']}: {notification_data['mensagem']}",
            'email': json.dumps({
                'subject': notification_data['titulo'],
                'body': notification_data['mensagem'],
                'details': notification_data.get('detalhes', {})
            }, ensure_ascii=False)
        }
        
        # Publicar no SNS
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=json.dumps(message, ensure_ascii=False),
            Subject=notification_data['titulo'],
            MessageStructure='json'
        )
        
        logger.info(f"Notificação enviada com sucesso: {response['MessageId']}")
        logger.info(f"Tipo: {notification_data['tipo']}, Mensagem: {notification_data['mensagem']}")
        
    except ClientError as e:
        logger.error(f"Erro ao enviar notificação SNS: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar notificação: {str(e)}")
        raise e