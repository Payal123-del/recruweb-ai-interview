from typing import Generator, Optional, List, Callable
from fastapi import Depends, HTTPException, status, Header, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException, TenantMismatchException
from app.models.entities import User, UserRoleType
from app.services.user_service import UserService, ROLE_PERMISSIONS_MAP

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not auth_header:
        raise UnauthorizedException("Authentication token required")

    token = auth_header.credentials
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedException("Invalid or expired authentication token")

    token_type = payload.get("type")
    if token_type and token_type != "access":
        raise UnauthorizedException(f"Invalid token type: expected 'access', received '{token_type}'")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid authentication token payload")

    user = await db.get(User, user_id)
    if not user:
        raise UnauthorizedException("User no longer exists")
    if not user.is_active:
        raise ForbiddenException("User account is inactive")

    return user


async def get_current_active_tenant(
    current_user: User = Depends(get_current_user)
) -> str:
    """
    Returns the tenant_id of the current authenticated user.
    If the user has no tenant_id (e.g. platform Super Admin), this will raise or return specific scope.
    """
    if not current_user.tenant_id and not current_user.is_superuser:
        raise ForbiddenException("User is not associated with any active company tenant")
    return current_user.tenant_id or ""


def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_superuser and current_user.role != UserRoleType.SUPER_ADMIN.value:
        raise ForbiddenException("Action requires Ardhnarishwar Super Admin privileges")
    return current_user


def require_permission(required_permission: str) -> Callable:
    """
    RBAC dependency factory that validates granular permission strings.
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.is_superuser or current_user.role == UserRoleType.SUPER_ADMIN.value:
            return current_user

        user_perms = ROLE_PERMISSIONS_MAP.get(current_user.role, [])
        if required_permission not in user_perms:
            raise ForbiddenException(f"Missing required permission: '{required_permission}'")
        return current_user

    return permission_checker


def verify_tenant_access(
    target_tenant_id: str,
    current_user: User
) -> None:
    """
    Strict IDOR prevention helper.
    Ensures that non-superusers cannot access or manipulate other tenants' resource paths.
    """
    if current_user.is_superuser or current_user.role == UserRoleType.SUPER_ADMIN.value:
        return
    if current_user.tenant_id != target_tenant_id:
        raise TenantMismatchException(
            f"Access denied: Attempted cross-tenant access from tenant '{current_user.tenant_id}' to '{target_tenant_id}'"
        )
