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

DB_PATH = Path(__file__).parent.parent / "VectorStore"
COLLECTION_NAME = "qcdt_all"
EMBEDDING_MODEL = "gemini-embedding-001"

# Load environment
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file!")
    st.stop()

gemini_client = genai.Client(api_key=API_KEY)

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
        client = chromadb.PersistentClient(path=str(DB_PATH))
        collection = client.get_collection(name=COLLECTION_NAME)
        return collection
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
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
