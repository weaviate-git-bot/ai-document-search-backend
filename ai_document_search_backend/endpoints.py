from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, FastAPI, status
from pydantic import BaseModel


from .containers import Container
from .services import SummarizationService


class SummarizationResponse(BaseModel):
    summary: str


router = APIRouter()


@router.get("/")
@router.get("/health")
async def health():
    return "OK"


@router.get("/summarization")
@inject
def summarization(
    text: str,
    summary_length: Optional[int] = None,
    default_summary_length: int = Depends(Provide[Container.config.default.summary_length]),
    summarization_service: SummarizationService = Depends(Provide[Container.summarization_service]),
) -> SummarizationResponse:
    summary_length = summary_length or default_summary_length

    summary = summarization_service.summarize(text, summary_length)

    return SummarizationResponse(summary=summary)
