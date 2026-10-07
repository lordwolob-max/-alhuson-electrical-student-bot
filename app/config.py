from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-6-luna"
    openai_vector_store_id: str | None = None

    file_search_max_results: int = 8
    session_history_messages: int = 12

    rate_limit_requests: int = 30
    rate_limit_window_seconds: int = 600

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def openai_ready(self) -> bool:
        return bool(self.openai_api_key and self.openai_vector_store_id)


settings = Settings()
