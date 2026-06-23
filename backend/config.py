from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # LLM
    gemini_api_key: str

    # Pinecone
    pinecone_api_key: str
    pinecone_index_name: str = "temporal-rag"
    pinecone_environment: str = "us-east-1"

    # Database
    postgres_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    environment: str = "development"
    log_level: str = "INFO"

    # Temporal tuning
    decay_rate_policy: float = 0.15
    decay_rate_research: float = 0.03
    decay_rate_changelog: float = 0.20
    decay_rate_news: float = 0.25
    decay_rate_default: float = 0.10

    conflict_threshold_days: int = 90
    topic_similarity_threshold: float = 0.88

    # Embedding
    embedding_model: str = "models/text-embedding-004"
    embedding_dimension: int = 768

    # LLM models
    main_llm_model: str = "gemini-1.5-pro"
    fast_llm_model: str = "gemini-1.5-flash"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
