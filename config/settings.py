"""Configuration management for the RAG system."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Supabase Configuration
    supabase_url: str = Field(..., env="SUPABASE_URL", description="Supabase project URL")
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY", description="Supabase anonymous key")
    supabase_service_role_key: Optional[str] = Field(
        default=None, env="SUPABASE_SERVICE_KEY", description="Supabase service role key"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY", description="OpenAI API key")
    openai_chat_model: str = Field(default="gpt-4o-mini", env="OPENAI_CHAT_MODEL")
    embedding_model: str = Field(default="text-embedding-3-small", env="OPENAI_EMBEDDING_MODEL")

    # Application Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="rag_system.log", env="LOG_FILE")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_tokens: int = Field(default=4096, env="MAX_TOKENS_PER_CHUNK")

    # Retrieval settings
    similarity_threshold: float = Field(default=0.2, env="SIMILARITY_THRESHOLD")
    max_search_results: int = Field(default=5, env="MAX_CONTEXT_CHUNKS")

    # File Processing
    max_file_size_mb: int = Field(default=10, env="MAX_FILE_SIZE_MB")
    allowed_file_types: list[str] = Field(default=["pdf", "txt"], description="Allowed file types")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra environment variables
    }


def get_settings() -> Settings:
    """Get settings instance with proper error handling."""
    try:
        settings_instance = Settings()

        # Validate required settings
        if not settings_instance.supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not settings_instance.supabase_anon_key:
            raise ValueError("SUPABASE_ANON_KEY environment variable is required")
        if not settings_instance.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return settings_instance

    except Exception as e:
        print(f"Error loading settings: {e}")
        raise


# Global settings instance
settings = get_settings()
