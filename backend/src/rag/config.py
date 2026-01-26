"""
Shared configuration and client initialization for RAG system.
All clients are initialized once as singletons to avoid reloading.
"""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from FlagEmbedding import BGEM3FlagModel
from groq import Groq
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- CENTRALIZED CONFIGURATION ---
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
