from turtle import title
from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.database import init_db
# from qdrant_client import QdrantClient
# from core.config import QDRANT_URL, QDRANT_API_KEY



 # qdrant_client: QdrantClient = None
# Lifespan manager for FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database connections
    mongo_client = await init_db()
    
    # Yield control back to FastAPI application
    yield
    
    # Cleanup actions can be performed here if necessary
    mongo_client.close()
    print("✅ Database connections closed.")



    # global qdrant_client
    # qdrant_client = QdrantClient(
    #     url=QDRANT_URL, 
    #     api_key=QDRANT_API_KEY
    # )
    # try:
    #     qdrant_client.get_collections()
    #     print("✅ Qdrant connected successfully.")
    # except Exception as e:
    #     print(f"❌ Failed to connect to Qdrant: {e}")

    yield # Application runs here

    print("✅ Application shutdown complete.")
    # if qdrant_client:
    #     qdrant_client.close()
    #     print("✅ Qdrant connection closed.")   

app = FastAPI(title="Lexi-rag", lifespan=lifespan)

# def get_qdrant():
#     return qdrant_client