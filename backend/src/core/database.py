# Mongo & Qdrant factories
from xmlrpc import client
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie  
from qdrant_client import QdrantClient
import os
from .config import MONGO_URI, QDRANT_URL, QDRANT_API_KEY
# Import the models to register in the module

from ..modules.retrieval.models import Conversation
from ..modules.matters.models import Matter
from ..modules.auth.models import User
from ..modules.documents.models import DocumentFile

async def init_db():
    # Initialize MongoDB Client

    db_client = MONGO_URI
    if not db_client:
        db_client = "DB not found from .env"
   
    mongo_client = AsyncIOMotorClient(db_client)
    database = mongo_client.lexi_rag_db
    
    # Initialize Beanie with the database and the document models
    await init_beanie(
        database, 
        document_models=[
            User, 
            Matter, 
            DocumentFile, 
            Conversation
            ]
         )
    
    print("✅ Database initialized! MongoDB and Beanie are connected.")
  
  
  
  
    # Initialize Qdrant Client
    qdrant_client = QdrantClient(
        url=QDRANT_URL, 
        api_key=QDRANT_API_KEY
        )
    
    collection_name = "legal_documents"
    
    if not qdrant_client.collection_exists(collection_name):
        print(f"Creating Cloud collection: {collection_name}")
        
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                "size": 1536,  # Adjust based on your embedding model
                "distance": "Cosine"
            }
        )
        print("✅ Qdrant client initialized and collection is ready!")
    else:
        print(f"Qdrant collection '{collection_name}' already exists.")
    
    return mongo_client, qdrant_client
