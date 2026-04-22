"""
Embedding Pipeline — Chatbot QCĐT
Embeds all chunked .txt files from Chunked Data/ into ChromaDB
using Google's gemini-embedding-001 model.

Usage:
    python embed_pipeline.py                  # embed all categories
    python embed_pipeline.py --category Do_an # embed one category only
    python embed_pipeline.py --dry-run        # parse only, no embedding
"""

import re
import time
import yaml
import argparse
import chromadb
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_DIR        = Path(__file__).parent.parent.parent  # Go up to workspace root
CHUNKED_DIR     = BASE_DIR / "Chunked Data"
DB_PATH         = BASE_DIR / "VectorStore"
COLLECTION_NAME = "qcdt_all"

EMBEDDING_MODEL  = "gemini-embedding-001"
EMBED_BATCH_SIZE = 20        # chunks per API batch (stay under TPM limit)
BATCH_SLEEP_SEC  = 1.0       # pause between batches to respect rate limits

# ── Setup ─────────────────────────────────────────────────────────────────────

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY not found in .env file.")

gemini_client = genai.Client(api_key=API_KEY)

# ── Parsing ───────────────────────────────────────────────────────────────────

# Matches:  <<<CHUNK>>>\n<yaml>\n<<<CHUNK>>>\n<content>  followed by next <<<CHUNK>>> or end-of-file
_CHUNK_PATTERN = re.compile(
    r"^<<<CHUNK>>>\n(.*?)\n<<<CHUNK>>>\n(.*?)(?=\n^<<<CHUNK>>>|\Z)",
    re.DOTALL | re.MULTILINE,
)


def parse_chunked_file(file_path: Path) -> list[dict]:
    """Parse a single *_chunked.txt file into a list of chunk dicts."""
    text = file_path.read_text(encoding="utf-8")
    chunks = []

    for match in _CHUNK_PATTERN.finditer(text):
        metadata_str = match.group(1).strip()
        content_str  = match.group(2).strip()

        if not metadata_str or not content_str:
            continue

        try:
            meta = yaml.safe_load(metadata_str)
        except yaml.YAMLError as e:
            print(f"  [WARN] YAML parse error in {file_path.name}: {e}")
            continue

        if not isinstance(meta, dict):
            continue

        tags = meta.get("topic_tags", [])
        if isinstance(tags, list):
            tags_str = ",".join(str(t) for t in tags)
        else:
            tags_str = str(tags)

        chunks.append({
            "chunk_id":      meta.get("chunk_id", ""),
            "chunk_index":   int(meta.get("chunk_index", 0)),
            "title":         str(meta.get("title", "")),
            "source":        str(meta.get("source", "")),
            "parent_doc_id": str(meta.get("parent_doc_id", "")),
            "language":      str(meta.get("language", "vi")),
            "category":      str(meta.get("category", "")),
            "year":          int(meta.get("year", 0)),
            "topic_tags":    tags_str,
            "content":       content_str,
        })

    return chunks


def collect_all_chunks(base_dir: Path, category_filter: str | None = None) -> list[dict]:
    """Walk Chunked Data/ and parse every *chunked*.txt file found."""
    all_chunks = []
    categories = (
        [base_dir / category_filter]
        if category_filter
        else [p for p in base_dir.iterdir() if p.is_dir()]
    )

    for cat_dir in sorted(categories):
        txt_files = sorted(cat_dir.glob("*chunked*.txt"))
        if not txt_files:
            print(f"  [SKIP] No chunked files in {cat_dir.name}/")
            continue
        for f in txt_files:
            chunks = parse_chunked_file(f)
            print(f"  [PARSE] {cat_dir.name}/{f.name} → {len(chunks)} chunks")
            all_chunks.extend(chunks)

    return all_chunks


# ── Embedding ─────────────────────────────────────────────────────────────────

def get_embeddings(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Call gemini-embedding-001 for a list of texts.
    task_type should be:
      - "RETRIEVAL_DOCUMENT" when indexing chunks
      - "RETRIEVAL_QUERY"    when embedding a search query
    """
    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config={"task_type": task_type},
    )
    return [e.values for e in response.embeddings]


# ── ChromaDB ──────────────────────────────────────────────────────────────────

def get_or_create_collection(db_path: Path, name: str) -> chromadb.Collection:
    db_path = Path(db_path) if not isinstance(db_path, Path) else db_path
    db_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(db_path))
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def embed_and_store(chunks: list[dict], collection: chromadb.Collection) -> None:
    """Embed chunks in batches and upsert into ChromaDB."""
    total   = len(chunks)
    batches = [chunks[i:i + EMBED_BATCH_SIZE] for i in range(0, total, EMBED_BATCH_SIZE)]

    print(f"\nEmbedding {total} chunks in {len(batches)} batches of ≤{EMBED_BATCH_SIZE}...")

    stored = 0
    for b_idx, batch in enumerate(batches, 1):
        texts = [c["content"] for c in batch]

        # Exponential backoff for API retries
        max_retries = 5
        retry_count = 0
        wait_time = 2.0  # Start with 2 seconds
        embeddings = None

        while retry_count < max_retries:
            try:
                embeddings = get_embeddings(texts, task_type="RETRIEVAL_DOCUMENT")
                break  # Success, exit retry loop
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"  [ERROR] Batch {b_idx} failed after {max_retries} retries: {e}")
                    print(f"  [SKIP] Skipping this batch...")
                    break
                else:
                    print(f"  [RETRY {retry_count}/{max_retries}] Batch {b_idx} failed, waiting {wait_time}s: {e}")
                    time.sleep(wait_time)
                    wait_time *= 2  # Exponential backoff: 2s, 4s, 8s, 16s, 32s
        
        if embeddings is None:
            continue  # Skip this batch if all retries failed

        ids        = [c["chunk_id"]  for c in batch]
        documents  = [c["content"]   for c in batch]
        metadatas  = [
            {
                "chunk_index":   c["chunk_index"],
                "title":         c["title"][:500],
                "source":        c["source"][:200],
                "parent_doc_id": c["parent_doc_id"][:100],
                "category":      c["category"],
                "year":          c["year"],
                "language":      c["language"],
                "topic_tags":    c["topic_tags"],
            }
            for c in batch
        ]

        # upsert: safe to re-run without duplicates
        collection.upsert(
            ids=ids,
            embeddings=[e for e in embeddings],
            documents=documents,
            metadatas=metadatas,
        )

        stored += len(batch)
        print(f"  Batch {b_idx}/{len(batches)} — {stored}/{total} chunks stored")

        if b_idx < len(batches):
            time.sleep(BATCH_SLEEP_SEC)

    print(f"\n✓ Done. Collection '{collection.name}' now has {collection.count()} documents.")


# ── Test retrieval ────────────────────────────────────────────────────────────

def test_retrieval(collection: chromadb.Collection, query: str, n: int = 3) -> None:
    print(f"\n── Test Query: '{query}' ──")

    # Embed the query using RETRIEVAL_QUERY task type
    query_embedding = get_embeddings([query], task_type="RETRIEVAL_QUERY")[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        include=["documents", "metadatas", "distances"],
    )

    for i, (doc, meta, dist) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ), 1):
        print(f"\n  {i}. [{meta['category']}] {meta['title'][:80]}")
        print(f"     Distance : {dist:.4f}")
        print(f"     Preview  : {doc[:180].strip()}...")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Embed chunked QCĐT docs into ChromaDB")
    parser.add_argument("--category", type=str, default=None,
                        help="Embed only one category folder (e.g. Do_an)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parse files only, skip embedding")
    parser.add_argument("--query", type=str, default="sinh viên elitech tốt nghiệp đại học cần học bao nhiêu tín chỉ",
                        help="Test query after embedding")
    args = parser.parse_args()

    print("=" * 60)
    print("QCĐT Embedding Pipeline — gemini-embedding-001")
    print("=" * 60)

    # 1. Collect chunks
    print(f"\nScanning: {CHUNKED_DIR}")
    chunks = collect_all_chunks(CHUNKED_DIR, args.category)
    print(f"\n✓ Total chunks parsed: {len(chunks)}")

    if not chunks:
        print("[WARN] No chunks found. Check CHUNKED_DIR path.")
        return

    if args.dry_run:
        print("\n[Dry run] Skipping embedding.")
        return

    # 2. Connect to ChromaDB
    collection = get_or_create_collection(DB_PATH, COLLECTION_NAME)
    print(f"✓ Collection '{COLLECTION_NAME}' opened (current count: {collection.count()})")

    # 3. Embed and store
    embed_and_store(chunks, collection)

    # 4. Quick retrieval test
    test_retrieval(collection, args.query)


if __name__ == "__main__":
    main()