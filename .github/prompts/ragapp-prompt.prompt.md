# Initial Prompt for RAG System Development

This is a project focused on developing a Retrieval-Augmented Generation (RAG) system. The goal is to create a system that can effectively retrieve and generate information based on user queries. The project will involve various stages, including data collection, model training, and evaluation. Collaboration and adherence to best practices in software development are essential for the success of this project.

I'd like to build a RAG AI agent with Pydantic AI and Supabase:

- Be sure to review the planning and task files.
- This project should create a simple RAG system with:

## [1]: A document ingestion pipeline that

- Accepts local TXT and PDF files
- Uses a simple chunking approach
- Generates embeddings using OpenAI
- Stores documents and vectors in Supabase with pgvector

## [2]: A Pydantic AI agent that:

- Has a tool for knowledge base search
- Uses OpenAI models for response generation
- Integrates retrieved contexts into responses

File Example:

@rag-example.sql as an example for the SQL to run to set up the necessary tables in Supabase.

## [3]: A Streamlit UI that:

- Allows document uploads
- Provides a clean interface for querying the agent
- Displays responses with source attribution

File Example:

Use @streamlit_ui_example.py to see exactly how to integrate Streamlit with a Pydantic AI agent.

## [4]: Project Setup Instructions:

Use the Supabase MCP server to create the necessary database tables with the pgvector extension enabled. For document processing, keep it simple using PyPDF2 for PDFs rather than complex document processing libraries.

Use the Crawl4AI RAG MCP server that already has the Pydantic AI and Supabase Python documentation available. So just perform RAG queries whenever necessary. Also use the Brave MCP server to search the web for supplemental docs/examples to aid in creating the agent.

## Subagent Integration Requirements:

This project must utilize the following specialized subagents for optimal development:

1. **Backend Architect**: Design the RAG system architecture, API endpoints, and data flow
2. **Frontend Developer**: Implement the Streamlit UI components and user interactions  
3. **UI/UX Designer**: Create intuitive interfaces for document upload and query interaction
4. **Database Optimization**: Optimize Supabase pgvector queries and indexing strategies
5. **Task Decomposition Expert**: Break down complex RAG implementation into manageable tasks
6. **MCP Expert**: Handle integration with Supabase, Crawl4AI RAG, and Brave MCP servers
7. **Code Reviewer**: Ensure code quality, security, and best practices throughout development

The main orchestrator should coordinate between these subagents, ensuring that:
- Backend Architect designs before implementation begins
- Database Optimization reviews all vector storage and retrieval code
- UI/UX Designer provides specifications for the Streamlit interface
- MCP Expert handles all external service integrations
- Code Reviewer validates all components before final integration
- Task Decomposition Expert manages the overall project workflow

## Required MCP Server Integration

**IMPORTANT**: Actively use these MCP servers throughout development:

### Supabase MCP Server
- Use `supabase:execute_sql` to run the database schema from @rag-example.sql
- Call `supabase:list_tables` to verify table creation
- Use `supabase:apply_migration` for any schema updates
- Query with `supabase:execute_sql` for testing vector operations

### Crawl4AI RAG MCP Server  
- Use `crawl4ai:search_documentation` for Pydantic AI implementation patterns
- Query for Supabase integration best practices
- Search for RAG system architecture examples
- Find embedding and vector search optimization techniques

### Brave Search MCP Server
- Use `brave-search-mcp:brave_web_search` for supplemental documentation
- Search for "Pydantic AI Supabase integration examples"
- Find "pgvector optimization techniques" 
- Look up "Streamlit file upload best practices"

### Additional MCP Servers (if available)
- GitHub MCP: For code examples and repository patterns
- Filesystem MCP: For project structure and file management
- Any other relevant MCP servers for documentation and examples

## Subagent Activation Protocol

Each subagent MUST be explicitly triggered with their specific expertise:
- **"Backend Architect subagent: Design the system architecture..."**
- **"MCP Expert subagent: Integrate Supabase MCP server..."** 
- **"Database Optimization subagent: Optimize vector queries..."**
- **"Frontend Developer subagent: Implement Streamlit UI..."**
- **"UI/UX Designer subagent: Create interface specifications..."**
- **"Code Reviewer subagent: Validate code quality..."**
- **"Task Decomposition Expert subagent: Break down this task..."**

Start development by having Task Decomposition Expert subagent analyze the requirements and create a detailed implementation plan using the planning documents provided.