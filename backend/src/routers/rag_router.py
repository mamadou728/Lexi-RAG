from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional

# Import Security
from core.security import get_current_user # <--- The Guard
from models.auth import User, SystemRole
import rag.vectorizer as rag

router = APIRouter(prefix="/search", tags=["Retrieval System"])

# --- UPDATED INPUT SCHEMA (No user_role here!) ---
class SearchRequest(BaseModel):
    query: str
    matter_id: Optional[str] = None

class SourceDocument(BaseModel):
    filename: str
    sensitivity: str
    score: float

class SearchResponse(BaseModel):
    ai_answer: str
    sources: List[SourceDocument]

@router.post("/query", response_model=SearchResponse)
async def ask_lexi(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user) # <--- Authenticated User Only
):
    """
    1. Authenticates the user via Token.
    2. Extracts their SystemRole automatically.
    3. Runs the Secure Search.
    """
    
    # Validation
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    print(f"👤 Authenticated Search for: {current_user.email} ({current_user.system_role})")

    # Pass the TRUSTED role from the database, not the user input
    retrieved_docs = rag.retrieve_safe_documents(
        query=payload.query,
        user_role=current_user.system_role, # <--- Comes from DB
        top_k=5 
    )

    answer_text = rag.generate_legal_answer(
        query=payload.query,
        context_docs=retrieved_docs
    )

    formatted_sources = [
        SourceDocument(
            filename=doc['filename'],
            sensitivity=doc['sensitivity'],
            score=doc['score']
        )
        for doc in retrieved_docs
    ]

    return SearchResponse(
        ai_answer=answer_text,
        sources=formatted_sources
    )
