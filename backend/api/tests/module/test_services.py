from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from ...models import (
    Category, Style, Warehouse, Assortment, Client, Order, 
    OrderItem, Kit, KitItem, Storage, Expense, Parish
)
from ...services.discount_strategy import (
    NoDiscountStrategy, PercentageDiscountStrategy, 
    KitDiscountStrategy, ClientLoyaltyStrategy
)
from ...services.order_service import OrderService
from ...services.order_processing_service import OrderProcessingService

class DiscountStrategyTest(TestCase):
    def test_no_discount(self):
        strategy = NoDiscountStrategy()
        discount = strategy.calculate_discount(Decimal('1000'))
        self.assertEqual(discount, Decimal('0'))
    
    def test_percentage_discount(self):
        strategy = PercentageDiscountStrategy(Decimal('10'))
        discount = strategy.calculate_discount(Decimal('1000'))
        self.assertEqual(discount, Decimal('100'))
    
    def test_kit_discount(self):
        strategy = KitDiscountStrategy()
        
        discount1 = strategy.calculate_discount(Decimal('30000'))
        self.assertEqual(discount1, Decimal('3000'))
        
        discount2 = strategy.calculate_discount(Decimal('60000'))
        self.assertEqual(discount2, Decimal('9000'))
        
        discount3 = strategy.calculate_discount(Decimal('10000'))
        self.assertEqual(discount3, Decimal('500'))
    
    def test_loyalty_discount(self):
        strategy = ClientLoyaltyStrategy(0)
        discount = strategy.calculate_discount(Decimal('1000'))
        self.assertEqual(discount, Decimal('0'))
        
        strategy = ClientLoyaltyStrategy(7)
        discount = strategy.calculate_discount(Decimal('1000'))
        self.assertEqual(discount, Decimal('100'))
        
        strategy = ClientLoyaltyStrategy(15)
        discount = strategy.calculate_discount(Decimal('1000'))
        self.assertEqual(discount, Decimal('150'))

class OrderProcessingServiceTest(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name="Тестовый склад")
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Тестовый стул",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
        self.client = Client.objects.create(
            full_name="Тест Клиент",
            address="Адрес",
            login="testclient",
            password="pass"
        )
        
        self.storage = Storage.objects.create(
            warehouse=self.warehouse,
            assortment=self.product,
            quantity=100
        )
        
        self.order = Order.objects.create(client=self.client)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            assortment=self.product,
            quantity=10
        )
    
    def test_check_availability_success(self):
        result = OrderProcessingService.check_availability(self.order.id)
        self.assertTrue(result['available'])
        self.assertEqual(len(result['missing_products']), 0)
    
    def test_check_availability_fail(self):
        big_order = Order.objects.create(client=self.client)
        OrderItem.objects.create(
            order=big_order,
            assortment=self.product,
            quantity=200
        )
        
        result = OrderProcessingService.check_availability(big_order.id)
        self.assertFalse(result['available'])
        self.assertGreater(len(result['missing_products']), 0)
    
    def test_process_order_success(self):
        warehouse_items = {
            str(self.warehouse.id): [{
                'assortment_id': self.product.id,
                'quantity': 5
            }]
        }
        
        result = OrderProcessingService.process_order(self.order.id, warehouse_items)
        self.assertEqual(result['status'], 'success')
        
        self.storage.refresh_from_db()
        self.assertEqual(self.storage.quantity, 95)
        
        expense = Expense.objects.filter(
            warehouse=self.warehouse,
            assortment=self.product
        ).first()
        self.assertIsNotNone(expense)
        self.assertEqual(expense.quantity, 5)
    
    def test_process_order_insufficient_stock(self):
        warehouse_items = {
            str(self.warehouse.id): [{
                'assortment_id': self.product.id,
                'quantity': 200 
            }]
        }
        
        result = OrderProcessingService.process_order(self.order.id, warehouse_items)
        self.assertEqual(result['status'], 'failed')
    
    def test_process_order_already_processed(self):
        self.order.status = 'processing'
        self.order.save()
        
        warehouse_items = {
            str(self.warehouse.id): [{
                'assortment_id': self.product.id,
                'quantity': 5
            }]
        }
        
        result = OrderProcessingService.process_order(self.order.id, warehouse_items)
        self.assertEqual(result['status'], 'failed')

class OrderServiceTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            full_name="Тест",
            address="Адрес",
            login="test",
            password="pass"
        )
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Стул",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
        self.order = Order.objects.create(client=self.client)
        OrderItem.objects.create(
            order=self.order,
            assortment=self.product,
            quantity=2
        )
    
    def test_calculate_order_total(self):
        service = OrderService()
        total = service.calculate_order_total(self.order.id)
        self.assertEqual(total, Decimal('10000.00'))
    
    def test_calculate_final_price_with_discount(self):
        service = OrderService(KitDiscountStrategy())
        total = service.calculate_final_price(self.order.id)
        self.assertLess(total, Decimal('10000.00'))
