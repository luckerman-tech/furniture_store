from abc import ABC, abstractmethod
from decimal import Decimal

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        pass

class NoDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        return Decimal('0')

class PercentageDiscountStrategy(DiscountStrategy):
    def __init__(self, percentage: Decimal):
        self.percentage = percentage
    
    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        return total_amount * (self.percentage / Decimal('100'))

class KitDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        # Специальная скидка для комплектов
        if total_amount > Decimal('50000'):
            return total_amount * Decimal('0.15')
        elif total_amount > Decimal('25000'):
            return total_amount * Decimal('0.10')
        return total_amount * Decimal('0.05')

class ClientLoyaltyStrategy(DiscountStrategy):
    def __init__(self, order_count: int):
        self.order_count = order_count
    
    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        if self.order_count > 20:
            return total_amount * Decimal('0.20')
        elif self.order_count > 10:
            return total_amount * Decimal('0.15')
        elif self.order_count > 5:
            return total_amount * Decimal('0.10')
        elif self.order_count > 0:
            return total_amount * Decimal('0.05')
        return Decimal('0')
