import os
from dotenv import load_dotenv  

load_dotenv()  # Load environment variables from .env file

MONGO_URI = os.getenv("MONGO_URI")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("LLM_API_KEY")

if not MONGO_URI or not QDRANT_URL or not QDRANT_API_KEY:
    raise ValueError("One or more required environment variables are missing.")

