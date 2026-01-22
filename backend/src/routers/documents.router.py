from fastapi import APIRouter, UploadFile, File, HTTPException
from bson import ObjectId
from datetime import datetime, timezone

from ..core.security import security_service
from ..rag.vectorizer import vectorizer 
from ..models.documents.model import DocumentFile, SensitivityLevel

# Placeholder for your extraction utility
# from utils.pdf_extractor import extract_text_helper 

router = APIRouter()

@router.post("/upload")
async def upload_document(
    matter_id: str, 
    sensitivity: SensitivityLevel,
    file: UploadFile = File(...)
):
    # Validate Matter ID format
    if not ObjectId.is_valid(matter_id):
        raise HTTPException(status_code=400, detail="Invalid Matter ID")

    # 1. Extract Text
    file_bytes = await file.read()
    try:
        # Swap this with your actual PDF/Docx extractor
        raw_text = file_bytes.decode("utf-8") 
    except Exception:
        raise HTTPException(status_code=400, detail="Text extraction failed")

    # 2. Encrypt (App-Side)
    encrypted_bytes = security_service.encrypt_text(raw_text)

    # 3. Create Record (MongoDB)
    # Serves as the vault for the content; no S3 path needed.
    doc = DocumentFile(
        filename=file.filename,
        file_type=file.filename.split('.')[-1] if '.' in file.filename else "txt",
        matter_id=ObjectId(matter_id),
        sensitivity=sensitivity,
        encrypted_blob=encrypted_bytes, 
        is_vectorized=False
    )
    await doc.insert() 
    
    # 4. Trigger Ingestion (Qdrant)
    # Pass raw_text to avoid decrypting again in the worker.
    await vectorizer.process_document(
        doc=doc, 
        raw_text=raw_text
    )

    return {
        "status": "processing_started", 
        "doc_id": str(doc.id),
        "filename": doc.filename
    }


@router.put("/documents/{doc_id}")
async def update_document(
    doc_id: str, 
    file: UploadFile = File(...)
):
    # 0. Validate & Fetch
    if not ObjectId.is_valid(doc_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    doc = await DocumentFile.get(ObjectId(doc_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. READ & EXTRACT NEW TEXT
    file_bytes = await file.read()
    try:
        new_raw_text = file_bytes.decode("utf-8") # Replace with PDF extractor
    except:
        raise HTTPException(status_code=400, detail="Extraction failed")

    # 2. UPDATE VAULT (MongoDB)
    # We encrypt the new content and overwrite the old blob
    doc.encrypted_blob = security_service.encrypt_text(new_raw_text)
    doc.filename = file.filename # Update name if changed
    doc.updated_at = datetime.now(timezone.utc)
    
    # Reset status since we are about to re-process
    doc.is_vectorized = False 
    await doc.save() # Commit changes to Mongo

    # 3. UPDATE BRAIN (Trigger Vectorizer)
    # This runs the "Flush & Fill"
    await vectorizer.update_vectors(doc, new_raw_text)

    return {"status": "updated", "doc_id": str(doc.id)} 


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    # 0. Validate & Fetch
    if not ObjectId.is_valid(doc_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    doc = await DocumentFile.get(ObjectId(doc_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1. DELETE FROM BRAIN (Qdrant)
    # We do this first so we don't lose the ID reference
    await vectorizer.delete_vectors(str(doc.id))

    # 2. DELETE FROM VAULT (MongoDB)
    await doc.delete()

    return {"status": "deleted", "id": doc_id}