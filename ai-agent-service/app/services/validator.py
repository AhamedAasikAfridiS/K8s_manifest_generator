"""YAML and Kubernetes manifest validation."""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from app.config import Settings
from app.schemas import ValidationIssue

logger = logging.getLogger(__name__)


def validate_yaml_syntax(yaml_content: str) -> tuple[bool, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    try:
        documents = list(yaml.safe_load_all(yaml_content))
        if not documents or all(doc is None for doc in documents):
            issues.append(
                ValidationIssue(
                    tool="yaml-syntax",
                    severity="error",
                    message="YAML content is empty or contains no documents",
                )
            )
            return False, issues

        for idx, doc in enumerate(documents):
            if doc is None:
                continue
            kind = doc.get("kind", "Unknown")
            api = doc.get("apiVersion", "unknown")
            if "kind" not in doc:
                issues.append(
                    ValidationIssue(
                        tool="yaml-syntax",
                        severity="error",
                        message=f"Document {idx + 1} missing 'kind' field",
                        resource=str(kind),
                    )
                )
            if "apiVersion" not in doc:
                issues.append(
                    ValidationIssue(
                        tool="yaml-syntax",
                        severity="warning",
                        message=f"Document {idx + 1} missing 'apiVersion' field",
                        resource=str(kind),
                    )
                )
            _ = api
        return len([i for i in issues if i.severity == "error"]) == 0, issues
    except yaml.YAMLError as exc:
        issues.append(
            ValidationIssue(
                tool="yaml-syntax",
                severity="error",
                message=f"YAML syntax error: {exc}",
            )
        )
        return False, issues


def _run_cli_tool(
    executable: str,
    args: list[str],
    tool_name: str,
) -> tuple[bool, list[ValidationIssue]]:
    issues: list[ValidationIssue] = []
    if not shutil.which(executable):
        issues.append(
            ValidationIssue(
                tool=tool_name,
                severity="info",
                message=f"{tool_name} not installed; skipped",
            )
        )
        return True, issues

    try:
        result = subprocess.run(
            [executable, *args],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if result.returncode == 0 and not output.strip():
            return True, issues

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            severity = "warning"
            lower = line.lower()
            if "error" in lower or "critical" in lower or "danger" in lower:
                severity = "error"
            elif "ok" in lower or "passed" in lower:
                continue
            issues.append(
                ValidationIssue(tool=tool_name, severity=severity, message=line)
            )

        has_errors = any(i.severity == "error" for i in issues)
        return not has_errors, issues
    except subprocess.TimeoutExpired:
        issues.append(
            ValidationIssue(
                tool=tool_name,
                severity="warning",
                message=f"{tool_name} timed out",
            )
        )
        return True, issues
    except Exception as exc:
        logger.warning("%s execution failed: %s", tool_name, exc)
        issues.append(
            ValidationIssue(
                tool=tool_name,
                severity="info",
                message=f"{tool_name} could not run: {exc}",
            )
        )
        return True, issues


def validate_with_tools(yaml_content: str, settings: Settings) -> tuple[list[str], list[ValidationIssue]]:
    tools_run: list[str] = []
    all_issues: list[ValidationIssue] = []

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False, encoding="utf-8") as tmp:
        tmp.write(yaml_content)
        tmp_path = Path(tmp.name)

    try:
        if settings.enable_kube_score:
            tools_run.append("kube-score")
            _, score_issues = _run_cli_tool(
                settings.kube_score_path,
                ["score", str(tmp_path)],
                "kube-score",
            )
            all_issues.extend(score_issues)

        if settings.enable_kube_linter:
            tools_run.append("kube-linter")
            _, linter_issues = _run_cli_tool(
                settings.kube_linter_path,
                ["lint", str(tmp_path)],
                "kube-linter",
            )
            all_issues.extend(linter_issues)
    finally:
        tmp_path.unlink(missing_ok=True)

    return tools_run, all_issues


def validate_manifest(yaml_content: str, settings: Settings) -> dict:
    tools_run = ["yaml-syntax"]
    issues: list[ValidationIssue] = []

    syntax_valid, syntax_issues = validate_yaml_syntax(yaml_content)
    issues.extend(syntax_issues)

    if syntax_valid:
        extra_tools, tool_issues = validate_with_tools(yaml_content, settings)
        tools_run.extend(extra_tools)
        issues.extend(tool_issues)

    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]

    if not syntax_valid:
        summary = "Manifest failed YAML syntax validation"
        valid = False
    elif errors:
        summary = f"Manifest has {len(errors)} error(s) and {len(warnings)} warning(s)"
        valid = False
    elif warnings:
        summary = f"Manifest is valid with {len(warnings)} warning(s)"
        valid = True
    else:
        summary = "Manifest passed all validation checks"
        valid = True

    return {
        "valid": valid,
        "syntax_valid": syntax_valid,
        "issues": issues,
        "summary": summary,
        "tools_run": tools_run,
    }
