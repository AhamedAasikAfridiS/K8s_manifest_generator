"""Unit tests for manifest generation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ai-agent-service"))

from app.schemas import DiagramAnalysis, ComponentSpec
from app.services.manifest_generator import combine_manifests, generate_from_analysis


def test_generate_default_manifests():
    analysis = DiagramAnalysis(
        namespace="staging",
        app_name="api",
        components=[
            ComponentSpec(name="api", type="deployment", image="myapi:1.0", port=8080, replicas=3),
            ComponentSpec(name="api", type="ingress", host="api.example.com", path="/", port=8080),
            ComponentSpec(name="api", type="configmap", data={"ENV": "staging"}),
            ComponentSpec(name="api", type="hpa", min_replicas=2, max_replicas=8, target_cpu_percent=75),
        ],
    )
    manifests, detected = generate_from_analysis(analysis)
    assert "deployment-api.yaml" in manifests
    assert "service-api.yaml" in manifests
    assert "ingress-api.yaml" in manifests
    assert "configmap-api.yaml" in manifests
    assert "hpa-api.yaml" in manifests
    assert len(detected) >= 5

    combined = combine_manifests(manifests)
    assert "kind: Deployment" in combined
    assert "namespace: staging" in combined
