import json
import os
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from FlagEmbedding import BGEM3FlagModel
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
EMBEDDING_MODEL = 'BAAI/bge-m3'
GROQ_API_KEY = os.getenv("LLM_API_KEY") 
LLM_MODEL = "llama-3.1-8b-instant" 

# 1. CHUNKING 
# chunk_size=500 chars is roughly 150-200 tokens, so max_length=512 is safe.
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)

def load_data():
    try:
        # Load the raw seed data
        with open("documents_mock.json", "r", encoding="utf-8") as f: 
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return []

    # Handle List vs Dict structure
    if isinstance(data, list):
        raw_documents = data
    elif isinstance(data, dict):
        raw_documents = data.get("documents", [])
    else:
        return []
        
    print(f"📂 Loaded {len(raw_documents)} raw documents.")
    all_chunks = []
    
    for doc in raw_documents:
        source_text = doc.get("content_text", "")
        if not source_text: continue

        text_fragments = text_splitter.split_text(source_text)

        for i, fragment in enumerate(text_fragments):
            chunk_object = {
                "chunk_index": i,
                "text": fragment,
                "original_doc_id": doc.get("_id"),
                "filename": doc.get("filename"),
                "matter_id": doc.get("matter_id"),
                "sensitivity": doc.get("sensitivity")
            }
            all_chunks.append(chunk_object)
            
    print(f"✅ Chunking Complete: {len(all_chunks)} chunks created.")
    return all_chunks

def vectorize(chunks):
    print("⏳ Loading Embedder...")
    model = BGEM3FlagModel(EMBEDDING_MODEL, use_fp16=False)
    
    print("🚀 Vectorizing...")
    texts = [c['text'] for c in chunks]
    
    # OPTIMIZATION: Added batch_size and max_length for safety and efficiency
    embeddings = model.encode(
        texts, 
        batch_size=12,      # Process 12 chunks at a time to save RAM
        max_length=512,     # Cap context to 512 tokens (matches chunk_size)
        return_dense=True, 
        return_sparse=False
    )['dense_vecs']
    
    for i, chunk in enumerate(chunks):
        chunk['vector'] = embeddings[i]
        
    return chunks, model

def retrieve(query, chunks, model, top_k=3):
    print(f"\n🔎 Retrieving context for: '{query}'...")
    # Also apply max_length to the query encoding
    query_vec = model.encode(
        [query], 
        max_length=512, 
        return_dense=True, 
        return_sparse=False
    )['dense_vecs'][0]
    
    results = []
    for chunk in chunks:
        doc_vec = chunk['vector']
        # Cosine Similarity
        score = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
        results.append((score, chunk))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return [item for score, item in results[:top_k]]

# --- PART 2: THE GENERATOR ---
def generate_answer(query, context_chunks):
    client = Groq(api_key=GROQ_API_KEY)
    
    # 1. Construct the "Lawyer Context"
    context_text = ""
    for i, chunk in enumerate(context_chunks):
        context_text += f"\n--- SOURCE {i+1} ({chunk['filename']}) ---\n{chunk['text']}\n"

    # 2. The Prompt Engineering
    system_prompt = """You are Lexi, an elite legal AI assistant. 
    Answer the user's question explicitly based on the provided Context.
    
    Rules:
    1. Cite your sources (e.g., "According to the Merger Agreement...").
    2. If the answer is not in the context, say "I cannot find that information in the documents."
    3. Be precise with numbers and dates."""

    user_message = f"""
    Context Documents:
    {context_text}

    User Question: {query}
    """

    print("🤖 Generating answer via Groq (Llama 3)...")
    
    # 3. The API Call
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        model=LLM_MODEL,
        temperature=0.1, 
    )

    return chat_completion.choices[0].message.content

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Setup
    chunks = load_data()
    if chunks:
        vectorized_chunks, model = vectorize(chunks)
        
        # 2. Run the Full Loop
        print("\n" + "="*50)
        user_query = "How much is the retention bonus and who gets it?"
        
        # A. Retrieve
        top_hits = retrieve(user_query, vectorized_chunks, model)
        
        # B. Generate
        final_answer = generate_answer(user_query, top_hits)
        
        print(f"\n📝 LEXI'S ANSWER:\n{final_answer}")
        print("="*50)