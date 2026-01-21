from beanie import Document, Link
from pydantic import Field
from enum import Enum
from datetime import datetime, timezone
from ..matters.models import Matter

class SensitivityLevel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVILEGED = "privileged"
    DISCOVERY = "discovery"

class DocumentFile(Document):
    filename: str
    file_type: str  # .pdf, .docx
    storage_path: str # S3 URL
    
    # Relationships
    matter: Link[Matter]
    
    # SECURITY LAYERS
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    
    # This field MUST be encrypted before saving (Layer 2)
    extracted_text: bytes 
    
    # Layer 1: Link to the "Blind Index" in Qdrant
    qdrant_point_id: str 
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "documents"