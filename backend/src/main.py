from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.database import init_db

# Lifespan manager for FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database connections
    mongo_client, qdrant_client = await init_db()
    
    # Yield control back to FastAPI application
    yield
    
    # Cleanup actions can be performed here if necessary
    mongo_client.close()
    print("✅ Database connections closed.")
