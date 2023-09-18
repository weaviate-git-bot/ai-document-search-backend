from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secretkey: str

    model_config = SettingsConfigDict(env_file="ai_document_search_backend/.env")


settings = Settings()
