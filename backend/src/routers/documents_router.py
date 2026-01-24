from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from bson import ObjectId
from qdrant_client import QdrantClient 

# Import your models, encryption, and the vector tool
from models.documents import DocumentFile, SensitivityLevel
from models.matters import Matter
from core.encryption import AES256Service
from rag.vectorizer import vectorize 
from core.config import QDRANT_URL, QDRANT_API_KEY 

router = APIRouter(prefix="/documents", tags=["Secure Documents"])

# --- 0. Global Qdrant Connection ---
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# --- 1. Request Schema ---
class DocumentUploadRequest(BaseModel):
    matter_id: str
    filename: str
    content: str
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL

# --- 2. Response Schema ---
class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    message: str
    is_vectorized: bool

# --- 3. Dependency ---
def get_encryption_service():
    return AES256Service() 

# --- 4. The Unified Endpoint ---
@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    payload: DocumentUploadRequest,
    cipher: AES256Service = Depends(get_encryption_service)
):
    """
    1. Encrypts content -> MongoDB (The Vault)
    2. Vectorizes content -> Qdrant (The Brain)
    """
    
    # A. Validate Matter ID
    if not ObjectId.is_valid(payload.matter_id):
        raise HTTPException(status_code=400, detail="Invalid Matter ID format")
    
    matter = await Matter.get(ObjectId(payload.matter_id))
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    # B. ENCRYPTION & MONGO STORAGE
    try:
        encrypted_blob = cipher.encrypt_text(payload.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

    new_doc = DocumentFile(
        filename=payload.filename,
        matter_id=matter.id,
        sensitivity=payload.sensitivity,
        encrypted_blob=encrypted_blob,
        is_vectorized=False 
    )
    
    # Save to MongoDB first (Safety First)
    await new_doc.insert()

    # C. VECTORIZATION (Qdrant)
    try:
        vectorize(
            content_text=payload.content, 
            metadata={
                "mongo_document_id": str(new_doc.id), # Linking ID
                "filename": payload.filename,
                "matter_id": payload.matter_id,
                "sensitivity": payload.sensitivity
            },
            qdrant_client=qdrant_client
        )
        
        # Update flag
        new_doc.is_vectorized = True
        await new_doc.save()
        
    except Exception as e:
        print(f"⚠️ Vectorization Error: {e}")

    return DocumentResponse(
        document_id=str(new_doc.id),
        filename=new_doc.filename,
        message="Document uploaded, encrypted, and indexed.",
        is_vectorized=new_doc.is_vectorized
    )
