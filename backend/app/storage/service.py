import os
import time
import hmac
import hashlib
import base64
from abc import ABC, abstractmethod
from typing import Optional, Tuple
import aiofiles
from app.core.config import settings
from app.core.exceptions import BadRequestException


class BaseStorageService(ABC):
    @abstractmethod
    async def upload_file(self, file_content: bytes, destination_key: str, content_type: str = "video/webm") -> str:
        pass

    @abstractmethod
    async def get_signed_url(self, storage_key: str, expires_in_seconds: int = 3600) -> str:
        pass

    @abstractmethod
    async def delete_file(self, storage_key: str) -> bool:
        pass

    @abstractmethod
    async def file_exists(self, storage_key: str) -> bool:
        pass

    def validate_file(self, file_bytes: bytes, max_size_mb: int = 100, allowed_mimes: Optional[list] = None) -> bool:
        if len(file_bytes) > max_size_mb * 1024 * 1024:
            raise BadRequestException(f"File size exceeds maximum allowed limit of {max_size_mb}MB")
        return True


class LocalStorageService(BaseStorageService):
    def __init__(self, base_dir: str = settings.STORAGE_LOCAL_DIR):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    async def upload_file(self, file_content: bytes, destination_key: str, content_type: str = "video/webm") -> str:
        safe_key = destination_key.replace("..", "").lstrip("/\\")
        file_path = os.path.join(self.base_dir, safe_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(file_content)
        return safe_key

    async def get_signed_url(self, storage_key: str, expires_in_seconds: int = 3600) -> str:
        # Generate tamper-proof signed token for secure local streaming
        expiry = int(time.time()) + expires_in_seconds
        payload = f"{storage_key}:{expiry}"
        signature = hmac.new(
            settings.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        token = base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()
        return f"/api/v1/recordings/stream/{token}"

    async def delete_file(self, storage_key: str) -> bool:
        safe_key = storage_key.replace("..", "").lstrip("/\\")
        file_path = os.path.join(self.base_dir, safe_key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    async def file_exists(self, storage_key: str) -> bool:
        safe_key = storage_key.replace("..", "").lstrip("/\\")
        file_path = os.path.join(self.base_dir, safe_key)
        return os.path.exists(file_path)


class S3StorageService(BaseStorageService):
    def __init__(self):
        import boto3
        from botocore.config import Config

        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.STORAGE_ENDPOINT if "minio" in settings.STORAGE_ENDPOINT or "localhost" in settings.STORAGE_ENDPOINT else None,
            aws_access_key_id=settings.STORAGE_ACCESS_KEY,
            aws_secret_access_key=settings.STORAGE_SECRET_KEY,
            region_name=settings.STORAGE_REGION,
            config=Config(signature_version="s3v4")
        )
        self.bucket = settings.STORAGE_BUCKET

    async def upload_file(self, file_content: bytes, destination_key: str, content_type: str = "video/webm") -> str:
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=destination_key,
            Body=file_content,
            ContentType=content_type
        )
        return destination_key

    async def get_signed_url(self, storage_key: str, expires_in_seconds: int = 3600) -> str:
        url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": storage_key},
            ExpiresIn=expires_in_seconds
        )
        return url

    async def delete_file(self, storage_key: str) -> bool:
        self.s3_client.delete_object(Bucket=self.bucket, Key=storage_key)
        return True

    async def file_exists(self, storage_key: str) -> bool:
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=storage_key)
            return True
        except Exception:
            return False


def get_storage_service() -> BaseStorageService:
    if settings.STORAGE_PROVIDER in ["s3", "minio", "r2"]:
        try:
            return S3StorageService()
        except Exception:
            return LocalStorageService()
    return LocalStorageService()
