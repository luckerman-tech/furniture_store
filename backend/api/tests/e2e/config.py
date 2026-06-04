import os

E2E_CONFIG = {
    'HEADLESS': os.getenv('E2E_HEADLESS', 'true').lower() == 'true',
    'TIMEOUT': int(os.getenv('E2E_TIMEOUT', '10')),
    'BASE_URL': os.getenv('BASE_URL', 'http://localhost:8000'),
    'SELENIUM_DRIVER': os.getenv('SELENIUM_DRIVER', 'chrome'),
}
