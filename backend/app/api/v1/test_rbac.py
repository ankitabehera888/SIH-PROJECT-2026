from fastapi import APIRouter, Depends
from app.core.dependencies import require_role
from app.core.roles import UserRole
from app.models.user import User

router = APIRouter(prefix="/test", tags=["RBAC Testing"])


@router.get("/patient-only", summary="Patient-only RBAC endpoint")
def patient_only_endpoint(
    current_user: User = Depends(require_role(UserRole.PATIENT)),
):
    return {
        "message": f"Welcome, patient {current_user.email}!",
        "role": current_user.role,
    }


@router.get("/doctor-only", summary="Doctor-only RBAC endpoint")
def doctor_only_endpoint(
    current_user: User = Depends(require_role(UserRole.DOCTOR)),
):
    return {
        "message": f"Access granted for Dr. {current_user.email}",
        "role": current_user.role,
    }


@router.get("/nurse-only", summary="Nurse-only RBAC endpoint")
def nurse_only_endpoint(
    current_user: User = Depends(require_role(UserRole.NURSE)),
):
    return {
        "message": f"Access granted for nurse {current_user.email}",
        "role": current_user.role,
    }


@router.get("/admin-only", summary="Admin-only RBAC endpoint")
def admin_only_endpoint(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    return {
        "message": f"System administration granted for {current_user.email}",
        "role": current_user.role,
    }
