from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .containers import Container
from .routers import (
    home_router,
    auth_router,
    users_router,
    chatbot_router,
    conversation_router,
)
from .services.chatbot_service import ChatbotException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    container = Container()
    app.container = container

    app.include_router(home_router.router)
    app.include_router(auth_router.router)
    app.include_router(users_router.router)
    app.include_router(chatbot_router.router)
    app.include_router(conversation_router.router)

    @app.exception_handler(ChatbotException)
    async def chatbot_exception_handler(request: Request, exc: ChatbotException):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )

    return app


app = create_app()
