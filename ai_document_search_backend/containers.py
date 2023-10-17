import os

import weaviate
from dependency_injector import containers, providers
from dotenv import load_dotenv

from .database_providers.cosmos_conversation_database import CosmosConversationDatabase
from .services.auth_service import AuthService
from .services.chatbot_service import ChatbotService
from .services.conversation_service import ConversationService
from .services.summarization_service import SummarizationService
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
            ".routers.conversation_router",
        ]
    )

    config = providers.Configuration(yaml_files=[CONFIG_PATH])

    summarization_service = providers.Factory(
        SummarizationService,
    )

    load_dotenv()

    cosmos_key = os.getenv("COSMOS_KEY")

    conversation_database = providers.Singleton(
        CosmosConversationDatabase,
        url=config.cosmos.url,
        key=cosmos_key,
        db_name=config.cosmos.db_name,
        offer_throughput=config.cosmos.offer_throughput,
    )

    conversation_service = providers.Factory(
        ConversationService,
        conversation_database=conversation_database,
    )

    openai_api_key = os.getenv("APP_OPENAI_API_KEY")
    weaviate_api_key = os.getenv("APP_WEAVIATE_API_KEY")

    weaviate_client = providers.Factory(
        weaviate.Client,
        url=config.weaviate.url,
        auth_client_secret=weaviate.AuthApiKey(weaviate_api_key),
    )

    chatbot_service = providers.Factory(
        ChatbotService,
        weaviate_client=weaviate_client,
        openai_api_key=openai_api_key,
        verbose=config.chatbot.verbose,
        temperature=config.chatbot.temperature,
    )

    config.auth.secret_key.from_env("AUTH_SECRET_KEY")
    config.auth.username.from_env("AUTH_USERNAME")
    config.auth.password.from_env("AUTH_PASSWORD")

    auth_service = providers.Factory(
        AuthService,
        algorithm=config.auth.algorithm,
        access_token_expire_minutes=config.auth.access_token_expire_minutes,
        secret_key=config.auth.secret_key,
        username=config.auth.username,
        password=config.auth.password,
    )
