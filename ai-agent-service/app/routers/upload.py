"""Diagram upload endpoints."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import get_settings
from app.schemas import UploadResponse
from app.security import get_current_user_email

logger = logging.getLogger(__name__)
router = APIRouter(tags=["upload"])
settings = get_settings()

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
    "application/pdf",
}


@router.post("/upload-diagram", response_model=UploadResponse)
async def upload_diagram(
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user_email),
) -> UploadResponse:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PNG, JPEG, WEBP, GIF, PDF",
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file")

    settings.upload_path.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    suffix = Path(file.filename or "diagram.png").suffix or ".png"
    stored_name = f"{file_id}{suffix}"
    dest = settings.upload_path / stored_name

    dest.write_bytes(content)

    meta_path = settings.upload_path / f"{file_id}.meta"
    meta_path.write_text(
        f"user={user_email}\noriginal={file.filename}\nstored={stored_name}\n",
        encoding="utf-8",
    )

    logger.info("Diagram uploaded by %s: %s", user_email, stored_name)

    return UploadResponse(
        file_id=stored_name,
        filename=file.filename or stored_name,
        size_bytes=len(content),
        content_type=file.content_type or "application/octet-stream",
        uploaded_at=datetime.now(UTC),
    )
