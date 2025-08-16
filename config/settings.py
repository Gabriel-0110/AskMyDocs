"""Configuration management for the RAG system."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Supabase Configuration
    supabase_url: str = Field(default="", description="Supabase project URL")
    supabase_anon_key: str = Field(default="", description="Supabase anonymous key")
    supabase_service_role_key: Optional[str] = Field(
        default=None, description="Supabase service role key"
    )

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")

    # Application Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="rag_system.log", description="Log file path")
    chunk_size: int = Field(
        default=1000, description="Document chunk size for processing"
    )
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    max_tokens: int = Field(default=4096, description="Maximum tokens for generation")

    # Vector Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model"
    )
    embedding_dimensions: int = Field(
        default=1536, description="Embedding vector dimensions"
    )
    similarity_threshold: float = Field(
        default=0.2, description="Minimum similarity threshold for retrieval"
    )
    max_search_results: int = Field(
        default=5, description="Maximum number of search results to return"
    )

    # File Processing
    max_file_size_mb: int = Field(default=10, description="Maximum file size in MB")
    allowed_file_types: list[str] = Field(
        default=["pdf", "txt"], description="Allowed file types for upload"
    )

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
        print(
            "Please ensure you have a .env file with the required environment variables:"
        )
        print("- SUPABASE_URL")
        print("- SUPABASE_ANON_KEY")
        print("- OPENAI_API_KEY")
        raise


# Global settings instance
settings = get_settings()
