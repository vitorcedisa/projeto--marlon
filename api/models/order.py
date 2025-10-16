import os
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute, ListAttribute
from datetime import datetime
import uuid

class Order(Model):
    """
    Modelo de pedido para farmácia usando PynamoDB
    """
    class Meta:
        table_name = os.environ.get('ORDER_TABLE', 'pharmacy-orders-dev')
        region = 'us-east-1'
    
    # Chave primária
    id = UnicodeAttribute(hash_key=True)
    
    # Dados do pedido
    medicamentos = ListAttribute(of=UnicodeAttribute)
    cliente = UnicodeAttribute()
    total = NumberAttribute()
    
    # Status do pedido
    entregue = BooleanAttribute(default=False)
    recebido = BooleanAttribute(default=False)
    
    # Timestamps
    created_at = UnicodeAttribute()
    updated_at = UnicodeAttribute()

    def save(self, **kwargs):
        """Override save para adicionar timestamps automaticamente"""
        now = datetime.utcnow().isoformat()
        
        if not self.created_at:
            self.created_at = now
        
        self.updated_at = now
        
        return super().save(**kwargs)

    @classmethod
    def create_order(cls, medicamentos, cliente, total):
        """Método helper para criar um novo pedido"""
        order_id = str(uuid.uuid4())
        
        order = cls(
            id=order_id,
            medicamentos=medicamentos,
            cliente=cliente,
            total=total
        )
        
        order.save()
        return order

    def to_dict(self):
        """Converte o modelo para dicionário"""
        return {
            'id': self.id,
            'medicamentos': self.medicamentos,
            'cliente': self.cliente,
            'total': self.total,
            'entregue': self.entregue,
            'recebido': self.recebido,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }