from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: str
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = {}
    timestamp: datetime

    class Config:
        from_attributes = True
