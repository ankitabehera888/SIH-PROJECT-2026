from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.consultation import DailyWebhookPayload
from app.services.consultation_service import ConsultationService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/daily",
    status_code=status.HTTP_200_OK,
    summary="Daily.co WebRTC Webhook Callback Handler",
)
def handle_daily_webhook(
    payload: DailyWebhookPayload,
    db: Session = Depends(get_db),
):
    service = ConsultationService(db)
    room_name = payload.room or payload.payload.get("room_name", "")
    res = service.handle_webhook_event(payload.event, room_name, payload.payload)
    return res
