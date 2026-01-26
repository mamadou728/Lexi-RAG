from typing import List, Optional
from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

# 1. The Exact Structure of your Source (Snapshot)
class Citation(BaseModel):
    mongo_document_id: str  # The ID of the original file in your DB
    filename: str           # "AI_Startup_Financials_FY2025.xlsx"
    matter_id: str          # "6976453b..." (Crucial for legal grouping)
    sensitivity: str        # "internal" / "confidential"
    chunk_index: int        # 0
    text_snippet: str       # The content used to answer
    score: Optional[float] = 0.0 # RAG Similarity Score (added during retrieval)

class ChatSession(Document):
    user_email: str
    name: Optional[str] = "New Chat"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_sessions"
        indexes = [
            "user_email",
            [("user_email", 1), ("updated_at", -1)]
        ]

class ChatMessage(Document):
    session_id: PydanticObjectId
    role: str    # "user" or "ai"
    content: str # The text answer
    
    # 2. Embedding the Citations directly in the message
    citations: List[Citation] = [] 
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_messages"
        indexes = [
            "session_id",
            [("session_id", 1), ("created_at", 1)]
        ]