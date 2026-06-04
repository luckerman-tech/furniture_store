from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ...models import Client

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Client.objects.create(
            full_name="Тест Пользователь",
            address="Тестовый адрес",
            login="testuser"
        )
        self.user.set_password("testpass123")
        self.user.save()
    
    def test_login_success(self):
        url = '/api/auth/'
        data = {'login': 'testuser', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('client_id', response.data)
    
    def test_login_fail_wrong_password(self):
        url = '/api/auth/'
        data = {'login': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_fail_wrong_login(self):
        url = '/api/auth/'
        data = {'login': 'nonexistent', 'password': 'testpass123'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_register_success(self):
        url = '/api/clients/'
        data = {
            'full_name': 'Новый Пользователь',
            'address': 'Новый адрес',
            'login': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Client.objects.filter(login='newuser').exists())
