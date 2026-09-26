from typing import Callable, Sequence, Union
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.roles import UserRole
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# OAuth2 scheme configured for OpenAPI Swagger authorization
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract and validate the JWT Bearer token and retrieve the active User."""
    if not token:
        raise UnauthorizedException("Authentication token is missing")

    payload = decode_token(token)
    token_type = payload.get("type")
    if token_type != "access":
        raise UnauthorizedException("Invalid token type: access token required")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token: subject missing")

    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    if not user:
        raise UnauthorizedException("User no longer exists")

    if not user.is_active:
        raise UnauthorizedException("Account is disabled")

    return user


def require_role(*allowed_roles: Union[UserRole, str]) -> Callable[[User], User]:
    """Dependency factory enforcing Role-Based Access Control (RBAC)."""
    normalized_roles = {
        role.value if isinstance(role, UserRole) else str(role)
        for role in allowed_roles
    }

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in normalized_roles:
            raise ForbiddenException(
                f"Access forbidden: requires one of {list(normalized_roles)} roles"
            )
        return current_user

    return role_checker
