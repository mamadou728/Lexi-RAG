from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException

# Import your models and encryption class
from models.documents import DocumentFile, SensitivityLevel
from models.matters import Matter
from core.encryption import AES256Service

class VaultService:
    def __init__(self):
        # Initialize encryption service once
        # In production, ensure APP_ENCRYPTION_KEY is in your .env
        self.cipher = AES256Service()

    async def secure_store_text(self, matter_id: str, filename: str, content: str, sensitivity: SensitivityLevel):
        """
        1. Verifies Matter exists.
        2. Encrypts the content.
        3. Saves to MongoDB (The Vault).
        """
        # 1. Verify Matter ID
        matter = await Matter.get(ObjectId(matter_id))
        if not matter:
            raise HTTPException(status_code=404, detail="Matter not found")

        # 2. Encrypt the content (Layer 2 Security)
        # This returns the packed bytes (Nonce + Ciphertext + Tag)
        encrypted_data = self.cipher.encrypt_text(content)

        # 3. Create Document Record
        doc = DocumentFile(
            filename=filename,
            matter_id=matter.id,
            sensitivity=sensitivity,
            encrypted_blob=encrypted_data, # <--- The secure payload
            is_vectorized=False # Flag to trigger background vectorization worker later
        )
        
        await doc.insert()
        return doc

    async def secure_retrieve_text(self, document_id: str) -> str:
        """
        1. Finds document.
        2. Decrypts blob.
        3. Returns Plaintext.
        """
        doc = await DocumentFile.get(ObjectId(document_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Decrypt
        try:
            plaintext = self.cipher.decrypt_text(doc.encrypted_blob)
            return plaintext
        except ValueError:
             raise HTTPException(status_code=500, detail="Decryption failed. Key mismatch or data corruption.")