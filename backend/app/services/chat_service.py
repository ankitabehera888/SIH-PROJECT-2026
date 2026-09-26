import uuid
from typing import List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from app.core.exceptions import AppException
from app.core.socket_manager import broadcast_event
from app.models.chat import ChatMessage, Conversation, ConversationParticipant
from app.models.user import User
from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse,
    ConversationCreate,
    ConversationResponse,
    ParticipantInfo,
)


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_or_get_conversation(self, data: ConversationCreate, current_user: User) -> ConversationResponse:
        """Create a new conversation thread or retrieve existing one with target user."""
        all_participant_ids = set(data.participant_user_ids)
        all_participant_ids.add(current_user.id)

        # Check if 1-on-1 conversation already exists
        if len(all_participant_ids) == 2:
            target_user_id = [uid for uid in all_participant_ids if uid != current_user.id][0]
            stmt = (
                select(Conversation.id)
                .join(ConversationParticipant)
                .where(ConversationParticipant.user_id.in_([current_user.id, target_user_id]))
                .group_by(Conversation.id)
                .having(func.count(ConversationParticipant.user_id) == 2)
            )
            existing_id = self.db.execute(stmt).scalar_one_or_none()
            if existing_id:
                conversation = self.db.get(Conversation, existing_id)
                if conversation:
                    return self._to_conversation_response(conversation, current_user.id)

        # Verify all target users exist
        users = self.db.scalars(select(User).where(User.id.in_(all_participant_ids))).all()
        if len(users) != len(all_participant_ids):
            raise AppException(status_code=404, detail="One or more participant users not found")

        conversation = Conversation(
            title=data.title or (f"Chat with {users[0].email}" if users else "Conversation"),
            treating_for=data.treating_for,
            patient_id=data.patient_id,
        )
        self.db.add(conversation)
        self.db.flush()

        # Add participants
        for uid in all_participant_ids:
            participant = ConversationParticipant(
                conversation_id=conversation.id,
                user_id=uid,
            )
            self.db.add(participant)

        # Send initial message if provided
        if data.initial_message:
            msg = ChatMessage(
                conversation_id=conversation.id,
                sender_id=current_user.id,
                content=data.initial_message,
            )
            self.db.add(msg)

        self.db.commit()
        self.db.refresh(conversation)

        return self._to_conversation_response(conversation, current_user.id)

    def list_user_conversations(self, current_user: User) -> List[ConversationResponse]:
        """List all conversations for the authenticated user with last message and unread count."""
        stmt = (
            select(Conversation)
            .join(ConversationParticipant)
            .where(ConversationParticipant.user_id == current_user.id)
            .order_by(desc(Conversation.updated_at))
        )
        conversations = self.db.scalars(stmt).all()
        return [self._to_conversation_response(conv, current_user.id) for conv in conversations]

    def get_conversation_details(self, conversation_id: uuid.UUID, current_user: User) -> ConversationResponse:
        """Get details for a conversation thread after verifying user access."""
        conversation = self._verify_access(conversation_id, current_user.id)
        return self._to_conversation_response(conversation, current_user.id)

    def get_messages(
        self, conversation_id: uuid.UUID, current_user: User, limit: int = 50
    ) -> List[ChatMessageResponse]:
        """Get list of messages in a conversation thread."""
        self._verify_access(conversation_id, current_user.id)
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
        )
        messages = self.db.scalars(stmt).all()
        return [
            ChatMessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender_id=msg.sender_id,
                sender_email=msg.sender.email if msg.sender else None,
                content=msg.content,
                attachment_url=msg.attachment_url,
                is_read=msg.is_read,
                created_at=msg.created_at,
            )
            for msg in messages
        ]

    def send_message(
        self, conversation_id: uuid.UUID, data: ChatMessageCreate, current_user: User
    ) -> ChatMessageResponse:
        """Send a message into a conversation and broadcast Socket.IO event."""
        conversation = self._verify_access(conversation_id, current_user.id)

        msg = ChatMessage(
            conversation_id=conversation.id,
            sender_id=current_user.id,
            content=data.content,
            attachment_url=data.attachment_url,
        )
        self.db.add(msg)
        conversation.updated_at = func.now()
        self.db.commit()
        self.db.refresh(msg)

        resp = ChatMessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            sender_id=msg.sender_id,
            sender_email=current_user.email,
            content=msg.content,
            attachment_url=msg.attachment_url,
            is_read=msg.is_read,
            created_at=msg.created_at,
        )

        # Real-time broadcast via Socket.IO
        broadcast_event(
            "new_chat_message",
            resp.model_dump(mode="json"),
            room=f"conversation_{conversation_id}",
        )

        return resp

    def mark_as_read(self, conversation_id: uuid.UUID, current_user: User) -> dict:
        """Mark unread messages in conversation sent by others as read."""
        self._verify_access(conversation_id, current_user.id)
        stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.sender_id != current_user.id,
                ChatMessage.is_read == False,
            )
        )
        unread_msgs = self.db.scalars(stmt).all()
        for msg in unread_msgs:
            msg.is_read = True
        self.db.commit()
        return {"status": "success", "marked_read": len(unread_msgs)}

    def _verify_access(self, conversation_id: uuid.UUID, user_id: int) -> Conversation:
        conversation = self.db.get(Conversation, conversation_id)
        if not conversation:
            raise AppException(status_code=404, detail="Conversation thread not found")
        participant_ids = [p.user_id for p in conversation.participants]
        if user_id not in participant_ids:
            raise AppException(status_code=403, detail="Not authorized to access this conversation thread")
        return conversation

    def _to_conversation_response(self, conv: Conversation, current_user_id: int) -> ConversationResponse:
        participants_info = [
            ParticipantInfo(user_id=p.user.id, email=p.user.email, role=p.user.role)
            for p in conv.participants
            if p.user
        ]

        last_msg = None
        if conv.messages:
            last = conv.messages[-1]
            last_msg = ChatMessageResponse(
                id=last.id,
                conversation_id=last.conversation_id,
                sender_id=last.sender_id,
                sender_email=last.sender.email if last.sender else None,
                content=last.content,
                attachment_url=last.attachment_url,
                is_read=last.is_read,
                created_at=last.created_at,
            )

        unread_count = sum(1 for m in conv.messages if not m.is_read and m.sender_id != current_user_id)

        return ConversationResponse(
            id=conv.id,
            title=conv.title,
            treating_for=conv.treating_for,
            patient_id=conv.patient_id,
            unread_count=unread_count,
            participants=participants_info,
            last_message=last_msg,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
