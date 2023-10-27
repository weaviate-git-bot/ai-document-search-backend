import logging
import os

from dotenv import load_dotenv
from locust import HttpUser, task, events
from locust.env import Environment

chatbot_response_hard_limit_sec = 15
chatbot_response_soft_limit_sec = 5


class ChatUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None

    def on_start(self):
        load_dotenv()
        username = os.getenv("AUTH_USERNAME")
        password = os.getenv("AUTH_PASSWORD")

        response = self.client.post(
            "/auth/token", data={"username": username, "password": password}
        )
        self.token = response.json()["access_token"]

        # create new conversation
        self.client.post("/conversation", headers={"Authorization": f"Bearer {self.token}"})

    @events.test_stop.add_listener
    def on_test_stop(environment: Environment):  # noqa: N805
        chatbot_entries = environment.stats.entries[("/chatbot", "POST")]
        if chatbot_entries.num_requests == 0:
            logging.error("No /chatbot requests completed during the test run.")
            environment.process_exit_code = 1
            return

        avg_chatbot_time = round(chatbot_entries.avg_response_time)
        logging.info(f"Average /chatbot response time: {avg_chatbot_time} ms")
        if avg_chatbot_time > chatbot_response_soft_limit_sec * 1000:
            logging.warning(
                f"Average /chatbot response time is greater than {chatbot_response_soft_limit_sec} seconds."
            )

    @task
    def ask_question(self):
        with self.client.post(
            "/chatbot",
            json={"question": "What is the Loan to value ratio?"},
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True,
        ) as response:
            if response.elapsed.total_seconds() > chatbot_response_hard_limit_sec:
                response.failure(
                    f"Chatbot response took more than {chatbot_response_hard_limit_sec} seconds."
                )
