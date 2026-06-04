from django.db import transaction
from django.core.exceptions import ValidationError
from ..models import Assortment, Order, Storage, Expense
from decimal import Decimal

class OrderProcessingService:    
    @staticmethod
    def check_availability(order_id, warehouse_id=None):
        order = Order.objects.get(id=order_id)
        missing_products = []
        
        for item in order.items.all():
            if item.assortment:
                if warehouse_id:
                    storage = Storage.objects.filter(
                        warehouse_id=warehouse_id,
                        assortment=item.assortment
                    ).first()
                else:
                    storage = Storage.objects.filter(
                        assortment=item.assortment
                    ).first()
                
                available = storage.quantity if storage else 0
                if available < item.quantity:
                    missing_products.append({
                        'product': item.assortment.name,
                        'required': item.quantity,
                        'available': available,
                        'deficit': item.quantity - available
                    })
            
            elif item.kit:
                for kit_item in item.kit.items.all():
                    if warehouse_id:
                        storage = Storage.objects.filter(
                            warehouse_id=warehouse_id,
                            assortment=kit_item.assortment
                        ).first()
                    else:
                        storage = Storage.objects.filter(
                            assortment=kit_item.assortment
                        ).first()
                    
                    required = kit_item.quantity * item.quantity
                    available = storage.quantity if storage else 0
                    
                    if available < required:
                        missing_products.append({
                            'product': kit_item.assortment.name,
                            'required': required,
                            'available': available,
                            'deficit': required - available
                        })
        
        return {
            'available': len(missing_products) == 0,
            'missing_products': missing_products
        }
    
    @staticmethod
    @transaction.atomic
    def process_order(order_id, warehouse_items):       
        try:
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                raise ValidationError(f"Заказ #{order_id} не найден")

            if order.status != 'new':
                raise ValidationError(f"Заказ уже {order.get_status_display()}")
        
            for warehouse_id, items in warehouse_items.items():
                for item in items:
                    try:
                        assortment = Assortment.objects.get(id=item['assortment_id'])
                        product_name = assortment.name
                    except Assortment.DoesNotExist:
                        product_name = f"Товар с ID {item['assortment_id']}"

                    storage = Storage.objects.filter(
                        warehouse_id=warehouse_id,
                        assortment_id=item['assortment_id']
                    ).first()
                
                    if not storage:
                        raise ValidationError(
                            f"Товар '{product_name}' не найден на складе #{warehouse_id}"
                        )
                
                    if storage.quantity < item['quantity']:
                        raise ValidationError(
                            f"Недостаточно товара '{product_name}' на складе #{warehouse_id}. "
                            f"Доступно: {storage.quantity}, требуется: {item['quantity']}"
                        )
        
            for warehouse_id, items in warehouse_items.items():
                for item in items:
                    storage = Storage.objects.get(
                        warehouse_id=warehouse_id,
                        assortment_id=item['assortment_id']
                    )
                    storage.quantity -= item['quantity']
                    storage.save()
                
                    Expense.objects.create(
                        warehouse_id=warehouse_id,
                        assortment_id=item['assortment_id'],
                        quantity=item['quantity']
                    )
        
            order.status = 'processing'
            order.save()
        
            return {'status': 'success', 'order_id': order.id}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    @staticmethod
    def get_order_picklist(order_id):
        order = Order.objects.get(id=order_id)
        picklist = []
        
        for item in order.items.all():
            if item.assortment:
                picklist.append({
                    'type': 'product',
                    'name': item.assortment.name,
                    'quantity': item.quantity,
                    'assortment_id': item.assortment.id,
                    'price': float(item.assortment.price)
                })
            elif item.kit:
                for kit_item in item.kit.items.all():
                    picklist.append({
                        'type': 'kit_component',
                        'kit_name': item.kit.name,
                        'name': kit_item.assortment.name,
                        'quantity': kit_item.quantity * item.quantity,
                        'assortment_id': kit_item.assortment.id
                    })
        
        return picklist
