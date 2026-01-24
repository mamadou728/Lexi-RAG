import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AES256Service:
    """
    Handles AES-256-GCM encryption.
    Secure, Authenticated, and Industry Standard for 'Data at Rest'.
    """
    def __init__(self, key_hex: str = None):
        # 1. Load Key
        # We expect a 64-character hex string (32 bytes) from env vars for safety
        key_str = key_hex or os.getenv("APP_ENCRYPTION_KEY")
        
        if not key_str:
            raise ValueError("CRITICAL: No encryption key found!")
            
        # Convert hex string back to raw bytes
        try:
            self.key = bytes.fromhex(key_str)
        except ValueError:
             # Fallback if user provided a base64 or raw string (less safe, but common error)
             raise ValueError("Key must be a 32-byte hex string.")

        if len(self.key) != 32:
            raise ValueError(f"Key must be exactly 32 bytes (256 bits). Current size: {len(self.key)}")

    def encrypt_text(self, plaintext: str) -> bytes:
        """
        Input: "Contract Section 1..."
        Output: b'<nonce><ciphertext><tag>' (Packed Blob)
        """
        if not plaintext:
            return b""
            
        # 1. Generate a unique Nonce (12 bytes is standard for GCM)
        nonce = os.urandom(12)
        
        # 2. Setup Cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # 3. Encrypt
        ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
        
        # 4. Pack the result: Nonce + Ciphertext + Tag
        # We need all three to decrypt, so we store them together.
        # Structure: [Nonce (12)] + [Ciphertext (Variable)] + [Tag (16)]
        return nonce + ciphertext + encryptor.tag

    def decrypt_text(self, encrypted_blob: bytes) -> str:
        """
        Input: b'<nonce><ciphertext><tag>'
        Output: "Contract Section 1..."
        """
        if not encrypted_blob:
            return ""

        try:
            # 1. Unpack the blob
            # First 12 bytes = Nonce
            nonce = encrypted_blob[:12]
            # Last 16 bytes = Tag
            tag = encrypted_blob[-16:]
            # Middle bytes = Actual Encrypted Data
            ciphertext = encrypted_blob[12:-16]

            # 2. Setup Cipher for Decryption
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.GCM(nonce, tag),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()

            # 3. Decrypt
            return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8')
            
        except Exception as e:
            # This fails if the key is wrong OR if the data was tampered with (Tag mismatch)
            raise ValueError("Decryption failed. Data may be corrupted or tampered with.") from e