import re
import yaml

CHUNKED_FILE = r"C:\Users\LENOVO\Documents\GitHub\Chatbot QCĐT\Chunked Data\Do_an\DATN_2021_Chunked.txt"

with open(CHUNKED_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

print("File size:", len(content), "characters")
print("\nFirst 800 characters:")
print(repr(content[:800]))

print("\n\nTrying split by ---:")
chunk_blocks = re.split(r'^---\n', content, flags=re.MULTILINE)
print(f"Got {len(chunk_blocks)} blocks after split")

print("\n\nFirst block preview:")
print(repr(chunk_blocks[1][:400]))

print("\n\nTrying to split first block by ---:")
parts = chunk_blocks[1].split('---\n', 1)
print(f"Split result: {len(parts)} parts")
if len(parts) == 2:
    print("Metadata part:")
    print(repr(parts[0][:300]))
    print("\nContent part:")
    print(repr(parts[1][:200]))
