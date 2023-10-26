import os

from dotenv import load_dotenv
from locust import HttpUser, task

chatbot_response_limit_sec = 15


class ChatUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    def on_start(self):
        load_dotenv()
        username = os.getenv("AUTH_USERNAME")
        password = os.getenv("AUTH_PASSWORD")

        response = self.client.post("/auth/token", data={"username": username, "password": password})
        self.token = response.json()["access_token"]

        # create new conversation
        self.client.post("/conversation", headers={"Authorization": f"Bearer {self.token}"})

    @task
    def ask_question(self):
        with self.client.post("/chatbot",
                              json={"question": "What is the Loan to value ratio?"},
                              headers={"Authorization": f"Bearer {self.token}"},
                              catch_response=True) as response:
            if response.elapsed.total_seconds() > chatbot_response_limit_sec:
                response.failure(f"Chatbot response took more than {chatbot_response_limit_sec} seconds.")
