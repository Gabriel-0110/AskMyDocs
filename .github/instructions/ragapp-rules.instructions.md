# Project Rules and Guidelines

## Development Standards

### Code Quality
- All code must pass through the Code Reviewer subagent before integration
- Follow PEP 8 standards for Python code formatting
- Include comprehensive docstrings for all functions and classes
- Implement proper error handling and logging throughout the system
- Use type hints consistently across all Python modules

### Architecture Principles
- Backend Architect must approve all system design decisions
- Follow modular design patterns with clear separation of concerns
- Implement proper dependency injection where applicable
- Use environment variables for all configuration settings
- Ensure scalable design that can handle growing document collections

### Database Guidelines
- Database Optimization subagent must review all SQL queries and schema designs
- Use pgvector extension efficiently for embedding storage and retrieval
- Implement proper indexing strategies for optimal search performance
- Follow normalization principles while considering query performance
- Include migration scripts for database schema changes

### Security Requirements
- Never commit API keys or sensitive credentials to version control
- Use environment variables or secure credential management
- Implement input validation for all user inputs
- Sanitize file uploads and validate file types
- Use parameterized queries to prevent SQL injection

### UI/UX Standards
- UI/UX Designer must approve all interface designs before implementation
- Ensure responsive design that works on different screen sizes
- Implement clear error messages and user feedback
- Follow accessibility guidelines (WCAG 2.1)
- Provide intuitive navigation and clear labeling

### Testing Requirements
- Write unit tests for all core functions
- Include integration tests for the complete RAG pipeline
- Test error handling and edge cases
- Validate embedding generation and retrieval accuracy
- Test UI components and user workflows

### Documentation Standards
- Maintain clear README with setup and usage instructions
- Document all API endpoints and their parameters
- Include code comments explaining complex logic
- Provide example usage for all major components
- Keep documentation updated with code changes

## Subagent Coordination Rules

### Task Flow Management
1. Task Decomposition Expert breaks down all major features
2. Backend Architect reviews and approves system design
3. Database Optimization designs data layer and queries
4. MCP Expert handles all external service integrations
5. Frontend Developer implements UI based on UX specifications
6. UI/UX Designer provides design guidance throughout
7. Code Reviewer validates all deliverables

### Communication Protocol
- All subagents must document their decisions and rationale
- Dependencies between subagents must be clearly identified
- Integration points must be agreed upon by relevant subagents
- Regular checkpoint reviews by Code Reviewer
- Clear handoff procedures between development phases

### Quality Assurance
- No component goes to production without Code Reviewer approval
- Database queries must be optimized before implementation
- UI components must meet UX standards before integration
- All MCP integrations must be tested and documented
- Performance benchmarks must be established and monitored

## Technology Constraints

### Required Technologies
- **Backend**: Python with Pydantic AI framework
- **Database**: Supabase with pgvector extension
- **UI**: Streamlit framework
- **Document Processing**: PyPDF2 (keep it simple)
- **Embeddings**: OpenAI embedding models
- **Vector Storage**: Supabase pgvector

### MCP Server Usage
- **Supabase MCP**: For database operations and schema management
- **Crawl4AI RAG MCP**: For accessing Pydantic AI and Supabase documentation
- **Brave MCP**: For searching additional documentation and examples

### Prohibited Technologies
- Avoid complex document processing libraries beyond PyPDF2
- No additional vector databases beyond Supabase pgvector
- Stick to Streamlit for UI (no React, Vue, or other frameworks)
- Use OpenAI for embeddings (no alternative embedding providers)

## File Organization
```
rag-system/
├── src/
│   ├── ingestion/
│   ├── retrieval/
│   ├── generation/
│   └── ui/
├── database/
│   └── migrations/
├── tests/
├── docs/
├── config/
└── examples/