from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId

# RAG functions
from rag import (
    check_if_search_needed,
    rewrite_query,
    retrieve_documents,
    generate_answer
)
from models.chat import ChatMessage, ChatSession, Citation
from models.auth import User
from core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: str

class CreateSessionRequest(BaseModel):
    name: Optional[str] = "New Chat"

# Helper functions for chat history
async def get_chat_history(session_id: str, limit: int = 6) -> str:
    """
    Retrieves chat history as a formatted string for the LLM.
    """
    try:
        session_obj_id = PydanticObjectId(session_id)
        messages = await ChatMessage.find(
            ChatMessage.session_id == session_obj_id
        ).sort("+created_at").limit(limit).to_list()
        
        # Format as conversation history
        history_lines = []
        for msg in messages:
            role_label = "User" if msg.role == "user" else "Lexi"
            history_lines.append(f"{role_label}: {msg.content}")
        
        return "\n".join(history_lines) if history_lines else ""
    except Exception as e:
        print(f"⚠️ Error retrieving chat history: {e}")
        return ""

async def save_message(session_id: str, role: str, content: str, citations: List[Citation] = None):
    """
    Saves a chat message to the database.
    """
    try:
        session_obj_id = PydanticObjectId(session_id)
        message = ChatMessage(
            session_id=session_obj_id,
            role=role,
            content=content,
            citations=citations or []
        )
        await message.insert()
        
        # Update session's updated_at timestamp
        session = await ChatSession.get(session_obj_id)
        if session:
            from datetime import datetime
            session.updated_at = datetime.utcnow()
            await session.save()
    except Exception as e:
        print(f"⚠️ Error saving message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")

@router.post("")
async def smart_chat(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    """
    Main chat endpoint that uses the RAG system with routing, retrieval, and generation.
    """
    
    # 1. GET CONTEXT (The Memory)
    chat_history = await get_chat_history(payload.session_id, limit=6)

    # 2. THE ROUTER (The Decision)
    needs_search = await check_if_search_needed(history=chat_history, query=payload.query)

    context_docs = []

    if needs_search:
        print("🔍 Router decided: SEARCH needed.")
        
        # 3a. REWRITE QUERY
        # "What about the second clause?" -> "What are the terms of the second clause in the Smith contract?"
        standalone_query = await rewrite_query(history=chat_history, query=payload.query)
        
        # 3b. RETRIEVE
        context_docs = await retrieve_documents(
            query=standalone_query,
            user_role=current_user.system_role,
            top_k=5
        )
    else:
        print("🧠 Router decided: MEMORY sufficient.")
        # We rely solely on chat_history, so context_docs remains empty

    # 4. GENERATE ANSWER
    # The generator sees: History + (Optional) New Docs + User Question
    answer = await generate_answer(
        query=payload.query,
        history=chat_history,
        context_chunks=context_docs
    )

    # 5. SAVE STATE with citations
    # Convert context_docs to Citation objects
    citations = []
    for doc in context_docs:
        citations.append(Citation(
            mongo_document_id=doc.get("mongo_document_id", "unknown"),
            filename=doc.get("filename", "Unknown File"),
            matter_id=doc.get("matter_id", "unknown"),
            sensitivity=doc.get("sensitivity", "unknown"),
            chunk_index=doc.get("chunk_index", 0),
            text_snippet=doc.get("text_snippet", ""),
            score=doc.get("score", 0.0)
        ))
    
    await save_message(payload.session_id, "user", payload.query)
    await save_message(payload.session_id, "ai", answer, citations)

    return {"answer": answer, "sources": context_docs}

# Session Management Endpoints

@router.post("/sessions")
async def create_session(
    payload: CreateSessionRequest, 
    current_user: User = Depends(get_current_user)
):
    """
    Create a new chat session for the current user.
    """
    try:
        session = ChatSession(
            user_email=current_user.email,
            name=payload.name or "New Chat"
        )
        await session.insert()
        return {
            "id": str(session.id),
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    except Exception as e:
        print(f"⚠️ Error creating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/sessions")
async def list_sessions(current_user: User = Depends(get_current_user)):
    """
    List all chat sessions for the current user, ordered by most recently updated.
    """
    try:
        sessions = await ChatSession.find(
            ChatSession.user_email == current_user.email
        ).sort("-updated_at").to_list()
        
        return [
            {
                "id": str(session.id),
                "name": session.name,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
            for session in sessions
        ]
    except Exception as e:
        print(f"⚠️ Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get all messages for a specific chat session.
    """
    try:
        session_obj_id = PydanticObjectId(session_id)
        
        # Verify session belongs to user
        session = await ChatSession.get(session_obj_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_email != current_user.email:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all messages for this session
        messages = await ChatMessage.find(
            ChatMessage.session_id == session_obj_id
        ).sort("+created_at").to_list()
        
        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "citations": [
                    {
                        "mongo_document_id": cit.mongo_document_id,
                        "filename": cit.filename,
                        "matter_id": cit.matter_id,
                        "sensitivity": cit.sensitivity,
                        "chunk_index": cit.chunk_index,
                        "text_snippet": cit.text_snippet,
                        "score": cit.score
                    }
                    for cit in msg.citations
                ],
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error retrieving messages: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a chat session and all its messages.
    """
    try:
        session_obj_id = PydanticObjectId(session_id)
        
        # Verify session belongs to user
        session = await ChatSession.get(session_obj_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_email != current_user.email:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete all messages in the session
        messages = await ChatMessage.find(
            ChatMessage.session_id == session_obj_id
        ).to_list()
        for msg in messages:
            await msg.delete()
        
        # Delete the session
        await session.delete()
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

class UpdateSessionRequest(BaseModel):
    name: str

@router.patch("/sessions/{session_id}")
async def update_session(
    session_id: str,
    payload: UpdateSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Update the name of a chat session.
    """
    try:
        session_obj_id = PydanticObjectId(session_id)
        
        # Verify session belongs to user
        session = await ChatSession.get(session_obj_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_email != current_user.email:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update session name
        session.name = payload.name
        from datetime import datetime
        session.updated_at = datetime.utcnow()
        await session.save()
        
        return {
            "id": str(session.id),
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Error updating session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")