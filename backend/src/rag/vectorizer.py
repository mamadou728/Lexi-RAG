"""
Vectorizer module for RAG system.
Handles text chunking, vectorization, and uploading to Qdrant.
"""
import uuid
from typing import Dict, Any, Optional, TypedDict
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Import shared clients and config
from rag.config import qdrant_client, embedding_model, text_splitter, COLLECTION_NAME


class VectorPayload(TypedDict):
    """
    Payload structure for vectorized documents in Qdrant.
    
    This is the exact structure stored with each vector in the vector database.
    Example:
    {
        "mongo_document_id": "697645446aa189363a751ffa",
        "filename": "AI_Startup_Financials_FY2025.xlsx",
        "matter_id": "6976453b4d7b3821fdd38804",
        "sensitivity": "internal",
        "chunk_index": 0,
        "text_snippet": "CONFIDENTIAL FINANCIAL REPORTING - FY 2025 SHEET …"
    }
    """
    mongo_document_id: str
    filename: str
    matter_id: str
    sensitivity: str
    chunk_index: int
    text_snippet: str


class VectorMetadata(BaseModel):
    """
    Input metadata for vectorization.
    This is what gets passed to vectorize() function.
    The vectorizer will add chunk_index and text_snippet automatically.
    """
    mongo_document_id: str
    filename: str
    matter_id: str
    sensitivity: str

def vectorize_and_upload(content_text: str, metadata: Dict[str, Any]):
    """
    Chunks text -> Creates Vectors -> Uploads to Qdrant.
    
    Args:
        content_text: The text content to vectorize
        metadata: Dictionary containing:
            - mongo_document_id: MongoDB document ID (str)
            - filename: Document filename (str)
            - matter_id: Matter ID (str)
            - sensitivity: Sensitivity level (str) - "public", "internal", "privileged", or "discovery"
    
    The function automatically adds:
        - chunk_index: Index of the chunk (int)
        - text_snippet: The actual text content of the chunk (str)
    
    Resulting payload structure (VectorPayload):
    {
        "mongo_document_id": str,
        "filename": str,
        "matter_id": str,
        "sensitivity": str,
        "chunk_index": int,
        "text_snippet": str
    }
    """
    if not content_text:
        return

    # A. Chunking
    chunks = text_splitter.split_text(content_text)
    
    # B. Vectorization (Batch)
    embeddings = embedding_model.encode(
        chunks, batch_size=12, max_length=512, return_dense=True
    )['dense_vecs']

    # C. Prepare Points
    points = []
    for i, (text, vector) in enumerate(zip(chunks, embeddings)):
        
        # Combine global metadata with chunk metadata
        # This creates the VectorPayload structure
        payload: VectorPayload = {
            "mongo_document_id": metadata.get("mongo_document_id", ""),
            "filename": metadata.get("filename", ""),
            "matter_id": metadata.get("matter_id", ""),
            "sensitivity": metadata.get("sensitivity", "internal"),
            "chunk_index": i,
            "text_snippet": text
        }

        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector={"dense_vector": vector.tolist()},  # Named vector to match collection schema
            payload=payload
        ))

    # D. Upload
    if points:
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"✅ Indexed {len(points)} chunks for {metadata.get('filename')}")


def vectorize(
    content_text: str,
    metadata: Dict[str, Any],
    qdrant_client: Optional[QdrantClient] = None,
) -> None:
    """
    Wrapper for vectorize_and_upload. Uses global qdrant_client if none passed.
    """
    vectorize_and_upload(content_text, metadata)