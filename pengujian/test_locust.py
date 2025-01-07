from locust import HttpUser, task, between

class MyUser(HttpUser):
    wait_time = between(1, 3)  # Time between simulated user actions

    @task
    def access_mark_attendance_menu(self):
        self.client.get("/?menu=MARK ATTENDANCE")

    @task
    def access_register_menu(self):
        self.client.get("/?menu=REGISTER")

    @task
    def access_attendance_menu(self):
        self.client.get("/?menu=ATTENDANCE")

    @task
    def access_home_menu(self):
        self.client.get("/?menu=HOME")

    @task
    def access_isi_Sendiri_menu(self):
        self.client.get("/?menu=isi Sendiri")

    # Additional tasks for specific actions within menus can be defined here