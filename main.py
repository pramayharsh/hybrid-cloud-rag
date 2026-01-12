import os
import sys
from dotenv import load_dotenv

print("--- [DEBUG] Script Started ---", flush=True)

try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    from src.database import create_vector_store
    from src.llm_logic import get_llm
    print("--- [DEBUG] Imports Successful ---", flush=True)
except Exception as e:
    print(f"--- [DEBUG] Import Error: {e} ---", flush=True)
    sys.exit(1)

load_dotenv()

def main():
    print("--- 📚 Modern RAG System Initializing ---", flush=True)
    
    # 1. Smart Load Data
    pdf_path = "data/test_facts.txt" # or "test_facts.txt"
    if not os.path.exists(pdf_path):
        print(f"Error: '{pdf_path}' not found.")
        return

    print(f"--- [DEBUG] Found {pdf_path}. Starting Load... ---", flush=True)
    
    # Check extension and pick the right loader
    if pdf_path.endswith(".pdf"):
        loader = PyPDFLoader(pdf_path)
    elif pdf_path.endswith(".txt"):
        loader = TextLoader(pdf_path)
    else:
        print("Unsupported file format!")
        return

    docs = loader.load()
    print(f"--- [DEBUG] File Loaded. Pages/Docs: {len(docs)} ---", flush=True)

    print("--- [DEBUG] Splitting Text... ---", flush=True)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(docs)

    print(f"--- [DEBUG] Created {len(chunks)} chunks. ---", flush=True)
    
    # SAFETY: Use only the first 20 chunks for the first test
    test_chunks = chunks[:20] 
    print(f"--- [DEBUG] Using 20 chunks for testing stability. ---", flush=True)

    print("--- [DEBUG] Initializing FAISS Vector Store... ---", flush=True)
    vector_db = create_vector_store(test_chunks)
    print("--- [DEBUG] Vector Store Ready. ---", flush=True)

    print("--- [DEBUG] Initializing LLM (Groq)... ---", flush=True)
    llm = get_llm()

    system_prompt = (
        "You are an assistant for question-answering tasks. Use the context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(vector_db.as_retriever(), combine_docs_chain)

    print("\n✅ System Ready! Ask a question (type 'exit' to stop):", flush=True)
    while True:
        query = input("\nYou: ")
        if query.lower() in ['exit', 'quit']: break
        
        print("--- [DEBUG] AI is thinking... ---", flush=True)
        response = rag_chain.invoke({"input": query})
        print(f"\nAI: {response['answer']}")

if __name__ == "__main__":
    main()