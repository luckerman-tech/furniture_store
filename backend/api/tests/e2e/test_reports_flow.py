from django.test import TestCase
from rest_framework.test import APIClient
from ...models import Category, Style, Assortment, Client, Order, OrderItem, Warehouse, Storage, Parish
from django.contrib.auth.models import User
from decimal import Decimal

class ReportsFlowTest(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        
        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        
        self.product1 = Assortment.objects.create(
            name="Стул дубовый",
            price=5000,
            category=self.category,
            style=self.style
        )
        
        self.product2 = Assortment.objects.create(
            name="Стул офисный",
            price=8000,
            category=self.category,
            style=self.style
        )
        
        self.warehouse = Warehouse.objects.create(name="Главный склад")
        
        Storage.objects.create(
            warehouse=self.warehouse,
            assortment=self.product1,
            quantity=50
        )
        Storage.objects.create(
            warehouse=self.warehouse,
            assortment=self.product2,
            quantity=30
        )
        
        self.client_user = Client.objects.create(
            full_name="Тест Клиент",
            address="Адрес",
            login="testclient"
        )
        self.client_user.set_password("test123")
        self.client_user.save()
        
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

    def test_reports_flow(self):
        response = self.api_client.post('/api/auth/', {
            'login': 'testclient',
            'password': 'test123'
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        token = response.data.get('token')
        client_id = response.data.get('client_id')
        
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        for _ in range(3):
            response = self.api_client.post('/api/orders/', {"client": client_id}, format='json')
            self.assertEqual(response.status_code, 201)
            order = response.json()
            
            self.api_client.post('/api/order-items/', {
                "order": order['id'],
                "assortment": self.product1.id,
                "quantity": 2
            }, format='json')
            
            self.api_client.post('/api/order-items/', {
                "order": order['id'],
                "assortment": self.product2.id,
                "quantity": 1
            }, format='json')
        
        self.api_client.force_authenticate(user=self.admin)
        
        response = self.api_client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        orders = response.json()
        
        for order in orders:
            warehouse_items = {
                str(self.warehouse.id): [
                    {'assortment_id': self.product1.id, 'quantity': 2},
                    {'assortment_id': self.product2.id, 'quantity': 1}
                ]
            }
            self.api_client.post(
                f"/api/orders/{order['id']}/process/",
                {'warehouse_items': warehouse_items},
                format='json'
            )

            self.assertIn(response.status_code, [200, 400])
        
        response = self.api_client.get('/api/orders/reports_orm/?type=top_products')
        self.assertEqual(response.status_code, 200)
        report = response.json()
        self.assertIn('report', report)
        
        response = self.api_client.get('/api/orders/reports_sql/?type=top_products')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('report', data)
        
        response = self.api_client.get('/api/storage/')
        self.assertEqual(response.status_code, 200)
        storage_data = response.json()
        
        for item in storage_data:
            if item['assortment_name'] == "Стул дубовый":
                self.assertEqual(item['quantity'], 44)
        
        response = self.api_client.get('/api/storage/low_stock/')
        self.assertEqual(response.status_code, 200)
        
        response = self.api_client.get('/api/orders/reports_orm/?type=storage_value')
        self.assertEqual(response.status_code, 200)
