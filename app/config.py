from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    gemini_api_key: str
    gemini_llm_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 768

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Single instance imported by the rest of the app.
settings = Settings()
