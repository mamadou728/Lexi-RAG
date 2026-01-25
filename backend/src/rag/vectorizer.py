import os
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Clients & Models
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchAny
from FlagEmbedding import BGEM3FlagModel
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import your data models
from models.auth import SystemRole

# --- 1. CENTRALIZED CONFIGURATION ---
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("LLM_API_KEY")
COLLECTION_NAME = "legal_documents"

# Initialize Clients ONCE (Global Singleton Pattern)
print("⏳ Initializing Global AI Engine...")

# A. The Brain (Qdrant)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# B. The Translator (BGE-M3 Model)
# We load this once to avoid reloading 2GB weights on every request
embedding_model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=False)

# C. The Generator (LLM)
groq_client = Groq(api_key=GROQ_API_KEY)

# D. The Text Splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

print("✅ AI Engine Ready.")

# --- 2. PERMISSIONS LOGIC ---
# Define who can see what. Centralized here for easy changes.
PERMISSION_MATRIX = {
    SystemRole.PARTNER:   ["public", "internal", "privileged", "discovery"],
    SystemRole.ASSOCIATE: ["public", "internal", "privileged", "discovery"],
    SystemRole.STAFF:     ["public", "internal"], 
    SystemRole.CLIENT:    ["public"]              
}

def get_allowed_sensitivities(role: SystemRole) -> List[str]:
    return PERMISSION_MATRIX.get(role, [])

# --- 3. CORE FUNCTIONS ---

def vectorize_and_upload(content_text: str, metadata: Dict[str, Any]):
    """
    Chunks text -> Creates Vectors -> Uploads to Qdrant.
    """
    if not content_text:
        return

    # A. Chunking
    chunks = text_splitter.split_text(content_text)
    
    # B. Vectorization (Batch)
    embeddings = embedding_model.encode(
        chunks, batch_size=12, max_length=512, return_dense=True
    )['dense_vecs']

    # C. Prepare Points
    points = []
    for i, (text, vector) in enumerate(zip(chunks, embeddings)):
        
        # Combine global metadata with chunk metadata
        payload = metadata.copy()
        payload.update({
            "chunk_index": i,
            "text_snippet": text 
        })

        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector={"dense_vector": vector.tolist()},  # Named vector to match collection schema
            payload=payload
        ))

    # D. Upload
    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✅ Indexed {len(points)} chunks for {metadata.get('filename')}")


def vectorize(
    content_text: str,
    metadata: Dict[str, Any],
    qdrant_client: Optional[QdrantClient] = None,
) -> None:
    """
    Wrapper for vectorize_and_upload. Uses global qdrant_client if none passed.
    """
    vectorize_and_upload(content_text, metadata)


def retrieve_safe_documents(query: str, user_role: SystemRole, top_k: int = 3) -> List[Dict]:
    """
    Searches Qdrant with a STRICT security filter based on User Role.
    """
    

    # A. Get Permissions
    allowed_levels = get_allowed_sensitivities(user_role)
    if not allowed_levels:
        print("⛔ Access Denied.")
        return []

    # B. Build Security Filter
    # "Only return docs where 'sensitivity' is inside the allowed_levels list"
    security_filter = Filter(
        must=[
            FieldCondition(
                key="sensitivity", 
                match=MatchAny(any=allowed_levels)
            )
        ]
    )

    # C. Search
    query_vector = embedding_model.encode(query, return_dense=True)['dense_vecs']
    
    hits = qdrant_client.search(
        collection_name=COLLECTION_NAME,
        query_vector=("dense_vector", query_vector),  # Specify named vector
        query_filter=security_filter,
        limit=top_k
    )

    # D. Clean Results
    return [
        {
            "filename": hit.payload.get("filename"),
            "sensitivity": hit.payload.get("sensitivity"),
            "text": hit.payload.get("text_snippet"),
            "score": hit.score
        }
        for hit in hits
    ]


def generate_legal_answer(query: str, context_docs: List[Dict]) -> str:
    """
    Generates an answer using Groq (Llama 3) based on retrieved docs.
    """
    if not context_docs:
        return "I cannot find any information relevant to your access level."

    # Format Context
    context_str = "\n".join([
        f"SOURCE: {d['filename']} ({d['sensitivity']})\nTEXT: {d['text']}\n"
        for d in context_docs
    ])

    # Prompt
    system_prompt = (
        "You are Lexi, a legal AI. Answer strictly using the provided context. "
        "Cite the Source filename for every fact."
    )

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {query}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {e}"

# --- 4. OPTIONAL: TEST RUNNER ---
if __name__ == "__main__":
    # Test as a Staff member (Should NOT see Privileged docs)
    test_role = SystemRole.STAFF 
    query = "What is the retention bonus?"

    docs = retrieve_safe_documents(query, test_role)
    answer = generate_legal_answer(query, docs)

    print(f"\n📝 Question: {query}")
    print(f"👤 Role: {test_role.value}")
    print(f"🤖 Answer: {answer}")