class SummarizationService:
    def summarize(self, text: str, summary_length: int) -> str:
        """Summarize text."""
        return text[:summary_length]
