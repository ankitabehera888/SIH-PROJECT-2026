import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.core.exceptions import AppException, ForbiddenException, NotFoundException
from app.core.roles import UserRole
from app.models.referral import Referral, ReferralStatus, VALID_REFERRAL_TRANSITIONS
from app.models.user import User
from app.repositories.encounter_repository import EncounterRepository
from app.repositories.facility_repository import FacilityRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.referral_repository import ReferralRepository
from app.schemas.referral import (
    ReferralCancelRequest,
    ReferralCompleteRequest,
    ReferralCreate,
    ReferralListResponse,
    ReferralRejectRequest,
    ReferralResponse,
    ReferralScheduleRequest,
)


class ReferralService:
    """Business service governing healthcare facility referrals, transitions, and care transfer tracking."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ReferralRepository(db)
        self.encounter_repo = EncounterRepository(db)
        self.patient_repo = PatientRepository(db)
        self.facility_repo = FacilityRepository(db)

    def create_from_encounter(
        self,
        encounter_id: uuid.UUID,
        data: ReferralCreate,
        current_user: User,
    ) -> ReferralResponse:
        encounter = self.encounter_repo.get_by_id(encounter_id)
        if not encounter:
            raise NotFoundException(message=f"Encounter with id '{encounter_id}' not found")

        patient = self.patient_repo.get_by_id(encounter.patient_id)
        if not patient or not patient.is_active:
            raise NotFoundException(message=f"Patient with id '{encounter.patient_id}' not found or inactive")

        # Verify receiving facility exists and is active
        receiving_fac = self.facility_repo.get_by_id(data.receiving_facility_id)
        if not receiving_fac or not receiving_fac.is_active:
            raise NotFoundException(message=f"Receiving facility with id '{data.receiving_facility_id}' not found or inactive")

        # Business Rule: Cannot refer to the same facility
        if encounter.facility_id == data.receiving_facility_id:
            raise AppException(
                message="Referring facility and receiving facility cannot be identical",
                code="REFERRAL_FACILITY_IDENTICAL",
                status_code=400,
            )

        referral = self.repository.create(
            patient_id=encounter.patient_id,
            encounter_id=encounter.id,
            referring_facility_id=encounter.facility_id,
            referring_provider_id=encounter.provider_id,
            data=data,
            created_by_id=current_user.id,
        )
        return ReferralResponse.model_validate(referral)

    def get_referral(
        self,
        referral_id: uuid.UUID,
        current_user: User,
    ) -> ReferralResponse:
        referral = self.repository.get_by_id(referral_id)
        if not referral:
            raise NotFoundException(message=f"Referral with id '{referral_id}' not found")

        # Resource authorization
        if current_user.role == UserRole.PATIENT.value:
            patient = self.patient_repo.get_by_id(referral.patient_id)
            if not patient or patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own referrals")

        return ReferralResponse.model_validate(referral)

    def list_patient_referrals(
        self,
        patient_id: uuid.UUID,
        current_user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> ReferralListResponse:
        patient = self.patient_repo.get_by_id(patient_id)
        if not patient:
            raise NotFoundException(message=f"Patient with id '{patient_id}' not found")

        if current_user.role == UserRole.PATIENT.value:
            if patient.user_id != current_user.id:
                raise ForbiddenException(message="Access denied: You can only view your own referrals")

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.get_patient_referrals(
            patient_id=patient_id,
            skip=skip,
            limit=page_size,
        )
        response_items = [ReferralResponse.model_validate(r) for r in items]
        return ReferralListResponse.create(response_items, total, page, page_size)

    def list_incoming_referrals(
        self,
        facility_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ReferralListResponse:
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise NotFoundException(message=f"Facility with id '{facility_id}' not found")

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.get_facility_incoming_referrals(
            facility_id=facility_id,
            status=status,
            priority=priority,
            skip=skip,
            limit=page_size,
        )
        response_items = [ReferralResponse.model_validate(r) for r in items]
        return ReferralListResponse.create(response_items, total, page, page_size)

    def list_outgoing_referrals(
        self,
        facility_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ReferralListResponse:
        facility = self.facility_repo.get_by_id(facility_id)
        if not facility:
            raise NotFoundException(message=f"Facility with id '{facility_id}' not found")

        if page < 1:
            page = 1
        if page_size < 1 or page_size > 100:
            page_size = 20

        skip = (page - 1) * page_size
        items, total = self.repository.get_facility_outgoing_referrals(
            facility_id=facility_id,
            status=status,
            priority=priority,
            skip=skip,
            limit=page_size,
        )
        response_items = [ReferralResponse.model_validate(r) for r in items]
        return ReferralListResponse.create(response_items, total, page, page_size)

    def accept_referral(
        self,
        referral_id: uuid.UUID,
        current_user: User,
    ) -> ReferralResponse:
        referral = self.repository.get_by_id(referral_id)
        if not referral:
            raise NotFoundException(message=f"Referral with id '{referral_id}' not found")

        if referral.status != ReferralStatus.SENT.value:
            raise AppException(
                message=f"Cannot accept referral in status '{referral.status}'. Referral must be in 'SENT' status.",
                code="INVALID_REFERRAL_TRANSITION",
                status_code=400,
            )

        updated = self.repository.accept(referral=referral, accepted_by_id=current_user.id)
        return ReferralResponse.model_validate(updated)

    def reject_referral(
        self,
        referral_id: uuid.UUID,
        data: ReferralRejectRequest,
        current_user: User,
    ) -> ReferralResponse:
        referral = self.repository.get_by_id(referral_id)
        if not referral:
            raise NotFoundException(message=f"Referral with id '{referral_id}' not found")

        if referral.status != ReferralStatus.SENT.value:
            raise AppException(
                message=f"Cannot reject referral in status '{referral.status}'. Referral must be in 'SENT' status.",
                code="INVALID_REFERRAL_TRANSITION",
                status_code=400,
            )

        updated = self.repository.reject(
            referral=referral,
            rejected_by_id=current_user.id,
            reason=data.reason,
        )
        return ReferralResponse.model_validate(updated)

    def schedule_referral(
        self,
        referral_id: uuid.UUID,
        data: ReferralScheduleRequest,
        current_user: User,
    ) -> ReferralResponse:
        referral = self.repository.get_by_id(referral_id)
        if not referral:
            raise NotFoundException(message=f"Referral with id '{referral_id}' not found")

        if referral.status != ReferralStatus.ACCEPTED.value:
            raise AppException(
                message=f"Cannot schedule referral in status '{referral.status}'. Referral must be in 'ACCEPTED' status.",
                code="INVALID_REFERRAL_TRANSITION",
                status_code=400,
            )

        updated = self.repository.schedule(
            referral=referral,
            scheduled_by_id=current_user.id,
            scheduled_date=data.scheduled_date,
            scheduled_time=data.scheduled_time,
        )
        return ReferralResponse.model_validate(updated)

    def complete_referral(
        self,
        referral_id: uuid.UUID,
        data: ReferralCompleteRequest,
        current_user: User,
    ) -> ReferralResponse:
        referral = self.repository.get_by_id(referral_id)
        if not referral:
            raise NotFoundException(message=f"Referral with id '{referral_id}' not found")

        if referral.status != ReferralStatus.SCHEDULED.value:
            raise AppException(
                message=f"Cannot complete referral in status '{referral.status}'. Referral must be in 'SCHEDULED' status.",
                code="INVALID_REFERRAL_TRANSITION",
                status_code=400,
            )

        updated = self.repository.complete(
            referral=referral,
            completed_by_id=current_user.id,
            outcome_status=data.outcome_status,
            outcome_notes=data.outcome_notes,
            follow_up_required=data.follow_up_required,
            follow_up_date=data.follow_up_date,
        )
        return ReferralResponse.model_validate(updated)

    def cancel_referral(
        self,
        referral_id: uuid.UUID,
        data: ReferralCancelRequest,
        current_user: User,
    ) -> ReferralResponse:
        referral = self.repository.get_by_id(referral_id)
        if not referral:
            raise NotFoundException(message=f"Referral with id '{referral_id}' not found")

        terminal_states = [
            ReferralStatus.COMPLETED.value,
            ReferralStatus.REJECTED.value,
            ReferralStatus.CANCELLED.value,
            ReferralStatus.EXPIRED.value,
        ]
        if referral.status in terminal_states:
            raise AppException(
                message=f"Cannot cancel referral in terminal status '{referral.status}'.",
                code="INVALID_REFERRAL_TRANSITION",
                status_code=400,
            )

        updated = self.repository.cancel(
            referral=referral,
            cancelled_by_id=current_user.id,
            reason=data.reason,
        )
        return ReferralResponse.model_validate(updated)
