from django.test import TestCase
from rest_framework.test import APIClient
from ...models import Client

class AuthenticationFlowTest(TestCase):
    def setUp(self):
        self.api_client = APIClient()
    
    def test_full_auth_flow(self):
        register_data = {
            'full_name': 'Новый Пользователь',
            'address': 'ул. Тестовая, 1',
            'login': 'newuser',
            'password': 'userpass123'
        }
        
        response = self.api_client.post('/api/clients/', register_data, format='json')
        self.assertIn(response.status_code, [200, 201])
        
        login_data = {
            'login': 'newuser',
            'password': 'userpass123'
        }
        
        response = self.api_client.post('/api/auth/', login_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('client_id', response.data)
        
        token = response.data['token']
        
        self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        
        response = self.api_client.get('/api/assortment/')
        self.assertEqual(response.status_code, 200)
        
        self.api_client.credentials()
        response = self.api_client.get('/api/assortment/')
        self.assertEqual(response.status_code, 401)
        
        login_data = {
            'login': 'newuser',
            'password': 'wrongpassword'
        }
        
        response = self.api_client.post('/api/auth/', login_data, format='json')
        self.assertEqual(response.status_code, 401)
        
        login_data = {
            'login': 'nonexistent',
            'password': 'pass123'
        }
        
        response = self.api_client.post('/api/auth/', login_data, format='json')
        self.assertEqual(response.status_code, 401)
