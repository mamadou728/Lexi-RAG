from beanie import Document, Link
from pydantic import Field
from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
# Import the User model to link to it
from src.models.auth.model import User

class PracticeArea(str, Enum):
    LITIGATION = "litigation"
    CORPORATE = "corporate"
    IP = "intellectual_property"
    REAL_ESTATE = "real_estate"

class Matter(Document):
    title: str
    description: Optional[str] = None
    
    # Link to the User document (Foreign Key logic)
    client: Link[User] 
    assigned_team: List[Link[User]] = []
    
    practice_area: PracticeArea
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "matters"