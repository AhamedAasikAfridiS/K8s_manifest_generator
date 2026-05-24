"""Kubernetes manifest YAML generation."""

from __future__ import annotations

from typing import Any

import yaml

from app.schemas import ComponentSpec, DiagramAnalysis


def _deployment(name: str, namespace: str, image: str, replicas: int, port: int) -> dict[str, Any]:
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name, "namespace": namespace, "labels": {"app": name}},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": {
                    "containers": [
                        {
                            "name": name,
                            "image": image,
                            "ports": [{"containerPort": port}],
                            "resources": {
                                "requests": {"cpu": "100m", "memory": "128Mi"},
                                "limits": {"cpu": "500m", "memory": "512Mi"},
                            },
                        }
                    ]
                },
            },
        },
    }


def _service(name: str, namespace: str, port: int) -> dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": f"{name}-svc", "namespace": namespace, "labels": {"app": name}},
        "spec": {
            "selector": {"app": name},
            "ports": [{"port": port, "targetPort": port, "protocol": "TCP"}],
            "type": "ClusterIP",
        },
    }


def _ingress(name: str, namespace: str, host: str, path: str, port: int) -> dict[str, Any]:
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"{name}-ingress",
            "namespace": namespace,
            "annotations": {"kubernetes.io/ingress.class": "nginx"},
        },
        "spec": {
            "rules": [
                {
                    "host": host,
                    "http": {
                        "paths": [
                            {
                                "path": path,
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": f"{name}-svc",
                                        "port": {"number": port},
                                    }
                                },
                            }
                        ]
                    },
                }
            ]
        },
    }


def _configmap(name: str, namespace: str, data: dict[str, str]) -> dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": f"{name}-config", "namespace": namespace},
        "data": data,
    }


def _namespace(name: str) -> dict[str, Any]:
    return {
        "apiVersion": "v1",
        "kind": "Namespace",
        "metadata": {"name": name, "labels": {"app.kubernetes.io/managed-by": "k8s-manifest-generator"}},
    }


def _hpa(
    name: str,
    namespace: str,
    min_replicas: int,
    max_replicas: int,
    target_cpu: int,
) -> dict[str, Any]:
    return {
        "apiVersion": "autoscaling/v2",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {"name": f"{name}-hpa", "namespace": namespace},
        "spec": {
            "scaleTargetRef": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": name,
            },
            "minReplicas": min_replicas,
            "maxReplicas": max_replicas,
            "metrics": [
                {
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {"type": "Utilization", "averageUtilization": target_cpu},
                    },
                }
            ],
        },
    }


def _to_yaml(doc: dict[str, Any]) -> str:
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)


def generate_from_analysis(analysis: DiagramAnalysis) -> tuple[dict[str, str], list[str]]:
    """Build Kubernetes manifests from diagram analysis."""
    manifests: dict[str, str] = {}
    detected: list[str] = []
    ns = analysis.namespace
    app = analysis.app_name

    if ns and ns != "default":
        manifests["namespace.yaml"] = _to_yaml(_namespace(ns))
        detected.append("Namespace")

    deployments = [c for c in analysis.components if c.type.lower() in ("deployment", "app", "web", "api", "service-app")]
    services = [c for c in analysis.components if c.type.lower() in ("service", "loadbalancer", "clusterip")]
    ingresses = [c for c in analysis.components if c.type.lower() == "ingress"]
    configmaps = [c for c in analysis.components if c.type.lower() == "configmap"]
    hpas = [c for c in analysis.components if c.type.lower() == "hpa"]

    if not deployments:
        deployments = [
            ComponentSpec(
                name=app,
                type="deployment",
                image="nginx:1.27-alpine",
                port=80,
                replicas=2,
            )
        ]

    for idx, dep in enumerate(deployments):
        name = dep.name or f"{app}-{idx}" if idx else app
        image = dep.image or "nginx:1.27-alpine"
        port = dep.port or 80
        replicas = dep.replicas or 2
        manifests[f"deployment-{name}.yaml"] = _to_yaml(_deployment(name, ns, image, replicas, port))
        detected.append(f"Deployment:{name}")

        svc_port = port
        manifests[f"service-{name}.yaml"] = _to_yaml(_service(name, ns, svc_port))
        detected.append(f"Service:{name}")

    for ing in ingresses:
        name = ing.name or app
        host = ing.host or f"{name}.example.com"
        path = ing.path or "/"
        port = ing.port or 80
        manifests[f"ingress-{name}.yaml"] = _to_yaml(_ingress(name, ns, host, path, port))
        detected.append(f"Ingress:{name}")

    if not ingresses and deployments:
        primary = deployments[0]
        name = primary.name or app
        port = primary.port or 80
        manifests[f"ingress-{name}.yaml"] = _to_yaml(
            _ingress(name, ns, f"{name}.example.com", "/", port)
        )
        detected.append(f"Ingress:{name}")

    for cm in configmaps:
        name = cm.name or f"{app}-config"
        data = cm.data or {"APP_ENV": "production", "LOG_LEVEL": "info"}
        manifests[f"configmap-{name}.yaml"] = _to_yaml(_configmap(name, ns, data))
        detected.append(f"ConfigMap:{name}")

    if not configmaps:
        manifests[f"configmap-{app}.yaml"] = _to_yaml(
            _configmap(app, ns, {"APP_NAME": app, "ENVIRONMENT": "production"})
        )
        detected.append(f"ConfigMap:{app}")

    for hpa in hpas:
        name = hpa.name or app
        manifests[f"hpa-{name}.yaml"] = _to_yaml(
            _hpa(
                name,
                ns,
                hpa.min_replicas or 2,
                hpa.max_replicas or 10,
                hpa.target_cpu_percent or 70,
            )
        )
        detected.append(f"HPA:{name}")

    if not hpas and deployments:
        primary_name = deployments[0].name or app
        manifests[f"hpa-{primary_name}.yaml"] = _to_yaml(_hpa(primary_name, ns, 2, 10, 70))
        detected.append(f"HPA:{primary_name}")

    _ = services  # reserved for explicit Service components in future diagrams

    return manifests, detected


def combine_manifests(manifests: dict[str, str]) -> str:
    parts = []
    for filename in sorted(manifests.keys()):
        parts.append(f"# --- {filename} ---")
        parts.append(manifests[filename].rstrip())
        parts.append("")
    return "\n".join(parts)


def default_analysis(app_name: str = "web-app", namespace: str = "default") -> DiagramAnalysis:
    return DiagramAnalysis(
        namespace=namespace,
        app_name=app_name,
        description="Default architecture inferred from diagram",
        components=[
            ComponentSpec(name=app_name, type="deployment", image="nginx:1.27-alpine", port=80, replicas=2),
            ComponentSpec(name=app_name, type="ingress", host=f"{app_name}.example.com", path="/", port=80),
            ComponentSpec(
                name=app_name,
                type="configmap",
                data={"APP_NAME": app_name, "ENVIRONMENT": "production"},
            ),
            ComponentSpec(
                name=app_name,
                type="hpa",
                min_replicas=2,
                max_replicas=10,
                target_cpu_percent=70,
            ),
        ],
    )
