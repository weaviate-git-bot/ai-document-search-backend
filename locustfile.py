from locust import HttpUser, task


class HealthUser(HttpUser):
    @task
    def health(self):
        self.client.get("/health")
