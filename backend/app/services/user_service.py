from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.entities import User, Company, UserRoleType
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import NotFoundException, ConflictException, UnauthorizedException, ForbiddenException


ROLE_PERMISSIONS_MAP = {
    UserRoleType.SUPER_ADMIN.value: [
        "company:create", "company:update", "company:delete", "company:view",
        "user:create", "user:update", "user:delete", "user:view",
        "job:create", "job:update", "job:delete", "job:view",
        "candidate:create", "candidate:update", "candidate:view",
        "interview:create", "interview:start", "interview:view", "interview:evaluate",
        "recording:view", "recording:download",
        "report:view", "report:download",
        "question:create", "question:update", "question:delete", "question:view",
        "dataset:create", "dataset:view", "dataset:upload",
        "analytics:view", "audit:view", "system:manage"
    ],
    UserRoleType.COMPANY_ADMIN.value: [
        "company:view", "company:update",
        "user:create", "user:update", "user:view",
        "job:create", "job:update", "job:delete", "job:view",
        "candidate:create", "candidate:update", "candidate:view",
        "interview:create", "interview:view", "interview:evaluate",
        "recording:view", "recording:download",
        "report:view", "report:download",
        "question:create", "question:update", "question:view",
        "analytics:view", "audit:view"
    ],
    UserRoleType.RECRUITER.value: [
        "job:create", "job:update", "job:view",
        "candidate:create", "candidate:update", "candidate:view",
        "interview:create", "interview:view",
        "recording:view",
        "report:view", "report:download",
        "question:view", "analytics:view"
    ],
    UserRoleType.INTERVIEWER.value: [
        "interview:view", "interview:evaluate", "recording:view", "report:view", "question:view"
    ],
    UserRoleType.CANDIDATE.value: [
        "interview:start", "interview:view"
    ]
}


class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException("User not found")
        return user

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalars().first()

    @staticmethod
    async def create_user(db: AsyncSession, data: UserCreate, is_superuser: bool = False) -> User:
        existing = await UserService.get_by_email(db, data.email)
        if existing:
            raise ConflictException(f"User with email '{data.email}' already exists")

        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            role=data.role,
            is_active=data.is_active,
            is_superuser=is_superuser,
            tenant_id=data.tenant_id
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def list_company_users(db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).where(User.tenant_id == tenant_id).offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def list_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())


class AuthService:
    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> User:
        user = await UserService.get_by_email(db, email)
        if not user:
            raise UnauthorizedException("Invalid email or password")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise ForbiddenException("User account is inactive")
        return user

    @staticmethod
    def generate_auth_tokens(user: User) -> dict:
        perms = ROLE_PERMISSIONS_MAP.get(user.role, [])
        access_token = create_access_token(
            subject=user.id,
            tenant_id=user.tenant_id,
            role=user.role,
            permissions=perms
        )
        refresh_token = create_refresh_token(
            subject=user.id,
            tenant_id=user.tenant_id
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900
        }
