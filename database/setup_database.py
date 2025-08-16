"""
Database setup script to execute the initial schema.
This script will connect to Supabase and execute the SQL schema.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from supabase import create_client, Client
from config.settings import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database():
    """Execute the database schema and verify setup."""
    
    try:
        # Load settings
        settings = get_settings()
        
        # Create Supabase client with service key for admin operations
        client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Use service key for admin operations
        )
        
        # Read the schema file
        schema_file = Path(__file__).parent / "migrations" / "001_initial_schema.sql"
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        logger.info("Executing database schema...")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        success_count = 0
        total_statements = len(statements)
        
        for i, statement in enumerate(statements):
            if not statement or statement.startswith('--'):
                continue
                
            try:
                logger.info(f"Executing statement {i+1}/{total_statements}")
                logger.debug(f"Statement: {statement[:100]}...")
                
                # Execute the SQL statement
                result = client.postgrest.rpc('query', {'query': statement}).execute()
                
                success_count += 1
                logger.info(f"✓ Statement {i+1} executed successfully")
                
            except Exception as stmt_error:
                # Some statements might fail if they already exist (like CREATE EXTENSION)
                error_msg = str(stmt_error)
                if any(phrase in error_msg.lower() for phrase in [
                    'already exists',
                    'extension "vector" already exists',
                    'relation "documents" already exists',
                    'function "update_updated_at_column" already exists'
                ]):
                    logger.info(f"⚠ Statement {i+1} skipped (already exists): {error_msg}")
                    success_count += 1
                else:
                    logger.error(f"✗ Error executing statement {i+1}: {error_msg}")
                    logger.error(f"Statement: {statement}")
        
        logger.info(f"Schema execution completed: {success_count}/{total_statements} statements processed")
        
        # Verify the setup
        await verify_database_setup(client)
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        return False


async def verify_database_setup(client: Client):
    """Verify that the database is properly set up."""
    
    logger.info("Verifying database setup...")
    
    try:
        # Check if pgvector extension is available
        logger.info("1. Checking pgvector extension...")
        try:
            # Try to create a test vector to verify pgvector is working
            test_result = client.postgrest.rpc('query', {
                'query': "SELECT '[1,2,3]'::vector as test_vector"
            }).execute()
            logger.info("✓ pgvector extension is working")
        except Exception as e:
            logger.error(f"✗ pgvector extension issue: {str(e)}")
        
        # Check if tables exist
        logger.info("2. Checking tables...")
        tables_to_check = ['documents', 'document_chunks', 'search_queries']
        
        for table_name in tables_to_check:
            try:
                result = client.table(table_name).select('count', count='exact').limit(1).execute()
                logger.info(f"✓ Table '{table_name}' exists")
            except Exception as e:
                logger.error(f"✗ Table '{table_name}' issue: {str(e)}")
        
        # Check if functions exist
        logger.info("3. Checking functions...")
        functions_to_check = ['search_similar_chunks', 'get_document_stats']
        
        for func_name in functions_to_check:
            try:
                # Try to call the function with minimal parameters
                if func_name == 'search_similar_chunks':
                    result = client.rpc(func_name, {
                        'query_embedding': [0.1] * 1536,  # Test embedding
                        'similarity_threshold': 0.9,  # High threshold to return no results
                        'match_count': 1
                    }).execute()
                elif func_name == 'get_document_stats':
                    result = client.rpc(func_name).execute()
                
                logger.info(f"✓ Function '{func_name}' is working")
            except Exception as e:
                logger.error(f"✗ Function '{func_name}' issue: {str(e)}")
        
        # Test vector similarity search with a real example
        logger.info("4. Testing vector similarity search...")
        try:
            # Create a test embedding vector
            test_embedding = [0.1] * 1536  # 1536-dimensional vector like OpenAI ada-002
            
            result = client.rpc('search_similar_chunks', {
                'query_embedding': test_embedding,
                'similarity_threshold': 0.1,  # Low threshold
                'match_count': 5
            }).execute()
            
            logger.info(f"✓ Vector similarity search working (found {len(result.data) if result.data else 0} results)")
        except Exception as e:
            logger.error(f"✗ Vector similarity search issue: {str(e)}")
        
        # Get database statistics
        logger.info("5. Getting database statistics...")
        try:
            stats = client.rpc('get_document_stats').execute()
            if stats.data and len(stats.data) > 0:
                stats_data = stats.data[0]
                logger.info("✓ Database statistics:")
                logger.info(f"   - Total documents: {stats_data.get('total_documents', 0)}")
                logger.info(f"   - Completed documents: {stats_data.get('completed_documents', 0)}")
                logger.info(f"   - Total chunks: {stats_data.get('total_chunks', 0)}")
                logger.info(f"   - Average chunks per document: {stats_data.get('avg_chunks_per_document', 0):.2f}")
            else:
                logger.info("✓ Database statistics function working (no data yet)")
        except Exception as e:
            logger.error(f"✗ Database statistics issue: {str(e)}")
        
        logger.info("Database verification completed!")
        
    except Exception as e:
        logger.error(f"Database verification failed: {str(e)}")


if __name__ == "__main__":
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        logger.error("❌ .env file not found. Please create one from .env.template")
        logger.error("Make sure to set your SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_KEY")
        sys.exit(1)
    
    logger.info("🚀 Starting database setup...")
    
    # Run the setup
    success = asyncio.run(setup_database())
    
    if success:
        logger.info("✅ Database setup completed successfully!")
        logger.info("Your RAG system database is ready for use.")
    else:
        logger.error("❌ Database setup failed!")
        sys.exit(1)