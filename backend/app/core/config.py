
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResearchPilot AI"
    app_version: str = "0.1.0"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"

    model_config = SettingsConfigDict(
        env_prefix="RESEARCHPILOT_",
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
