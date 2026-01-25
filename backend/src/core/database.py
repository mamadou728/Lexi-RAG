# Mongo & Qdrant factories
from xmlrpc import client
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie  
from qdrant_client import QdrantClient, models
import os
import ssl
from .config import MONGO_URI, QDRANT_URL, QDRANT_API_KEY
import certifi
# Import the models to register in the module
from models.message import Conversation
from models.matters import Matter
from models.auth import User
from models.documents import DocumentFile

async def init_db():
    # Initialize MongoDB Client
    mongo_client = AsyncIOMotorClient(
        MONGO_URI,
        tlsCAFile=certifi.where()
    )
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

    # --- EDITED SECTION: SAFE INITIALIZATION ---
    
    # Check if the collection exists
    if qdrant_client.collection_exists(collection_name):
        # If it exists, do NOTHING. Just print success.
        print(f"✅ Qdrant collection '{collection_name}' already exists. Skipping creation.")
        
    else:
        # Only create if it does NOT exist
        print(f"⚠️ Collection '{collection_name}' not found. Creating Cloud collection...")
        
        qdrant_client.create_collection(
           collection_name=collection_name,
           vectors_config={
               "dense_vector": models.VectorParams(
                   size=1024,  
                   distance=models.Distance.COSINE
               )
           },
        )
        
        # Create payload indexes for filtering
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="mongo_document_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="sensitivity",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name="matter_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        
        print("✅ Qdrant collection created and indexes set!")
    
    return mongo_client, qdrant_client