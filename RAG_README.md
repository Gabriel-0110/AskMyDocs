# RAG System - Document-Based Question Answering

This is a production-ready RAG (Retrieval-Augmented Generation) system built with Pydantic AI and Supabase. The system allows users to upload documents and ask questions to get AI-powered answers with source attribution.

## 🏗️ Architecture

- **Pydantic AI Framework**: Core agent orchestration with structured outputs
- **Supabase Database**: PostgreSQL with pgvector extension for vector similarity search
- **OpenAI API**: Text embeddings and chat completions
- **Streamlit UI**: Interactive web interface for document upload and querying
- **Document Processing**: Support for PDF and TXT files with chunking

## 🚀 Quick Start

### Prerequisites

1. Python 3.11 or higher
2. Supabase account and project
3. OpenAI API key

### Installation

1. Clone and navigate to the repository:
```bash
cd rag-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

1. Set up your environment variables in a `.env` file:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# RAG System Settings
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_DIMENSIONS=1536
SIMILARITY_THRESHOLD=0.1
```

2. The system uses these Supabase database tables (already created):
   - `documents`: Store document metadata
   - `document_chunks`: Store text chunks with embeddings
   - `search_queries`: Log search queries for analytics

### Running the System

1. **Test the system components**:
```bash
python test_system.py
```

2. **Run the Streamlit web interface**:
```bash
streamlit run streamlit_main.py
```

3. **Access the application**:
   Open your browser to `http://localhost:8501`

## 📖 Usage

### Document Upload
1. Use the sidebar to upload PDF or TXT files
2. Click "Process" to ingest documents into the knowledge base
3. Wait for processing to complete

### Querying
1. Type your question in the chat input
2. The system will:
   - Search for relevant document chunks
   - Generate an AI-powered answer
   - Show source attribution with similarity scores
   - Provide confidence and reasoning

### Features
- **Structured Responses**: Every answer includes confidence scores and reasoning
- **Source Attribution**: See which documents were used with similarity scores
- **Real-time Processing**: Upload and query documents instantly  
- **Error Handling**: Robust error handling with informative messages
- **Logging**: Comprehensive logging for debugging and analytics

## 🔧 System Components

### Core Components

1. **Database Client** (`src/database/client_new.py`)
   - Supabase integration with pgvector
   - Document and chunk storage
   - Vector similarity search

2. **Document Processing** (`src/ingestion/`)
   - `processor_simple.py`: PDF/TXT text extraction
   - `embeddings_new.py`: OpenAI embedding generation
   - `orchestrator_new.py`: Document ingestion pipeline

3. **RAG Agent** (`src/generation/agent_new.py`)
   - Pydantic AI agent with structured outputs
   - Knowledge search and document info tools
   - Structured response format

4. **Streamlit UI** (`src/ui/streamlit_app_new.py`)
   - Document upload interface
   - Chat-based querying
   - Real-time results display

### Configuration
- `config/settings.py`: Centralized configuration using Pydantic Settings
- Environment variable support
- Default values for all parameters

## 🧪 Testing

Run the test suite to verify all components:

```bash
python test_system.py
```

This will test:
- Database connectivity
- Embedding generation
- RAG agent initialization  
- Full pipeline functionality

## 📊 Database Schema

### Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
    status TEXT DEFAULT 'pending',
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### Document Chunks Table
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}'::jsonb
);
```

### Indexes
- Vector similarity search index on `embedding` column
- Performance indexes on frequently queried columns

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and virtual environment is activated
2. **Database Connection**: Verify Supabase credentials and URL
3. **OpenAI API**: Check API key and rate limits
4. **Memory Issues**: Large documents may require chunking adjustment

### Logs
Check `rag_system.log` for detailed error messages and debugging information.

### Health Checks
- Database: Test connection with simple query
- OpenAI API: Test embedding generation
- Full Pipeline: End-to-end document processing and querying

## 🚀 Deployment

For production deployment:

1. Set up environment variables securely
2. Use a production WSGI server (not Streamlit's development server)
3. Configure proper logging and monitoring
4. Set up database backups
5. Configure rate limiting and authentication

## 📄 License

This project is built for educational and demonstration purposes following the provided specifications and requirements.
