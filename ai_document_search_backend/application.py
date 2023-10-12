from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .containers import Container
from .routers import (
    home_router,
    summarization_router,
    auth_router,
    users_router,
    chatbot_router,
    conversation_router,
)


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
    app.include_router(summarization_router.router)
    app.include_router(chatbot_router.router)
    app.include_router(conversation_router.router)

    return app


app = create_app()
