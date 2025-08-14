# AskMyDocs - Streamlit Cloud Deployment

A Document-Based RAG System deployed on Streamlit Community Cloud.

## 🚀 Live Demo
[Visit the live app](your-streamlit-url-here)

## 📋 Setup for Development

### Local Development
```bash
git clone https://github.com/Gabriel-0110/AskMyDocs.git
cd AskMyDocs
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
streamlit run app.py
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL  
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key

## 🔧 Architecture
- **Frontend**: Streamlit
- **Backend**: Python with async support
- **Database**: Supabase (PostgreSQL + pgvector)
- **AI**: OpenAI GPT-4o + Embeddings
- **Deployment**: Streamlit Community Cloud

## 📁 Key Files
- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `src/` - Core RAG system modules

Built with ❤️ using Streamlit, OpenAI, and Supabase
