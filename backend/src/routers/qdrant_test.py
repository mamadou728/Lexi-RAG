import sys
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from httpx import ConnectError

# ---------------------------------------------------------
# Configuration Load
# ---------------------------------------------------------
try:
    from src.core.config import QDRANT_URL, QDRANT_API_KEY
    print(f"🔹 Loaded config from file: URL='{QDRANT_URL}'")
except ImportError:
    # FALLBACK DEFAULTS
    QDRANT_URL = "http://localhost:6333" 
    QDRANT_API_KEY = None
    print(f"🔸 Config not found. Using default: URL='{QDRANT_URL}'")

def main():
    # 1. Initialize Client
    print(f"Connecting to client at: {QDRANT_URL}...")
    
    try:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        
        # 2. Connection Test: List ALL collections
        # This proves the script can actually talk to the DB
        collections_response = client.get_collections()
        available_collections = [c.name for c in collections_response.collections]
        
        print(f"✅ Connection Successful!")
        print(f"📂 Available Collections in DB: {available_collections}")

        # 3. Check Specific Collection
        target_collection = "legal_documents"
        
        if target_collection in available_collections:
            info = client.get_collection(target_collection)
            print(f"\n🔎 Inspecting '{target_collection}':")
            print(f"   - Status: {info.status}")
            print(f"   - Points (Rows): {info.points_count}")
        else:
            print(f"\n❌ Error: Collection '{target_collection}' does not exist in the DB.")
            print("   (Did you name it something else? Check the list above)")

    except ConnectError:
        print("\n❌ CONNECTION REFUSED")
        print("   The script cannot reach Qdrant.")
        print("   Troubleshooting:")
        print("   1. If script is in Docker, change QDRANT_URL to 'http://qdrant:6333' (or your service name).")
        print("   2. If script is local, ensure Docker is running and port 6333 is mapped.")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    main()