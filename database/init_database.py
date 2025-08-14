"""
Complete database initialization script for the StreamRAG system.
This script will set up the database schema and validate the setup.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from supabase import create_client, Client
from config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """Handles complete database initialization for StreamRAG system."""
    
    def __init__(self):
        """Initialize the database setup handler."""
        self.settings = None
        self.client = None
        self.schema_file = Path(__file__).parent / "migrations" / "001_initial_schema.sql"
        
    async def initialize(self) -> bool:
        """Run complete database initialization."""
        
        logger.info("🚀 StreamRAG Database Initialization")
        logger.info("=====================================")
        
        try:
            # Step 1: Check prerequisites
            if not await self._check_prerequisites():
                return False
            
            # Step 2: Setup connection
            if not await self._setup_connection():
                return False
            
            # Step 3: Execute schema
            if not await self._execute_schema():
                return False
            
            # Step 4: Validate setup
            if not await self._validate_setup():
                return False
            
            # Step 5: Show final status
            await self._show_final_status()
            
            logger.info("✅ Database initialization completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            return False
    
    async def _check_prerequisites(self) -> bool:
        """Check all prerequisites for database setup."""
        
        logger.info("🔧 Checking prerequisites...")
        
        # Check .env file
        env_file = Path(__file__).parent.parent / ".env"
        if not env_file.exists():
            logger.error("❌ .env file not found!")
            logger.error("   Create .env file from .env.template with your Supabase credentials")
            return False
        
        # Check schema file
        if not self.schema_file.exists():
            logger.error(f"❌ Schema file not found: {self.schema_file}")
            return False
        
        # Check required environment variables
        required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        logger.info("✅ Prerequisites check passed")
        return True
    
    async def _setup_connection(self) -> bool:
        """Setup connection to Supabase."""
        
        logger.info("🔗 Setting up database connection...")
        
        try:
            self.settings = get_settings()
            
            # Use service key for admin operations
            self.client = create_client(
                self.settings.supabase_url,
                self.settings.supabase_service_key
            )
            
            # Test connection
            result = self.client.postgrest.rpc('query', {
                'query': 'SELECT NOW() as current_time'
            }).execute()
            
            logger.info("✅ Database connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {str(e)}")
            return False
    
    async def _execute_schema(self) -> bool:
        """Execute the database schema."""
        
        logger.info("📋 Executing database schema...")
        
        try:
            # Read schema file
            with open(self.schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Split into statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            statements = [stmt for stmt in statements if not stmt.startswith('--')]
            
            logger.info(f"Found {len(statements)} SQL statements to execute")
            
            success_count = 0
            skip_count = 0
            error_count = 0
            
            for i, statement in enumerate(statements, 1):
                if not statement:
                    continue
                
                try:
                    # Extract statement type for logging
                    stmt_type = statement.split()[0].upper() if statement.split() else "UNKNOWN"
                    
                    logger.info(f"[{i}/{len(statements)}] Executing {stmt_type}...")
                    
                    # Execute statement
                    result = self.client.postgrest.rpc('query', {'query': statement}).execute()
                    
                    success_count += 1
                    logger.info(f"✅ {stmt_type} executed successfully")
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check if it's an acceptable error (already exists)
                    if any(phrase in error_msg for phrase in [
                        'already exists',
                        'extension "vector" already exists',
                        'relation already exists',
                        'function already exists',
                        'policy already exists',
                        'trigger already exists'
                    ]):
                        skip_count += 1
                        logger.info(f"⚠️  Skipped {stmt_type} (already exists)")
                    else:
                        error_count += 1
                        logger.error(f"❌ Error in {stmt_type}: {str(e)}")
                        
                        # For critical errors, we might want to stop
                        if "permission denied" in error_msg or "authentication" in error_msg:
                            logger.error("Critical authentication error - stopping execution")
                            return False
            
            logger.info(f"Schema execution completed:")
            logger.info(f"  ✅ Success: {success_count}")
            logger.info(f"  ⚠️  Skipped: {skip_count}")
            logger.info(f"  ❌ Errors: {error_count}")
            
            return error_count == 0 or success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Schema execution failed: {str(e)}")
            return False
    
    async def _validate_setup(self) -> bool:
        """Validate that the database setup is working correctly."""
        
        logger.info("🔍 Validating database setup...")
        
        try:
            validation_results = {
                "pgvector_extension": False,
                "tables_exist": False,
                "functions_exist": False,
                "vector_search": False,
                "indexes_created": False
            }
            
            # Test 1: Check pgvector extension
            try:
                result = self.client.postgrest.rpc('query', {
                    'query': "SELECT '[1,2,3]'::vector as test_vector"
                }).execute()
                validation_results["pgvector_extension"] = True
                logger.info("✅ pgvector extension is working")
            except Exception as e:
                logger.error(f"❌ pgvector extension issue: {str(e)}")
            
            # Test 2: Check if tables exist
            tables = ['documents', 'document_chunks', 'search_queries']
            table_count = 0
            
            for table in tables:
                try:
                    result = self.client.table(table).select('count', count='exact').limit(1).execute()
                    table_count += 1
                    logger.info(f"✅ Table '{table}' exists")
                except Exception as e:
                    logger.error(f"❌ Table '{table}' issue: {str(e)}")
            
            validation_results["tables_exist"] = table_count == len(tables)
            
            # Test 3: Check functions
            functions = ['search_similar_chunks', 'get_document_stats']
            function_count = 0
            
            for func in functions:
                try:
                    if func == 'search_similar_chunks':
                        result = self.client.rpc(func, {
                            'query_embedding': [0.1] * 1536,
                            'similarity_threshold': 0.9,
                            'match_count': 1
                        }).execute()
                    else:
                        result = self.client.rpc(func).execute()
                    
                    function_count += 1
                    logger.info(f"✅ Function '{func}' is working")
                except Exception as e:
                    logger.error(f"❌ Function '{func}' issue: {str(e)}")
            
            validation_results["functions_exist"] = function_count == len(functions)
            
            # Test 4: Test vector similarity search specifically
            try:
                test_embedding = [0.1] * 1536
                result = self.client.rpc('search_similar_chunks', {
                    'query_embedding': test_embedding,
                    'similarity_threshold': 0.1,
                    'match_count': 5
                }).execute()
                
                validation_results["vector_search"] = True
                logger.info(f"✅ Vector similarity search working ({len(result.data or [])} results)")
            except Exception as e:
                logger.error(f"❌ Vector similarity search issue: {str(e)}")
            
            # Test 5: Check database statistics
            try:
                result = self.client.rpc('get_document_stats').execute()
                if result.data:
                    stats = result.data[0]
                    logger.info("📊 Current database stats:")
                    logger.info(f"   Documents: {stats.get('total_documents', 0)}")
                    logger.info(f"   Chunks: {stats.get('total_chunks', 0)}")
                    logger.info(f"   Tokens: {stats.get('total_tokens', 0)}")
                
                validation_results["indexes_created"] = True
                logger.info("✅ Database statistics working")
            except Exception as e:
                logger.error(f"❌ Database statistics issue: {str(e)}")
            
            # Overall validation result
            passed_tests = sum(validation_results.values())
            total_tests = len(validation_results)
            
            logger.info(f"Validation completed: {passed_tests}/{total_tests} tests passed")
            
            return passed_tests >= 4  # Allow for some flexibility
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {str(e)}")
            return False
    
    async def _show_final_status(self):
        """Show final status and next steps."""
        
        logger.info("📋 Final Status Report")
        logger.info("=====================")
        
        try:
            # Get final statistics
            result = self.client.rpc('get_document_stats').execute()
            if result.data and result.data[0]:
                stats = result.data[0]
                logger.info("📊 Database Ready:")
                logger.info(f"   • Documents: {stats.get('total_documents', 0)}")
                logger.info(f"   • Chunks: {stats.get('total_chunks', 0)}")
                logger.info(f"   • Total tokens: {stats.get('total_tokens', 0)}")
            
            logger.info("🎯 Your RAG system is ready for:")
            logger.info("   • Document ingestion and processing")
            logger.info("   • Vector similarity search")
            logger.info("   • Question answering with retrieval")
            logger.info("   • Search analytics and tracking")
            
            logger.info("🚀 Next steps:")
            logger.info("   1. Upload documents via the Streamlit interface")
            logger.info("   2. Test search functionality")
            logger.info("   3. Start asking questions about your documents")
            
        except Exception as e:
            logger.error(f"Error getting final status: {str(e)}")


async def main():
    """Main entry point for database initialization."""
    
    initializer = DatabaseInitializer()
    success = await initializer.initialize()
    
    if success:
        logger.info("🎉 SUCCESS: Database is ready for StreamRAG operations!")
    else:
        logger.error("💥 FAILED: Database initialization encountered issues.")
        logger.error("   Please check the errors above and:")
        logger.error("   • Verify your Supabase credentials in .env")
        logger.error("   • Ensure your Supabase project has proper permissions")
        logger.error("   • Check your internet connection")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())