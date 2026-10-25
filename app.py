import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.document_loader import load_uploaded_file
from src.text_splitter import split_documents
from src.vector_store import create_or_update_vector_store, load_vector_store
from src.rag_pipeline import generate_rag_response
from src.study_planner import generate_study_plan

st.set_page_config(page_title="Student Assistance Chatbot", page_icon="🎓", layout="wide")

# Initialize Session States
if "vector_store" not in st.session_state:
    # Try loading existing disk cache if available
    st.session_state.vector_store = load_vector_store()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []

# Sidebar
with st.sidebar:
    st.title("🎓 Student Assistant")
    st.caption("RAG-Powered Academic Helper")
    st.markdown("---")
    
    st.subheader("📁 Upload Materials")
    
    # Allow multiple file selection
    uploaded_files = st.file_uploader(
        "Upload PDF or TXT notes (Select multiple)",
        type=["pdf", "txt"],
        accept_multiple_files=True
    )
    
    if st.button("⚙️ Process Documents", type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("Please upload at least one document.")
        else:
            with st.spinner("Processing & Indexing Multiple Documents..."):
                all_new_docs = []
                newly_processed_names = []
                
                for file in uploaded_files:
                    # Avoid re-processing files that are already indexed
                    if file.name in st.session_state.processed_files:
                        st.info(f"Skipping '{file.name}' (already processed).")
                        continue
                        
                    try:
                        docs = load_uploaded_file(file)
                        all_new_docs.extend(docs)
                        newly_processed_names.append(file.name)
                    except Exception as e:
                        st.error(f"Failed to process {file.name}: {e}")
                
                if all_new_docs:
                    chunks = split_documents(all_new_docs)
                    
                    # Update FAISS vector store (appends chunks to current store)
                    st.session_state.vector_store = create_or_update_vector_store(
                        chunks, 
                        existing_vector_store=st.session_state.vector_store
                    )
                    
                    # Append new file names to tracking list
                    st.session_state.processed_files.extend(newly_processed_names)
                    st.success(f"Successfully processed {len(newly_processed_names)} new file(s) into {len(chunks)} chunks!")
                elif not newly_processed_names and uploaded_files:
                    st.warning("All selected files have already been processed.")

    # Show list of all active indexed documents
    if st.session_state.processed_files:
        st.markdown("**Indexed Materials:**")
        for f in st.session_state.processed_files:
            st.text(f"• {f}")

    st.markdown("---")
    if st.button("🗑️ Clear Everything", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.vector_store = None
        st.session_state.processed_files = []
        
        # Clear cached vector store from disk
        if os.path.exists(".faiss_index"):
            import shutil
            shutil.rmtree(".faiss_index")
            
        st.rerun()

# Main UI
tab_chat, tab_planner = st.tabs(["💬 Academic Chatbot", "📅 Study Plan Generator"])

# TAB 1: Chatbot Interface
with tab_chat:
    st.title("Academic Q&A Assistant")
    st.write("Ask questions across all your uploaded study materials.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                st.caption(f"**Sources:** {', '.join(message['sources'])}")

    if user_query := st.chat_input("Ask an academic question from your documents..."):
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Searching uploaded documents..."):
                res = generate_rag_response(st.session_state.vector_store, user_query)
                st.markdown(res["answer"])
                
                if res["sources"]:
                    st.caption(f"**Sources:** {', '.join(res['sources'])}")

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": res["answer"],
            "sources": res["sources"]
        })

# TAB 2: Study Planner Interface
with tab_planner:
    st.title("Personalized Study Plan Generator")
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Subject Name", placeholder="e.g., Machine Learning")
        level = st.selectbox("Current Knowledge Level", ["Beginner", "Intermediate", "Advanced"])
    with col2:
        hours = st.number_input("Available Hours Per Day", min_value=0.5, max_value=16.0, value=2.0, step=0.5)
        days = st.number_input("Preparation Days", min_value=1, max_value=60, value=7, step=1)

    if st.button("🚀 Generate Plan", type="primary"):
        if not subject.strip():
            st.warning("Please enter a subject name.")
        else:
            with st.spinner("Drafting study plan..."):
                plan = generate_study_plan(subject, level, hours, days)
                st.markdown(plan)