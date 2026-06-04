from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from ...models import Category, Style, Assortment

class SearchAndFilterFlowTest(TestCase):
    def setUp(self):
        self.api_client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.api_client.force_authenticate(user=self.user)
        
        self.category1 = Category.objects.create(name="Стулья")
        self.category2 = Category.objects.create(name="Столы")
        self.category3 = Category.objects.create(name="Шкафы")
        
        self.style1 = Style.objects.create(name="Классика")
        self.style2 = Style.objects.create(name="Современный")
        
        self.products = [
            Assortment.objects.create(
                name="Стул дубовый классический",
                price=5000,
                category=self.category1,
                style=self.style1
            ),
            Assortment.objects.create(
                name="Стул офисный современный",
                price=8000,
                category=self.category1,
                style=self.style2
            ),
            Assortment.objects.create(
                name="Стол обеденный дубовый",
                price=15000,
                category=self.category2,
                style=self.style1
            ),
            Assortment.objects.create(
                name="Стол письменный современный",
                price=12000,
                category=self.category2,
                style=self.style2
            ),
            Assortment.objects.create(
                name="Шкаф-купе классический",
                price=25000,
                category=self.category3,
                style=self.style1
            ),
        ]

    def test_full_search_flow(self):
        response = self.api_client.get('/api/assortment/using_orm/?name=Стул')
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        self.assertEqual(len(results), 2)
        
        response = self.api_client.get('/api/assortment/using_sql/?name=Стул')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('items', [])
        self.assertEqual(len(results), 2)
        
        response = self.api_client.get(f'/api/assortment/using_orm/?category_id={self.category2.id}')
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(len(results), 2)
        
        response = self.api_client.get('/api/assortment/using_sql/?min_price=10000&max_price=20000')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('items', [])
        self.assertGreaterEqual(len(results), 2)
        
        response = self.api_client.get(
            f'/api/assortment/using_orm/'
            f'?category_id={self.category1.id}'
            f'&min_price=6000'
            f'&max_price=10000'
        )
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(len(results), 1)
        self.assertIn("офисный", results[0]['name'])
        
        response = self.api_client.get('/api/assortment/using_orm/?name=дубовый кл')
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(len(results), 1)
        
        response = self.api_client.get('/api/assortment/using_orm/?name=дуб')
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertEqual(len(results), 2)
