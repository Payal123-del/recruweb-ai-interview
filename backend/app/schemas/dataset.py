from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DatasetBase(BaseModel):
    name: str = Field(..., min_length=2)
    category: str = "Question Dataset"
    description: Optional[str] = None
    current_version: str = "v1.0"
    records_count: int = 0
    status: str = "ACTIVE"


class DatasetCreate(DatasetBase):
    pass


class DatasetRead(DatasetBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DatasetVersionCreate(BaseModel):
    version_tag: str
    records_count: int = 0
    validation_status: str = "PASSED"
    validation_summary: Dict[str, Any] = {}


class DatasetVersionRead(BaseModel):
    id: str
    dataset_id: str
    version_tag: str
    file_storage_key: Optional[str] = None
    records_count: int
    validation_status: str
    validation_summary: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelVersionRead(BaseModel):
    id: str
    name: str
    version_tag: str
    model_type: str
    status: str
    metrics: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
