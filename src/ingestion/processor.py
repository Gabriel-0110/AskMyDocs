"""Document processor for PDF and TXT files."""

import io
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import tiktoken
import PyPDF2
from config.settings import settings
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Handles document ingestion and text processing."""

    def __init__(self):
        """Initialize the document processor."""
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def extract_text_from_bytes(
        self, file_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        """Extract text content from file bytes."""
        file_type = Path(filename).suffix.lower().lstrip(".")

        if file_type not in settings.allowed_file_types:
            raise ValueError(f"Unsupported file type: {file_type}")

        try:
            if file_type == "pdf":
                return self._extract_from_pdf_bytes(file_bytes)
            elif file_type == "txt":
                return self._extract_from_txt_bytes(file_bytes)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Failed to extract text from {filename}: {e}")
            raise

    def _extract_from_pdf_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract text from PDF bytes."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

            text_content = []
            metadata = {"num_pages": len(pdf_reader.pages), "page_texts": []}

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(page_text)
                        metadata["page_texts"].append(
                            {"page": page_num + 1, "text_length": len(page_text)}
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to extract text from page {page_num + 1}: {e}"
                    )
                    continue

            full_text = "\n\n".join(text_content)

            return {
                "content": full_text,
                "metadata": metadata,
                "word_count": len(full_text.split()),
                "char_count": len(full_text),
            }

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise

    def _extract_from_txt_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        """Extract text from TXT bytes."""
        try:
            # Try UTF-8 first
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Fallback to latin-1
                content = file_bytes.decode("latin-1")
            except UnicodeDecodeError:
                # Last resort - ignore errors
                content = file_bytes.decode("utf-8", errors="ignore")

        return {
            "content": content,
            "metadata": {"encoding_detected": True},
            "word_count": len(content.split()),
            "char_count": len(content),
        }

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Chunk text into smaller segments for processing."""
        if metadata is None:
            metadata = {}

        # Clean and normalize text
        cleaned_text = self._clean_text(text)

        # Split into chunks
        chunks = self._split_text_by_tokens(
            cleaned_text,
            max_tokens=settings.chunk_size,
            overlap_tokens=settings.chunk_overlap,
        )

        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {**metadata, "chunk_index": i, "total_chunks": len(chunks)}

            processed_chunks.append(
                {
                    "content": chunk,
                    "token_count": self._count_tokens(chunk),
                    "metadata": chunk_metadata,
                }
            )

        logger.info(f"Text chunked into {len(processed_chunks)} segments")
        return processed_chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might interfere with processing
        text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)

        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        return text.strip()

    def _split_text_by_tokens(
        self, text: str, max_tokens: int, overlap_tokens: int
    ) -> List[str]:
        """Split text by token count with overlap."""
        tokens = self.encoding.encode(text)

        if len(tokens) <= max_tokens:
            return [text]

        chunks = []
        start_idx = 0

        while start_idx < len(tokens):
            # Get chunk tokens
            end_idx = min(start_idx + max_tokens, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]

            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)

            # Clean up potential truncated words at chunk boundaries
            if end_idx < len(tokens):
                # Find the last complete sentence or word
                chunk_text = self._find_clean_break(chunk_text)

            chunks.append(chunk_text)

            # Move start position with overlap
            if end_idx >= len(tokens):
                break

            start_idx = end_idx - overlap_tokens

            # Ensure we make progress
            if start_idx <= 0 and len(chunks) > 1:
                start_idx = end_idx

        return chunks

    def _find_clean_break(self, text: str) -> str:
        """Find a clean break point in text (sentence or word boundary)."""
        # Try to break at sentence end
        sentence_breaks = [".", "!", "?", "\n\n"]
        for break_char in sentence_breaks:
            last_break = text.rfind(break_char)
            if last_break > len(text) * 0.7:  # Only if break is in last 30%
                return text[: last_break + 1].strip()

        # Fallback to word boundary
        last_space = text.rfind(" ")
        if last_space > len(text) * 0.5:  # Only if break is in last 50%
            return text[:last_space].strip()

        # If no good break found, return as is
        return text

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))

    def validate_file_size(self, file_size: int) -> bool:
        """Validate file size against limits."""
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
