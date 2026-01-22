# Mongo & Qdrant factories
from xmlrpc import client
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie  
from qdrant_client import QdrantClient , models
import os
from .config import MONGO_URI, QDRANT_URL, QDRANT_API_KEY
import certifi
# Import the models to register in the module

from ..models.message.model import Conversation
from ..models.matters.model import Matter
from ..models.auth.model import User
from ..models.documents.model import DocumentFile

async def init_db():
    # Initialize MongoDB Client

    db_client = MONGO_URI
    if not db_client:
        db_client = "DB not found from .env"
   
    mongo_client = AsyncIOMotorClient(
        db_client,
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

    if qdrant_client.collection_exists(collection_name):
        qdrant_client.delete_collection(collection_name) 
    if not qdrant_client.collection_exists(collection_name):
        print(f"Creating Cloud collection: {collection_name}")
        
        qdrant_client.recreate_collection(
           collection_name=collection_name,
    vectors_config={
        "dense_vector": models.VectorParams(
            size=1024,  # BGE-M3 fixed size
            distance=models.Distance.COSINE
        )
    },
    sparse_vectors_config={
        "sparse_vector": models.SparseVectorParams(
            index=models.SparseIndexParams(
                on_disk=False, # Keep in RAM for speed
            )
        )
    }
)
        print("✅ Qdrant client initialized and collection is ready!")
    else:
        print(f"Qdrant collection '{collection_name}' already exists.")
    
    return mongo_client, qdrant_client
