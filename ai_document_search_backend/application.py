from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from . import auth, endpoints
from .containers import Container


def create_app() -> FastAPI:
    container = Container()
    container.config.giphy.api_key.from_env("GIPHY_API_KEY")

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.container = container
    app.include_router(endpoints.router)
    app.include_router(auth.router, prefix="/auth")
    return app


app = create_app()
