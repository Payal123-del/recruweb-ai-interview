import os
import time
import hmac
import hashlib
import base64
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse
from app.core.config import settings
from app.schemas.common import StandardResponse
from app.storage.service import get_storage_service
from app.core.exceptions import ForbiddenException, NotFoundException, BadRequestException

router = APIRouter(prefix="/recordings", tags=["Video/Audio Recordings"])


@router.post("/upload-chunk", response_model=StandardResponse[dict])
async def upload_recording_chunk(
    file: UploadFile = File(...),
    interview_id: str = Form(...),
    question_id: str = Form(...),
    chunk_index: int = Form(0)
):
    storage = get_storage_service()
    content = await file.read()
    storage.validate_file(content, max_size_mb=50)

    key = f"interviews/{interview_id}/q_{question_id}_chunk_{chunk_index}.webm"
    storage_key = await storage.upload_file(content, key, content_type=file.content_type or "video/webm")

    return StandardResponse(
        message="Recording chunk uploaded successfully",
        data={"storage_key": storage_key, "size_bytes": len(content)}
    )


@router.get("/stream/{token}")
async def stream_recording_file(token: str):
    """
    Secure signed video streaming endpoint. Verifies cryptographic HMAC signature and expiry.
    """
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        storage_key, expiry_str, signature = decoded.rsplit(":", 2)
        payload = f"{storage_key}:{expiry_str}"
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_sig):
            raise ForbiddenException("Invalid signature on stream token")
        if int(expiry_str) < int(time.time()):
            raise ForbiddenException("Stream link has expired")

        safe_path = os.path.join(os.path.abspath(settings.STORAGE_LOCAL_DIR), storage_key.replace("..", "").lstrip("/\\"))
        if not os.path.exists(safe_path):
            raise NotFoundException("Recording file not found")

        return FileResponse(safe_path, media_type="video/webm")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unable to stream media: unauthorized or corrupted token")
