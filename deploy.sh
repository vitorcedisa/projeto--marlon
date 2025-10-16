#!/bin/bash

# Script de deploy para Farmácia Delivery App
# Este script automatiza o processo de deploy da aplicação serverless

echo "🏥 Farmácia Delivery - Script de Deploy"
echo "======================================"

# Verificar se o Serverless Framework está instalado
if ! command -v serverless &> /dev/null; then
    echo "❌ Serverless Framework não encontrado!"
    echo "📦 Instalando Serverless Framework..."
    npm install -g serverless
fi

# Verificar se as credenciais AWS estão configuradas
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Credenciais AWS não configuradas!"
    echo "🔧 Configure suas credenciais AWS:"
    echo "   aws configure"
    exit 1
fi

echo "✅ Credenciais AWS configuradas"

# Navegar para o diretório da API
cd api

echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

echo "🚀 Fazendo deploy da aplicação..."
serverless deploy

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deploy realizado com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Copie a URL da API Gateway exibida acima"
    echo "2. Abra o arquivo client/index.html no navegador"
    echo "3. Cole a URL no campo 'URL Base da API'"
    echo "4. Clique em 'Salvar'"
    echo ""
    echo "🌐 Para testar a aplicação:"
    echo "   Abra: client/index.html"
    echo ""
else
    echo "❌ Erro no deploy!"
    echo "🔍 Verifique os logs acima para mais detalhes"
    exit 1
fi
