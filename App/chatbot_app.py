"""
Streamlit Chatbot — QCĐT Information Assistant
Sử dụng ChromaDB + Google Gemini để trả lời câu hỏi
"""

import streamlit as st
import chromadb
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import time

# ── Configuration ─────────────────────────────────────────────────────────────

# Resolve database path (works on both local and Streamlit Cloud)
def get_db_path():
    """
    Find VectorStore path - tries multiple locations
    1. Parent directory of this script (normal case)
    2. Current working directory
    3. VECTORSTORE_PATH environment variable
    """
    # Try 1: Relative to this script
    script_dir = Path(__file__).parent  # App/
    workspace_root = script_dir.parent  # workspace root
    db_candidate = workspace_root / "VectorStore"
    
    if db_candidate.exists() and (db_candidate / "chroma.sqlite3").exists():
        return db_candidate
    
    # Try 2: Current working directory
    cwd_candidate = Path.cwd() / "VectorStore"
    if cwd_candidate.exists() and (cwd_candidate / "chroma.sqlite3").exists():
        return cwd_candidate
    
    # Try 3: Environment variable
    if "VECTORSTORE_PATH" in os.environ:
        env_candidate = Path(os.environ["VECTORSTORE_PATH"])
        if env_candidate.exists() and (env_candidate / "chroma.sqlite3").exists():
            return env_candidate
    
    # Default (will fail with clear error message)
    return workspace_root / "VectorStore"

BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / ".env"
DB_PATH = BASE_DIR / "VectorStore"
COLLECTION_NAME = "qcdt_all"
EMBEDDING_MODEL = "gemini-embedding-001"

# Load API key from Streamlit secrets (Cloud) or .env (Local)
def get_api_key():
    """Get API key from Streamlit secrets or .env file"""
    
    # Try 1: Streamlit secrets (for Cloud deployment)
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        # Secrets file doesn't exist or can't be read - proceed to next option
        pass
    
    # Try 2: Environment variable (might already be set)
    if "GOOGLE_API_KEY" in os.environ:
        return os.environ["GOOGLE_API_KEY"]
    
    # Try 3: Load from .env file
    # Try multiple .env paths to be robust
    env_paths = [
        ENV_PATH,  # workspace root
        Path.cwd() / ".env",  # current working directory
        Path.home() / ".env",  # home directory
    ]
    
    for env_file in env_paths:
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                return api_key
    
    return None

try:
    API_KEY = get_api_key()
    
    if not API_KEY:
        raise ValueError(f"""
        GOOGLE_API_KEY not found in:
        - Streamlit secrets
        - Environment variables
        - .env file at {ENV_PATH}
        - .env file at {Path.cwd() / ".env"}
        """)
    
    gemini_client = genai.Client(api_key=API_KEY)
    
except Exception as e:
    st.error(f"""
    ❌ **API Configuration Error**
    
    {str(e)}
    
    **For Local Development:**
    1. Make sure `.env` file exists in workspace root
    2. It should contain: `GOOGLE_API_KEY=your_actual_key`
    3. Restart Streamlit after creating/editing .env
    
    **For Streamlit Cloud Deployment:**
    1. Go to app settings
    2. Click "Secrets"
    3. Add: `GOOGLE_API_KEY = "your_api_key_here"`
    """)
    st.stop()

# ── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="QCĐT Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #e7f3ff;
        border-left: 4px solid #0066cc;
        padding: 0.8rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session State Initialization ──────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "collection" not in st.session_state:
    st.session_state.collection = None

if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = False

# ── Database Connection ───────────────────────────────────────────────────────

@st.cache_resource
def init_database():
    """Initialize ChromaDB connection (cached)"""
    try:
        # Check if database path exists
        if not DB_PATH.exists():
            st.error(f"""
            ❌ **Database folder not found!**
            
            Looking for: `{DB_PATH}`
            
            **This can happen on Streamlit Cloud if:**
            1. VectorStore wasn't committed to git
            2. Database path is wrong
            
            **Solution:**
            1. Make sure VectorStore/chroma.sqlite3 exists locally
            2. Commit to git: `git add VectorStore/`
            3. Push: `git push`
            4. Redeploy on Streamlit Cloud
            
            **Debug Info:**
            - Current working directory: {Path.cwd()}
            - Script location: {Path(__file__)}
            - DB_PATH looking for: {DB_PATH}
            """)
            return None
        
        if not (DB_PATH / "chroma.sqlite3").exists():
            st.error(f"""
            ❌ **Database file not found!**
            
            Found folder: {DB_PATH}
            But missing: {DB_PATH / "chroma.sqlite3"}
            
            **This means the database wasn't embedded yet.**
            
            **Solution:**
            1. Run locally: `python Script/Indexing/batch_embedding.py`
            2. Commit: `git add VectorStore/`
            3. Push: `git push`
            4. Redeploy on Streamlit Cloud
            """)
            return None
        
        # Connect to database
        client = chromadb.PersistentClient(path=str(DB_PATH))
        collection = client.get_collection(name=COLLECTION_NAME)
        return collection
        
    except Exception as e:
        error_msg = str(e)
        
        # Enhanced error messaging for common issues
        if "_type" in error_msg or "deserialization" in error_msg.lower():
            suggestion = """
**This is a database version incompatibility issue.** The solution:

**For Local Machine:**
1. Delete the corrupted VectorStore (or just the files inside it, keep folder):
   ```bash
   rm -rf VectorStore/*
   ```
2. Run the indexing script to rebuild:
   ```bash
   python Script/Indexing/batch_embedding.py
   ```
3. Test locally before pushing

**For Streamlit Cloud:**
1. After rebuilding locally, commit and push:
   ```bash
   git add VectorStore/
   git commit -m "Rebuild VectorStore with fixed Chroma version"
   git push
   ```
2. Redeploy on Streamlit Cloud
3. It will pull the fresh VectorStore files
            """
        else:
            suggestion = f"""
**Database Connection Failed**

**Debug Info:**
- Error: {error_msg}
- DB_PATH: {DB_PATH}
- Collection: {COLLECTION_NAME}
- DB Exists: {DB_PATH.exists()}
- Has chroma.sqlite3: {(DB_PATH / 'chroma.sqlite3').exists()}

**Quick Fix:**
1. Run: `python Script/Indexing/batch_embedding.py`
2. Commit: `git add VectorStore/ && git commit -m "Rebuild VectorStore"`
3. Push: `git push`
4. Redeploy on Streamlit Cloud
            """
        
        st.error(f"❌ **Database Connection Error**\n\n{suggestion}")
        return None


# ── Embedding Functions ───────────────────────────────────────────────────────

def embed_query(query: str) -> list[float]:
    """Embed a query using Google Gemini"""
    try:
        response = gemini_client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[query],
            config={"task_type": "RETRIEVAL_QUERY"},
        )
        return response.embeddings[0].values
    except Exception as e:
        st.error(f"❌ Embedding Error: {e}")
        return None


def retrieve_context(query: str, top_k: int = 3) -> tuple[str, list[dict]]:
    """Retrieve relevant documents from ChromaDB"""
    collection = st.session_state.collection
    
    try:
        query_embedding = embed_query(query)
        if query_embedding is None:
            return "", []
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Combine retrieved documents into context
        context_parts = []
        metadata_list = []
        
        if results["documents"] and len(results["documents"][0]) > 0:
            for i, (doc, meta) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0]
            ), 1):
                context_parts.append(f"[Source {i}]\n{doc}")
                metadata_list.append(meta)
        
        context = "\n\n".join(context_parts)
        return context, metadata_list
        
    except Exception as e:
        st.error(f"❌ Retrieval Error: {e}")
        return "", []


def generate_response(query: str, context: str) -> str:
    """Generate response using Google Gemini with retrieved context"""
    try:
        system_prompt = """Bạn là một trợ lý thông minh chuyên trả lời các câu hỏi về Đại học Bách Khoa Hà Nội (QCĐT).
Dựa trên thông tin được cung cấp, hãy trả lời câu hỏi của người dùng một cách rõ ràng, chính xác và hữu ích.
Nếu thông tin không đủ để trả lời, hãy nói rõ ràng điều đó.
Luôn sử dụng tiếng Việt để trả lời."""

        full_prompt = f"""Thông tin tham khảo:
{context}

Câu hỏi của người dùng: {query}

Vui lòng trả lời dựa trên thông tin được cung cấp ở trên."""

        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                },
                {
                    "role": "user",
                    "parts": [{"text": full_prompt}]
                }
            ],
        )
        
        return response.text
        
    except Exception as e:
        return f"❌ Lỗi tạo phản hồi: {e}"


def format_source_metadata(metadata: dict) -> str:
    """Format metadata for display"""
    parts = []
    if metadata.get("category"):
        parts.append(f"📁 Danh mục: {metadata['category']}")
    if metadata.get("title"):
        parts.append(f"📄 Tiêu đề: {metadata['title'][:100]}")
    if metadata.get("source"):
        parts.append(f"📋 Nguồn: {metadata['source']}")
    if metadata.get("year"):
        parts.append(f"📅 Năm: {metadata['year']}")
    return " | ".join(parts)


# ── Main UI ───────────────────────────────────────────────────────────────────

def main():
    # Header
    st.markdown('<div class="main-header">🤖 QCĐT Chatbot</div>', unsafe_allow_html=True)
    st.markdown("*Trợ lý thông tin về Đại học Bách Khoa Hà Nội*")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Cài đặt")
        
        # Database status
        st.subheader("📊 Trạng thái Database")
        
        collection = init_database()
        if collection:
            doc_count = collection.count()
            st.success(f"✅ Kết nối thành công!")
            st.info(f"📚 Documents: **{doc_count}**")
            st.session_state.collection = collection
            st.session_state.db_initialized = True
        else:
            st.error("❌ Không thể kết nối database")
            st.stop()
        
        st.divider()
        
        # Settings
        st.subheader("🎛️ Cài đặt Truy vấn")
        top_k = st.slider(
            "Số lượng tài liệu tham khảo:",
            min_value=1,
            max_value=10,
            value=3,
            help="Số lượng chunks được truy xuất để trả lời câu hỏi"
        )
        
        st.divider()
        
        # Info
        st.subheader("ℹ️ Hướng dẫn")
        st.markdown("""
        **Cách sử dụng:**
        1. Nhập câu hỏi vào ô bên dưới
        2. Bot sẽ tìm kiếm thông tin liên quan
        3. Trả lời dựa trên dữ liệu có sẵn
        
        **Ví dụ câu hỏi:**
        - "Điều kiện xét tuyển cao học?"
        - "Học phí năm 2025?"
        - "Quy trình đăng ký đồ án?"
        """)
        
        # Clear chat button
        if st.button("🗑️ Xóa cuộc trò chuyện", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat area
    if not st.session_state.db_initialized:
        st.warning("⏳ Đang khởi tạo database...")
        st.stop()
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"], avatar=message.get("avatar")):
                st.markdown(message["content"])
                
                # Show sources for assistant messages
                if message["role"] == "assistant" and message.get("sources"):
                    with st.expander("📚 Xem nguồn tham khảo"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(
                                f'<div class="source-box">{source}</div>',
                                unsafe_allow_html=True
                            )
    
    st.divider()
    
    # Chat input
    user_input = st.chat_input(
        "Nhập câu hỏi của bạn...",
        key="user_input"
    )
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "avatar": "👤"
        })
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)
        
        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⏳ Đang tìm kiếm thông tin..."):
                # Retrieve context
                context, metadata_list = retrieve_context(user_input, top_k=top_k)
                
                if not context:
                    response = "❌ Xin lỗi, không tìm thấy thông tin liên quan trong cơ sở dữ liệu."
                    sources = []
                else:
                    # Generate response
                    response = generate_response(user_input, context)
                    
                    # Format sources
                    sources = []
                    for i, meta in enumerate(metadata_list, 1):
                        source_text = format_source_metadata(meta)
                        sources.append(source_text)
            
            # Display response
            st.markdown(response)
            
            # Display sources
            if sources:
                with st.expander("📚 Xem nguồn tham khảo"):
                    for source in sources:
                        st.markdown(
                            f'<div class="source-box">{source}</div>',
                            unsafe_allow_html=True
                        )
        
        # Save to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "sources": sources,
            "avatar": "🤖"
        })


if __name__ == "__main__":
    main()
