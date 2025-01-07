import unittest
from app import app  # Import aplikasi Flask

class TestRoutes(unittest.TestCase):
    def setUp(self):
        # Buat testing client
        self.client = app.test_client()

    def test_test_route(self):
        # Lakukan request ke route
        response = self.client.get('/update_employee_superadmin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Hello, World!")

if __name__ == '__main__':
    unittest.main()
