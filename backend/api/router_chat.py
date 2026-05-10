from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from agent import parse_and_execute_intent

logger = logging.getLogger("sentinel-router-chat")

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str
    data: Optional[dict] = None

@router.post("/chat", response_model=ChatResponse)
def chat_agent(request: ChatRequest):
    logger.info(f"Received chat request from session {request.session_id}")
    try:
        result = parse_and_execute_intent(request.message, request.session_id)
        logger.info("Chat request processed successfully")
        return result
    except Exception as e:
        logger.error(f"Chat request failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
