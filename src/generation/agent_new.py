"""Pydantic AI agent with RAG search capabilities."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from src.database.client_new import SupabaseClient
from src.ingestion.embeddings_new import EmbeddingGenerator
from config.settings import settings
from src.utils.logging_simple import get_logger

logger = get_logger(__name__)


class RAGDependencies(BaseModel):
    """Dependencies for the RAG agent."""

    db_client: SupabaseClient
    embedding_generator: EmbeddingGenerator
    user_id: Optional[str] = None


class RAGResponse(BaseModel):
    """Structured response from the RAG agent."""

    answer: str = Field(description="The answer to the user's question")
    sources: List[Dict[str, Any]] = Field(
        description="Source documents and chunks used"
    )
    confidence: float = Field(
        description="Confidence score for the answer", ge=0.0, le=1.0
    )
    reasoning: str = Field(description="Explanation of how the answer was derived")


class RAGAgent:
    """RAG-powered AI agent using Pydantic AI framework."""

    def __init__(self):
        """Initialize the RAG agent."""
        self.agent = Agent(
            model="openai:gpt-4o",
            deps_type=RAGDependencies,
            result_type=RAGResponse,
            system_prompt=self._get_system_prompt(),
            retries=2,
        )

        # Register tools
        self._register_tools()

        logger.info("RAG Agent initialized successfully")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """
        You are a helpful AI assistant with access to a knowledge base through document search.
        
        When answering questions:
        1. Use the knowledge_search tool to find relevant information
        2. Base your answers on the retrieved content
        3. Clearly indicate the sources you used
        4. If you can't find relevant information, say so honestly
        5. Provide confidence scores based on the quality and relevance of sources
        6. Explain your reasoning process
        
        Always prioritize accuracy over completeness. If the available information 
        is insufficient or unclear, acknowledge the limitations.
        """

    def _register_tools(self) -> None:
        """Register tools for the agent."""

        @self.agent.tool
        async def knowledge_search(
            ctx: RunContext[RAGDependencies], query: str, limit: int = 5
        ) -> List[Dict[str, Any]]:
            """
            Search the knowledge base for information relevant to the query.

            Args:
                query: The search query
                limit: Maximum number of results to return

            Returns:
                List of relevant document chunks with metadata
            """
            logger.info(f"Knowledge search: {query}")

            try:
                # Generate embedding for the query
                query_embedding = await ctx.deps.embedding_generator.generate_embedding(
                    query
                )

                # Search for similar chunks
                results = await ctx.deps.db_client.search_similar_chunks(
                    query_embedding=query_embedding,
                    limit=limit,
                    similarity_threshold=settings.similarity_threshold,
                )

                # Format results for the agent
                formatted_results = []
                for result in results:
                    formatted_results.append(
                        {
                            "content": result["content"],
                            "similarity": result["similarity"],
                            "source_document": result["document_filename"],
                            "document_type": result["document_file_type"],
                            "chunk_index": result["chunk_index"],
                            "metadata": result.get("metadata", {}),
                        }
                    )

                logger.info(f"Found {len(formatted_results)} relevant chunks")
                return formatted_results

            except Exception as e:
                logger.error(f"Knowledge search failed: {e}")
                return []

        @self.agent.tool
        async def get_document_info(
            ctx: RunContext[RAGDependencies], document_id: str
        ) -> Optional[Dict[str, Any]]:
            """
            Get detailed information about a specific document.

            Args:
                document_id: The UUID of the document

            Returns:
                Document metadata and information
            """
            try:
                document_uuid = UUID(document_id)
                document = await ctx.deps.db_client.get_document_by_id(document_uuid)

                if document:
                    return {
                        "filename": document["filename"],
                        "file_type": document["file_type"],
                        "upload_date": str(document["upload_date"]),
                        "status": document["status"],
                        "file_size": document["file_size"],
                        "metadata": document.get("metadata", {}),
                    }
                return None

            except Exception as e:
                logger.error(f"Failed to get document info: {e}")
                return None

    async def query(
        self,
        question: str,
        db_client: SupabaseClient,
        embedding_generator: EmbeddingGenerator,
        user_id: Optional[str] = None,
    ) -> RAGResponse:
        """
        Process a user query and return a structured response.

        Args:
            question: The user's question
            db_client: Database client instance
            embedding_generator: Embedding generator instance
            user_id: Optional user identifier

        Returns:
            Structured response with answer and sources
        """
        logger.info(f"Processing query: {question[:100]}...")

        dependencies = RAGDependencies(
            db_client=db_client,
            embedding_generator=embedding_generator,
            user_id=user_id,
        )

        try:
            result = await self.agent.run(question, deps=dependencies)

            # Log the interaction
            if hasattr(result, "data") and isinstance(result.data, RAGResponse):
                response = result.data

                # Extract source document IDs for logging
                source_doc_ids = []
                for source in response.sources:
                    if "document_id" in source:
                        try:
                            source_doc_ids.append(UUID(source["document_id"]))
                        except ValueError:
                            pass

                # Generate query embedding for logging
                query_embedding = await embedding_generator.generate_embedding(question)

                # Log the search query
                await db_client.log_search_query(
                    query_text=question,
                    query_embedding=query_embedding,
                    response_text=response.answer,
                    source_document_ids=source_doc_ids,
                    response_time_ms=0,  # Would be calculated by timing wrapper
                    relevance_score=response.confidence,
                )

                logger.info(
                    f"Query processed successfully with {len(response.sources)} sources"
                )
                return response

            else:
                # Fallback response if structured output failed
                fallback_response = RAGResponse(
                    answer="I apologize, but I encountered an issue processing your request.",
                    sources=[],
                    confidence=0.0,
                    reasoning="The system encountered an unexpected error during processing.",
                )
                return fallback_response

        except Exception as e:
            logger.error(f"Query processing failed: {e}")

            error_response = RAGResponse(
                answer="I apologize, but I'm unable to process your request at the moment due to a technical issue.",
                sources=[],
                confidence=0.0,
                reasoning=f"Error occurred during processing: {str(e)}",
            )
            return error_response

    async def health_check(self) -> Dict[str, bool]:
        """Perform a health check on the agent."""
        try:
            # Simple test - just check that agent exists
            # In production you might want more comprehensive checks
            return {"agent": True}

        except Exception as e:
            logger.error(f"Agent health check failed: {e}")
            return {"agent": False}


# Global RAG agent instance
rag_agent = RAGAgent()
