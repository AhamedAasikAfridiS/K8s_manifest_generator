"""LangChain-based Kubernetes architecture analyzer with mock fallback."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.config import Settings
from app.schemas import ComponentSpec, DiagramAnalysis
from app.services.manifest_generator import default_analysis

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a Kubernetes architecture expert.
Analyze the described Kubernetes architecture diagram and return ONLY valid JSON with this structure:
{
  "namespace": "string",
  "app_name": "string",
  "description": "string",
  "components": [
    {
      "name": "string",
      "type": "deployment|service|ingress|configmap|hpa",
      "image": "optional container image",
      "port": 80,
      "replicas": 2,
      "host": "optional ingress host",
      "path": "/",
      "data": {"KEY": "value"},
      "min_replicas": 2,
      "max_replicas": 10,
      "target_cpu_percent": 70
    }
  ]
}
Include Deployment, Service, Ingress, ConfigMap, and HPA where appropriate.
"""


class K8sArchitectureAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def analyze(self, image_path: Path, user_hint: str | None = None) -> DiagramAnalysis:
        if self.settings.should_use_mock:
            logger.info("Using mock LLM analysis (no API key or USE_MOCK_LLM=true)")
            return self._mock_analysis(image_path, user_hint)

        return self._llm_analysis(image_path, user_hint)

    def _mock_analysis(self, image_path: Path, user_hint: str | None) -> DiagramAnalysis:
        stem = image_path.stem.lower().replace(" ", "-")
        app_name = "web-app"
        namespace = "production"

        if "api" in stem or (user_hint and "api" in user_hint.lower()):
            app_name = "api-service"
        elif "frontend" in stem or "ui" in stem:
            app_name = "frontend"
        elif stem and stem not in ("diagram", "architecture", "upload"):
            app_name = stem[:40]

        analysis = default_analysis(app_name=app_name, namespace=namespace)
        if user_hint:
            analysis.description = user_hint
        else:
            analysis.description = (
                f"Mock analysis for diagram '{image_path.name}'. "
                "Set OPENAI_API_KEY and USE_MOCK_LLM=false for AI-powered analysis."
            )

        analysis.components.extend(
            [
                ComponentSpec(
                    name="redis-cache",
                    type="deployment",
                    image="redis:7-alpine",
                    port=6379,
                    replicas=1,
                ),
            ]
        )
        return analysis

    def _llm_analysis(self, image_path: Path, user_hint: str | None) -> DiagramAnalysis:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            logger.warning("LangChain import failed, falling back to mock: %s", exc)
            return self._mock_analysis(image_path, user_hint)

        llm = ChatOpenAI(
            model=self.settings.openai_model,
            api_key=self.settings.openai_api_key,
            base_url=self.settings.openai_api_base,
            temperature=0.2,
        )

        hint = user_hint or f"Architecture diagram file: {image_path.name}"
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Analyze this Kubernetes architecture diagram context and infer components.\n"
                    f"User context: {hint}\n"
                    "Return JSON only."
                )
            ),
        ]

        try:
            response = llm.invoke(messages)
            content = response.content if isinstance(response.content, str) else str(response.content)
            data = self._extract_json(content)
            return DiagramAnalysis.model_validate(data)
        except Exception as exc:
            logger.error("LLM analysis failed, using mock fallback: %s", exc)
            return self._mock_analysis(image_path, user_hint)

    @staticmethod
    def _extract_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in LLM response")
        return json.loads(text[start : end + 1])
