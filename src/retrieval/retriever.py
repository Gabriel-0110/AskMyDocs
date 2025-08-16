"""
Vector retrieval system for the RAG pipeline.
Handles similarity search and context preparation.
"""

import logging
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from functools import lru_cache
import hashlib
import json

from src.database.client import db_client
from src.ingestion.embeddings import embedding_service
from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Result from a retrieval operation."""
    chunks: List[Dict[str, Any]]
    query_embedding: List[float]
    search_time_ms: int
    total_results: int
    avg_similarity: float


class VectorRetriever:
    """Handles vector similarity search and context retrieval."""
    
    def __init__(self):
        """Initialize the retriever."""
        self.similarity_threshold = settings.similarity_threshold
        self.max_context_chunks = settings.max_context_chunks
    
    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_document_ids: Optional[List[str]] = None
    ) -> RetrievalResult:
        """
        Search for relevant document chunks using vector similarity.
        
        Args:
            query: Search query text
            max_results: Maximum number of results to return
            similarity_threshold: Minimum similarity score
            filter_document_ids: Optional list of document IDs to filter by
            
        Returns:
            RetrievalResult with matching chunks and metadata
            
        Raises:
            Exception: If search fails
        """
        start_time = time.time()
        
        try:
            # Use provided values or defaults
            max_results = max_results or self.max_context_chunks
            similarity_threshold = similarity_threshold or self.similarity_threshold
            
            logger.info(f"Searching for query: {query[:100]}...")
            
            # Generate query embedding
            query_embedding = await embedding_service.embed_query(query)
            
            # Perform vector similarity search
            chunks = await db_client.search_similar_chunks(
                query_embedding=query_embedding,
                similarity_threshold=similarity_threshold,
                match_count=max_results,
                filter_document_ids=filter_document_ids
            )
            
            search_time_ms = int((time.time() - start_time) * 1000)
            
            # Calculate average similarity
            avg_similarity = 0.0
            if chunks:
                avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)
            
            result = RetrievalResult(
                chunks=chunks,
                query_embedding=query_embedding,
                search_time_ms=search_time_ms,
                total_results=len(chunks),
                avg_similarity=avg_similarity
            )
            
            logger.info(f"Found {len(chunks)} relevant chunks in {search_time_ms}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during vector search: {str(e)}")
            raise
    
    def prepare_context(
        self,
        chunks: List[Dict[str, Any]],
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Prepare context from retrieved chunks for the AI agent.
        
        Args:
            chunks: List of retrieved chunks
            max_tokens: Maximum tokens for context (uses system default if None)
            
        Returns:
            Dictionary with prepared context and metadata
        """
        try:
            if not chunks:
                return {
                    'context': '',
                    'sources': [],
                    'total_chunks': 0,
                    'total_tokens': 0
                }
            
            # Sort chunks by similarity (descending)
            sorted_chunks = sorted(
                chunks,
                key=lambda x: x.get('similarity', 0),
                reverse=True
            )
            
            # Build context while respecting token limits
            context_parts = []
            sources = []
            total_tokens = 0
            max_tokens = max_tokens or (settings.max_tokens_per_chunk * 5)  # Default limit
            
            for i, chunk in enumerate(sorted_chunks):
                chunk_content = chunk.get('content', '')
                chunk_tokens = chunk.get('token_count', len(chunk_content.split()))
                
                # Check if adding this chunk would exceed token limit
                if total_tokens + chunk_tokens > max_tokens and context_parts:
                    logger.info(f"Stopping at chunk {i} due to token limit ({total_tokens} tokens)")
                    break
                
                # Add chunk to context
                filename = chunk.get('filename', 'unknown')
                chunk_index = chunk.get('chunk_index', i)
                similarity = chunk.get('similarity', 0)
                
                # Format the context entry
                context_entry = f"[Source: {filename}, Chunk {chunk_index + 1}]\\n{chunk_content}\\n"
                context_parts.append(context_entry)
                
                # Add to sources for attribution
                source_info = {
                    'document_id': chunk.get('document_id'),
                    'filename': filename,
                    'chunk_index': chunk_index,
                    'similarity': similarity,
                    'content_preview': chunk_content[:200] + '...' if len(chunk_content) > 200 else chunk_content,
                    'token_count': chunk_tokens
                }
                sources.append(source_info)
                
                total_tokens += chunk_tokens
            
            # Join all context parts
            full_context = "\\n\\n".join(context_parts)
            
            result = {
                'context': full_context,
                'sources': sources,
                'total_chunks': len(sources),
                'total_tokens': total_tokens,
                'truncated': len(sources) < len(chunks)
            }
            
            logger.info(f"Prepared context with {len(sources)} chunks ({total_tokens} tokens)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error preparing context: {str(e)}")
            return {
                'context': '',
                'sources': [],
                'total_chunks': 0,
                'total_tokens': 0,
                'error': str(e)
            }
    
    async def search_and_prepare(
        self,
        query: str,
        max_results: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        filter_document_ids: Optional[List[str]] = None,
        max_context_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Combined search and context preparation operation.
        
        Args:
            query: Search query text
            max_results: Maximum number of chunks to retrieve
            similarity_threshold: Minimum similarity score
            filter_document_ids: Optional document ID filter
            max_context_tokens: Maximum tokens for prepared context
            
        Returns:
            Dictionary with retrieval results and prepared context
        """
        try:
            # Perform search
            search_result = await self.search(
                query=query,
                max_results=max_results,
                similarity_threshold=similarity_threshold,
                filter_document_ids=filter_document_ids
            )
            
            # Prepare context from results
            context_data = self.prepare_context(
                chunks=search_result.chunks,
                max_tokens=max_context_tokens
            )
            
            # Combine results
            combined_result = {
                'query': query,
                'search_time_ms': search_result.search_time_ms,
                'total_results': search_result.total_results,
                'avg_similarity': search_result.avg_similarity,
                'query_embedding': search_result.query_embedding,
                **context_data
            }
            
            return combined_result
            
        except Exception as e:
            logger.error(f"Error in search and prepare: {str(e)}")
            raise
    
    def rank_results(
        self,
        chunks: List[Dict[str, Any]],
        query: str,
        boost_recent: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Re-rank search results using additional scoring factors.
        
        Args:
            chunks: List of retrieved chunks
            query: Original query for relevance scoring
            boost_recent: Whether to boost more recent documents
            
        Returns:
            Re-ranked list of chunks
        """
        try:
            if not chunks:
                return []
            
            # Create scored results
            scored_chunks = []
            
            for chunk in chunks:
                score = chunk.get('similarity', 0.0)
                
                # Boost based on content length (prefer more substantial chunks)
                content_length = len(chunk.get('content', ''))
                if content_length > 500:
                    score += 0.05
                elif content_length < 100:
                    score -= 0.05
                
                # Boost based on token count
                token_count = chunk.get('token_count', 0)
                if token_count > settings.chunk_size * 0.8:
                    score += 0.03
                
                # Optional: boost recent documents
                if boost_recent:
                    # This would require accessing document metadata
                    pass
                
                chunk_with_score = chunk.copy()
                chunk_with_score['final_score'] = score
                scored_chunks.append(chunk_with_score)
            
            # Sort by final score
            ranked_chunks = sorted(
                scored_chunks,
                key=lambda x: x['final_score'],
                reverse=True
            )
            
            logger.debug(f"Re-ranked {len(chunks)} results")
            return ranked_chunks
            
        except Exception as e:
            logger.error(f"Error ranking results: {str(e)}")
            return chunks  # Return original order on error
    
    async def get_document_chunks(
        self,
        document_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific document.
        
        Args:
            document_id: ID of the document
            limit: Optional limit on number of chunks
            
        Returns:
            List of chunks for the document
        """
        try:
            # This would require a method in the database client
            # For now, we can use search with a very low threshold
            empty_query_embedding = [0.0] * 1536  # Dummy embedding
            
            chunks = await db_client.search_similar_chunks(
                query_embedding=empty_query_embedding,
                similarity_threshold=0.0,
                match_count=limit or 1000,
                filter_document_ids=[document_id]
            )
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x.get('chunk_index', 0))
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error getting document chunks: {str(e)}")
            return []


# Global retriever instance
vector_retriever = VectorRetriever()