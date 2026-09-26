from sqlalchemy.orm import Session
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)


class AuthService:
    """Service layer handling user registration, credential validation, and JWT lifecycle."""

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, data: UserRegisterRequest) -> UserResponse:
        existing = self.repository.get_by_email(data.email)
        if existing:
            raise ConflictException(
                message=f"User with email '{data.email}' already exists",
            )

        hashed = hash_password(data.password)
        user = self.repository.create(
            email=data.email,
            password_hash=hashed,
            role=data.role.value,
        )
        return UserResponse.model_validate(user)

    def login(self, data: UserLoginRequest) -> TokenResponse:
        user = self.repository.get_by_email(data.email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(data.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled. Please contact an administrator.")

        access_token = create_access_token(user_id=user.id, role=user.role)
        refresh_token = create_refresh_token(user_id=user.id, role=user.role)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def refresh(self, data: TokenRefreshRequest) -> TokenResponse:
        payload = decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type: refresh token required")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid token payload")

        user = self.repository.get_by_id(int(user_id_str))
        if not user:
            raise UnauthorizedException("User no longer exists")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled. Please contact an administrator.")

        new_access_token = create_access_token(user_id=user.id, role=user.role)
        new_refresh_token = create_refresh_token(user_id=user.id, role=user.role)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    def update_profile(self, user: User, data: UserUpdateProfileRequest) -> UserResponse:
        if data.email and data.email != user.email:
            existing = self.repository.get_by_email(data.email)
            if existing:
                raise ConflictException(message=f"Email '{data.email}' is already in use")
            user.email = data.email

        self.repository.db.commit()
        self.repository.db.refresh(user)
        return UserResponse.model_validate(user)

    def change_password(self, user: User, data: ChangePasswordRequest) -> dict:
        if not verify_password(data.old_password, user.password_hash):
            raise UnauthorizedException("Current password is incorrect")

        user.password_hash = hash_password(data.new_password)
        self.repository.db.commit()
        return {"status": "success", "message": "Password updated successfully"}

