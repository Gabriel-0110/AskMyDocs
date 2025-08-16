# AskMyDocs 📋

A powerful Document-Based RAG (Retrieval-Augmented Generation) system that allows you to upload documents and ask intelligent questions about their content using AI.

## ✨ Features

- **📄 Document Upload**: Support for PDF and TXT files with drag-and-drop interface
- **🔍 Intelligent Search**: Vector-based similarity search using OpenAI embeddings
- **💬 AI-Powered Q&A**: Get accurate answers to questions about your documents
- **📊 Real-time Analytics**: View system statistics and document status
- **🎨 Clean UI**: Beautiful Streamlit interface with intuitive design
- **🔄 Live Processing**: Watch documents being processed in real-time

## 🏗️ Architecture

- **Frontend**: Streamlit web application
- **Backend**: Python with async support
- **Database**: Supabase (PostgreSQL with pgvector)
- **AI/ML**: OpenAI GPT-4o and text-embedding-3-small
- **Package Manager**: UV for fast, reliable dependency management

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- UV package manager
- OpenAI API key
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd askmydocs
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   uv run python run.py
   ```

5. **Open your browser**
   ```
   http://localhost:8502
   ```## ⚙️ Configuration

### Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Supabase Configuration  
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# RAG System Configuration
SIMILARITY_THRESHOLD=0.2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Key Settings

- **Similarity Threshold**: Controls how strict the document matching is (0.1-1.0)
- **Chunk Size**: Size of document segments for processing
- **Max File Size**: 10MB limit for uploaded documents

## 📖 Usage

1. **Upload Documents**: Drag and drop PDF/TXT files or use the browse button
2. **Wait for Processing**: Documents are automatically chunked and embedded
3. **Ask Questions**: Type questions about your uploaded documents
4. **Get AI Answers**: Receive accurate responses with source citations

### Example Queries

- "What is the main topic of this document?"
- "Who are the key people mentioned?"
- "Summarize the key findings"
- "What are the recommendations?"## 🧪 Testing

Run the comprehensive test suite:

```bash
uv run python tests/test_system.py
```

Test individual components:
```bash
# Test database connection
uv run python -c "import asyncio; from src.database.client import SupabaseClient; asyncio.run(SupabaseClient().get_documents_list())"

# Test embeddings
uv run python -c "import asyncio; from src.ingestion.embeddings import EmbeddingGenerator; asyncio.run(EmbeddingGenerator().test_connection())"
```

## 📁 Project Structure

```
askmydocs/
├── src/
│   ├── database/          # Supabase client and operations
│   ├── generation/        # RAG agent and response generation  
│   ├── ingestion/         # Document processing and embeddings
│   ├── retrieval/         # Vector search and retrieval
│   ├── ui/               # Streamlit interface
│   └── utils/            # Logging and utilities
├── config/               # Application settings
├── tests/                # Test suite
├── docs/                 # Documentation
└── database/            # Database setup and migrations
```

## 🛠️ Technology Stack

- **Python 3.11+** - Core language
- **Streamlit** - Web interface
- **Supabase** - Database and storage
- **OpenAI GPT-4o** - Language model
- **OpenAI Embeddings** - Vector embeddings
- **UV** - Package management
- **Pydantic** - Data validation
- **AsyncIO** - Asynchronous operations## 🔧 Development

### Adding New Features

1. Follow the modular architecture
2. Add tests for new functionality
3. Update documentation
4. Follow Python best practices

### Database Migrations

Database schema changes are handled in `database/migrations/`

### Logging

Comprehensive logging is available:
- Application logs: `rag_system.log`
- Console output with color coding
- Structured logging with timestamps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features
- **Documentation**: Check the `/docs` folder
- **Logs**: Check `rag_system.log` for troubleshooting

## 🎯 Roadmap

- [ ] Support for more document formats (DOCX, HTML)
- [ ] Advanced search filters
- [ ] Multi-language support
- [ ] Document versioning
- [ ] User authentication
- [ ] API endpoints
- [ ] Docker deployment
- [ ] Cloud deployment guides

---

Built with ❤️ using Python, Streamlit, and OpenAI