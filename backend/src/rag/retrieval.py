"""
Retrieval module for RAG system.
Handles document retrieval with security filtering based on user roles.
"""
from typing import List, Dict
from qdrant_client.models import Filter, FieldCondition, MatchAny

# Import shared clients and config
from rag.config import qdrant_client, embedding_model, COLLECTION_NAME
from models.auth import SystemRole

# --- PERMISSIONS LOGIC ---
# Define who can see what. Centralized here for easy changes.
PERMISSION_MATRIX = {
    SystemRole.PARTNER:   ["public", "internal", "privileged", "discovery"],
    SystemRole.ASSOCIATE: ["public", "internal", "privileged", "discovery"],
    SystemRole.STAFF:     ["public", "internal"], 
    SystemRole.CLIENT:    ["public"]              
}

def get_allowed_sensitivities(role: SystemRole) -> List[str]:
    """Get list of allowed sensitivity levels for a given user role."""
    return PERMISSION_MATRIX.get(role, [])


async def retrieve_documents(query: str, user_role: SystemRole, top_k: int = 5) -> List[Dict]:
    """
    Searches Qdrant with a STRICT security filter based on User Role.
    """
    

    # A. Get Permissions
    allowed_levels = get_allowed_sensitivities(user_role)
    if not allowed_levels:
        print(f"⛔ Access Denied for role: {user_role}")
        return []

    # B. Build Security Filter
    security_filter = Filter(
        must=[
            FieldCondition(
                key="sensitivity", 
                match=MatchAny(any=allowed_levels)
            )
        ]
    )

    # C. Search with Qdrant
    try:
        # Encode query
        embeddings_result = embedding_model.encode(query, return_dense=True)
        query_vector = embeddings_result['dense_vecs']
        
        # Convert to list
        if hasattr(query_vector, 'tolist'):
            query_vector_list = query_vector.tolist()
        else:
            query_vector_list = list(query_vector)
        
        response = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector_list,
            using="dense_vector",
            query_filter=security_filter,
            limit=top_k
        )
        
        hits = response.points

    except Exception as e:
        print(f"❌ Qdrant search error: {e}")
        return []

    # D. Format Results (CRITICAL: Mapping to Citation Model)
    results = []
    for hit in hits:
        try:
            payload = hit.payload or {}
            results.append({
                # Metadata for the database link
                "mongo_document_id": payload.get("mongo_document_id", "unknown"),
                "matter_id": payload.get("matter_id", "unknown"),
                "chunk_index": payload.get("chunk_index", 0),
                "sensitivity": payload.get("sensitivity", "unknown"),
                
                # Content for the LLM & Display
                "filename": payload.get("filename", "Unknown File"),
                "text_snippet": payload.get("text_snippet", ""),
                
                # Search Metric
                "score": hit.score if hasattr(hit, 'score') else 0.0
            })
        except Exception as e:
            print(f"⚠️ Error parsing hit: {e}")
            continue
    
    print(f"   ✅ Returning {len(results)} formatted results")
    return results
