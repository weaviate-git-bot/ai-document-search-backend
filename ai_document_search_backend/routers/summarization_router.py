from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.summarization_service import SummarizationService

router = APIRouter(
    prefix="/summarization",
    tags=["summarization"],
)


class SummarizationResponse(BaseModel):
    summary: str


@router.get("/")
@inject
async def summarization(
        text: str,
        summary_length: Optional[int] = None,
        default_summary_length: int = Depends(Provide[Container.config.default.summary_length]),
        summarization_service: SummarizationService = Depends(Provide[Container.summarization_service]),
) -> SummarizationResponse:
    summary_length = summary_length or default_summary_length

    summary = summarization_service.summarize(text, summary_length)

    return SummarizationResponse(summary=summary)
