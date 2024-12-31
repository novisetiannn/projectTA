import unittest
from app import get_db_connection, findEncodings, markAttendance, app
import numpy as np
import cv2

class TestDatabaseConnection(unittest.TestCase):
    def test_db_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)
        conn.close()

class TestFaceEncoding(unittest.TestCase):
    def test_face_encodings(self):
        # Using a real image for testing
        img = cv2.imread('Train/Nabila Sivana_001.png')  # Make sure this path points to a real face image
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = findEncodings([img])
        self.assertEqual(len(encodings), 1)
        self.assertEqual(len(encodings[0]), 128)

class TestMarkAttendance(unittest.TestCase):
    def test_mark_attendance(self):
        name = "TestUser"
        roll = "12345"
        markAttendance(name, roll)

        # Verify if attendance is recorded in the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM absensi WHERE name = %s AND id_karyawan = %s", (name, roll))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        cursor.close()
        conn.close()
        
class TestLoginFunctionality(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_login_invalid_credentials(self):
        response = self.app.post('/login', data=dict(usr='nabila@gmail.com', pwd='Nabila_24'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid login', response.data)

class TestSignupFunctionality(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_signup(self):
        response = self.app.post('/signup', data=dict(nama='Sivanaa', usrup='sivanaa@gmail.com', pwdup='Sivana_24'))
        self.assertEqual(response.status_code, 302)  # Redirect to login page after successful signup

if __name__ == '__main__':
    unittest.main()
