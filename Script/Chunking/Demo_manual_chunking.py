import os
from google import genai
from dotenv import load_dotenv
import uuid # to create a unique id for each chunk
# Import get_vector_db function 
from Script.Indexing.setup_db import get_vector_db 

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def run_pipeline(file_path):
    # 1. Đọc file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. Agentic Chunking 
    print("--- Đang thực hiện Agentic Chunking... ---")
    prompt = f"""
    Bạn là chuyên gia phân tích văn bản của Bách Khoa.
    Nhiệm vụ: Chia văn bản sau thành các chunk logic hoàn chỉnh.
    Quy tắc: Không ngắt ở giữa bảng biểu, giữ nguyên tiêu đề Điều/Mục.
    Phân cách bằng: '---CHUNK_BREAK---'
    Văn bản:
    {content}
    """
    response = client.models.generate_content(model='gemini-3.1-flash-lite', contents=prompt)
    chunks = [c.strip() for c in response.text.split('---CHUNK_BREAK---') if c.strip()]

    # 3. Embedding & Indexing vào ChromaDB
    print(f"--- Đang Indexing {len(chunks)} chunks vào Database... ---")
    collection = get_vector_db()

    for chunk in chunks:
        # Tạo Embedding cho từng chunk bằng Gemini
        emb_response = client.models.embed_content(
            model='text-embedding-004',
            contents=chunk
        )
        vector = emb_response.embeddings[0].values

        # Đẩy vào ChromaDB
        collection.add(
            ids=[str(uuid.uuid4())],
            embeddings=[vector],
            documents=[chunk],
            metadatas=[{"source": os.path.basename(file_path)}]
        )
    
    print("--- Hoàn tất! Dữ liệu đã sẵn sàng trong VectorStore. ---")

# test 
run_pipeline("Data/Hoc_phi/Hoc_phi_2025_DHCQ_KSCS_VLVH_SDH.txt")