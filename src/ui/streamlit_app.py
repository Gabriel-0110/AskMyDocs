"""Streamlit UI for the RAG system."""

import streamlit as st
import asyncio
import time
from typing import Dict, Any

# Import our RAG system components
from src.ingestion.orchestrator import DocumentOrchestrator
from src.generation.agent import RAGAgent
from src.database.client import SupabaseClient
from src.ingestion.embeddings import EmbeddingGenerator
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class RAGStreamlitApp:
    """Main Streamlit application for the RAG system."""

    def __init__(self):
        """Initialize the application components."""
        self.orchestrator = DocumentOrchestrator()
        self.rag_agent = RAGAgent()
        self.db_client = SupabaseClient()
        self.embedding_generator = EmbeddingGenerator()

    def run(self):
        """Run the main Streamlit application."""
        st.set_page_config(
            page_title="RAG System",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded",
        )

        st.title("📚 Document-Based RAG System")
        st.markdown(
            "Upload documents and ask questions to get AI-powered answers with source attribution."
        )

        # Initialize session state
        self._init_session_state()

        # Display sidebar
        self._display_sidebar()

        # Main content area
        self._display_main_content()

    def _init_session_state(self):
        """Initialize Streamlit session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "documents" not in st.session_state:
            st.session_state.documents = []
        if "processing_status" not in st.session_state:
            st.session_state.processing_status = {}

    def _display_sidebar(self):
        """Display the sidebar with document management."""
        st.sidebar.header("📄 Document Management")

        # Document upload section
        uploaded_files = st.sidebar.file_uploader(
            "Upload Documents",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Upload PDF or TXT files to add to the knowledge base",
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file not in [
                    doc.get("file_obj") for doc in st.session_state.documents
                ]:
                    col1, col2 = st.sidebar.columns([3, 1])
                    with col1:
                        st.write(f"📄 {uploaded_file.name}")
                        st.write(f"Size: {uploaded_file.size:,} bytes")
                    with col2:
                        if st.button("Process", key=f"process_{uploaded_file.name}"):
                            self._process_uploaded_file(uploaded_file)

        # Display processed documents
        st.sidebar.subheader("📚 Knowledge Base")

        # Get documents from database
        try:
            documents = asyncio.run(self.db_client.get_documents_list(limit=10))

            if documents:
                for doc in documents:
                    with st.sidebar.expander(f"📄 {doc['filename']}"):
                        st.write(f"**Type:** {doc['file_type'].upper()}")
                        st.write(f"**Size:** {doc['file_size']:,} bytes")
                        st.write(f"**Status:** {doc['status'].title()}")
                        st.write(f"**Uploaded:** {doc['upload_date'][:10]}")

                        if doc["status"] == "completed":
                            st.success("✅ Ready for queries")
                        elif doc["status"] == "processing":
                            st.info("⏳ Processing...")
                        elif doc["status"] == "error":
                            st.error("❌ Processing failed")
                            if doc.get("error_message"):
                                st.write(f"Error: {doc['error_message']}")
            else:
                st.sidebar.info("No documents uploaded yet")

        except Exception as e:
            st.sidebar.error(f"Failed to load documents: {e}")

        # System statistics
        st.sidebar.subheader("📊 System Stats")
        try:
            documents = asyncio.run(self.db_client.get_documents_list(limit=10))
            total_docs = len(documents) if documents else 0
            completed_docs = (
                len([d for d in documents if d["status"] == "completed"])
                if documents
                else 0
            )

            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("Total Docs", total_docs)
            with col2:
                st.metric("Ready", completed_docs)
        except Exception:
            st.sidebar.write("Stats unavailable")

    def _display_main_content(self):
        """Display the main content area with chat interface."""
        # Chat interface
        st.header("💬 Ask Questions")

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

                if message.get("sources"):
                    st.subheader("📑 Sources")
                    for i, source in enumerate(message["sources"], 1):
                        with st.expander(
                            f"Source {i}: {source.get('source_document', 'Unknown')}"
                        ):
                            st.write(
                                f"**Similarity:** {source.get('similarity', 0):.2%}"
                            )
                            st.write(
                                f"**Content:** {source.get('content', '')[:500]}..."
                            )

        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.write(prompt)

            # Process the query
            with st.chat_message("assistant"):
                with st.spinner("Searching knowledge base and generating response..."):
                    response = self._process_query(prompt)

                # Display response
                st.write(response["answer"])

                if response.get("sources"):
                    st.subheader("📑 Sources")
                    for i, source in enumerate(response["sources"], 1):
                        with st.expander(
                            f"Source {i}: {source.get('source_document', 'Unknown')}"
                        ):
                            st.write(
                                f"**Similarity:** {source.get('similarity', 0):.2%}"
                            )
                            st.write(
                                f"**Content:** {source.get('content', '')[:500]}..."
                            )

                # Add assistant response to chat
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response["answer"],
                        "sources": response.get("sources", []),
                    }
                )

        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    def _process_uploaded_file(self, uploaded_file):
        """Process an uploaded file through the ingestion pipeline."""
        try:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                start_time = time.time()

                # Get file bytes
                file_bytes = uploaded_file.read()

                # Process through orchestrator
                result = asyncio.run(
                    self.orchestrator.ingest_document_from_bytes(
                        file_bytes=file_bytes, filename=uploaded_file.name
                    )
                )

                processing_time = time.time() - start_time

                if result["success"]:
                    st.success(
                        f"✅ Successfully processed {uploaded_file.name} in {processing_time:.1f}s"
                    )
                    st.write(f"Created {result['chunks_created']} chunks")

                    # Add to session state
                    st.session_state.documents.append(
                        {
                            "name": uploaded_file.name,
                            "type": uploaded_file.type,
                            "size": uploaded_file.size,
                            "status": "Processed",
                            "chunks": result["chunks_created"],
                            "document_id": result["document_id"],
                            "file_obj": uploaded_file,
                        }
                    )

                    # Rerun to update the interface
                    st.rerun()

                else:
                    st.error(
                        f"❌ Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}"
                    )

        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {e}")
            logger.error(f"File processing error: {e}")

    def _process_query(self, query: str) -> Dict[str, Any]:
        """Process a user query and return the response."""
        try:
            start_time = time.time()

            # Query the RAG agent
            response = asyncio.run(
                self.rag_agent.query(
                    question=query,
                    db_client=self.db_client,
                    embedding_generator=self.embedding_generator,
                )
            )

            processing_time = time.time() - start_time

            return {
                "answer": response.answer,
                "sources": response.sources,
                "confidence": response.confidence,
                "reasoning": response.reasoning,
                "processing_time": processing_time,
            }

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "processing_time": 0.0,
            }


def main():
    """Main entry point for the Streamlit app."""
    app = RAGStreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
