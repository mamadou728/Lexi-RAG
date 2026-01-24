from beanie import Document, Link, PydanticObjectId
from pydantic import Field, ConfigDict
from enum import Enum
from datetime import datetime, timezone

class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVILEGED = "privileged"
    DISCOVERY = "discovery"

class DocumentFile(Document):
    """
    THE VAULT (Text Only)
    No PDFs. No S3. Just the secure text.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # This acts as the "Title" of the document
    filename: str 
    
    # Relationships
    matter_id: PydanticObjectId 
    
    # SECURITY
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    
    # THE CONTENT (Layer 2)
    # Since we have no S3, this is the ONLY place the text exists.
    # It MUST be here, or you lose the data.
    encrypted_blob: bytes 
    
    # Status
    is_vectorized: bool = False
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "documents"