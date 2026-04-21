"""
Script to embed DATN_2021_Chunked.txt into ChromaDB
"""

import re
import yaml
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Configuration
CHUNKED_FILE = r"C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\Chunked Data\Do_an\DATN_2021_Chunked.txt"
DB_PATH = r"C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\VectorStore"
COLLECTION_NAME = "datn_2021"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def parse_chunked_file(file_path):
    """
    Parse the chunked file and extract chunks with their metadata.
    
    File format:
    ---
    [YAML metadata]
    ---
    [chunk content]
    
    [blank line]
    ---
    [next chunk...]
    
    Returns:
        list: List of dictionaries containing chunk metadata and content
    """
    chunks = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by --- separator (accounting for the pattern)
    parts = content.split('---')
    
    # Process parts in groups of 3: empty/start, metadata, content
    # After split by ---, we get: ['', '\nmetadata\n', '\ncontent\n\n', ...]
    i = 1  # Start from 1 to skip the first empty part
    
    while i < len(parts) - 1:
        metadata_str = parts[i].strip()
        content_str = parts[i + 1].strip() if i + 1 < len(parts) else ""
        
        if not metadata_str or not content_str:
            i += 2
            continue
        
        # Parse YAML metadata
        try:
            metadata = yaml.safe_load(metadata_str)
            if metadata is None:
                i += 2
                continue
            
            # Extract chunk information
            chunk_data = {
                'chunk_id': metadata.get('chunk_id', ''),
                'chunk_index': metadata.get('chunk_index', 0),
                'title': metadata.get('title', ''),
                'content': content_str,
                'source': metadata.get('source', ''),
                'parent_doc_id': metadata.get('parent_doc_id', ''),
                'language': metadata.get('language', 'vi'),
                'category': metadata.get('category', ''),
                'year': metadata.get('year', 2021),
                'topic_tags': metadata.get('topic_tags', []),
            }
            
            chunks.append(chunk_data)
            
        except yaml.YAMLError as e:
            print(f"Error parsing YAML metadata for chunk at position {i}: {e}")
        
        i += 2
    
    return chunks


def embed_and_store_chunks(chunks, embedding_model, db_path, collection_name):
    """
    Embed chunks and store them in ChromaDB.
    
    Args:
        chunks: List of chunk dictionaries
        embedding_model: Model name for embeddings
        db_path: Path to store the ChromaDB
        collection_name: Name of the collection
    """
    # Initialize ChromaDB client (persistent)
    db_path_obj = Path(db_path)
    db_path_obj.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(db_path))
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Load embedding model
    print(f"Loading embedding model: {embedding_model}")
    model = SentenceTransformer(embedding_model)
    
    # Process and store chunks
    print(f"Embedding {len(chunks)} chunks...")
    
    for idx, chunk in enumerate(chunks, 1):
        chunk_id = chunk['chunk_id']
        content = chunk['content']
        title = chunk['title']
        
        # Create embedding
        embedding = model.encode(content)
        
        # Prepare metadata (exclude large fields)
        metadata = {
            'chunk_index': chunk['chunk_index'],
            'title': title[:500],  # Limit title length
            'source': chunk['source'][:200],
            'category': chunk['category'],
            'year': chunk['year'],
            'parent_doc_id': chunk['parent_doc_id'][:100],
        }
        
        # Add to collection
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding.tolist()],
            documents=[content],
            metadatas=[metadata]
        )
        
        if idx % 5 == 0:
            print(f"  Processed {idx}/{len(chunks)} chunks")
    
    print(f"✓ Successfully embedded all {len(chunks)} chunks")
    print(f"✓ Collection '{collection_name}' created with {collection.count()} documents")
    
    return collection


def main():
    """Main function"""
    print("=" * 60)
    print("Embedding DATN_2021 Chunks to ChromaDB")
    print("=" * 60)
    
    # Parse chunked file
    print(f"\nParsing chunks from: {CHUNKED_FILE}")
    chunks = parse_chunked_file(CHUNKED_FILE)
    print(f"✓ Found {len(chunks)} chunks")
    
    # Embed and store chunks
    print(f"\nStoring chunks in ChromaDB at: {DB_PATH}")
    collection = embed_and_store_chunks(
        chunks, 
        EMBEDDING_MODEL, 
        DB_PATH, 
        COLLECTION_NAME
    )
    
    # Test retrieval
    print("\n" + "=" * 60)
    print("Testing Retrieval")
    print("=" * 60)
    
    test_query = "đăng ký đồ án tốt nghiệp"
    print(f"\nTest Query: '{test_query}'")
    
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )
    
    print(f"\nTop 3 results:")
    for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0]), 1):
        print(f"\n{i}. (Distance: {distance:.4f})")
        print(f"   {doc[:200]}...")


if __name__ == "__main__":
    main()
