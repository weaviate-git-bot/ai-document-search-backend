import weaviate
from dependency_injector import containers, providers
from dotenv import load_dotenv

from .database_providers.cosmos_conversation_database import CosmosConversationDatabase
from .services.auth_service import AuthService
from .services.chatbot_service import ChatbotService
from .services.conversation_service import ConversationService
from .utils.relative_path_from_file import relative_path_from_file

CONFIG_PATH = relative_path_from_file(__file__, "../config.yml")


class Container(containers.DeclarativeContainer):
    # Specify modules in which you want to use the @inject decorator.
    wiring_config = containers.WiringConfiguration(
        modules=[
            ".routers.auth_router",
            ".routers.users_router",
            ".routers.chatbot_router",
            ".routers.conversation_router",
        ]
    )

    config = providers.Configuration(yaml_files=[CONFIG_PATH])

    load_dotenv()

    config.cosmos.key.from_env("COSMOS_KEY")

    conversation_database = providers.Singleton(
        CosmosConversationDatabase,
        url=config.cosmos.url,
        key=config.cosmos.key,
        db_name=config.cosmos.db_name,
        offer_throughput=config.cosmos.offer_throughput,
    )

    conversation_service = providers.Factory(
        ConversationService,
        conversation_database=conversation_database,
    )

    config.openai.api_key.from_env("APP_OPENAI_API_KEY")
    config.weaviate.api_key.from_env("APP_WEAVIATE_API_KEY")

    auth_client_secret = providers.Factory(
        weaviate.AuthApiKey,
        api_key=config.weaviate.api_key,
    )

    weaviate_client = providers.Factory(
        weaviate.Client,
        url=config.weaviate.url,
        auth_client_secret=auth_client_secret,
        additional_headers=providers.Dict(
            {
                "X-OpenAI-Api-Key": config.openai.api_key,
            }
        ),
    )

    chatbot_service = providers.Factory(
        ChatbotService,
        weaviate_client=weaviate_client,
        openai_api_key=config.openai.api_key,
        question_answering_model=config.chatbot.question_answering_model,
        condense_question_model=config.chatbot.condense_question_model,
        weaviate_class_name=config.weaviate.class_name,
        num_sources=config.chatbot.num_sources,
        max_history_length=config.chatbot.max_history_length,
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
