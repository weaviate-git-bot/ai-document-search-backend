from typing import Optional, Annotated

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel

from ai_document_search_backend.containers import Container
from ai_document_search_backend.services.summarization_service import SummarizationService
from ai_document_search_backend.services.auth_service import AuthService


router = APIRouter(
    prefix="/summarization",
    tags=["summarization"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


class SummarizationResponse(BaseModel):
    summary: str


@router.get("/")
@inject
async def summarization(
    text: str,
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(Provide[Container.auth_service]),
    summary_length: Optional[int] = None,
    default_summary_length: int = Depends(Provide[Container.config.default.summary_length]),
    summarization_service: SummarizationService = Depends(Provide[Container.summarization_service]),
) -> SummarizationResponse:
    auth_service.get_current_user(token)
    summary_length = summary_length or default_summary_length

    summary = summarization_service.summarize(text, summary_length)

    return SummarizationResponse(summary=summary)
