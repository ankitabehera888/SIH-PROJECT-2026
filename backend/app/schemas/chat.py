import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Text message content")
    attachment_url: Optional[str] = Field(None, description="Optional URL for attached file or image")


class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: int
    sender_email: Optional[str] = None
    content: str
    attachment_url: Optional[str] = None
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationCreate(BaseModel):
    participant_user_ids: List[int] = Field(..., min_items=1, description="List of target user IDs to include in conversation")
    title: Optional[str] = Field(None, description="Optional thread title")
    treating_for: Optional[str] = Field(None, description="Clinical context (e.g. Hypertension Care)")
    patient_id: Optional[uuid.UUID] = Field(None, description="Linked patient UUID if applicable")
    initial_message: Optional[str] = Field(None, description="Optional first message content")


class ParticipantInfo(BaseModel):
    user_id: int
    email: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: Optional[str] = None
    treating_for: Optional[str] = None
    patient_id: Optional[uuid.UUID] = None
    unread_count: int = 0
    participants: List[ParticipantInfo] = []
    last_message: Optional[ChatMessageResponse] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
