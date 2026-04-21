import re
import yaml

CHUNKED_FILE = r"C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\Chunked Data\Do_an\DATN_2021_Chunked.txt"

with open(CHUNKED_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Count --- separators
separators = content.count('---')
print(f"Total '---' occurrences: {separators}")
print(f"Expected chunks: {separators // 2}")

# Try my parsing logic
parts = content.split('---')
print(f"\nParts after split: {len(parts)}")

i = 1
chunk_count = 0
while i < len(parts) - 1:
    metadata_str = parts[i].strip()
    content_str = parts[i + 1].strip() if i + 1 < len(parts) else ""
    
    if metadata_str and content_str:
        try:
            metadata = yaml.safe_load(metadata_str)
            if metadata:
                chunk_id = metadata.get('chunk_id', 'unknown')
                chunk_count += 1
                print(f"Chunk {chunk_count}: {chunk_id}")
        except:
            pass
    
    i += 2

print(f"\nTotal chunks parsed: {chunk_count}")

# Check if there are any remaining unparsed chunks
print(f"\nRemaining parts analysis:")
print(f"Final i value: {i}, len(parts): {len(parts)}")
if i < len(parts):
    print(f"Remaining part size: {len(parts[i])}")
