// Configuração da API
let API_BASE_URL = localStorage.getItem('pharmacy-api-url') || '';

// Elementos do DOM
const orderForm = document.getElementById('orderForm');
const orderResult = document.getElementById('orderResult');
const deliveryResult = document.getElementById('deliveryResult');
const clientResult = document.getElementById('clientResult');
const notificationsContainer = document.getElementById('notifications');
const apiBaseUrlInput = document.getElementById('apiBaseUrl');

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    apiBaseUrlInput.value = API_BASE_URL;
    loadNotifications();
});

// Função para salvar configuração da API
function saveApiConfig() {
    const url = apiBaseUrlInput.value.trim();
    if (url) {
        API_BASE_URL = url;
        localStorage.setItem('pharmacy-api-url', url);
        showNotification('Configuração da API salva com sucesso!', 'success');
    } else {
        showNotification('Por favor, insira uma URL válida', 'error');
    }
}

// Função para adicionar medicamento
function addMedicamento() {
    const container = document.getElementById('medicamentos-container');
    const medicamentoItem = document.createElement('div');
    medicamentoItem.className = 'medicamento-item';
    medicamentoItem.innerHTML = `
        <input type="text" name="medicamento" placeholder="Nome do medicamento" required>
        <button type="button" onclick="removeMedicamento(this)" class="btn-remove">-</button>
    `;
    container.appendChild(medicamentoItem);
}

// Função para remover medicamento
function removeMedicamento(button) {
    const container = document.getElementById('medicamentos-container');
    if (container.children.length > 1) {
        button.parentElement.remove();
    } else {
        showNotification('Deve haver pelo menos um medicamento', 'error');
    }
}

// Função para criar pedido
orderForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!API_BASE_URL) {
        showNotification('Configure a URL da API primeiro', 'error');
        return;
    }
    
    const formData = new FormData(orderForm);
    const medicamentos = Array.from(document.querySelectorAll('input[name="medicamento"]'))
        .map(input => input.value.trim())
        .filter(value => value);
    
    const orderData = {
        cliente: formData.get('cliente'),
        medicamentos: medicamentos,
        total: parseFloat(formData.get('total'))
    };
    
    try {
        showLoading(orderResult);
        
        const response = await fetch(`${API_BASE_URL}/order/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(orderResult, `Pedido criado com sucesso! ID: ${result.pedido.id}`, 'success');
            
            // Copiar ID para área do entregador
            document.getElementById('deliveryOrderId').value = result.pedido.id;
            document.getElementById('clientOrderId').value = result.pedido.id;
            
            // Simular notificação para o dono
            simulateOwnerNotification('novo_pedido', `Novo pedido de ${orderData.cliente}`, {
                cliente: orderData.cliente,
                medicamentos: medicamentos,
                total: orderData.total
            });
            
            orderForm.reset();
            // Manter pelo menos um campo de medicamento
            const container = document.getElementById('medicamentos-container');
            container.innerHTML = `
                <div class="medicamento-item">
                    <input type="text" name="medicamento" placeholder="Nome do medicamento" required>
                    <button type="button" onclick="removeMedicamento(this)" class="btn-remove">-</button>
                </div>
            `;
        } else {
            showResult(orderResult, `Erro: ${result.error}`, 'error');
        }
    } catch (error) {
        showResult(orderResult, `Erro de conexão: ${error.message}`, 'error');
    }
});

// Função para marcar como entregue
async function markAsDelivered() {
    const orderId = document.getElementById('deliveryOrderId').value.trim();
    
    if (!orderId) {
        showNotification('Digite o ID do pedido', 'error');
        return;
    }
    
    if (!API_BASE_URL) {
        showNotification('Configure a URL da API primeiro', 'error');
        return;
    }
    
    try {
        showLoading(deliveryResult);
        
        const response = await fetch(`${API_BASE_URL}/delivery/order/${orderId}/delivered`, {
            method: 'GET'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(deliveryResult, `Pedido ${orderId} marcado como entregue!`, 'success');
            
            // Simular notificação para o dono
            simulateOwnerNotification('entregue', `Pedido ${orderId} foi entregue`, {
                id_pedido: orderId
            });
        } else {
            showResult(deliveryResult, `Erro: ${result.error}`, 'error');
        }
    } catch (error) {
        showResult(deliveryResult, `Erro de conexão: ${error.message}`, 'error');
    }
}

// Função para marcar como recebido
async function markAsReceived() {
    const orderId = document.getElementById('clientOrderId').value.trim();
    
    if (!orderId) {
        showNotification('Digite o ID do pedido', 'error');
        return;
    }
    
    if (!API_BASE_URL) {
        showNotification('Configure a URL da API primeiro', 'error');
        return;
    }
    
    try {
        showLoading(clientResult);
        
        const response = await fetch(`${API_BASE_URL}/client/order/${orderId}/received`, {
            method: 'GET'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showResult(clientResult, `Pedido ${orderId} confirmado como recebido!`, 'success');
            
            // Simular notificação para o dono
            simulateOwnerNotification('recebido', `Pedido ${orderId} foi confirmado pelo cliente`, {
                id_pedido: orderId
            });
        } else {
            showResult(clientResult, `Erro: ${result.error}`, 'error');
        }
    } catch (error) {
        showResult(clientResult, `Erro de conexão: ${error.message}`, 'error');
    }
}

// Função para simular notificação do dono (já que não temos SNS configurado)
function simulateOwnerNotification(type, message, details) {
    const notification = {
        type: type,
        title: getNotificationTitle(type),
        message: message,
        details: details,
        timestamp: new Date().toLocaleString('pt-BR')
    };
    
    addNotificationToPanel(notification);
    showNotification(`Notificação enviada: ${message}`, 'success');
}

// Função para obter título da notificação
function getNotificationTitle(type) {
    const titles = {
        'novo_pedido': 'Novo Pedido Recebido!',
        'entregue': 'Pedido Entregue!',
        'recebido': 'Pedido Confirmado!'
    };
    return titles[type] || 'Notificação';
}

// Função para adicionar notificação ao painel
function addNotificationToPanel(notification) {
    const notificationsList = document.getElementById('notifications');
    const noNotifications = notificationsList.querySelector('.no-notifications');
    
    if (noNotifications) {
        noNotifications.remove();
    }
    
    const notificationElement = document.createElement('div');
    notificationElement.className = `notification-item ${notification.type}`;
    notificationElement.innerHTML = `
        <div class="notification-title">${notification.title}</div>
        <div class="notification-message">${notification.message}</div>
        <div class="notification-time">${notification.timestamp}</div>
    `;
    
    notificationsList.insertBefore(notificationElement, notificationsList.firstChild);
    
    // Salvar no localStorage
    saveNotifications();
}

// Função para carregar notificações do localStorage
function loadNotifications() {
    const savedNotifications = localStorage.getItem('pharmacy-notifications');
    if (savedNotifications) {
        const notifications = JSON.parse(savedNotifications);
        const notificationsList = document.getElementById('notifications');
        
        if (notifications.length > 0) {
            const noNotifications = notificationsList.querySelector('.no-notifications');
            if (noNotifications) {
                noNotifications.remove();
            }
            
            notifications.forEach(notification => {
                const notificationElement = document.createElement('div');
                notificationElement.className = `notification-item ${notification.type}`;
                notificationElement.innerHTML = `
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message}</div>
                    <div class="notification-time">${notification.timestamp}</div>
                `;
                notificationsList.appendChild(notificationElement);
            });
        }
    }
}

// Função para salvar notificações no localStorage
function saveNotifications() {
    const notifications = Array.from(document.querySelectorAll('.notification-item')).map(item => ({
        type: item.className.split(' ')[1],
        title: item.querySelector('.notification-title').textContent,
        message: item.querySelector('.notification-message').textContent,
        timestamp: item.querySelector('.notification-time').textContent
    }));
    
    localStorage.setItem('pharmacy-notifications', JSON.stringify(notifications));
}

// Função para limpar notificações
function clearNotifications() {
    const notificationsList = document.getElementById('notifications');
    notificationsList.innerHTML = '<p class="no-notifications">Aguardando notificações...</p>';
    localStorage.removeItem('pharmacy-notifications');
    showNotification('Notificações limpas', 'success');
}

// Funções auxiliares
function showLoading(element) {
    element.innerHTML = '<div class="result">Carregando...</div>';
}

function showResult(element, message, type) {
    element.innerHTML = `<div class="result ${type}">${message}</div>`;
}

function showNotification(message, type) {
    // Criar elemento de notificação temporário
    const notification = document.createElement('div');
    notification.className = `notification-toast ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    
    if (type === 'success') {
        notification.style.background = '#38a169';
    } else if (type === 'error') {
        notification.style.background = '#e53e3e';
    }
    
    document.body.appendChild(notification);
    
    // Remover após 3 segundos
    setTimeout(() => {
        notification.remove();
    }, 3000);
}