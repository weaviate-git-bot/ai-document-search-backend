import os

from dependency_injector import containers, providers
from dotenv import load_dotenv

from .services.auth_service import AuthService
from .services.summarization_service import SummarizationService
from .services.chatbot_service import ChatbotService
from .utils.relative_path_from_file import relative_path_from_file

CONFIG_PATH = relative_path_from_file(__file__, "../config.yml")


class Container(containers.DeclarativeContainer):
    # Specify modules in which you want to use the @inject decorator.
    wiring_config = containers.WiringConfiguration(
        modules=[
            ".routers.summarization_router",
            ".routers.auth_router",
            ".routers.users_router",
            ".routers.chatbot_router",
        ]
    )

    config = providers.Configuration(yaml_files=[CONFIG_PATH])

    summarization_service = providers.Factory(
        SummarizationService,
    )

    load_dotenv()
    openai_api_key = os.getenv("APP_OPENAI_API_KEY")
    weaviate_api_key = os.getenv("APP_WEAVIATE_API_KEY")

    chatbot_service = providers.Factory(
        ChatbotService,
        weaviate_url=config.weaviate.url,
        weaviate_api_key=weaviate_api_key,
        openai_api_key=openai_api_key,
        verbose=config.chatbot.verbose,
    )

    secret_key = os.getenv("AUTH_SECRET_KEY")
    username = os.getenv("AUTH_USERNAME")
    password = os.getenv("AUTH_PASSWORD")

    auth_service = providers.Factory(
        AuthService,
        algorithm=config.auth.algorithm,
        access_token_expire_minutes=config.auth.access_token_expire_minutes,
        secret_key=secret_key,
        username=username,
        password=password,
    )
