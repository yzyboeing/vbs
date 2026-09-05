#!/usr/bin/env python3
"""Load and verify the shared VBS ASR runtime without reading media or secrets."""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import subprocess


SCHEMA_VERSION = 1
DEFAULT_CONFIG = Path.home() / ".config" / "vbs" / "runtime.json"


class RuntimeConfigError(RuntimeError):
    """Raised when the shared runtime configuration is missing or invalid."""


def resolve_config_path(explicit=None):
    raw = explicit or os.environ.get("VBS_RUNTIME_CONFIG")
    return Path(raw).expanduser() if raw else DEFAULT_CONFIG


def load_runtime_config(explicit=None):
    path = resolve_config_path(explicit)
    if not path.is_file():
        raise RuntimeConfigError(
            f"Shared VBS runtime config not found: {path}. "
            "Create it as described in references/dependencies.md."
        )
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeConfigError(f"Cannot read VBS runtime config {path}: {exc}") from exc

    required = (
        "schema_version",
        "python_executable",
        "python_version",
        "mlx_whisper_cli",
        "mlx_whisper_version",
        "model_id",
        "model_revision",
        "model_path",
        "weights_bytes",
        "weights_sha256",
    )
    missing = [key for key in required if not config.get(key)]
    if missing:
        raise RuntimeConfigError(
            f"VBS runtime config {path} is missing: {', '.join(missing)}"
        )
    if config["schema_version"] != SCHEMA_VERSION:
        raise RuntimeConfigError(
            f"Unsupported VBS runtime schema {config['schema_version']}; expected {SCHEMA_VERSION}."
        )
    config["config_path"] = str(path)
    return config


def _sha256(path, chunk_size=8 * 1024 * 1024):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def probe_runtime(explicit=None, timeout=20, deep=False):
    report = {
        "configured": False,
        "ok": False,
        "config_path": str(resolve_config_path(explicit)),
        "errors": [],
        "warnings": [],
    }
    try:
        config = load_runtime_config(explicit)
    except RuntimeConfigError as exc:
        report["errors"].append(str(exc))
        return report

    report["configured"] = True
    python = Path(config["python_executable"]).expanduser()
    cli = Path(config["mlx_whisper_cli"]).expanduser()
    model = Path(config["model_path"]).expanduser()
    report.update(
        {
            "python_executable": str(python),
            "expected_python": config["python_version"],
            "mlx_whisper_cli": str(cli),
            "expected_mlx_whisper": config["mlx_whisper_version"],
            "model_id": config["model_id"],
            "model_revision": config["model_revision"],
            "model_path": str(model),
            "deep_model_check": deep,
        }
    )

    if not python.is_file() or not os.access(python, os.X_OK):
        report["errors"].append(f"Configured Python is missing or not executable: {python}")
    if not cli.is_file() or not os.access(cli, os.X_OK):
        report["errors"].append(f"MLX Whisper CLI is missing or not executable: {cli}")

    required_model_files = ("config.json", "weights.safetensors")
    for name in required_model_files:
        candidate = model / name
        if not candidate.is_file() or candidate.stat().st_size == 0:
            report["errors"].append(f"Model file is missing or empty: {candidate}")
    weights = model / "weights.safetensors"
    if weights.is_file():
        actual_bytes = weights.stat().st_size
        report["weights_bytes"] = actual_bytes
        if actual_bytes != config["weights_bytes"]:
            report["errors"].append(
                f"Model size mismatch: expected {config['weights_bytes']} bytes, found {actual_bytes}."
            )
        if deep:
            actual_sha256 = _sha256(weights)
            report["weights_sha256"] = actual_sha256
            if actual_sha256 != config["weights_sha256"]:
                report["errors"].append(
                    "Model SHA-256 mismatch: expected "
                    f"{config['weights_sha256']}, found {actual_sha256}."
                )
    incomplete = sorted(str(path) for path in model.rglob("*.incomplete")) if model.is_dir() else []
    if incomplete:
        report["warnings"].append(
            f"Model directory contains {len(incomplete)} incomplete download marker(s)."
        )

    if python.is_file() and os.access(python, os.X_OK):
        snippet = (
            "import importlib.metadata, json, platform; import mlx_whisper; "
            "print(json.dumps({'python': platform.python_version(), "
            "'mlx_whisper': importlib.metadata.version('mlx-whisper')}))"
        )
        try:
            result = subprocess.run(
                [str(python), "-c", snippet],
                text=True,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            report["errors"].append(f"Configured Python health check failed: {exc}")
        else:
            if result.returncode:
                detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
                report["errors"].append(f"Cannot import mlx_whisper in configured Python: {detail}")
            else:
                try:
                    versions = json.loads(result.stdout)
                except json.JSONDecodeError:
                    report["errors"].append("Configured Python returned an unreadable version report.")
                else:
                    report["actual_python"] = versions.get("python")
                    report["actual_mlx_whisper"] = versions.get("mlx_whisper")
                    expected_python = str(config["python_version"])
                    if not str(versions.get("python", "")).startswith(expected_python + "."):
                        report["errors"].append(
                            f"Python version mismatch: expected {expected_python}.x, "
                            f"found {versions.get('python')}."
                        )
                    if versions.get("mlx_whisper") != config["mlx_whisper_version"]:
                        report["errors"].append(
                            "MLX Whisper version mismatch: expected "
                            f"{config['mlx_whisper_version']}, found {versions.get('mlx_whisper')}."
                        )

    report["ok"] = not report["errors"]
    return report


def build_whisper_command(config, whisper_args):
    args = list(whisper_args)
    if not args:
        raise RuntimeConfigError("No audio input or MLX Whisper arguments were provided.")
    has_model = any(arg == "--model" or arg.startswith("--model=") for arg in args)
    command = [str(Path(config["mlx_whisper_cli"]).expanduser()), *args]
    if not has_model:
        command.extend(["--model", str(Path(config["model_path"]).expanduser())])
    return command


def runtime_environment(config):
    env = os.environ.copy()
    if config.get("hf_home"):
        env["HF_HOME"] = str(Path(config["hf_home"]).expanduser())
    return env
