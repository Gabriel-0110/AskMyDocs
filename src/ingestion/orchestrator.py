"""Document ingestion orchestrator."""

from typing import Dict, Any, List, Optional
from uuid import UUID
from pathlib import Path
from src.ingestion.processor import DocumentProcessor
from src.ingestion.embeddings import EmbeddingGenerator
from src.database.client import SupabaseClient
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DocumentOrchestrator:
    """Orchestrates the complete document ingestion pipeline."""

    def __init__(self):
        """Initialize the orchestrator with required components."""
        self.processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.db_client = SupabaseClient()

    async def ingest_document_from_bytes(
        self, file_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        """Process a document from bytes through the complete pipeline."""
        logger.info(f"Starting document ingestion: {filename}")

        document_id = None  # Initialize to handle error cases

        try:
            # Validate file size
            file_size = len(file_bytes)
            if not self.processor.validate_file_size(file_size):
                raise ValueError(f"File size {file_size} bytes exceeds limit")

            # Extract file information
            file_type = Path(filename).suffix.lower().lstrip(".")

            # Extract text content
            logger.info(f"Extracting text from {filename}")
            extraction_result = self.processor.extract_text_from_bytes(
                file_bytes, filename
            )
            content = extraction_result["content"]
            metadata = extraction_result["metadata"]

            # Insert document record
            document_id = await self.db_client.insert_document(
                filename=filename,
                file_type=file_type,
                content=content,
                metadata=metadata,
                file_size=file_size,
            )

            # Update status to processing
            await self.db_client.update_document_status(document_id, "processing")

            # Chunk the text
            logger.info(f"Chunking text for document {document_id}")
            chunks = self.processor.chunk_text(content, metadata)

            if not chunks:
                raise ValueError("No content chunks were generated")

            # Generate embeddings for chunks
            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            enhanced_chunks = (
                await self.embedding_generator.generate_embeddings_for_chunks(chunks)
            )

            # Insert chunks into database
            logger.info(f"Inserting {len(enhanced_chunks)} chunks into database")
            await self.db_client.insert_document_chunks(document_id, enhanced_chunks)

            # Update document status to completed
            await self.db_client.update_document_status(document_id, "completed")

            result = {
                "success": True,
                "document_id": str(document_id),
                "filename": filename,
                "chunks_created": len(enhanced_chunks),
                "total_tokens": sum(
                    chunk.get("token_count", 0) for chunk in enhanced_chunks
                ),
                "processing_time": None,  # Would be calculated by caller
            }

            logger.info(f"Document ingestion completed: {filename} -> {document_id}")
            return result

        except Exception as e:
            logger.error(f"Document ingestion failed for {filename}: {e}")

            # Update document status to error if document was created
            try:
                if document_id is not None:
                    await self.db_client.update_document_status(
                        document_id, "error", str(e)
                    )
            except Exception:
                pass

            return {"success": False, "error": str(e), "filename": filename}

    async def ingest_document_from_path(self, file_path: str) -> Dict[str, Any]:
        """Process a document from file path."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            file_bytes = f.read()

        return await self.ingest_document_from_bytes(file_bytes, path.name)

    async def batch_ingest_documents(
        self, file_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """Process multiple documents in batch."""
        results = []

        for file_path in file_paths:
            try:
                result = await self.ingest_document_from_path(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch processing failed for {file_path}: {e}")
                results.append(
                    {
                        "success": False,
                        "error": str(e),
                        "filename": Path(file_path).name,
                    }
                )

        return results

    async def get_ingestion_status(self, document_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the current status of document ingestion."""
        document = await self.db_client.get_document_by_id(document_id)

        if not document:
            return None

        return {
            "document_id": document["id"],
            "filename": document["filename"],
            "status": document["status"],
            "upload_date": document["upload_date"],
            "processed_date": document.get("processed_date"),
            "error_message": document.get("error_message"),
            "file_size": document["file_size"],
            "file_type": document["file_type"],
        }

    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all components."""
        health = {}

        try:
            health["database"] = await self.db_client.health_check()
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health["database"] = False

        try:
            health["embeddings"] = await self.embedding_generator.test_connection()
        except Exception as e:
            logger.error(f"Embeddings health check failed: {e}")
            health["embeddings"] = False

        health["overall"] = all(health.values())

        return health


# Global orchestrator instance
document_orchestrator = DocumentOrchestrator()
