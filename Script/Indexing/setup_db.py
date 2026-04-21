import chromadb 
from chromadb.config import Settings
import os

def get_vector_db():
    #store vectors in VectorStore
    db_path = os.path.join(os.getcwd(), "VectorStore")

    client = chromadb.PersistentClient(path = db_path)

    #either create or get collection
    collection = client.get_or_create_collection("hoc_phi_dhbk_2025")
    
