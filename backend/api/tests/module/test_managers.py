from django.test import TestCase
from decimal import Decimal
from ...models import Category, Style, Assortment, Client, Order, OrderItem
from ...db_managers.orm_managers import ORMAssortmentManager, ORMOrderManager
from ...db_managers.sql_managers import SQLAssortmentManager

class ORMAssortmentManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product1 = Assortment.objects.create(
            name="Стул дубовый",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
        self.product2 = Assortment.objects.create(
            name="Стул офисный",
            price=Decimal('3000.00'),
            category=self.category,
            style=self.style
        )
    
    def test_get_all(self):
        products = ORMAssortmentManager.get_all()
        self.assertEqual(products.count(), 2)
    
    def test_filter_by_category(self):
        products = ORMAssortmentManager.filter_by_category(self.category.id)
        self.assertEqual(products.count(), 2)
    
    def test_filter_by_price_range(self):
        products = ORMAssortmentManager.filter_by_price_range(4000, 6000)
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().name, "Стул дубовый")
    
    def test_search_by_name(self):
        products = ORMAssortmentManager.search_by_name("дубовый")
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().name, "Стул дубовый")

class ORMOrderManagerTest(TestCase):
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
    
    def test_get_client_orders(self):
        orders = ORMOrderManager.get_client_orders(self.client.id)
        self.assertEqual(orders.count(), 1)
    
    def test_get_order_total(self):
        total = ORMOrderManager.get_order_total(self.order.id)
        self.assertEqual(total, Decimal('10000.00'))

class SQLAssortmentManagerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Стул тестовый",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
    
    def test_get_all(self):
        products = SQLAssortmentManager.get_all()
        self.assertEqual(len(products), 1)
    
    def test_filter_by_price_range(self):
        products = SQLAssortmentManager.filter_by_price_range(4000, 6000)
        self.assertEqual(len(products), 1)
        
        products2 = SQLAssortmentManager.filter_by_price_range(6000, 8000)
        self.assertEqual(len(products2), 0)
