"""Simplified RAG agent using OpenAI directly instead of pydantic-ai."""

from typing import List, Dict
from pydantic import BaseModel, Field
import openai
from src.database.client import SupabaseClient
from src.ingestion.embeddings import EmbeddingGenerator
from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DocumentChunk(BaseModel):
    """A relevant document chunk from the vector search."""

    content: str = Field(..., description="The text content of the chunk")
    document_id: str = Field(..., description="The ID of the source document")
    source_document: str = Field(..., description="The filename of the source document")
    similarity: float = Field(..., description="The similarity score (0.0 to 1.0)")


class RAGResponse(BaseModel):
    """Structured response from the RAG agent."""

    answer: str = Field(..., description="The answer to the user's question")
    confidence: float = Field(..., description="Confidence in the answer (0.0 to 1.0)")
    reasoning: str = Field(..., description="Explanation of how the answer was derived")
    sources: List[DocumentChunk] = Field(
        default_factory=list, description="Source documents used"
    )


class RAGAgent:
    """Simplified RAG agent using OpenAI directly."""

    def __init__(self):
        """Initialize the RAG agent."""
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        logger.info("Simple RAG Agent initialized successfully")

    async def query(
        self,
        question: str,
        db_client: SupabaseClient,
        embedding_generator: EmbeddingGenerator,
    ) -> RAGResponse:
        """Query the RAG system with a question."""
        logger.info(f"Processing query: {question[:100]}...")

        try:
            # Search for relevant documents
            embeddings = await embedding_generator.generate_embeddings([question])
            query_embedding = embeddings[0]

            results = await db_client.search_similar_chunks(
                query_embedding=query_embedding,
                limit=5,
                similarity_threshold=settings.similarity_threshold,
            )

            logger.info(f"Found {len(results)} relevant chunks with threshold {settings.similarity_threshold}")
            
            # Convert to DocumentChunk objects
            sources = []
            for result in results:
                logger.info(f"Chunk similarity: {result.get('similarity', 'N/A')} from {result.get('document_filename', 'Unknown')}")
                chunk = DocumentChunk(
                    content=result["content"],
                    document_id=result["document_id"],
                    source_document=result.get("document_filename", "Unknown"),
                    similarity=result["similarity"],
                )
                sources.append(chunk)

            # Generate response using OpenAI
            context = "\\n\\n".join(
                [f"Source ({s.source_document}): {s.content}" for s in sources]
            )
            
            logger.info(f"Context length: {len(context)} characters")
            if not context.strip():
                logger.warning("No context found for question - returning generic response")

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Answer based on provided context. Be concise and cite sources.",
                    },
                    {
                        "role": "user",
                        "content": f"Question: {question}\\n\\nContext: {context}",
                    },
                ],
                temperature=0.1,
                max_tokens=1000,
            )

            answer = response.choices[0].message.content or "No response generated"

            return RAGResponse(
                answer=answer,
                confidence=0.8 if sources else 0.3,
                reasoning="Generated response based on document search and OpenAI completion.",
                sources=sources,
            )

        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return RAGResponse(
                answer="I apologize, but I encountered an error processing your question.",
                confidence=0.0,
                reasoning=f"Error: {str(e)}",
                sources=[],
            )

    def health_check(self) -> Dict[str, bool]:
        """Perform a health check on the agent."""
        return {"agent": True, "openai_configured": bool(settings.openai_api_key)}
