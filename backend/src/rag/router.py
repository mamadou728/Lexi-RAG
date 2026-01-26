"""
Router module for RAG system.
Decides if retrieval is necessary and contextualizes queries.
"""
from rag.config import groq_client

async def check_if_search_needed(history: str, query: str) -> bool:
    """
    Determines if the user's query requires external legal information 
    or if it can be answered purely from conversation history/chit-chat.
    """
    system_prompt = (
        "You are a routing agent for a legal RAG system. "
        "Your job is to determine if the user's last message requires searching the legal database. "
        "Return strictly 'YES' or 'NO'."
        "\n\nRules:"
        "\n- Return NO if the user is just saying hello, thank you, or chit-chat."
        "\n- Return NO if the user asks a follow-up clearly answered in the chat history."
        "\n- Return YES if the user asks for facts, definitions, or specific legal content."
    )
    
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Chat History:\n{history}\n\nCurrent Query: {query}"}
            ],
            model="llama-3.1-8b-instant", # Fast & Cheap model for routing
            temperature=0.0,
            max_tokens=5
        )
        decision = response.choices[0].message.content.strip().upper()
        return "YES" in decision
    except Exception as e:
        print(f"⚠️ Router Error: {e}")
        return True # Default to searching if router fails (Safe fallback)


async def rewrite_query(history: str, query: str) -> str:
    """
    Rewrites the user's query to be standalone by resolving coreferences 
    (e.g., 'What is *his* address?' -> 'What is *John Doe's* address?').
    """
    system_prompt = (
        "You are a query rewriting expert. "
        "Rewrite the user's last question to be a standalone search query based on the history. "
        "Do not answer the question. Just rewrite it for a search engine. "
        "If the query is already specific, return it unchanged."
    )

    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Chat History:\n{history}\n\nLast Question: {query}"}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        rewritten = response.choices[0].message.content.strip()
        print(f"🔄 Query Rewritten: '{query}' -> '{rewritten}'")
        return rewritten
    except Exception as e:
        print(f"⚠️ Rewrite Error: {e}")
        return query # Fallback to original query
