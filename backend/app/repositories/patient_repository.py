import uuid
from datetime import date, datetime
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientRepository:
    """Data access repository for Patient entities using SQLAlchemy 2.0."""

    def __init__(self, db: Session):
        self.db = db

    def generate_next_patient_number(self) -> str:
        """Generate human-readable sequential identifier in format: PAT-YYYY-XXXXXX."""
        current_year = datetime.now().year
        prefix = f"PAT-{current_year}-"

        # Count existing patients for this year prefix to compute next sequence
        stmt = select(func.count(Patient.id)).where(Patient.patient_number.startswith(prefix))
        count = self.db.scalar(stmt) or 0
        next_seq = count + 1
        return f"{prefix}{next_seq:06d}"

    def create(
        self,
        data: PatientCreate,
        patient_number: str,
        created_by_id: Optional[int] = None,
    ) -> Patient:
        patient = Patient(
            patient_number=patient_number,
            first_name=data.first_name.strip(),
            middle_name=data.middle_name.strip() if data.middle_name else None,
            last_name=data.last_name.strip(),
            date_of_birth=data.date_of_birth,
            gender=data.gender.value,
            phone=data.phone,
            email=data.email.lower() if data.email else None,
            address=data.address,
            emergency_contact_name=data.emergency_contact_name,
            emergency_contact_phone=data.emergency_contact_phone,
            user_id=data.user_id,
            is_active=True,
            created_by=created_by_id,
            updated_by=created_by_id,
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def get_by_id(self, patient_id: uuid.UUID) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.id == patient_id)
        return self.db.scalars(stmt).first()

    def get_by_number(self, patient_number: str) -> Optional[Patient]:
        stmt = select(Patient).where(Patient.patient_number == patient_number)
        return self.db.scalars(stmt).first()

    def find_potential_duplicate(
        self,
        first_name: str,
        last_name: str,
        dob: date,
        phone: Optional[str] = None,
    ) -> Optional[Patient]:
        """Detect potential duplicates matching first name, last name, DOB, and phone."""
        conditions = [
            func.lower(Patient.first_name) == first_name.strip().lower(),
            func.lower(Patient.last_name) == last_name.strip().lower(),
            Patient.date_of_birth == dob,
        ]
        if phone:
            conditions.append(Patient.phone == phone)

        stmt = select(Patient).where(*conditions)
        return self.db.scalars(stmt).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 20,
        is_active_only: bool = True,
    ) -> Tuple[List[Patient], int]:
        """Retrieve paginated patient records and total count."""
        base_query = select(Patient)
        if is_active_only:
            base_query = base_query.where(Patient.is_active == True)

        total_stmt = select(func.count()).select_from(base_query.subquery())
        total = self.db.scalar(total_stmt) or 0

        stmt = base_query.order_by(Patient.created_at.desc()).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def search(
        self,
        query_str: str,
        skip: int = 0,
        limit: int = 20,
        is_active_only: bool = True,
    ) -> Tuple[List[Patient], int]:
        """Search patients by substring match across names, patient number, and phone."""
        pattern = f"%{query_str.strip()}%"
        filters = [
            Patient.first_name.ilike(pattern),
            Patient.last_name.ilike(pattern),
            Patient.patient_number.ilike(pattern),
        ]
        if query_str.strip().isdigit() or "+" in query_str:
            filters.append(Patient.phone.ilike(pattern))

        base_query = select(Patient).where(or_(*filters))
        if is_active_only:
            base_query = base_query.where(Patient.is_active == True)

        total_stmt = select(func.count()).select_from(base_query.subquery())
        total = self.db.scalar(total_stmt) or 0

        stmt = base_query.order_by(Patient.last_name, Patient.first_name).offset(skip).limit(limit)
        items = list(self.db.scalars(stmt).all())
        return items, total

    def update(
        self,
        patient: Patient,
        data: PatientUpdate,
        updated_by_id: Optional[int] = None,
    ) -> Patient:
        update_dict = data.model_dump(exclude_unset=True)
        if "gender" in update_dict and update_dict["gender"] is not None:
            update_dict["gender"] = update_dict["gender"].value

        for field, value in update_dict.items():
            setattr(patient, field, value)

        patient.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def deactivate(
        self,
        patient: Patient,
        updated_by_id: Optional[int] = None,
    ) -> Patient:
        """Soft deactivate patient record."""
        patient.is_active = False
        patient.updated_by = updated_by_id
        self.db.commit()
        self.db.refresh(patient)
        return patient
