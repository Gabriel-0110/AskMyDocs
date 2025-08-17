"""Configuration management for the RAG system."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment + Streamlit secrets support."""

    # Supabase Configuration
    supabase_url: str = Field(
        ..., description="Supabase project URL", validation_alias="SUPABASE_URL"
    )
    supabase_anon_key: str = Field(
        ..., description="Supabase anonymous key", validation_alias="SUPABASE_ANON_KEY"
    )
    supabase_service_role_key: Optional[str] = Field(
        default=None,
        description="Supabase service role key",
        validation_alias="SUPABASE_SERVICE_KEY",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ..., description="OpenAI API key", validation_alias="OPENAI_API_KEY"
    )
    openai_chat_model: str = Field(
        default="gpt-4o-mini", validation_alias="OPENAI_CHAT_MODEL"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small", validation_alias="OPENAI_EMBEDDING_MODEL"
    )

    # Application Configuration
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file: str = Field(default="rag_system.log",
                          validation_alias="LOG_FILE")
    chunk_size: int = Field(default=1000, validation_alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, validation_alias="CHUNK_OVERLAP")
    max_tokens: int = Field(
        default=4096, validation_alias="MAX_TOKENS_PER_CHUNK")

    # Retrieval settings
    similarity_threshold: float = Field(
        default=0.2, validation_alias="SIMILARITY_THRESHOLD"
    )
    max_search_results: int = Field(
        default=5, validation_alias="MAX_CONTEXT_CHUNKS"
    )

    # File Processing
    max_file_size_mb: int = Field(
        default=10, validation_alias="MAX_FILE_SIZE_MB")
    allowed_file_types: list[str] = Field(
        default=["pdf", "txt"], description="Allowed file types"
    )
    auth_mode: str = Field("public", validation_alias="AUTH_MODE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get settings instance with Streamlit Cloud fallback.

    Attempts to load from environment/.env first. If validation fails, and
    Streamlit is available, falls back to constructing from ``st.secrets``.
    If Streamlit isn't available, re-raises the original validation error.
    """
    try:
        # Normal env load (works if Streamlit injected secrets as env vars)
        return Settings()  # type: ignore[call-arg]
    except Exception as e:
        # Fallback: pull directly from Streamlit secrets if available
        try:
            import streamlit as st  # type: ignore
        except Exception:
            # Streamlit not available; surface the original error
            raise e

        return Settings(
            supabase_url=st.secrets.get("SUPABASE_URL", ""),
            supabase_anon_key=st.secrets.get("SUPABASE_ANON_KEY", ""),
            supabase_service_role_key=st.secrets.get("SUPABASE_SERVICE_KEY"),
            openai_api_key=st.secrets.get("OPENAI_API_KEY", ""),
            openai_chat_model=st.secrets.get(
                "OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            embedding_model=st.secrets.get(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            ),
            chunk_size=st.secrets.get("CHUNK_SIZE", 1000),
            chunk_overlap=st.secrets.get("CHUNK_OVERLAP", 200),
            max_tokens=st.secrets.get("MAX_TOKENS_PER_CHUNK", 4096),
            similarity_threshold=st.secrets.get("SIMILARITY_THRESHOLD", 0.2),
            max_search_results=st.secrets.get("MAX_CONTEXT_CHUNKS", 5),
            log_level=st.secrets.get("LOG_LEVEL", "INFO"),
            auth_mode=st.secrets.get("AUTH_MODE", "public"),
        )


# Global instance
settings = get_settings()
