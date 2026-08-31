from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.entities import AuditLog
from app.schemas.audit import AuditLogRead


class AuditService:
    @staticmethod
    async def log_action(
        db: AsyncSession,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        audit_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            tenant_id=tenant_id,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        db.add(audit_entry)
        await db.flush()
        return audit_entry

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        tenant_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        query = select(AuditLog)
        if tenant_id:
            query = query.where(AuditLog.tenant_id == tenant_id)
        query = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
