import logging
import random
import string
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from .containers import Container
from .routers import (
    home_router,
    auth_router,
    users_router,
    chatbot_router,
    conversation_router,
)
from .services.chatbot_service import ChatbotError

logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


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

    @app.exception_handler(ChatbotError)
    async def chatbot_error_handler(request: Request, exc: ChatbotError):
        return JSONResponse(
            status_code=400,
            content={"detail": exc.message},
        )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        idem = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        logger.info(f"rid={idem} start request path={request.url.path}")
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        logger.info(
            f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}"
        )

        return response

    return app


app = create_app()
