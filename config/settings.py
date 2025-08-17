"""Configuration management for the RAG system."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import streamlit as st


class Settings(BaseSettings):
        """Application settings with environment + st.secrets support."""

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
        auth_mode: str = Field("public", env="AUTH_MODE")

        model_config = {
            "env_file": ".env",
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
            "extra": "ignore",  # Ignore extra environment variables
        }


def get_settings() -> Settings:
    """Get settings instance with Streamlit Cloud fallback."""
    try:
        # Normal env load (works if Streamlit injected secrets as env vars)
        return Settings()
    except Exception:
        # Fallback: pull directly from st.secrets
        return Settings(
            supabase_url=st.secrets.get("SUPABASE_URL", ""),
            supabase_anon_key=st.secrets.get("SUPABASE_ANON_KEY", ""),
            supabase_service_role_key=st.secrets.get("SUPABASE_SERVICE_KEY"),
            openai_api_key=st.secrets.get("OPENAI_API_KEY", ""),
            openai_chat_model=st.secrets.get("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            embedding_model=st.secrets.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            chunk_size=st.secrets.get("CHUNK_SIZE", 1000),
            chunk_overlap=st.secrets.get("CHUNK_OVERLAP", 200),
            max_tokens=st.secrets.get("MAX_TOKENS_PER_CHUNK", 1500),
            similarity_threshold=st.secrets.get("SIMILARITY_THRESHOLD", 0.7),
            max_search_results=st.secrets.get("MAX_CONTEXT_CHUNKS", 10),
            log_level=st.secrets.get("LOG_LEVEL", "INFO"),
            auth_mode=st.secrets.get("AUTH_MODE", "public"),
        )


# Global instance
settings = get_settings()
