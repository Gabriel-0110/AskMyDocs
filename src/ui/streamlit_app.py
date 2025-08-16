"""Streamlit UI for the RAG system."""

import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List

import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning, module=r"streamlit\..*")

# ----- Robust import path handling (works when run from repo root) -----
try:
    from src.ingestion.orchestrator import DocumentOrchestrator  # type: ignore
    from src.generation.agent import RAGAgent  # type: ignore
    from src.database.client import SupabaseClient  # type: ignore
    from src.ingestion.embeddings import EmbeddingGenerator  # type: ignore
    from src.utils.logging_config import get_logger  # type: ignore
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[2]  # repo root
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "src"))
    from src.ingestion.orchestrator import DocumentOrchestrator  # type: ignore
    from src.generation.agent import RAGAgent  # type: ignore
    from src.database.client import SupabaseClient  # type: ignore
    from src.ingestion.embeddings import EmbeddingGenerator  # type: ignore
    from src.utils.logging_config import get_logger  # type: ignore

logger = get_logger(__name__)


@st.cache_resource(show_spinner=False)
def get_services():
    orchestrator = DocumentOrchestrator()
    rag_agent = RAGAgent()
    db_client = SupabaseClient()
    embedding_generator = EmbeddingGenerator()
    return orchestrator, rag_agent, db_client, embedding_generator


@st.cache_data(ttl=60, show_spinner=False)
def get_recent_documents(_db_client: "SupabaseClient", limit: int = 10):
    return asyncio.run(_db_client.get_documents_list(limit=limit))


class RAGStreamlitApp:
    def __init__(self):
        self.orchestrator, self.rag_agent, self.db_client, self.embedding_generator = get_services()

    def run(self):
        st.set_page_config(
            page_title="RAG System",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        self._init_session_state()
        self._inject_css()
        st.title("📚 Document-Based RAG System")
        st.markdown("Upload documents and ask questions to get AI-powered answers with source attribution.")
        self._display_sidebar()
        self._display_main_content()

    def _inject_css(self):
        st.markdown(
            """
            <style>
            section[data-testid="stSidebar"] > div:first-child { width: 30rem !important; }
            section[data-testid="stSidebar"] { width: 30rem !important; }
            .main .block-container { margin-left: 31rem !important; max-width: calc(100% - 32rem) !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def _init_session_state(self):
        st.session_state.setdefault("messages", [])
        st.session_state.setdefault("documents", [])
        st.session_state.setdefault("processing_status", {})

    def _display_sidebar(self):
        st.sidebar.header("📄 Document Management")

        uploaded_files = st.sidebar.file_uploader(
            "Upload Documents",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Upload PDF or TXT files to add to the knowledge base",
        )
        if uploaded_files:
            for f in uploaded_files:
                if f not in [d.get("file_obj") for d in st.session_state.documents]:
                    st.sidebar.write(f"📄 **{f.name}**  —  📏 {f.size:,} bytes")
                    if st.sidebar.button("🚀 Process Document", key=f"process_{f.name}", use_container_width=True):
                        self._process_uploaded_file(f)
                    st.sidebar.divider()

        st.sidebar.subheader("📚 Knowledge Base")
        docs: List[Dict[str, Any]] = []
        try:
            docs = get_recent_documents(self.db_client, limit=10) or []
            if docs:
                for doc in docs:
                    with st.sidebar.expander(f"📄 {doc.get('filename', '(unknown)')}"):
                        st.write(f"**Type:** {doc.get('file_type', '').upper()}")
                        st.write(f"**Size:** {doc.get('file_size', 0):,} bytes")
                        st.write(f"**Status:** {doc.get('status', '').title()}")
                        if doc.get("upload_date"):
                            st.write(f"**Uploaded:** {doc['upload_date'][:10]}")
                        status = doc.get("status")
                        if status == "completed":
                            st.success("✅ Ready for queries")
                        elif status == "processing":
                            st.info("⏳ Processing...")
                        elif status == "error":
                            st.error("❌ Processing failed")
                            if doc.get("error_message"):
                                st.write(f"Error: {doc['error_message']}")
            else:
                st.sidebar.info("No documents uploaded yet")
        except Exception as e:
            st.sidebar.error(f"Failed to load documents: {e}")

        st.sidebar.subheader("📊 System Stats")
        total_docs = len(docs)
        completed_docs = sum(1 for d in docs if d.get("status") == "completed")
        c1, c2 = st.sidebar.columns(2)
        c1.metric("Total Docs", total_docs)
        c2.metric("Ready", completed_docs)

    def _display_main_content(self):
        st.header("💬 Ask Questions")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                if msg.get("sources"):
                    st.subheader("📑 Sources")
                    for i, src in enumerate(msg["sources"], 1):
                        with st.expander(f"Source {i}: {src.get('source_document', 'Unknown')}"):
                            st.write(f"**Similarity:** {src.get('similarity', 0):.2%}")
                            st.write(f"**Content:** {src.get('content', '')[:500]}...")

        prompt = st.chat_input("Ask a question about your documents...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Searching knowledge base and generating response..."):
                    resp = self._process_query(prompt)
                st.write(resp["answer"])
                if resp.get("sources"):
                    st.subheader("📑 Sources")
                    for i, src in enumerate(resp["sources"], 1):
                        with st.expander(f"Source {i}: {src.get('source_document', 'Unknown')}"):
                            st.write(f"**Similarity:** {src.get('similarity', 0):.2%}")
                            st.write(f"**Content:** {src.get('content', '')[:500]}...")

                st.session_state.messages.append(
                    {"role": "assistant", "content": resp["answer"], "sources": resp.get("sources", [])}
                )

        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    def _process_uploaded_file(self, uploaded_file):
        try:
            with st.spinner(f"Processing {uploaded_file.name}..."):
                start = time.time()
                file_bytes = uploaded_file.read()
                result = asyncio.run(
                    self.orchestrator.ingest_document_from_bytes(
                        file_bytes=file_bytes, filename=uploaded_file.name
                    )
                )
                dt = time.time() - start

                if result["success"]:
                    st.success(f"✅ Processed {uploaded_file.name} in {dt:.1f}s")
                    st.write(f"Created {result['chunks_created']} chunks")
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
                    st.rerun()
                else:
                    st.error(f"❌ Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Error processing {uploaded_file.name}: {e}")
            logger.error(f"File processing error: {e}")

    def _process_query(self, query: str) -> Dict[str, Any]:
        try:
            start = time.time()
            response = asyncio.run(
                self.rag_agent.query(
                    question=query,
                    db_client=self.db_client,
                    embedding_generator=self.embedding_generator,
                )
            )
            dt = time.time() - start
            return {
                "answer": response.answer,
                "sources": [
                    {
                        "source_document": s.source_document,
                        "content": s.content,
                        "similarity": s.similarity,
                        "document_id": s.document_id,
                    }
                    for s in response.sources
                ],
                "confidence": response.confidence,
                "reasoning": response.reasoning,
                "processing_time": dt,
            }
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "answer": "I hit an error while processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0,
                "reasoning": f"Error: {e}",
                "processing_time": 0.0,
            }


def main():
    app = RAGStreamlitApp()
    app.run()


if __name__ == "__main__":
    main()
