import os
from typing import List, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.embeddings import get_embedding_model

INDEX_PATH = ".faiss_index"

def create_or_update_vector_store(chunks: List[Document], existing_vector_store: Optional[FAISS] = None) -> Optional[FAISS]:
    """
    Creates a new FAISS vector store or merges new document chunks into an existing one.
    """
    if not chunks:
        return existing_vector_store
        
    embedding_model = get_embedding_model()
    
    if existing_vector_store is None:
        # Create a fresh vector store
        vector_store = FAISS.from_documents(chunks, embedding_model)
    else:
        # Append new chunks to the existing FAISS store
        vector_store = existing_vector_store
        vector_store.add_documents(chunks)
    
    # Save updated index locally
    vector_store.save_local(INDEX_PATH)
    return vector_store

def load_vector_store() -> Optional[FAISS]:
    """Loads FAISS index from disk if present."""
    if os.path.exists(INDEX_PATH):
        embedding_model = get_embedding_model()
        return FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)
    return None