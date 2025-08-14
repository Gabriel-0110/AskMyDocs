"""Database client for Supabase integration with pgvector."""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from supabase import create_client, Client
from supabase.client import ClientOptions
from config.settings import settings
from src.utils.logging_simple import get_logger

logger = get_logger(__name__)


class SupabaseClient:
    """Supabase client for RAG system database operations."""

    def __init__(self):
        """Initialize Supabase client with configuration."""
        self._client: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the Supabase client."""
        try:
            self._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_anon_key,
                options=ClientOptions(
                    postgrest_client_timeout=10, storage_client_timeout=10
                ),
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    @property
    def client(self) -> Client:
        """Get the Supabase client instance."""
        if self._client is None:
            self._initialize_client()
        assert self._client is not None, "Client should be initialized"
        return self._client

    async def insert_document(
        self,
        filename: str,
        file_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        file_size: Optional[int] = None,
    ) -> UUID:
        """Insert a new document into the database."""
        if metadata is None:
            metadata = {}

        document_id = uuid4()

        try:
            self.client.table("documents").insert(
                {
                    "id": str(document_id),
                    "filename": filename,
                    "file_type": file_type,
                    "content": content,
                    "metadata": metadata,
                    "file_size": file_size,
                    "status": "uploaded",
                }
            ).execute()

            logger.info(
                f"Document inserted successfully: {filename} (ID: {document_id})"
            )
            return document_id

        except Exception as e:
            logger.error(f"Failed to insert document {filename}: {e}")
            raise

    async def insert_document_chunks(
        self, document_id: UUID, chunks: List[Dict[str, Any]]
    ) -> List[UUID]:
        """Insert document chunks with embeddings."""
        chunk_ids = []

        try:
            chunk_data = []
            for i, chunk in enumerate(chunks):
                chunk_id = uuid4()
                chunk_ids.append(chunk_id)

                chunk_data.append(
                    {
                        "id": str(chunk_id),
                        "document_id": str(document_id),
                        "chunk_index": i,
                        "content": chunk["content"],
                        "token_count": chunk.get("token_count"),
                        "embedding": chunk.get("embedding"),
                        "metadata": chunk.get("metadata", {}),
                    }
                )

            self.client.table("document_chunks").insert(chunk_data).execute()

            logger.info(f"Inserted {len(chunks)} chunks for document {document_id}")
            return chunk_ids

        except Exception as e:
            logger.error(f"Failed to insert chunks for document {document_id}: {e}")
            raise

    async def update_document_status(
        self, document_id: UUID, status: str, error_message: Optional[str] = None
    ) -> None:
        """Update document processing status."""
        try:
            update_data = {"status": status}
            if status == "completed":
                update_data["processed_date"] = "now()"
            if error_message:
                update_data["error_message"] = error_message

            self.client.table("documents").update(update_data).eq(
                "id", str(document_id)
            ).execute()

            logger.info(f"Document status updated: {document_id} -> {status}")

        except Exception as e:
            logger.error(f"Failed to update document status {document_id}: {e}")
            raise

    async def search_similar_chunks(
        self,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar document chunks using vector similarity."""
        try:
            # Convert embedding to string format for pgvector
            embedding_str = f"[{','.join(map(str, query_embedding))}]"

            # Perform vector similarity search
            result = self.client.rpc(
                "search_document_chunks",
                {
                    "query_embedding": embedding_str,
                    "similarity_threshold": similarity_threshold,
                    "match_count": limit,
                },
            ).execute()

            chunks = result.data if result.data else []

            logger.info(f"Found {len(chunks)} similar chunks")
            return chunks

        except Exception as e:
            logger.error(f"Failed to search similar chunks: {e}")
            raise

    async def get_document_by_id(self, document_id: UUID) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            result = (
                self.client.table("documents")
                .select("*")
                .eq("id", str(document_id))
                .single()
                .execute()
            )
            return result.data if result.data else None

        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {e}")
            return None

    async def get_documents_list(
        self, status: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get list of documents with optional status filter."""
        try:
            query = (
                self.client.table("documents")
                .select("*")
                .order("upload_date", desc=True)
            )

            if status:
                query = query.eq("status", status)

            result = query.limit(limit).execute()
            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Failed to get documents list: {e}")
            raise

    async def log_search_query(
        self,
        query_text: str,
        query_embedding: List[float],
        response_text: str,
        source_document_ids: List[UUID],
        response_time_ms: int,
        relevance_score: Optional[float] = None,
    ) -> None:
        """Log search query for analytics."""
        try:
            embedding_str = f"[{','.join(map(str, query_embedding))}]"

            self.client.table("search_queries").insert(
                {
                    "query_text": query_text,
                    "query_embedding": embedding_str,
                    "response_text": response_text,
                    "source_document_ids": [
                        str(doc_id) for doc_id in source_document_ids
                    ],
                    "response_time_ms": response_time_ms,
                    "relevance_score": relevance_score,
                }
            ).execute()

            logger.debug(f"Search query logged: {query_text[:50]}...")

        except Exception as e:
            logger.warning(f"Failed to log search query: {e}")
            # Don't raise here as this is not critical functionality

    async def health_check(self) -> bool:
        """Perform database health check."""
        try:
            self.client.table("documents").select("id").limit(1).execute()
            logger.info("Database health check passed")
            return True

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database client instance
db_client = SupabaseClient()
