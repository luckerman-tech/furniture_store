from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import threading
import subprocess
import os
import sys

class BaseE2ETest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
        except:
            cls.driver = webdriver.Firefox()
        
        cls.driver.implicitly_wait(10)
        cls.api_client = APIClient()
        
        cls.client_process = None
        
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        if cls.client_process:
            cls.client_process.terminate()
        super().tearDownClass()
    
    def login(self, username, password):
        self.driver.get(f"{self.live_server_url}/admin/login/")
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.XPATH, "//input[@value='Log in']").click()
    
    def api_login(self, login, password):
        response = self.api_client.post('/api/auth/', {
            'login': login,
            'password': password
        }, format='json')
        
        if response.status_code == 200:
            token = response.data.get('token')
            self.api_client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
            return token
        return None
