"""
Basic tests for RAG system components.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.ingestion.processor import document_processor
from src.ingestion.embeddings import embedding_service


class TestDocumentProcessor:
    """Test cases for document processing."""
    
    def test_token_counting(self):
        """Test token counting functionality."""
        text = "This is a test document with some text."
        token_count = document_processor.count_tokens(text)
        
        assert isinstance(token_count, (int, float))
        assert token_count > 0
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        dirty_text = "This   has    excessive   whitespace.\\n\\n\\n\\n\\nAnd extra newlines."
        clean_text = document_processor.clean_text(dirty_text)
        
        assert "   " not in clean_text
        assert "\\n\\n\\n" not in clean_text
        assert len(clean_text) < len(dirty_text)
    
    def test_chunking(self):
        """Test text chunking functionality."""
        text = "This is a long text. " * 100  # Create long text
        metadata = {"test": True}
        
        chunks = document_processor.create_chunks(text, metadata)
        
        assert len(chunks) > 1  # Should create multiple chunks
        assert all('content' in chunk for chunk in chunks)
        assert all('token_count' in chunk for chunk in chunks)
        assert all('metadata' in chunk for chunk in chunks)


class TestEmbeddingService:
    """Test cases for embedding generation."""
    
    def test_embedding_validation(self):
        """Test embedding validation."""
        # Valid embedding
        valid_embedding = [0.1] * 1536
        assert embedding_service.validate_embedding(valid_embedding)
        
        # Invalid embeddings
        assert not embedding_service.validate_embedding([0.1] * 100)  # Wrong dimension
        assert not embedding_service.validate_embedding("not a list")  # Wrong type
        assert not embedding_service.validate_embedding([])  # Empty
    
    @pytest.mark.asyncio
    async def test_embedding_generation_mock(self):
        """Test embedding generation with mocked API."""
        with patch.object(embedding_service.client.embeddings, 'create') as mock_create:
            # Mock the API response
            mock_response = Mock()
            mock_response.data = [Mock()]
            mock_response.data[0].embedding = [0.1] * 1536
            mock_create.return_value = mock_response
            
            text = "Test text for embedding"
            embedding = await embedding_service.generate_embedding(text)
            
            assert len(embedding) == 1536
            assert all(isinstance(x, (int, float)) for x in embedding)


class TestConfiguration:
    """Test configuration and settings."""
    
    def test_settings_loading(self):
        """Test that settings can be loaded."""
        assert hasattr(settings, 'chunk_size')
        assert hasattr(settings, 'similarity_threshold')
        assert hasattr(settings, 'max_context_chunks')
        
        # Check defaults
        assert settings.chunk_size > 0
        assert 0 <= settings.similarity_threshold <= 1
        assert settings.max_context_chunks > 0


if __name__ == "__main__":
    pytest.main([__file__])