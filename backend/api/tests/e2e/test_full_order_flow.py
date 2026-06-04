from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from ...models import Category, Style, Assortment, Client, Order, OrderItem, Warehouse, Storage
import time

class FullOrderFlowTest(TestCase):
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
            name="Стол обеденный",
            price=15000,
            category=self.category,
            style=self.style
        )
        
        self.warehouse = Warehouse.objects.create(name="Главный склад")
        
        self.storage1 = Storage.objects.create(
            warehouse=self.warehouse,
            assortment=self.product1,
            quantity=100
        )
        
        self.storage2 = Storage.objects.create(
            warehouse=self.warehouse,
            assortment=self.product2,
            quantity=50
        )
        
        self.client_user = Client.objects.create(
            full_name="Тестовый Клиент",
            address="Тестовый адрес",
            login="testclient"
        )
        self.client_user.set_password("testpass123")
        self.client_user.save()
        
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )

    def test_complete_order_flow(self):
        response = self.api_client.post('/api/auth/', {
            'login': 'testclient',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        client_token = response.data.get('token')
        client_id = response.data.get('client_id')
        
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {client_token}')
        response = self.api_client.get('/api/assortment/')
        self.assertEqual(response.status_code, 200)
        products = response.json()
        self.assertGreaterEqual(len(products), 2)
        
        order_data = {"client": client_id}
        response = self.api_client.post('/api/orders/', order_data, format='json')
        self.assertEqual(response.status_code, 201)
        order = response.json()
        order_id = order['id']
        
        item1_data = {
            "order": order_id,
            "assortment": self.product1.id,
            "quantity": 2
        }
        response = self.api_client.post('/api/order-items/', item1_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        item2_data = {
            "order": order_id,
            "assortment": self.product2.id,
            "quantity": 1
        }
        response = self.api_client.post('/api/order-items/', item2_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        response = self.api_client.get(f'/api/orders/{order_id}/')
        self.assertEqual(response.status_code, 200)
        order_detail = response.json()
        self.assertEqual(len(order_detail.get('items', [])), 2)
        
        self.api_client.force_authenticate(user=self.admin)
        
        response = self.api_client.get(f'/api/orders/{order_id}/check_availability/')
        self.assertEqual(response.status_code, 200)
        availability = response.json()
        self.assertTrue(availability.get('available', False))
        
        response = self.api_client.get(f'/api/orders/{order_id}/get_picklist/')
        self.assertEqual(response.status_code, 200)
        picklist = response.json()
        self.assertIn('picklist', picklist)
        
        warehouse_items = {
            str(self.warehouse.id): [
                {'assortment_id': self.product1.id, 'quantity': 2},
                {'assortment_id': self.product2.id, 'quantity': 1}
            ]
        }
        
        response = self.api_client.post(
            f'/api/orders/{order_id}/process/',
            {'warehouse_items': warehouse_items},
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        
        self.storage1.refresh_from_db()
        self.storage2.refresh_from_db()
        
        self.assertEqual(self.storage1.quantity, 98)
        self.assertEqual(self.storage2.quantity, 49)
        
        response = self.api_client.get(f'/api/orders/{order_id}/')
        self.assertEqual(response.status_code, 200)
        order_updated = response.json()
        self.assertEqual(order_updated.get('status'), 'processing')

    def test_insufficient_stock_flow(self):       
        response = self.api_client.post('/api/auth/', {
            'login': 'testclient',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, 200)
        client_token = response.data.get('token')
        client_id = response.data.get('client_id')
        
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {client_token}')
        response = self.api_client.post('/api/orders/', {"client": client_id}, format='json')
        order = response.json()
        order_id = order['id']
        
        item_data = {
            "order": order_id,
            "assortment": self.product1.id,
            "quantity": 200 
        }
        response = self.api_client.post('/api/order-items/', item_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        self.api_client.force_authenticate(user=self.admin)
        
        warehouse_items = {
            str(self.warehouse.id): [
                {'assortment_id': self.product1.id, 'quantity': 200}
            ]
        }
        
        response = self.api_client.post(
            f'/api/orders/{order_id}/process/',
            {'warehouse_items': warehouse_items},
            format='json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())