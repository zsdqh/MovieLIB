from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(5, 15)

    @task
    def me(self):
        self.client.get("/me")

    @task
    def refresh(self):
        self.client.get("/refresh")

    @task
    def login(self):
        self.client.post("/login", {
            "username": "zsd",
            "password": "12345678"
        })
