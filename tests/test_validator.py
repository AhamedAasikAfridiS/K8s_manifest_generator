"""Unit tests for YAML validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai-agent-service"))

from app.config import Settings
from app.services.validator import validate_manifest, validate_yaml_syntax

SAMPLE_YAML = """
apiVersion: v1
kind: Namespace
metadata:
  name: demo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
"""


def test_yaml_syntax_valid():
    valid, issues = validate_yaml_syntax(SAMPLE_YAML)
    assert valid is True
    assert isinstance(issues, list)


def test_yaml_syntax_invalid():
    valid, issues = validate_yaml_syntax("apiVersion: v1\nkind: [broken")
    assert valid is False
    assert len(issues) >= 1


def test_validate_manifest_integration():
    settings = Settings(enable_kube_score=False, enable_kube_linter=False)
    result = validate_manifest(SAMPLE_YAML, settings)
    assert result["syntax_valid"] is True
    assert "yaml-syntax" in result["tools_run"]
