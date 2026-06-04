from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ...models import Category, Style, Assortment, Client

class AssortmentViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.user)

        self.category = Category.objects.create(name="Стулья")
        self.style = Style.objects.create(name="Классика")
        self.product = Assortment.objects.create(
            name="Тестовый стул",
            price=5000,
            category=self.category,
            style=self.style
        )
    
    def test_get_assortment_list(self):
        url = '/api/assortment/'
        response = self.client_api.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_filter_by_category(self):
        url = f'/api/assortment/?category_id={self.category.id}'
        response = self.client_api.get(url, {'category': self.category.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_by_price_orm(self):
        url = '/api/assortment/using_orm/'
        response = self.client_api.get(url, {'min_price': 4000, 'max_price': 6000})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class CategoryViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Стулья")
    
    def test_get_categories(self):
        url = reverse('category-list')
        response = self.client_api.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

class WarehouseViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client_api = APIClient()
        self.client_api.force_authenticate(user=self.user)
        from ...models import Warehouse
        self.warehouse = Warehouse.objects.create(name="Главный склад")
    
    def test_get_warehouses(self):
        url = reverse('warehouse-list')
        response = self.client_api.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
