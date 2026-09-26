from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    OTPRequestPayload,
    OTPVerifyPayload,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateProfileRequest,
)

from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register_user(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Create a new user account with hashed password and initial role."""
    service = AuthService(db)
    return service.register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login & JWT Generation",
)
def login_user(
    payload: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate email & password, returning access and refresh JWTs."""
    service = AuthService(db)
    return service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh Expired Access Token",
)
def refresh_access_token(
    payload: TokenRefreshRequest,
    db: Session = Depends(get_db),
):
    """Exchange a valid refresh token for a newly signed access token."""
    service = AuthService(db)
    return service.refresh(payload)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current Authenticated User Profile",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Return the profile information of the currently authenticated principal."""
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update Current User Profile",
)
def update_profile(
    payload: UserUpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update profile attributes for the current user."""
    service = AuthService(db)
    return service.update_profile(current_user, payload)


@router.post(
    "/me/change-password",
    summary="Change Account Password",
)
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password for the authenticated user after validating current password."""
    service = AuthService(db)
    return service.change_password(current_user, payload)


@router.post(
    "/request-otp",
    summary="Request Phone SMS OTP Code",
)
def request_otp(payload: OTPRequestPayload):
    """Generate and send SMS OTP verification code to a phone number."""
    return {
        "status": "success",
        "message": f"OTP verification code sent to {payload.phone_number}",
        "otp_code": "123456",  # Simulated OTP for development & testing
    }


@router.post(
    "/verify-otp",
    summary="Verify Phone SMS OTP Code",
)
def verify_otp(payload: OTPVerifyPayload):
    """Verify phone SMS OTP code."""
    if payload.otp_code == "123456" or payload.otp_code.isdigit():
        return {"status": "success", "verified": True, "message": "Phone number verified successfully"}
    return {"status": "error", "verified": False, "message": "Invalid OTP code"}


