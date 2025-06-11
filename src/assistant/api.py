from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from .assistant_manager import assistant_manager, AssistantType
from src.auth.dependencies import get_current_user
from src.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    assistant_type: str  # "openai" or "mistral"
    thread_id: Optional[str] = None

class CompareRequest(BaseModel):
    message: str
    openai_thread_id: Optional[str] = None
    mistral_thread_id: Optional[str] = None

class ThreadRequest(BaseModel):
    assistant_type: str  # "openai" or "mistral"

class MessageResponse(BaseModel):
    response: str
    thread_id: str
    status: str
    assistant_type: str

class ConversationHistoryResponse(BaseModel):
    conversation: List[Dict[str, Any]]
    thread_id: str
    assistant_type: str

@router.post("/initialize")
async def initialize_assistants(current_user: User = Depends(get_current_user)):
    """
    Initialize both OpenAI and Mistral assistants
    """
    try:
        results = await assistant_manager.initialize_assistants()
        return {
            "message": "Assistants initialized",
            "results": results,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error initializing assistants: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize assistants: {str(e)}")

@router.post("/message", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to the specified assistant
    """
    try:
        # Validate assistant type
        if request.assistant_type not in ["openai", "mistral"]:
            raise HTTPException(status_code=400, detail="Invalid assistant type. Use 'openai' or 'mistral'")
        
        assistant_type = AssistantType(request.assistant_type)
        
        response = await assistant_manager.send_message(
            message=request.message,
            assistant_type=assistant_type,
            thread_id=request.thread_id
        )
        
        if response["status"] == "error":
            raise HTTPException(status_code=500, detail=response["response"])
        
        return MessageResponse(**response)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid assistant type: {str(e)}")
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.post("/thread")
async def create_thread(
    request: ThreadRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation thread for the specified assistant
    """
    try:
        # Validate assistant type
        if request.assistant_type not in ["openai", "mistral"]:
            raise HTTPException(status_code=400, detail="Invalid assistant type. Use 'openai' or 'mistral'")
        
        assistant_type = AssistantType(request.assistant_type)
        
        thread_id = await assistant_manager.create_thread(assistant_type)
        
        return {
            "thread_id": thread_id,
            "assistant_type": request.assistant_type,
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid assistant type: {str(e)}")
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create thread: {str(e)}")

@router.get("/conversation/{assistant_type}/{thread_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    assistant_type: str,
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation history for a specific thread
    """
    try:
        # Validate assistant type
        if assistant_type not in ["openai", "mistral"]:
            raise HTTPException(status_code=400, detail="Invalid assistant type. Use 'openai' or 'mistral'")
        
        assistant_type_enum = AssistantType(assistant_type)
        
        conversation = await assistant_manager.get_conversation_history(
            thread_id=thread_id,
            assistant_type=assistant_type_enum
        )
        
        return ConversationHistoryResponse(
            conversation=conversation,
            thread_id=thread_id,
            assistant_type=assistant_type
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid assistant type: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")

@router.post("/compare")
async def compare_responses(
    request: CompareRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send the same message to both assistants and compare responses
    """
    try:
        thread_ids = {}
        if request.openai_thread_id:
            thread_ids[AssistantType.OPENAI] = request.openai_thread_id
        if request.mistral_thread_id:
            thread_ids[AssistantType.MISTRAL] = request.mistral_thread_id
        
        results = await assistant_manager.compare_responses(
            message=request.message,
            thread_ids=thread_ids if thread_ids else None
        )
        
        return {
            "message": request.message,
            "responses": results,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error comparing responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare responses: {str(e)}")

@router.get("/status")
async def get_assistant_status(current_user: User = Depends(get_current_user)):
    """
    Get status of all assistants
    """
    try:
        status = assistant_manager.get_assistant_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting assistant status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assistant status: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint for assistant service
    """
    return {
        "status": "healthy",
        "service": "assistant",
        "available_assistants": ["openai", "mistral"]
    }