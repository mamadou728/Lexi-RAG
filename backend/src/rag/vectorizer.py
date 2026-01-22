import uuid
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from models import DocumentFile
# Placeholder for your embedding provider
from services.ai import embedding_service 

class Vectorizer:
    def __init__(self):
        # Initialize Qdrant
        self.qdrant = QdrantClient(host="localhost", port=6333)
        self.collection_name = "lexiray_vectors"
        self._ensure_collection()

    async def process_document(self, doc: DocumentFile, raw_text: str):
        print(f"⚡ Vectorizing {doc.filename}...")

        # 1. SPLIT (Chunking)
        chunks = self._split_text(raw_text, chunk_size=1000, overlap=100)
        
        points_batch = []

        # 2. EMBED (The "Vectorization")
        for index, chunk_text in enumerate(chunks):
            vector = await embedding_service.get_embedding(chunk_text)
            
            # 3. PACK (Create Qdrant Point)
            points_batch.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "mongo_doc_id": str(doc.id),      # Link to Parent
                    "matter_id": str(doc.matter_id),  # Security Filter
                    "chunk_index": index,
                    "preview": chunk_text[:50]        # Snippet only
                }
            ))

        # 4. PUSH (Upsert)
        if points_batch:
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=points_batch
            )

        # 5. FINALIZE (Update Status)
        doc.is_vectorized = True
        await doc.save()
        
        print(f"✅ Vectorization Complete: {len(points_batch)} chunks created.")

    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    def _ensure_collection(self):
        if not self.qdrant.collection_exists(self.collection_name):
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config={"size": 1536, "distance": "Cosine"}
            )

    async def delete_vectors(self, doc_id: str):
        """
        FLUSH: Deletes all vector chunks linked to this document ID.
        """
        print(f"🗑️  Flushing vectors for Doc ID: {doc_id}...")
        
        self.qdrant.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="mongo_doc_id", 
                        match=MatchValue(value=doc_id)
                    )
                ]
            )
        )

    async def update_vectors(self, doc: DocumentFile, new_raw_text: str):
        """
        FLUSH & FILL: Clears old brain, creates new brain.
        """
        # Step 1: Flush (Delete old vectors)
        await self.delete_vectors(str(doc.id))
        
        # Step 2: Fill (Reuse the existing process logic)
        # This will chunk the NEW text and insert NEW points
        await self.process_document(doc, new_raw_text)
        
        print(f"🔄 Update Complete: Document {doc.filename} re-indexed.")
# Singleton instance
vectorizer = Vectorizer()