from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.schemas.auth import LoginRequest, Token, RefreshTokenRequest
from app.schemas.user import UserRead, UserProfile
from app.schemas.common import StandardResponse, MessageResponse
from app.services.user_service import AuthService, UserService, ROLE_PERMISSIONS_MAP
from app.services.audit_service import AuditService
from app.api.deps import get_current_user
from app.models.entities import User, Company

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=StandardResponse[Token])
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await AuthService.authenticate(db, payload.email, payload.password)
    tokens = AuthService.generate_auth_tokens(user)

    await AuditService.log_action(
        db=db,
        action="LOGIN",
        resource_type="USER",
        resource_id=user.id,
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_email=user.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return StandardResponse(
        success=True,
        message="Login successful",
        data=Token(**tokens)
    )


@router.get("/me", response_model=StandardResponse[UserProfile])
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    perms = ROLE_PERMISSIONS_MAP.get(current_user.role, [])
    company_name = None
    if current_user.tenant_id:
        company = await db.get(Company, current_user.tenant_id)
        if company:
            company_name = company.name

    profile = UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        tenant_id=current_user.tenant_id,
        permissions=perms,
        company_name=company_name,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    return StandardResponse(data=profile)


@router.post("/refresh", response_model=StandardResponse[Token])
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    token_data = decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh":
        raise UnauthorizedException("Invalid or expired refresh token")
    
    user_id = token_data.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid refresh token payload")
        
    user = await db.get(User, user_id)
    if not user:
        raise UnauthorizedException("User no longer exists")
    if not user.is_active:
        raise ForbiddenException("User account is inactive")
        
    tokens = AuthService.generate_auth_tokens(user)
    return StandardResponse(
        success=True,
        message="Token refreshed successfully",
        data=Token(**tokens)
    )


@router.post("/logout", response_model=StandardResponse[MessageResponse])
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await AuditService.log_action(
        db=db,
        action="LOGOUT",
        resource_type="USER",
        resource_id=current_user.id,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    return StandardResponse(data=MessageResponse(message="Logged out successfully"))
