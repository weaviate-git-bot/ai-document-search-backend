from ai_document_search_backend.services.chat_history_service import ChatHistoryService, Exchange


class InMemoryChatHistoryService(ChatHistoryService):
    def __init__(self):
        self.db: dict[str, list[Exchange]] = {}

        super().__init__()

    def get_chat_history(self, username: str) -> list[Exchange]:
        return self.db.get(username, [])

    def add_chat_history(self, username: str, question: str, answer: str) -> None:
        self.db.setdefault(username, []).append((question, answer))

    def delete_chat_history(self, username: str) -> None:
        self.db.pop(username, None)
