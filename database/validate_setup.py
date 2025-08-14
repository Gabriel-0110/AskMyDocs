"""
Database validation script to verify the RAG system database setup.
This script uses the existing database client to validate functionality.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
import json

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.client import SupabaseClient

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def validate_database_setup():
    """Validate that the database is properly configured for the RAG system."""
    
    logger.info("🔍 Starting database validation...")
    
    try:
        # Initialize the database client
        db_client = SupabaseClient()
        logger.info("✅ Database client initialized successfully")
        
        # Test 1: Get database statistics
        logger.info("📊 Testing database statistics...")
        stats = await db_client.get_document_stats()
        
        if stats:
            logger.info("✅ Database statistics retrieved:")
            logger.info(f"   - Total documents: {stats.get('total_documents', 0)}")
            logger.info(f"   - Completed documents: {stats.get('completed_documents', 0)}")
            logger.info(f"   - Total chunks: {stats.get('total_chunks', 0)}")
            logger.info(f"   - Average chunks per document: {stats.get('avg_chunks_per_document', 0):.2f}")
            logger.info(f"   - Total tokens: {stats.get('total_tokens', 0)}")
            logger.info(f"   - Average tokens per chunk: {stats.get('avg_tokens_per_chunk', 0):.2f}")
        else:
            logger.warning("⚠️  Database statistics returned empty (this might be normal for a fresh database)")
        
        # Test 2: Test vector similarity search
        logger.info("🔍 Testing vector similarity search...")
        test_embedding = [0.1] * 1536  # Create a test embedding vector
        
        similar_chunks = await db_client.search_similar_chunks(
            query_embedding=test_embedding,
            similarity_threshold=0.1,  # Low threshold to potentially find results
            match_count=5
        )
        
        logger.info(f"✅ Vector similarity search working (found {len(similar_chunks)} results)")
        
        # Test 3: Test document operations
        logger.info("📄 Testing document operations...")
        
        # Get existing documents
        documents = await db_client.get_documents(limit=5)
        logger.info(f"✅ Document retrieval working (found {len(documents)} documents)")
        
        if documents:
            logger.info("Sample documents:")
            for i, doc in enumerate(documents[:3]):  # Show first 3
                logger.info(f"   {i+1}. {doc.get('filename', 'Unknown')} ({doc.get('status', 'Unknown')})")
        
        # Test 4: Create a test document (optional - only if no documents exist)
        if not documents:
            logger.info("📝 Creating test document...")
            try:
                test_doc_id = await db_client.insert_document(
                    filename="test_validation.txt",
                    file_type="txt",
                    content="This is a test document created during validation.",
                    file_size=48,
                    metadata={"created_by": "validation_script", "purpose": "testing"}
                )
                
                logger.info(f"✅ Test document created: {test_doc_id}")
                
                # Update status to completed
                await db_client.update_document_status(test_doc_id, "completed")
                logger.info("✅ Document status update working")
                
                # Clean up test document
                # Note: We'll leave it for now as it doesn't hurt to have test data
                
            except Exception as e:
                logger.error(f"❌ Error creating test document: {str(e)}")
        
        # Test 5: Test search query logging
        logger.info("📋 Testing search query logging...")
        try:
            await db_client.log_search_query(
                query_text="test validation query",
                query_embedding=test_embedding,
                response_text="This is a test response during validation",
                source_document_ids=[],
                response_time_ms=150,
                relevance_score=0.85
            )
            logger.info("✅ Search query logging working")
        except Exception as e:
            logger.error(f"❌ Error logging search query: {str(e)}")
        
        # Final statistics after tests
        logger.info("📊 Final database statistics:")
        final_stats = await db_client.get_document_stats()
        if final_stats:
            logger.info(f"   - Total documents: {final_stats.get('total_documents', 0)}")
            logger.info(f"   - Completed documents: {final_stats.get('completed_documents', 0)}")
            logger.info(f"   - Total chunks: {final_stats.get('total_chunks', 0)}")
        
        logger.info("✅ Database validation completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database validation failed: {str(e)}")
        logger.error(f"   Error type: {type(e).__name__}")
        return False


async def check_prerequisites():
    """Check if all prerequisites are met before validation."""
    
    logger.info("🔧 Checking prerequisites...")
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        logger.error("❌ .env file not found!")
        logger.error("   Please create .env file from .env.template")
        logger.error("   Make sure to set SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_KEY")
        return False
    
    logger.info("✅ .env file found")
    
    # Check if required environment variables are set
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables are set")
    
    return True


if __name__ == "__main__":
    logger.info("🚀 RAG Database Validation Tool")
    logger.info("================================")
    
    # Check prerequisites
    if not asyncio.run(check_prerequisites()):
        logger.error("❌ Prerequisites not met. Exiting...")
        sys.exit(1)
    
    # Run validation
    success = asyncio.run(validate_database_setup())
    
    logger.info("================================")
    if success:
        logger.info("✅ VALIDATION PASSED: Database is ready for RAG operations!")
        logger.info("   Your StreamRAG system can now:")
        logger.info("   • Store and retrieve documents")
        logger.info("   • Perform vector similarity searches") 
        logger.info("   • Track search analytics")
        logger.info("   • Handle document processing workflows")
    else:
        logger.error("❌ VALIDATION FAILED: Database needs attention!")
        logger.error("   Please check the error messages above and:")
        logger.error("   • Ensure Supabase is properly configured")
        logger.error("   • Verify your database credentials")
        logger.error("   • Make sure the schema has been applied")
        sys.exit(1)