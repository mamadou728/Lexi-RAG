from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.database import init_db
from routers import auth_router, documents_router, rag_router 

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan Manager:
    Runs BEFORE the app starts (to connect DBs)
    and AFTER the app stops (to close connections).
    """
    
    # 1. Initialize MongoDB & Beanie
    # This connects to Mongo and sets up your User/Document/Matter models
    mongo_client, qdrant_client = await init_db()
    
    # Yield control -> The Application runs now
    yield
    
    # 2. Cleanup (When you press Ctrl+C)
    mongo_client.close()
    print("✅ Database connections closed. Application shutdown complete.")

# Create the App
app = FastAPI(
    title="Lexi-RAG API",
    version="1.0.0",
    lifespan=lifespan
)

# Register the Routers
app.include_router(auth_router.router)       # /auth/login
app.include_router(documents_router.router)  # /documents/upload
app.include_router(rag_router.router)        # /search/query

@app.get("/")
async def root():
    return {"status": "online", "message": "Lexi AI is ready to help! 🟢"}