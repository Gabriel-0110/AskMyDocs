# MCP Server Integration Instructions

This document explains how to integrate the Supabase MCP server for database operations in the StreamRAG system.

## Ideal MCP Server Usage

If you have access to the Supabase MCP server, you would typically:

1. **Configure the MCP server** in your Claude Code environment
2. **Use direct SQL execution** through MCP server tools
3. **Execute the schema file** directly without Python wrappers

### Example MCP Server Commands

```bash
# If Supabase MCP server was available, you would use commands like:

# Execute the complete schema
supabase-mcp execute-sql --file="database/migrations/001_initial_schema.sql"

# Check pgvector extension
supabase-mcp query "SELECT extname FROM pg_extension WHERE extname = 'vector';"

# Verify tables
supabase-mcp query "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"

# Test vector search function
supabase-mcp query "SELECT search_similar_chunks(ARRAY[0.1,0.2], 0.7, 5);"

# Get database statistics
supabase-mcp query "SELECT * FROM get_document_stats();"
```

## Alternative Python Implementation

Since MCP server access is not available in this environment, we've created Python scripts that accomplish the same goals:

### Scripts Created

1. **`init_database.py`** - Complete database initialization
   - Executes the SQL schema
   - Validates all components
   - Provides comprehensive logging

2. **`validate_setup.py`** - Database validation only
   - Tests existing database setup
   - Verifies vector search functionality
   - Reports current status

3. **`setup_database.py`** - Basic schema execution
   - Executes SQL statements
   - Basic validation
   - Simpler implementation

### Usage Instructions

```bash
# Make sure you have a .env file with your Supabase credentials
cp .env.template .env
# Edit .env with your actual Supabase credentials

# Run complete database initialization
cd database
python init_database.py

# Or just validate existing setup
python validate_setup.py
```

## Required Environment Variables

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_KEY=your_service_key_here
```

## What Gets Set Up

The database initialization creates:

### Extensions
- `vector` - pgvector for similarity search

### Tables
- `documents` - Document metadata and content
- `document_chunks` - Text chunks with embeddings
- `search_queries` - Search analytics

### Indexes
- HNSW index on `document_chunks.embedding` for fast vector search
- Standard indexes for queries and filtering

### Functions
- `search_similar_chunks()` - Vector similarity search
- `get_document_stats()` - Database statistics
- `update_updated_at_column()` - Timestamp trigger function

### Security
- Row Level Security (RLS) enabled
- Policies for authenticated users
- Proper permissions granted

## Verification Steps

The validation process checks:

1. ✅ pgvector extension functionality
2. ✅ Table existence and accessibility
3. ✅ Function availability and execution
4. ✅ Vector similarity search performance
5. ✅ Database statistics collection
6. ✅ Insert/update operations

## Performance Considerations

- HNSW index parameters: `m=16, ef_construction=64`
- Vector dimension: 1536 (OpenAI ada-002 compatible)
- Optimized for cosine similarity searches
- Proper indexing for metadata filtering

## Next Steps After Setup

1. Test document upload functionality
2. Verify embedding generation pipeline
3. Test end-to-end RAG workflow
4. Monitor search performance
5. Set up analytics dashboards

## Troubleshooting

Common issues and solutions:

- **Connection errors**: Check Supabase URL and keys
- **Permission errors**: Ensure service key has admin privileges
- **Vector errors**: Verify pgvector extension is enabled
- **Function errors**: Check SQL syntax in schema file
- **Index errors**: May need manual index creation for large datasets