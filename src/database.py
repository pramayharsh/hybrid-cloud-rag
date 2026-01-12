from langchain_community.vectorstores import FAISS
from src.embeddings_logic import get_embedding_model
import os

def create_vector_store(chunks):
    embeddings = get_embedding_model()
    
    print("--- [DEBUG] Encoding chunks via Hugging Face... ---", flush=True)
    
    # FAISS is much more stable on Windows
    vector_db = FAISS.from_documents(chunks, embeddings)
    
    # Save it locally so we don't have to re-encode every time
    vector_db.save_local("faiss_index")
    
    return vector_db