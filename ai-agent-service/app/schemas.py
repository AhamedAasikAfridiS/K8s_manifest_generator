"""Request and response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    llm_mode: str


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size_bytes: int
    content_type: str
    uploaded_at: datetime


class ComponentSpec(BaseModel):
    name: str
    type: str
    image: str | None = None
    port: int | None = None
    replicas: int | None = 1
    host: str | None = None
    path: str | None = None
    data: dict[str, str] | None = None
    min_replicas: int | None = None
    max_replicas: int | None = None
    target_cpu_percent: int | None = None


class GenerateManifestRequest(BaseModel):
    file_id: str
    namespace: str = "default"
    app_name: str = "web-app"
    components: list[ComponentSpec] | None = None
    description: str | None = None


class GenerateManifestResponse(BaseModel):
    manifest_id: str
    namespace: str
    manifests: dict[str, str]
    combined_yaml: str
    components_detected: list[str]
    llm_mode: str


class ValidateManifestRequest(BaseModel):
    manifest_id: str | None = None
    yaml_content: str | None = None


class ValidationIssue(BaseModel):
    tool: str
    severity: str
    message: str
    resource: str | None = None


class ValidateManifestResponse(BaseModel):
    valid: bool
    syntax_valid: bool
    issues: list[ValidationIssue]
    summary: str
    tools_run: list[str]


class DiagramAnalysis(BaseModel):
    namespace: str = "default"
    app_name: str = "web-app"
    components: list[ComponentSpec] = Field(default_factory=list)
    description: str = ""
