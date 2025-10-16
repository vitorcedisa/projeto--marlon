import json

def success_response(data, status_code=200):
    """
    Cria uma resposta de sucesso padrão para API Gateway
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': json.dumps(data, ensure_ascii=False)
    }

def error_response(message, status_code=500):
    """
    Cria uma resposta de erro padrão para API Gateway
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS'
        },
        'body': json.dumps({
            'error': message
        }, ensure_ascii=False)
    }

def parse_body(event):
    """
    Extrai e faz parse do body da requisição
    """
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            return json.loads(body)
        return body
    except json.JSONDecodeError:
        return {}

def get_path_parameter(event, param_name):
    """
    Extrai parâmetro do path da requisição
    """
    path_params = event.get('pathParameters') or {}
    return path_params.get(param_name)