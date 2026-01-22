# 2_vectorize_and_upload.py
from FlagEmbedding import BGEM3FlagModel
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
import uuid
from src.core.config import QDRANT_URL, QDRANT_API_KEY

# 1. Initialize Model & Client
print("Loading BGE-M3 model... (this may take a moment)")
model = BGEM3FlagModel('BAAI/bge-m3', use_fp16=True) # use_fp16=True saves RAM
client = QdrantClient(
        url=QDRANT_URL, 
        api_key=QDRANT_API_KEY
        )
collection_name = "legal_documents"

# 2. Your Data (Example: A Legal Clause)
documents = [
    "The Consultant shall not be liable for any indirect damages.",
    "Termination requires 30 days written notice by either party.",
    "Intellectual property created during this engagement belongs to the Client."
]

def compute_sparse_vector(text):
    """
    Helper to convert BGE-M3's {word: weight} output 
    into Qdrant's required [indices], [values] format.
    """
    output = model.encode(text, return_dense=True, return_sparse=True)
    
    # Extract Dense
    dense_vec = output['dense_vecs'].tolist()
    
    # Extract Sparse (Convert tokens to integer IDs)
    lexical_weights = output['lexical_weights']
    indices = []
    values = []
    
    for token, weight in lexical_weights.items():
        # IMPORTANT: We map the word (token) to its internal Integer ID
        token_id = model.tokenizer.vocab.get(token)
        if token_id is not None:
            indices.append(token_id)
            values.append(weight)
            
    return dense_vec, indices, values

# 3. Process and Upload
points_to_upload = []

print("Vectorizing documents...")
for doc in documents:
    dense, sp_indices, sp_values = compute_sparse_vector(doc)
    
    # Create the Point
    point = rest_models.PointStruct(
        id=str(uuid.uuid4()), 
        vector={
            "dense_vector": dense,
            "sparse_vector": rest_models.SparseVector(
                indices=sp_indices,
                values=sp_values
            )
        },
        payload={"text": doc} # Storing the actual text to retrieve later
    )
    points_to_upload.append(point)

# 4. Upsert (Upload) to Qdrant
client.upsert(
    collection_name=collection_name,
    points=points_to_upload
)

print(f"SUCCESS: Uploaded {len(documents)} documents to Qdrant.")