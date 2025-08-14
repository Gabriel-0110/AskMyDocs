"""
Streamlit UI Example for RAG System with Pydantic AI Integration
This file demonstrates how to integrate Streamlit with a Pydantic AI agent for the RAG system.
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
import time
from datetime import datetime

# Import your RAG components (these will be implemented by Backend Architect)
# from rag_system.agent import RAGAgent
# from rag_system.ingestion import DocumentProcessor
# from rag_system.database import SupabaseClient

# For demonstration purposes, we'll create mock classes
class MockRAGAgent:
    """Mock RAG Agent for demonstration - replace with actual implementation"""
    
    def __init__(self):
        self.processing = False
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Mock query processing"""
        await asyncio.sleep(1)  # Simulate processing time
        return {
            "response": f"This is a mock response to: {query}",
            "sources": [
                {"document": "sample.pdf", "chunk": "Page 1, paragraph 2", "similarity": 0.89},
                {"document": "example.txt", "chunk": "Section 3", "similarity": 0.82}
            ],
            "processing_time": 1.2
        }

class MockDocumentProcessor:
    """Mock Document Processor for demonstration"""
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Mock document processing"""
        await asyncio.sleep(2)  # Simulate processing time
        return {
            "success": True,
            "chunks_created": 15,
            "embeddings_generated": 15,
            "processing_time": 2.1
        }

# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = {}

def display_sidebar():
    """Display sidebar with document upload and management"""
    st.sidebar.header("📄 Document Management")
    
    # Document upload section
    uploaded_files = st.sidebar.file_uploader(
        "Upload Documents",
        type=['pdf', 'txt'],
        accept_multiple_files=True,
        help="Upload PDF or TXT files to add to the knowledge base"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file not in st.session_state.documents:
                if st.sidebar.button(f"Process {uploaded_file.name}", key=f"process_{uploaded_file.name}"):
                    process_uploaded_file(uploaded_file)
    
    # Display processed documents
    st.sidebar.subheader("📚 Knowledge Base")
    if st.session_state.documents:
        for doc_info in st.session_state.documents:
            with st.sidebar.expander(f"📄 {doc_info['name']}"):
                st.write(f"**Type:** {doc_info['type']}")
                st.write(f"**Size:** {doc_info['size']} bytes")
                st.write(f"**Status:** {doc_info['status']}")
                if doc_info['status'] == 'Processed':
                    st.write(f"**Chunks:** {doc_info.get('chunks', 'N/A')}")
                    st.success("✅ Ready for queries")
    else:
        st.sidebar.info("No documents uploaded yet")
    
    # System statistics
    st.sidebar.subheader("📊 System Stats")
    total_docs = len(st.session_state.documents)
    processed_docs = len([d for d in st.session_state.documents if d['status'] == 'Processed'])
    st.sidebar.metric("Total Documents", total_docs)
    st.sidebar.metric("Processed Documents", processed_docs)

def process_uploaded_file(uploaded_file):
    """Process an uploaded file and add it to the knowledge base"""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    # Add to processing queue
    doc_info = {
        'name': uploaded_file.name,
        'type': uploaded_file.type,
        'size': uploaded_file.size,
        'status': 'Processing...',
        'upload_time': datetime.now()
    }
    st.session_state.documents.append(doc_info)
    st.session_state.processing_status[uploaded_file.name] = "processing"
    
    # Process the document (this would be async in real implementation)
    try:
        processor = MockDocumentProcessor()
        # In real implementation, this would be: await processor.process_document(tmp_file_path)
        result = asyncio.run(processor.process_document(tmp_file_path))
        
        if result['success']:
            # Update document status
            for doc in st.session_state.documents:
                if doc['name'] == uploaded_file.name:
                    doc['status'] = 'Processed'
                    doc['chunks'] = result['chunks_created']
                    doc['processing_time'] = result['processing_time']
                    break
            
            st.sidebar.success(f"✅ {uploaded_file.name} processed successfully!")
        else:
            st.sidebar.error(f"❌ Failed to process {uploaded_file.name}")
            
    except Exception as e:
        st.sidebar.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)
        st.session_state.processing_status[uploaded_file.name] = "completed"

def display_chat_interface():
    """Display the main chat interface"""
    st.header("🤖 RAG Assistant")
    st.subheader("Ask questions about your uploaded documents")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources for assistant messages
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**{i}. {source['document']}**")
                        st.write(f"   - Location: {source['chunk']}")
                        st.write(f"   - Relevance: {source['similarity']:.2%}")

def handle_user_query():
    """Handle user query input and generate response"""
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Check if documents are available
        if not st.session_state.documents:
            st.warning("⚠️ Please upload and process some documents first!")
            return
        
        processed_docs = [d for d in st.session_state.documents if d['status'] == 'Processed']
        if not processed_docs:
            st.warning("⚠️ No processed documents available. Please wait for processing to complete.")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Show processing indicator
            with st.spinner("🔍 Searching knowledge base..."):
                # Initialize RAG agent and process query
                agent = MockRAGAgent()
                
                try:
                    # In real implementation: response = await agent.process_query(prompt)
                    response = asyncio.run(agent.process_query(prompt))
                    
                    # Display the response
                    message_placeholder.markdown(response["response"])
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "sources": response["sources"],
                        "processing_time": response["processing_time"]
                    })
                    
                    # Display sources
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(response["sources"], 1):
                            st.write(f"**{i}. {source['document']}**")
                            st.write(f"   - Location: {source['chunk']}")
                            st.write(f"   - Relevance: {source['similarity']:.2%}")
                    
                    # Display processing time
                    st.caption(f"⏱️ Response generated in {response['processing_time']:.1f}s")
                    
                except Exception as e:
                    error_message = f"❌ Error processing query: {str(e)}"
                    message_placeholder.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })

def display_system_info():
    """Display system information and settings"""
    with st.expander("⚙️ System Information"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Queries",
                value=len([m for m in st.session_state.messages if m["role"] == "user"]),
                help="Total number of queries processed"
            )
        
        with col2:
            avg_response_time = 1.5  # This would be calculated from actual responses
            st.metric(
                label="Avg Response Time",
                value=f"{avg_response_time:.1f}s",
                help="Average response generation time"
            )
        
        with col3:
            st.metric(
                label="Knowledge Base Size",
                value=f"{len(st.session_state.documents)} docs",
                help="Number of documents in knowledge base"
            )
        
        # Configuration options
        st.subheader("Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            max_sources = st.slider(
                "Max Sources per Response",
                min_value=1,
                max_value=10,
                value=5,
                help="Maximum number of source documents to include in responses"
            )
        
        with col2:
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.5,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="Minimum similarity score for source relevance"
            )

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="RAG Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Main layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display main chat interface
        display_chat_interface()
        
        # Handle user input
        handle_user_query()
        
        # Display system information
        display_system_info()
    
    with col2:
        # Display sidebar in the right column for wider layout
        display_sidebar()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**RAG Assistant** - Powered by Pydantic AI and Supabase | "
        "Upload documents and ask questions to get intelligent responses with source attribution."
    )

if __name__ == "__main__":
    main()