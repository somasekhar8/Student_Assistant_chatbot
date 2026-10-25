import os
import tempfile
from typing import List
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_core.documents import Document

def load_uploaded_file(uploaded_file) -> List[Document]:
    if uploaded_file is None:
        return []

    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_path = temp_file.name

    documents = []
    try:
        if file_extension == ".pdf":
            # PyMuPDF is significantly faster than PyPDFLoader
            loader = PyMuPDFLoader(temp_file_path)
            documents = loader.load()
        elif file_extension == ".txt":
            loader = TextLoader(temp_file_path, encoding="utf-8")
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
        for doc in documents:
            doc.metadata["source"] = uploaded_file.name

    except Exception as e:
        raise RuntimeError(f"Error processing document '{uploaded_file.name}': {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    return documents