# Claude Code Commands to Get Started

## Installation & Setup

### Install Claude Code (if available)
```bash
# Try installing with uv
uv tool install claude-code

# Or check if available
uv search claude-code
```

### Alternative: Manual Setup with uv
```bash
# Create project with uv (recommended)
uv init rag-system
cd rag-system

# Add dependencies
uv add pydantic-ai supabase streamlit openai pypdf2 python-dotenv

# Create .env file
touch .env
```

## Initial Project Creation

Use this command to create your RAG system with Claude Code:

```bash
claude-code create rag-system --prompt "@.github/prompts/ragapp-prompt.prompt.md"
```

## Alternative Incremental Approach

If you prefer to build incrementally, use these commands:

### Phase 1: Project Setup
```bash
claude-code create rag-foundation --prompt "
Set up the foundation for a RAG system project:
1. Create project structure as defined in planning.md
2. Set up environment configuration with .env template
3. Create requirements.txt with all necessary packages
4. Use MCP Expert subagent to configure Supabase connection
5. Use Database Optimization subagent to implement the rag-example.sql schema
6. Create basic configuration management system
Follow the rules.md and instructions.md for setup standards.
"
```

### Phase 2: Core RAG Engine
```bash
claude-code update --prompt "
Implement the core RAG engine components:
1. Backend Architect: Design document ingestion architecture
2. MCP Expert: Implement OpenAI embedding integration
3. Database Optimization: Create vector storage and retrieval functions
4. Create document processing pipeline (PDF/TXT with PyPDF2)
5. Implement text chunking and embedding generation
6. Test vector similarity search functionality
Follow the task breakdown in tasks.md for Phase 3 requirements.
"
```

### Phase 3: Pydantic AI Agent
```bash
claude-code update --prompt "
Build the Pydantic AI agent:
1. Backend Architect: Design agent architecture and tools
2. MCP Expert: Integrate with OpenAI language models
3. Implement knowledge search tool for vector retrieval
4. Create context assembly and response generation
5. Add source attribution and citation tracking
6. Test agent responses with mock data
Reference the agent specifications in instructions.md.
"
```

### Phase 4: Streamlit Interface
```bash
claude-code update --prompt "
Implement the Streamlit user interface:
1. UI/UX Designer: Design interface specifications
2. Frontend Developer: Implement based on streamlit_ui_example.py
3. Create document upload and processing components
4. Build query interface with real-time responses
5. Implement source attribution display
6. Add error handling and user feedback
7. Integrate with Pydantic AI agent
Ensure the UI matches the example in streamlit_ui_example.py.
"
```

### Phase 5: Integration & Testing
```bash
claude-code update --prompt "
Complete integration and testing:
1. Code Reviewer: Perform comprehensive code review
2. Task Decomposition Expert: Validate all requirements met
3. Implement end-to-end testing suite
4. Add performance benchmarking
5. Create deployment configuration
6. Complete documentation per planning.md requirements
7. Validate all subagent deliverables are integrated properly
"
```

## Continuous Development Commands

### Add New Features
```bash
claude-code update --prompt "
Add [specific feature] to the RAG system:
- Ensure Backend Architect reviews architecture impact
- Have MCP Expert handle any external integrations
- Get Code Reviewer approval before implementation
- Follow the established patterns in the existing codebase
"
```

### Debug Issues
```bash
claude-code update --prompt "
Debug [specific issue] in the RAG system:
- Use appropriate subagent expertise (Database Optimization for query issues, MCP Expert for API issues, etc.)
- Follow error handling patterns established in rules.md
- Ensure fix doesn't break existing functionality
- Add tests to prevent regression
"
```

### Optimize Performance
```bash
claude-code update --prompt "
Optimize RAG system performance:
- Database Optimization subagent: Review and optimize vector queries
- Backend Architect: Review system bottlenecks
- Code Reviewer: Validate optimization effectiveness
- Focus on query response times and embedding generation speed
"
```

## File Upload Strategy

When running these commands, make sure you have all the project files available:
- Save each artifact as the specified filename
- Upload all files when prompted by Claude Code
- Reference the files by name in your prompts (e.g., @planning.md)

This approach will leverage all your subagents effectively and create a comprehensive RAG system following your specifications.