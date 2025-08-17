"""Streamlit UI for the RAG system."""

import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from streamlit_app import EASY_AUTH

import os
import streamlit as st
# ✅ fixes Pylance: use explicit import
import streamlit.components.v1 as components
import warnings

# =========================
# Auth mode (portable across providers)
# =========================
# "azure" | "public" | "auto" | "custom"
AUTH_MODE = os.getenv("AUTH_MODE", "auto")


def easy_auth_enabled() -> bool:
    if AUTH_MODE == "azure":
        return True
    if AUTH_MODE == "public":
        return False
    if AUTH_MODE == "custom":
        return False  # extension point for non-Azure providers
    # auto-detect Azure App Service / Easy Auth
    return bool(os.getenv("WEBSITE_SITE_NAME") or os.getenv("WEBSITE_AUTH_ENABLED"))


EASY_AUTH = easy_auth_enabled()

LOGIN_PAGE = "/ui/login"
LOGOUT_URL = "/.auth/logout?post_logout_redirect_uri=/ui/login"


def inject_auth_guard():

    if EASY_AUTH:
        st.markdown("""... your /.auth login buttons ...""", unsafe_allow_html=True)
    else:
        st.info("🔓 Public mode: no login required here")

    """In Azure, redirect anonymous users to the custom login page."""
    if not EASY_AUTH:
        return
    st.markdown(
        f"""
        <script>
          (async function() {{
            try {{
              const r = await fetch('/.auth/me', {{credentials:'include'}});
              if (r.ok) {{
                const d = await r.json();
                if (!Array.isArray(d) || d.length === 0) {{
                  window.location.href = '{LOGIN_PAGE}';
                }}
              }}
              // If 404 or not ok, do nothing (covers Streamlit Community/other hosts)
            }} catch (e) {{
              // network error? keep page (don’t hard fail)
            }}
          }})();
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_user_badge():
    """Sidebar badge with email/provider + logout (shown only when auth is on)."""
    if not EASY_AUTH:
        return
    st.sidebar.markdown("### 👤 Sessão")
    components.html(
        """
        <div id="userbox" style="font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial;">
          <div id="who" style="color:#ddd; font-size:14px;">Carregando usuário…</div>
          <div style="margin-top:6px;">
            <a href="/.auth/logout?post_logout_redirect_uri=/ui/login" style="color:#9bd; text-decoration:none;">Sair</a>
          </div>
        </div>
        <script>
          (async function() {
            try {
              const r = await fetch('/.auth/me', {credentials:'include'});
              if (!r.ok) return;  // in public mode there's no /.auth
              const data = await r.json();
              const box = document.getElementById('who');
              if (Array.isArray(data) && data.length > 0) {
                const claims = data[0].user_claims || [];
                const emailClaim = claims.find(c => c.typ === 'email')
                                  || claims.find(c => (c.typ||'').toLowerCase().includes('name'));
                const email = (emailClaim && emailClaim.val) || 'Usuário autenticado';
                const provider = (data[0].identity_provider || 'Conta').replace(/^.*\\//,'');
                box.textContent = email + ' · ' + provider;
              } else {
                box.textContent = 'Não autenticado';
              }
            } catch(e) {}
          })();
        </script>
        """,
        height=84,
    )


warnings.filterwarnings("ignore", category=SyntaxWarning,
                        module=r"streamlit\..*")

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
        self.orchestrator, self.rag_agent, self.db_client, self.embedding_generator = (
            get_services()
        )

    def run(self):
        st.set_page_config(
            page_title="RAG System",
            page_icon="📚",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        self._init_session_state()
        inject_auth_guard()  # ✅ enforce auth (no-op outside Azure)
        self._inject_css()

        st.title("📚 Document-Based RAG System")
        st.markdown(
            "Upload documents and ask questions to get AI-powered answers with source attribution."
        )

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
        render_user_badge()  # ✅ show user + logout when auth is enabled

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
                    if st.sidebar.button(
                        "🚀 Process Document",
                        key=f"process_{f.name}",
                        use_container_width=True,
                    ):
                        self._process_uploaded_file(f)
                    st.sidebar.divider()

        st.sidebar.subheader("📚 Knowledge Base")
        docs: List[Dict[str, Any]] = []
        try:
            docs = get_recent_documents(self.db_client, limit=10) or []
            if docs:
                for doc in docs:
                    with st.sidebar.expander(f"📄 {doc.get('filename', '(unknown)')}"):
                        st.write(
                            f"**Type:** {doc.get('file_type', '').upper()}")
                        st.write(
                            f"**Size:** {doc.get('file_size', 0):,} bytes")
                        st.write(
                            f"**Status:** {doc.get('status', '').title()}")
                        if doc.get("upload_date"):
                            st.write(
                                f"**Uploaded:** {doc['upload_date'][:10]}")
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
                        with st.expander(
                            f"Source {i}: {src.get('source_document', 'Unknown')}"
                        ):
                            st.write(
                                f"**Similarity:** {src.get('similarity', 0):.2%}")
                            st.write(
                                f"**Content:** {src.get('content', '')[:500]}...")

        prompt = st.chat_input("Ask a question about your documents...")
        if prompt:
            st.session_state.messages.append(
                {"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Searching knowledge base and generating response..."):
                    resp = self._process_query(prompt)
                st.write(resp["answer"])
                if resp.get("sources"):
                    st.subheader("📑 Sources")
                    for i, src in enumerate(resp["sources"], 1):
                        with st.expander(
                            f"Source {i}: {src.get('source_document', 'Unknown')}"
                        ):
                            st.write(
                                f"**Similarity:** {src.get('similarity', 0):.2%}")
                            st.write(
                                f"**Content:** {src.get('content', '')[:500]}...")

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": resp["answer"],
                        "sources": resp.get("sources", []),
                    }
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
                    st.success(
                        f"✅ Processed {uploaded_file.name} in {dt:.1f}s")
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
                    st.error(
                        f"❌ Failed to process {uploaded_file.name}: {result.get('error', 'Unknown error')}"
                    )
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
