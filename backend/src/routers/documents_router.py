from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from bson import ObjectId
from qdrant_client import QdrantClient, models  # <--- Added 'models' for filtering
from models.documents import DocumentFile, SensitivityLevel
from models.matters import Matter
from core.encryption import AES256Service
from rag import vectorize 
from core.config import QDRANT_URL, QDRANT_API_KEY 
import asyncio  
from fastapi.concurrency import run_in_threadpool


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
    3. Verifies Qdrant Storage -> Confirms (The Check)
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
    
    # Save to MongoDB first
    await new_doc.insert()

   # C. VECTORIZATION & VERIFICATION
    verification_msg = "Pending"
    
    try:
        # --- THE FIX: Run blocking code in a threadpool ---
        await run_in_threadpool(
            vectorize, 
            content_text=payload.content, 
            metadata={
                "mongo_document_id": str(new_doc.id),
                "filename": payload.filename,
                "matter_id": payload.matter_id,
                "sensitivity": payload.sensitivity
            },
            qdrant_client=qdrant_client
        )
        # -------------------------------------------------
        
        # Give Qdrant a moment
        await asyncio.sleep(1.0) 

        # The check (Async is fine here because client.scroll is fast/network bound)
        # Note: If qdrant_client is the synchronous client, wrap this too!
        # Assuming qdrant_client is standard sync client:
        scroll_result, _ = await run_in_threadpool(
            qdrant_client.scroll,
            collection_name="legal_documents",
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="mongo_document_id",
                        match=models.MatchValue(value=str(new_doc.id))
                    )
                ]
            ),
            limit=1
        )

        if scroll_result:
            new_doc.is_vectorized = True
            verification_msg = "Verified: Found in Vector DB"
        else:
            verification_msg = "Warning: Upload ran, but not found."
            print(f"⚠️ Doc {new_doc.id} missing from Qdrant.")

        await new_doc.save()
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        # Check your SERVER TERMINAL for the full error if this happens!
        verification_msg = f"Failed: {str(e)}"

    return DocumentResponse(
        document_id=str(new_doc.id),
        filename=new_doc.filename,
        message=f"Status: {verification_msg}",
        is_vectorized=new_doc.is_vectorized
    )