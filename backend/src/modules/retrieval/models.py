from beanie import Document, Link
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from enum import Enum
from modules.matters.models import Matter
from modules.auth.models import User

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

# Sub-model (Embedded inside Message, not a separate collection)
class Citation(BaseModel):
    document_id: str
    filename: str
    page_number: Optional[int]
    quote_snippet: str
    score: float

class Message(BaseModel):
    role: Role
    content: str
    citations: List[Citation] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Conversation(Document):
    title: str
    matter: Link[Matter]
    user: Link[User]
    
    # We store messages as a list inside the Conversation document
    # efficient for reading history
    messages: List[Message] = []
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "conversations"