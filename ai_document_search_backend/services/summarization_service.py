from ai_document_search_backend.services.base_service import BaseService


class SummarizationService(BaseService):
    def summarize(self, text: str, summary_length: int) -> str:
        """Summarize text."""
        return text[:summary_length]
