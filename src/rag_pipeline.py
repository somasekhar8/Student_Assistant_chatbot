import os
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

SYSTEM_RAG_PROMPT = """
You are an expert, encouraging Academic Assistant for university and technical students.
Your task is to answer the student's question based strictly on the provided context materials.

Context:
{context}

Question:
{question}

Instructions:
1. Provide clear, simple, student-friendly explanations.
2. If the answer is present in the Context, answer thoroughly using bullet points where appropriate.
3. If the Context does NOT contain enough information to answer the question, state clearly:
   "I could not find the answer to this question in your uploaded study materials."
   Do NOT attempt to invent or hallucinate facts outside the provided text.
"""

def get_fallback_llm():
    groq_key = os.getenv("GROQ_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    # Primary Model: Groq LPU (Ultra-fast primary)
    primary_llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.2,
        groq_api_key=groq_key,
        timeout=10.0
    )

    # Secondary Backup: Google Gemini
    fallback_llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        temperature=0.2,
        google_api_key=google_key,
        timeout=10.0
    )

    # Set Groq as Primary and Gemini as Fallback
    return primary_llm.with_fallbacks([fallback_llm])

def get_rag_chain():
    llm = get_fallback_llm()
    prompt = ChatPromptTemplate.from_template(SYSTEM_RAG_PROMPT)
    return prompt | llm | StrOutputParser()

def generate_rag_response(vector_store, question: str) -> Dict[str, Any]:
    if not vector_store:
        return {
            "answer": "No documents have been uploaded or processed yet. Please upload study materials in the sidebar first.",
            "sources": [],
            "recommendations": []
        }

    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    relevant_docs: List[Document] = retriever.invoke(question)

    if not relevant_docs:
        return {
            "answer": "I could not find relevant information in your uploaded materials.",
            "sources": [],
            "recommendations": []
        }

    context_str = "\n\n".join([f"--- Chunk from {doc.metadata.get('source', 'Unknown')} ---\n{doc.page_content}" for doc in relevant_docs])
    
    rag_chain = get_rag_chain()
    
    try:
        answer = rag_chain.invoke({"context": context_str, "question": question})
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"

    sources = list(set([
        f"{doc.metadata.get('source', 'Document')} (Page {doc.metadata.get('page', 0) + 1})"
        for doc in relevant_docs
    ]))

    return {
        "answer": answer,
        "sources": sources,
        "recommendations": []
    }