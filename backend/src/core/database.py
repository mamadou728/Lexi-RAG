# Mongo & Qdrant factories
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie  
from qdrant_client import QdrantClient
import os

# Import the models to register in the module

from modules.retrieval.models import Conversation
from modules.matters.models import Matter
from modules.auth.models import User
from modules.documents.models import DocumentFile

async def init_db():
    # Initialize MongoDB Client

    db_client = os.getenv("MONGO_URL")
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
    qdrant_client = QdrantClient(url="http://localhost:6333")
    
    # You can add additional setup for Qdrant here if needed
    
    return mongo_client, qdrant_client
