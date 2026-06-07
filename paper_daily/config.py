from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    telegram_token: str
    telegram_chat_id: str

    paper_queries: list[str] = ["machine learning", "deep learning"]
    paper_venues: list[str] = []
    profile_path: str = "profile.txt"
    candidates_per_query: int = 100
    top_k: int = 30
    model_name: str = "allenai/specter2_base"
    abstract_max_chars: int = 800

    @field_validator("paper_queries", "paper_venues", mode="before")
    @classmethod
    def parse_csv(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v  # type: ignore[return-value]
