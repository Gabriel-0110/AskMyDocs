"""
Validation utilities for the RAG system.
Provides comprehensive validation for documents, embeddings, and system components.
"""

import logging
import re
import hashlib
from typing import List, Dict, Any, Optional, Set, Union, Tuple
from pathlib import Path
from dataclasses import dataclass
import mimetypes

from config.settings import settings

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass
class ValidationResult:
    """Result from validation operations."""
    valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]
    
    def add_error(self, error: str, code: str = None):
        """Add an error to the result."""
        self.valid = False
        self.errors.append(error)
        if code:
            self.details[f'error_code_{len(self.errors)}'] = code
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)


class DocumentValidator:
    """Validator for document files and content."""
    
    def __init__(self):
        """Initialize the document validator."""
        self.supported_types = {'pdf', 'txt'}
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024
        self.min_content_length = 10
        self.max_content_length = 50 * 1024 * 1024  # 50MB of text
    
    def validate_file(self, filename: str, file_content: bytes, 
                     declared_type: Optional[str] = None) -> ValidationResult:
        """
        Validate a document file comprehensively.
        
        Args:
            filename: Name of the file
            file_content: File content as bytes
            declared_type: Optionally declared file type
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        # Basic file validation
        self._validate_filename(filename, result)
        self._validate_file_size(file_content, result)
        self._validate_file_type(filename, file_content, declared_type, result)
        
        # Content validation
        if result.valid:
            self._validate_content_basic(file_content, result)
            
            # Type-specific validation
            file_ext = Path(filename).suffix.lower().lstrip('.')
            if file_ext == 'pdf':
                self._validate_pdf_content(file_content, result)
            elif file_ext == 'txt':
                self._validate_text_content(file_content, result)
        
        result.details.update({
            'filename': filename,
            'file_size': len(file_content),
            'detected_type': self._detect_file_type(file_content),
            'validation_timestamp': str(time.time())
        })
        
        return result
    
    def _validate_filename(self, filename: str, result: ValidationResult):
        """Validate filename format and safety."""
        if not filename or not filename.strip():
            result.add_error("Filename is empty or whitespace", "EMPTY_FILENAME")
            return
        
        # Check for dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        if any(char in filename for char in dangerous_chars):
            result.add_error("Filename contains unsafe characters", "UNSAFE_FILENAME")
        
        # Check filename length
        if len(filename) > 255:
            result.add_error("Filename too long (>255 characters)", "FILENAME_TOO_LONG")
        
        # Check for valid extension
        file_ext = Path(filename).suffix.lower().lstrip('.')
        if file_ext not in self.supported_types:
            result.add_error(f"Unsupported file type: {file_ext}. Supported: {self.supported_types}", "UNSUPPORTED_TYPE")
    
    def _validate_file_size(self, file_content: bytes, result: ValidationResult):
        """Validate file size constraints."""
        file_size = len(file_content)
        
        if file_size == 0:
            result.add_error("File is empty", "EMPTY_FILE")
        elif file_size > self.max_file_size:
            result.add_error(
                f"File too large: {file_size / 1024 / 1024:.1f}MB > {settings.max_file_size_mb}MB",
                "FILE_TOO_LARGE"
            )
        elif file_size < 10:  # Less than 10 bytes
            result.add_error("File suspiciously small", "FILE_TOO_SMALL")
    
    def _validate_file_type(self, filename: str, file_content: bytes, 
                          declared_type: Optional[str], result: ValidationResult):
        """Validate file type consistency."""
        file_ext = Path(filename).suffix.lower().lstrip('.')
        detected_type = self._detect_file_type(file_content)
        
        # Check extension vs content mismatch
        if file_ext == 'pdf' and not detected_type.startswith('pdf'):
            result.add_warning(f"File extension suggests PDF but content appears to be {detected_type}")
        elif file_ext == 'txt' and not detected_type.startswith('text'):
            result.add_warning(f"File extension suggests text but content appears to be {detected_type}")
        
        # Check declared type vs actual
        if declared_type and declared_type != file_ext:
            result.add_warning(f"Declared type '{declared_type}' doesn't match extension '{file_ext}'")
    
    def _detect_file_type(self, file_content: bytes) -> str:
        """Detect file type from content."""
        if len(file_content) < 4:
            return "unknown"
        
        # Check PDF signature
        if file_content.startswith(b'%PDF-'):
            return "pdf"
        
        # Check for binary content (likely not text)
        try:
            # Try to decode as text
            text_content = file_content[:1024].decode('utf-8')
            # Check for common text patterns
            if any(char in text_content for char in ['\n', '\r', '\t']) or text_content.isprintable():
                return "text/plain"
        except UnicodeDecodeError:
            pass
        
        # Use mimetypes as fallback
        return "binary/unknown"
    
    def _validate_content_basic(self, file_content: bytes, result: ValidationResult):
        """Basic content validation."""
        content_size = len(file_content)
        
        if content_size > self.max_content_length:
            result.add_error(
                f"Content too large: {content_size / 1024 / 1024:.1f}MB",
                "CONTENT_TOO_LARGE"
            )
    
    def _validate_pdf_content(self, file_content: bytes, result: ValidationResult):
        """PDF-specific content validation."""
        try:
            from io import BytesIO
            import PyPDF2
            
            pdf_stream = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_stream)
            
            # Check if encrypted
            if pdf_reader.is_encrypted:
                result.add_error("PDF is encrypted and cannot be processed", "ENCRYPTED_PDF")
                return
            
            # Check number of pages
            num_pages = len(pdf_reader.pages)
            if num_pages == 0:
                result.add_error("PDF contains no pages", "NO_PAGES")
            elif num_pages > 1000:
                result.add_warning(f"PDF has many pages ({num_pages}) - processing may be slow")
            
            # Try to extract some text to verify readability
            text_found = False
            for i, page in enumerate(pdf_reader.pages[:5]):  # Check first 5 pages
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_found = True
                        break
                except Exception as e:
                    logger.debug(f"Error extracting text from page {i}: {str(e)}")
            
            if not text_found:
                result.add_warning("No readable text found in first 5 pages - may be image-based PDF")
            
            result.details['pdf_pages'] = num_pages
            
        except Exception as e:
            result.add_error(f"Error validating PDF content: {str(e)}", "PDF_VALIDATION_ERROR")
    
    def _validate_text_content(self, file_content: bytes, result: ValidationResult):
        """Text-specific content validation."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            decoded_text = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    decoded_text = file_content.decode(encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue
            
            if decoded_text is None:
                result.add_error("Could not decode text file with any supported encoding", "ENCODING_ERROR")
                return
            
            # Validate text content
            text_length = len(decoded_text)
            if text_length < self.min_content_length:
                result.add_error(f"Text content too short: {text_length} characters", "TEXT_TOO_SHORT")
            
            # Check for suspicious content
            null_bytes = decoded_text.count('\x00')
            if null_bytes > 0:
                result.add_warning(f"Text contains {null_bytes} null bytes - may be binary data")
            
            # Check text quality
            word_count = len(decoded_text.split())
            if word_count == 0:
                result.add_warning("Text appears to contain no words")
            elif word_count < 10:
                result.add_warning(f"Text contains very few words: {word_count}")
            
            result.details.update({
                'encoding_used': used_encoding,
                'character_count': text_length,
                'word_count': word_count,
                'line_count': decoded_text.count('\n') + 1
            })
            
        except Exception as e:
            result.add_error(f"Error validating text content: {str(e)}", "TEXT_VALIDATION_ERROR")


class EmbeddingValidator:
    """Validator for embedding vectors and related operations."""
    
    def __init__(self):
        """Initialize the embedding validator."""
        self.expected_dimensions = settings.get_embedding_dimensions()
        self.reasonable_value_range = (-10.0, 10.0)
        self.zero_tolerance = 1e-10
    
    def validate_embedding(self, embedding: List[float], context: str = "") -> ValidationResult:
        """
        Validate a single embedding vector.
        
        Args:
            embedding: Embedding vector to validate
            context: Optional context for better error messages
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        context_prefix = f"{context}: " if context else ""
        
        # Basic type checking
        if not isinstance(embedding, (list, tuple)):
            result.add_error(f"{context_prefix}Embedding must be a list or tuple", "INVALID_TYPE")
            return result
        
        if not embedding:
            result.add_error(f"{context_prefix}Embedding is empty", "EMPTY_EMBEDDING")
            return result
        
        # Dimension validation
        if len(embedding) != self.expected_dimensions:
            result.add_error(
                f"{context_prefix}Wrong embedding dimensions: got {len(embedding)}, expected {self.expected_dimensions}",
                "WRONG_DIMENSIONS"
            )
        
        # Value validation
        non_numeric = []
        out_of_range = []
        zero_count = 0
        
        for i, value in enumerate(embedding):
            if not isinstance(value, (int, float)):
                non_numeric.append(i)
                continue
            
            if not (self.reasonable_value_range[0] <= value <= self.reasonable_value_range[1]):
                out_of_range.append((i, value))
            
            if abs(value) < self.zero_tolerance:
                zero_count += 1
        
        if non_numeric:
            result.add_error(
                f"{context_prefix}Non-numeric values at indices: {non_numeric[:10]}",  # Show first 10
                "NON_NUMERIC_VALUES"
            )
        
        if out_of_range:
            result.add_warning(
                f"{context_prefix}Values outside reasonable range at {len(out_of_range)} positions"
            )
        
        if zero_count == len(embedding):
            result.add_error(f"{context_prefix}All embedding values are zero", "ALL_ZEROS")
        elif zero_count > len(embedding) * 0.9:  # More than 90% zeros
            result.add_warning(f"{context_prefix}Embedding is mostly zeros ({zero_count}/{len(embedding)})")
        
        # Statistical validation
        if len(embedding) > 0 and all(isinstance(v, (int, float)) for v in embedding):
            import statistics
            
            try:
                mean_val = statistics.mean(embedding)
                stdev_val = statistics.stdev(embedding) if len(embedding) > 1 else 0
                
                # Check for unusual statistical properties
                if abs(mean_val) > 1.0:
                    result.add_warning(f"{context_prefix}Unusual mean value: {mean_val:.4f}")
                
                if stdev_val < 0.01:
                    result.add_warning(f"{context_prefix}Very low standard deviation: {stdev_val:.6f}")
                elif stdev_val > 5.0:
                    result.add_warning(f"{context_prefix}Very high standard deviation: {stdev_val:.4f}")
                
                result.details.update({
                    'mean': mean_val,
                    'std_dev': stdev_val,
                    'zero_count': zero_count,
                    'out_of_range_count': len(out_of_range)
                })
                
            except statistics.StatisticsError as e:
                result.add_warning(f"{context_prefix}Could not calculate statistics: {str(e)}")
        
        result.details.update({
            'dimensions': len(embedding),
            'expected_dimensions': self.expected_dimensions,
            'validation_timestamp': str(time.time())
        })
        
        return result
    
    def validate_embedding_batch(self, embeddings: List[List[float]], 
                                context: str = "") -> ValidationResult:
        """
        Validate a batch of embeddings.
        
        Args:
            embeddings: List of embedding vectors
            context: Optional context for better error messages
            
        Returns:
            ValidationResult with validation outcome
        """
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        if not embeddings:
            result.add_error(f"{context}Empty embedding batch", "EMPTY_BATCH")
            return result
        
        # Validate each embedding
        invalid_count = 0
        dimension_mismatches = 0
        
        for i, embedding in enumerate(embeddings):
            individual_result = self.validate_embedding(embedding, f"Embedding {i}")
            
            if not individual_result.valid:
                invalid_count += 1
                # Only report first few errors to avoid spam
                if invalid_count <= 5:
                    result.errors.extend([f"Batch {context}: {error}" for error in individual_result.errors])
            
            if len(embedding) != self.expected_dimensions:
                dimension_mismatches += 1
        
        if invalid_count > 0:
            result.valid = False
            if invalid_count > 5:
                result.add_error(f"Total invalid embeddings in batch: {invalid_count}/{len(embeddings)}")
        
        # Batch-level statistics
        if embeddings and all(isinstance(emb, list) for emb in embeddings):
            dimensions = [len(emb) for emb in embeddings]
            unique_dimensions = set(dimensions)
            
            if len(unique_dimensions) > 1:
                result.add_error(f"Inconsistent dimensions in batch: {unique_dimensions}", "INCONSISTENT_DIMENSIONS")
        
        result.details.update({
            'batch_size': len(embeddings),
            'invalid_count': invalid_count,
            'dimension_mismatches': dimension_mismatches,
            'success_rate': (len(embeddings) - invalid_count) / len(embeddings)
        })
        
        return result
    
    def validate_similarity_scores(self, scores: List[float]) -> ValidationResult:
        """Validate similarity scores from vector search."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            details={}
        )
        
        if not scores:
            result.add_warning("No similarity scores to validate")
            return result
        
        # Check score ranges (should be 0-1 for cosine similarity)
        out_of_range = []
        for i, score in enumerate(scores):
            if not isinstance(score, (int, float)):
                result.add_error(f"Non-numeric similarity score at index {i}", "NON_NUMERIC_SCORE")
                continue
            
            if not (0.0 <= score <= 1.0):
                out_of_range.append((i, score))
        
        if out_of_range:
            result.add_error(f"Similarity scores outside [0,1] range: {len(out_of_range)} instances", "SCORES_OUT_OF_RANGE")
        
        # Check for proper ordering (should be descending)
        if len(scores) > 1:
            non_descending = []
            for i in range(len(scores) - 1):
                if scores[i] < scores[i + 1]:
                    non_descending.append(i)
            
            if non_descending:
                result.add_warning(f"Similarity scores not in descending order at positions: {non_descending[:5]}")
        
        result.details.update({
            'score_count': len(scores),
            'min_score': min(scores) if scores else None,
            'max_score': max(scores) if scores else None,
            'out_of_range_count': len(out_of_range)
        })
        
        return result


# Utility functions for quick validation
def validate_document_file(filename: str, content: bytes) -> bool:
    """Quick document validation - returns True if valid."""
    validator = DocumentValidator()
    result = validator.validate_file(filename, content)
    return result.valid


def validate_embedding_vector(embedding: List[float]) -> bool:
    """Quick embedding validation - returns True if valid."""
    validator = EmbeddingValidator()
    result = validator.validate_embedding(embedding)
    return result.valid


# Import time for timestamp
import time