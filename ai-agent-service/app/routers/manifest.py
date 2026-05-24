"""Manifest generation, validation, and download endpoints."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from app.agents.k8s_agent import K8sArchitectureAgent
from app.config import get_settings
from app.schemas import (
    GenerateManifestRequest,
    GenerateManifestResponse,
    ValidateManifestRequest,
    ValidateManifestResponse,
)
from app.security import get_current_user_email
from app.services.manifest_generator import combine_manifests, generate_from_analysis
from app.services.validator import validate_manifest
from app.schemas import DiagramAnalysis

logger = logging.getLogger(__name__)
router = APIRouter(tags=["manifest"])
settings = get_settings()


def _manifest_meta_path(manifest_id: str) -> Path:
    return settings.generated_path / f"{manifest_id}.json"


def _manifest_yaml_path(manifest_id: str) -> Path:
    return settings.generated_path / f"{manifest_id}.yaml"


@router.post("/generate-manifest", response_model=GenerateManifestResponse)
def generate_manifest(
    payload: GenerateManifestRequest,
    user_email: str = Depends(get_current_user_email),
) -> GenerateManifestResponse:
    upload_path = settings.upload_path / payload.file_id
    if not upload_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploaded diagram not found")

    agent = K8sArchitectureAgent(settings)

    if payload.components:
        analysis = DiagramAnalysis(
            namespace=payload.namespace,
            app_name=payload.app_name,
            description=payload.description or "",
            components=payload.components,
        )
        llm_mode = "manual"
    else:
        analysis = agent.analyze(upload_path, payload.description)
        if payload.namespace:
            analysis.namespace = payload.namespace
        if payload.app_name:
            analysis.app_name = payload.app_name
        llm_mode = "mock" if settings.should_use_mock else "openai"

    manifests, detected = generate_from_analysis(analysis)
    combined = combine_manifests(manifests)
    manifest_id = str(uuid.uuid4())

    settings.generated_path.mkdir(parents=True, exist_ok=True)
    meta = {
        "manifest_id": manifest_id,
        "user_email": user_email,
        "file_id": payload.file_id,
        "namespace": analysis.namespace,
        "created_at": datetime.now(UTC).isoformat(),
        "manifests": manifests,
        "combined_yaml": combined,
        "components_detected": detected,
        "llm_mode": llm_mode,
    }
    _manifest_meta_path(manifest_id).write_text(json.dumps(meta, indent=2), encoding="utf-8")
    _manifest_yaml_path(manifest_id).write_text(combined, encoding="utf-8")

    logger.info("Generated manifest %s for user %s", manifest_id, user_email)

    return GenerateManifestResponse(
        manifest_id=manifest_id,
        namespace=analysis.namespace,
        manifests=manifests,
        combined_yaml=combined,
        components_detected=detected,
        llm_mode=llm_mode,
    )


@router.post("/validate-manifest", response_model=ValidateManifestResponse)
def validate_manifest_endpoint(
    payload: ValidateManifestRequest,
    user_email: str = Depends(get_current_user_email),
) -> ValidateManifestResponse:
    yaml_content = payload.yaml_content

    if payload.manifest_id:
        meta_path = _manifest_meta_path(payload.manifest_id)
        if not meta_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manifest not found")
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("user_email") != user_email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        yaml_content = meta.get("combined_yaml")

    if not yaml_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide manifest_id or yaml_content",
        )

    result = validate_manifest(yaml_content, settings)
    return ValidateManifestResponse(**result)


@router.get("/download-manifest")
def download_manifest(
    manifest_id: str = Query(..., description="Manifest UUID"),
    user_email: str = Depends(get_current_user_email),
) -> FileResponse:
    meta_path = _manifest_meta_path(manifest_id)
    yaml_path = _manifest_yaml_path(manifest_id)

    if not meta_path.exists() or not yaml_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manifest not found")

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("user_email") != user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    filename = f"k8s-manifests-{manifest_id[:8]}.yaml"
    return FileResponse(
        path=yaml_path,
        media_type="application/x-yaml",
        filename=filename,
    )
