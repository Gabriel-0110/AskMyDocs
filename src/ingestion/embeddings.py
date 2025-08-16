"""Embedding generation service using OpenAI API."""

import asyncio
from typing import List, Dict, Any
import openai
from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using OpenAI API."""

    def __init__(self):
        """Initialize OpenAI client with API key."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.batch_size = 100  # OpenAI's batch limit for embeddings

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0] if embeddings else []

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []

        try:
            # Process in batches to respect API limits
            all_embeddings = []

            for i in range(0, len(texts), self.batch_size):
                batch = texts[i : i + self.batch_size]

                # Create embeddings using OpenAI API
                response = self.client.embeddings.create(model=self.model, input=batch)

                batch_embeddings = [embedding.embedding for embedding in response.data]
                all_embeddings.extend(batch_embeddings)

                logger.debug(
                    f"Generated embeddings for batch {i // self.batch_size + 1}"
                )

                # Small delay to be nice to the API
                if i + self.batch_size < len(texts):
                    await asyncio.sleep(0.1)

            logger.info(f"Generated embeddings for {len(texts)} texts")
            return all_embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    async def generate_embeddings_for_chunks(
        self, chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate embeddings for document chunks."""
        if not chunks:
            return []

        try:
            # Extract text content from chunks
            texts = [chunk["content"] for chunk in chunks]

            # Generate embeddings
            embeddings = await self.generate_embeddings(texts)

            # Add embeddings to chunks
            enhanced_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                enhanced_chunk = chunk.copy()
                enhanced_chunk["embedding"] = embedding
                enhanced_chunks.append(enhanced_chunk)

            logger.info(f"Enhanced {len(enhanced_chunks)} chunks with embeddings")
            return enhanced_chunks

        except Exception as e:
            logger.error(f"Failed to generate embeddings for chunks: {e}")
            raise

    def get_embedding_dimensions(self) -> int:
        """Get the dimensions of embeddings for the current model."""
        return settings.embedding_dimensions

    async def test_connection(self) -> bool:
        """Test OpenAI API connection."""
        try:
            test_embedding = await self.generate_embedding("test connection")
            return len(test_embedding) > 0
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False


# Global embedding generator instance
embedding_generator = EmbeddingGenerator()
