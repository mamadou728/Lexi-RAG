"""
RAG module - exports all RAG functionality.
"""
from rag.vectorizer import vectorize, vectorize_and_upload, VectorPayload, VectorMetadata
from rag.retrieval import retrieve_documents, get_allowed_sensitivities
from rag.generator import generate_answer
from rag.router import check_if_search_needed, rewrite_query

# Backward compatibility alias
retrieve_safe_documents = retrieve_documents

__all__ = [
    "vectorize",
    "vectorize_and_upload",
    "retrieve_documents",
    "retrieve_safe_documents",  # Backward compatibility
    "get_allowed_sensitivities",
    "generate_answer",
    "check_if_search_needed",
    "rewrite_query",
    "VectorPayload",
    "VectorMetadata",
]
