"""
Generator module for RAG system.
Handles answer generation using LLM based on retrieved documents and history.
"""
from typing import List, Dict
from rag.config import groq_client

async def generate_answer(query: str, history: str, context_chunks: List[Dict]) -> str:
    """
    Generates an answer using Groq (Llama 3) based on retrieved docs AND history.
    """
    
    # 1. Prepare Context String
    if context_chunks:
        context_str = "\n---\n".join([
            f"SOURCE: {d['filename']} (Sensitivity: {d['sensitivity']})\n"
            f"CONTENT: {d['text_snippet']}"
            for d in context_chunks
        ])
    else:
        context_str = "No external documents retrieved. Answer based on conversation history only."

    # 2. System Prompt
    system_prompt = (
        "You are Lexi, a secure legal AI assistant. "
        "Answer the user's question clearly and professionally.\n"
        "Guidelines:\n"
        "1. Use the provided 'Context' (legal documents) to answer facts.\n"
        "2. Use 'Chat History' to understand context (e.g., 'he' refers to the client).\n"
        "3. If the answer is in the documents, cite the filename explicitly.\n"
        "4. If you cannot find the answer in the context or history, admit it. Do not hallucinate."
    )

    # 3. User Prompt
    user_message = (
        f"CHAT HISTORY:\n{history}\n\n"
        f"NEW RETRIEVED CONTEXT:\n{context_str}\n\n"
        f"USER QUESTION: {query}"
    )

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3 # Slightly higher creativity for conversation flow
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {e}"
