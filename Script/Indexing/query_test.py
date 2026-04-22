"""
Interactive Query Script for ChromaDB QCDT Collection
Truy vấn và kiểm tra dữ liệu trong ChromaDB một cách tương tác
Uses Google Gemini embedding model to match database embeddings
"""

import chromadb
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai


# Configuration
DB_PATH = r"C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\VectorStore"
COLLECTION_NAME = "qcdt_all"
EMBEDDING_MODEL = "gemini-embedding-001"

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY not found in .env file.")

gemini_client = genai.Client(api_key=API_KEY)


def print_separator(char="=", length=80):
    """In một dòng ngăn cách"""
    print(char * length)


def get_query_embedding(query: str) -> list[float]:
    """
    Embed a query using Google Gemini with RETRIEVAL_QUERY task type.
    This matches the embeddings stored in the database.
    """
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[query],
        config={"task_type": "RETRIEVAL_QUERY"},
    )
    return response.embeddings[0].values


def print_result(index, doc, metadata, distance):
    """In một kết quả tìm kiếm với định dạng đẹp"""
    print(f"\n{'─' * 80}")
    print(f"📌 Kết quả #{index}")
    print(f"{'─' * 80}")
    
    # Distance (Khoảng cách - độ tương đồng)
    similarity = 1 - distance  # Convert distance to similarity
    similarity_percent = similarity * 100
    print(f"🔍 Khoảng cách (Distance): {distance:.4f}")
    print(f"   Độ tương đồng: {similarity_percent:.2f}%")
    
    # Metadata
    print(f"\n📋 Thông tin (Metadata):")
    print(f"   • Chunk ID: {metadata.get('chunk_index', 'N/A')}")
    print(f"   • Tiêu đề: {metadata.get('title', 'N/A')}")
    print(f"   • Danh mục: {metadata.get('category', 'N/A')}")
    print(f"   • Năm: {metadata.get('year', 'N/A')}")
    print(f"   • Nguồn: {metadata.get('source', 'N/A')}")
    
    # Document content
    print(f"\n📄 Nội dung (Document):")
    print(f"   {doc[:400]}...")
    

def format_results_summary(results):
    """In tóm tắt kết quả"""
    num_results = len(results['documents'][0]) if results['documents'] else 0
    print(f"\n✅ Tìm thấy {num_results} kết quả liên quan nhất")
    

def main():
    """Hàm chính"""
    print_separator()
    print("🤖 CHROMADB INTERACTIVE QUERY SYSTEM".center(80))
    print("💬 Hệ thống truy vấn tương tác ChromaDB".center(80))
    print_separator()
    
    # Initialize ChromaDB client
    print(f"\n🔌 Đang kết nối đến ChromaDB...")
    print(f"   📂 Đường dẫn: {DB_PATH}")
    print(f"   🤖 Embedding model: {EMBEDDING_MODEL}")
    
    try:
        client = chromadb.PersistentClient(path=str(DB_PATH))
        print(f"   ✓ Kết nối thành công!")
    except Exception as e:
        print(f"   ✗ Lỗi kết nối: {e}")
        return
    
    # Get collection (without specifying embedding function to use the persisted one)
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME
        )
        doc_count = collection.count()
        print(f"   ✓ Collection '{COLLECTION_NAME}' được tải thành công!")
        print(f"   • Số lượng documents: {doc_count}")
    except Exception as e:
        print(f"   ✗ Lỗi tải collection: {e}")
        return
    
    # Interactive query loop
    print_separator()
    print("\n💡 Hướng dẫn sử dụng:")
    print("   • Nhập câu hỏi hoặc từ khóa để truy vấn")
    print("   • Nhập 'exit' hoặc 'quit' để thoát chương trình")
    print("   • Nhập 'help' để xem hỗ trợ")
    print_separator()
    
    while True:
        print("\n")
        query = input("❓ Nhập câu hỏi (hoặc 'exit' để thoát): ").strip()
        
        # Handle special commands
        if query.lower() in ['exit', 'quit', 'thoát', 'q']:
            print("\n👋 Tạm biệt! Cảm ơn bạn đã sử dụng!")
            break
        
        if query.lower() in ['help', 'trợ giúp', 'h']:
            print("\n" + "=" * 80)
            print("📖 TRỢ GIÚP")
            print("=" * 80)
            print("Lệnh có sẵn:")
            print("  • exit, quit, thoát, q  - Thoát chương trình")
            print("  • help, trợ giúp, h     - Hiển thị trợ giúp")
            print("  • stats, info            - Xem thông tin collection")
            print("\nVí dụ câu hỏi:")
            print("  • 'đăng ký đồ án tốt nghiệp'")
            print("  • 'điều kiện xét tuyển thạc sĩ'")
            print("  • 'học phí năm 2021'")
            continue
        
        if query.lower() in ['stats', 'info']:
            print(f"\n📊 Thông tin Collection:")
            print(f"   • Tên: {COLLECTION_NAME}")
            print(f"   • Số documents: {doc_count}")
            print(f"   • Embedding model: {EMBEDDING_MODEL}")
            print(f"   • Đường dẫn DB: {DB_PATH}")
            continue
        
        if not query:
            print("⚠️  Vui lòng nhập một câu hỏi!")
            continue
        
        # Execute query
        print(f"\n⏳ Đang truy vấn...")
        try:
            # Embed the query using Google Gemini
            query_embedding = get_query_embedding(query)
            
            # Query using the embedding
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            format_results_summary(results)
            
            # Display results
            if results['documents'] and len(results['documents'][0]) > 0:
                for idx, (doc, metadata, distance) in enumerate(
                    zip(results['documents'][0], 
                        results['metadatas'][0], 
                        results['distances'][0]),
                    1
                ):
                    print_result(idx, doc, metadata, distance)
            else:
                print("❌ Không tìm thấy kết quả!")
            
            print(f"\n{'─' * 80}")
            
        except Exception as e:
            print(f"\n❌ Lỗi truy vấn: {e}")
            print(f"   Vui lòng thử lại!")
    
    print("\n" + "=" * 80)
    print("Chương trình kết thúc.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
