"""Models package - imports all models so Alembic and SQLAlchemy can discover them."""
from app.db.base import Base
from app.models.appointment import (
    VALID_APPOINTMENT_TRANSITIONS,
    Appointment,
    AppointmentStatus,
    AppointmentType,
)
from app.models.chat import ChatMessage, Conversation, ConversationParticipant
from app.models.followup import Followup, FollowupPriority, FollowupStatus
from app.models.inventory import InventoryItem
from app.models.dispensing import MedicationDispense
from app.models.billing import Invoice





from app.models.diagnostic_order import (
    VALID_DIAGNOSTIC_ORDER_TRANSITIONS,
    DiagnosticOrder,
    DiagnosticOrderPriority,
    DiagnosticOrderStatus,
)
from app.models.diagnostic_order_item import (
    DiagnosticItemStatus,
    DiagnosticOrderItem,
)
from app.models.diagnostic_result import (
    DiagnosticResult,
    DiagnosticResultStatus,
)
from app.models.diagnostic_test import DiagnosticTest
from app.models.encounter import (
    VALID_ENCOUNTER_TRANSITIONS,
    Encounter,
    EncounterStatus,
    EncounterType,
)
from app.models.facility import Facility, FacilityType
from app.models.medication import Medication
from app.models.patient import Patient
from app.models.prescription import (
    VALID_PRESCRIPTION_TRANSITIONS,
    Prescription,
    PrescriptionStatus,
)
from app.models.prescription_item import PrescriptionItem
from app.models.queue import (
    VALID_QUEUE_TRANSITIONS,
    QueueEntry,
    QueuePriority,
    QueueStatus,
)
from app.models.referral import (
    VALID_REFERRAL_TRANSITIONS,
    Referral,
    ReferralPriority,
    ReferralStatus,
    ReferralType,
)
from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from app.models.notification_preference import NotificationPreference
from app.models.consultation import (
    VALID_CONSULTATION_TRANSITIONS,
    Consultation,
    ConsultationStatus,
    ConsultationType,
)
from app.models.consultation_participant import (
    ConnectionStatus,
    ConsultationParticipant,
    ParticipantRole,
)
from app.models.consent import (
    Consent,
    ConsentPurpose,
    ConsentScope,
    ConsentStatus,
)
from app.models.interoperability_audit import InteropAction, InteroperabilityAudit
from app.models.patient_identifier import (
    IdentifierStatus,
    IdentifierType,
    PatientIdentifier,
)
from app.models.system_check import SystemCheck
from app.models.user import User
from app.models.vital import Vital

__all__ = [
    "Base",
    "User",
    "Patient",
    "Facility",
    "FacilityType",
    "Appointment",
    "AppointmentStatus",
    "AppointmentType",
    "VALID_APPOINTMENT_TRANSITIONS",
    "QueueEntry",
    "QueuePriority",
    "QueueStatus",
    "VALID_QUEUE_TRANSITIONS",
    "Encounter",
    "EncounterStatus",
    "EncounterType",
    "VALID_ENCOUNTER_TRANSITIONS",
    "Vital",
    "Referral",
    "ReferralStatus",
    "ReferralType",
    "ReferralPriority",
    "VALID_REFERRAL_TRANSITIONS",
    "Medication",
    "Prescription",
    "PrescriptionStatus",
    "VALID_PRESCRIPTION_TRANSITIONS",
    "PrescriptionItem",
    "DiagnosticTest",
    "DiagnosticOrder",
    "DiagnosticOrderStatus",
    "DiagnosticOrderPriority",
    "VALID_DIAGNOSTIC_ORDER_TRANSITIONS",
    "DiagnosticOrderItem",
    "DiagnosticItemStatus",
    "DiagnosticResult",
    "DiagnosticResultStatus",
    "SystemCheck",
    "NotificationChannel",
    "NotificationStatus",
    "NotificationType",
    "Notification",
    "NotificationPreference",
    "ConsultationType",
    "ConsultationStatus",
    "VALID_CONSULTATION_TRANSITIONS",
    "Consultation",
    "ParticipantRole",
    "ConnectionStatus",
    "ConsultationParticipant",
    "PatientIdentifier",
    "IdentifierType",
    "IdentifierStatus",
    "Consent",
    "ConsentStatus",
    "ConsentPurpose",
    "ConsentScope",
    "InteroperabilityAudit",
    "InteropAction",
    "Conversation",
    "ConversationParticipant",
    "ChatMessage",
    "Followup",
    "FollowupStatus",
    "FollowupPriority",
    "InventoryItem",
    "MedicationDispense",
    "Invoice",
]






