from locust import HttpUser, task, between

class TestPostSignup(HttpUser):
    wait_time = between(1, 3)
    host = "http://127.0.0.1:81"

    @task
    def signup(self):
        data_form = {
            'usrup': 'newuser@example.com',
            'pwdup': 'NewUser*123',
            'nama': 'New User'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # Melakukan POST request ke endpoint /signup
        response = self.client.post("/signup", data=data_form, headers=headers)

        # Memeriksa hasil dari respons
        if response.status_code == 200:
            print("Signup successful!")
        else:
            print(f"Signup failed! Status Code: {response.status_code}")

    @task
    def login(self):
        
        data_form = {
            'usr': 'ihza09@gmail.com',
            'pwd': 'Ihza_2610'
        }
        response = self.client.post("/login", data=data_form)

        if response.status_code == 200:
            print("Login successful!")
        else:
            print(f"Login failed! Status Code: {response.status_code}")

    @task
    def attendance(self):
        data_form = {
            'name': 'Nabila Sivana',
            'id_karyawan': '001'
        }
        response = self.client.get("/attendance")

        if response.status_code == 200:
            print("Berhasil Absen")
        else:
            print(f"Absen gagal Status Code: {response.status_code}")