# Project Instructions

## Setup Phase

### 1. Environment Preparation
```bash
# Create virtual environment
python -m venv rag-env
source rag-env/bin/activate  # On Windows: rag-env\Scripts\activate

# Install required packages
pip install pydantic-ai supabase streamlit openai pypdf2 python-dotenv
```

### 2. Supabase Configuration
- **MCP Expert**: Use Supabase MCP server to:
  - Enable pgvector extension in your Supabase database
  - Create necessary tables using the provided SQL schema
  - Set up proper indexes for vector similarity search
  - Configure row-level security policies

### 3. Environment Variables
Create a `.env` file with:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
```

## Development Workflow

### Phase 1: Architecture Design
**Backend Architect** should:
1. Design the overall system architecture
2. Define API interfaces between components
3. Plan the data flow from ingestion to response generation
4. Create component interaction diagrams
5. Establish error handling strategies

**Database Optimization** should:
1. Design the database schema for documents and embeddings
2. Plan indexing strategies for vector similarity search
3. Optimize query patterns for retrieval performance
4. Design data partitioning strategies if needed

### Phase 2: Core Implementation
**Task Decomposition Expert** breaks down into subtasks:
1. Document ingestion pipeline
2. Embedding generation service
3. Vector storage and retrieval
4. Pydantic AI agent with search tools
5. Response generation with context integration

**MCP Expert** handles:
1. Supabase database operations
2. Integration with OpenAI API
3. Vector similarity search implementation
4. External service error handling

### Phase 3: User Interface
**UI/UX Designer** specifies:
1. Document upload interface design
2. Query input and response display layout
3. Source attribution presentation
4. Error message and loading state designs
5. Overall user experience flow

**Frontend Developer** implements:
1. Streamlit components based on UX specifications
2. File upload handling and validation
3. Real-time query interface
4. Response formatting and source display
5. User feedback and error handling

### Phase 4: Integration and Testing
**Code Reviewer** validates:
1. Code quality and adherence to standards
2. Security best practices implementation
3. Error handling completeness
4. Performance optimization
5. Documentation quality

## Implementation Guidelines

### Document Ingestion Pipeline
```python
# Example structure - Backend Architect to design details
class DocumentIngester:
    def __init__(self, supabase_client, openai_client):
        self.supabase = supabase_client
        self.openai = openai_client
    
    def process_document(self, file_path: str) -> bool:
        # Extract text (PyPDF2 for PDFs, direct read for TXT)
        # Chunk text into appropriate segments
        # Generate embeddings using OpenAI
        # Store in Supabase with pgvector
        pass
```

### Pydantic AI Agent Structure
```python
# Example structure - Backend Architect to design details
from pydantic_ai import Agent

class RAGAgent:
    def __init__(self):
        self.agent = Agent(
            'openai:gpt-4',  # or appropriate model
            system_prompt="You are a helpful assistant...",
        )
        
    @self.agent.tool
    def knowledge_search(query: str) -> str:
        # Perform vector similarity search
        # Return relevant context
        pass
```

### Streamlit UI Integration
```python
# Example structure - refer to streamlit_ui_example.py
import streamlit as st
from your_agent import RAGAgent

def main():
    st.title("RAG System Interface")
    
    # Document upload section
    uploaded_file = st.file_uploader("Upload Document", type=['txt', 'pdf'])
    
    # Query interface
    query = st.text_input("Ask a question")
    
    # Response display with sources
    if query:
        response = agent.run(query)
        st.write(response)
```

## Quality Checkpoints

### Code Review Criteria
- [ ] All functions have proper type hints and docstrings
- [ ] Error handling is comprehensive and informative
- [ ] Security best practices are followed
- [ ] Performance considerations are addressed
- [ ] Code follows established patterns and standards

### Testing Requirements
- [ ] Unit tests for ingestion pipeline
- [ ] Integration tests for end-to-end RAG flow
- [ ] UI functionality tests
- [ ] Error handling tests
- [ ] Performance benchmarking

### Documentation Checklist
- [ ] README with clear setup instructions
- [ ] API documentation for all components
- [ ] Usage examples and tutorials
- [ ] Architecture diagrams and explanations
- [ ] Troubleshooting guide

## MCP Server Usage Instructions

### Supabase MCP Server
Use for:
- Creating and managing database tables
- Executing SQL queries and migrations
- Managing pgvector operations
- Monitoring database performance

### Crawl4AI RAG MCP Server
Use for:
- Accessing Pydantic AI documentation
- Finding Supabase integration examples
- Researching RAG implementation patterns
- Getting coding best practices

### Brave MCP Server
Use for:
- Finding supplementary documentation
- Researching implementation examples
- Discovering optimization techniques
- Finding troubleshooting solutions

## Handoff Protocol

Each subagent must:
1. Document all decisions and implementations
2. Provide clear interfaces for dependent components
3. Include testing instructions for their deliverables
4. Update project documentation with their contributions
5. Notify Code Reviewer when ready for validation