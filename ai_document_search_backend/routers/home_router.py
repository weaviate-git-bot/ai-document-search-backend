from fastapi import APIRouter

router = APIRouter(
    prefix="",
    tags=["home"],
)


@router.get("/")
@router.get("/health")
async def health():
    return "OK"
