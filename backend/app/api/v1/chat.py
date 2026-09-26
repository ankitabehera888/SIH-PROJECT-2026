import uuid
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
)
from app.services.chat_service import ChatService

router = APIRouter(prefix="/messages", tags=["Messaging & Chat"])


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List authenticated user's active conversations",
)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve all chat threads/conversations involving the current user."""
    service = ChatService(db)
    items = service.list_user_conversations(current_user)
    return ConversationListResponse(items=items, total=len(items))


@router.post(
    "/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create or retrieve a chat conversation thread",
)
def create_conversation(
    payload: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start or retrieve a conversation thread between users (Doctor, Patient, Worker, etc.)."""
    service = ChatService(db)
    return service.create_or_get_conversation(payload, current_user)


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation details by UUID",
)
def get_conversation(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve metadata and participants for a specific conversation thread."""
    service = ChatService(db)
    return service.get_conversation_details(conversation_id, current_user)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[ChatMessageResponse],
    summary="Get message history for a conversation thread",
)
def get_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch chronological message stream for a conversation."""
    service = ChatService(db)
    return service.get_messages(conversation_id, current_user, limit=limit)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message in a conversation thread",
)
def send_message(
    conversation_id: uuid.UUID,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Post a new message to a conversation thread and emit real-time Socket.IO event."""
    service = ChatService(db)
    return service.send_message(conversation_id, payload, current_user)


@router.post(
    "/conversations/{conversation_id}/read",
    summary="Mark messages in conversation as read",
)
def mark_read(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge unread incoming messages in a conversation."""
    service = ChatService(db)
    return service.mark_as_read(conversation_id, current_user)
