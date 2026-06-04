from decimal import Decimal
from ..models import Client, Order, OrderItem, Kit
from .discount_strategy import DiscountStrategy, NoDiscountStrategy, ClientLoyaltyStrategy

class OrderService:
    def __init__(self, discount_strategy: DiscountStrategy = None):
        self.discount_strategy = discount_strategy or NoDiscountStrategy()
    
    def set_strategy(self, discount_strategy: DiscountStrategy):
        self.discount_strategy = discount_strategy
    
    def calculate_order_total(self, order_id):
        try:
            order = Order.objects.get(id=order_id)
            total = Decimal('0')
            
            for item in order.items.all():
                if item.assortment:
                    total += item.assortment.price * item.quantity
                elif item.kit:
                    for kit_item in item.kit.items.all():
                        discounted_price = kit_item.assortment.price * (1 - kit_item.discount_percent / 100)
                        total += discounted_price * kit_item.quantity * item.quantity
            
            return total
        except Order.DoesNotExist:
            return Decimal('0')
    
    def calculate_final_price(self, order_id):
        total = self.calculate_order_total(order_id)
        discount = self.discount_strategy.calculate_discount(total)
        return total - discount

    def create_order_with_loyalty(self, client_id: int):
        client = Client.objects.get(id=client_id)
        order_count = Order.objects.filter(client_id=client_id).count()
        
        self.set_strategy(ClientLoyaltyStrategy(order_count))
        return self.create_order(client_id)
    
    def create_order(self, client_id: int):
        from ..db_managers.orm_managers import ORMOrderManager
        
        order = ORMOrderManager.create_order(client_id)
        return orders
