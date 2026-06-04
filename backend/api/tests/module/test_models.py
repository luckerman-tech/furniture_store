from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ...models import (
    Category, Style, Warehouse, Assortment, Client, 
    Order, OrderItem, Kit, KitItem, Parish, Storage, Expense
)
from decimal import Decimal

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Стулья")
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Стулья")
        self.assertIsNotNone(self.category.id)
    
    def test_category_str(self):
        self.assertEqual(str(self.category), "Стулья")
    
    def test_category_unique_name(self):
        with self.assertRaises(Exception):
            Category.objects.create(name="Стулья")

class StyleModelTest(TestCase):
    def setUp(self):
        self.style = Style.objects.create(name="Классика")
    
    def test_style_creation(self):
        self.assertEqual(self.style.name, "Классика")
    
    def test_style_str(self):
        self.assertEqual(str(self.style), "Классика")

class WarehouseModelTest(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name="Главный склад")
    
    def test_warehouse_creation(self):
        self.assertEqual(self.warehouse.name, "Главный склад")

class AssortmentModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Дубовый стул",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Дубовый стул")
        self.assertEqual(self.product.price, Decimal('5000.00'))
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.style, self.style)
    
    def test_product_str(self):
        self.assertEqual(str(self.product), "Дубовый стул")
    
    def test_product_price_positive(self):
        with self.assertRaises(Exception):
            Assortment.objects.create(
                name="Тест",
                price=Decimal('-100.00'),
                category=self.category,
                style=self.style
            )

class ClientModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            full_name="Иван Иванов",
            address="Москва, ул. Ленина, 1",
            login="ivan",
            password="test123"
        )
    
    def test_client_creation(self):
        self.assertEqual(self.client.full_name, "Иван Иванов")
        self.assertEqual(self.client.login, "ivan")
    
    def test_password_hashing(self):
        self.client.set_password("newpassword")
        self.client.save()
        self.assertTrue(self.client.check_password("newpassword"))
        self.assertFalse(self.client.check_password("wrongpassword"))
    
    def test_client_str(self):
        self.assertEqual(str(self.client), "Иван Иванов")
    
    def test_unique_login(self):
        with self.assertRaises(Exception):
            Client.objects.create(
                full_name="Петр Петров",
                address="Адрес",
                login="ivan",
                password="pass"
            )

class OrderModelTest(TestCase):
    def setUp(self):
        self.client = Client.objects.create(
            full_name="Иван Иванов",
            address="Адрес",
            login="ivan",
            password="pass"
        )
        self.order = Order.objects.create(client=self.client)
    
    def test_order_creation(self):
        self.assertEqual(self.order.client, self.client)
        self.assertIsNotNone(self.order.datetime)
    
    def test_order_str(self):
        self.assertIn(str(self.client), str(self.order))

class KitModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Стул",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
        self.kit = Kit.objects.create(name="Обеденный набор")
        self.kit_item = KitItem.objects.create(
            kit=self.kit,
            assortment=self.product,
            quantity=4,
            discount_percent=Decimal('10.00')
        )
    
    def test_kit_creation(self):
        self.assertEqual(self.kit.name, "Обеденный набор")
        self.assertEqual(self.kit.items.count(), 1)
    
    def test_kit_item_discount(self):
        self.assertEqual(self.kit_item.discount_percent, Decimal('10.00'))
        self.assertEqual(self.kit_item.quantity, 4)

class StorageModelTest(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name="Склад")
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Стул",
            price=Decimal('5000.00'),
            category=self.category,
            style=self.style
        )
        self.storage = Storage.objects.create(
            warehouse=self.warehouse,
            assortment=self.product,
            quantity=100
        )
    
    def test_storage_creation(self):
        self.assertEqual(self.storage.quantity, 100)
        self.assertEqual(self.storage.warehouse, self.warehouse)
        self.assertEqual(self.storage.assortment, self.product)
    
    def test_storage_unique_together(self):
        with self.assertRaises(Exception):
            Storage.objects.create(
                warehouse=self.warehouse,
                assortment=self.product,
                quantity=50
            )
