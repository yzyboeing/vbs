#!/usr/bin/env python3
"""Run MLX Whisper through the configured shared VBS runtime."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from runtime_config import (
    RuntimeConfigError,
    build_whisper_command,
    load_runtime_config,
    probe_runtime,
    runtime_environment,
)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Example: run_asr.py audio.wav --language en --output-format srt "
            "--output-dir output"
        ),
    )
    parser.add_argument("--config", help="Override VBS_RUNTIME_CONFIG or ~/.config/vbs/runtime.json")
    parser.add_argument("--check", action="store_true", help="Check the runtime without transcribing")
    parser.add_argument(
        "--deep-check",
        action="store_true",
        help="With --check, also verify the full model SHA-256",
    )
    args, whisper_args = parser.parse_known_args()

    report = probe_runtime(args.config, deep=args.deep_check)
    if args.check:
        print(json.dumps(report, indent=2))
        return 0 if report["ok"] else 2
    if not report["ok"]:
        print("VBS shared ASR runtime is not ready:", file=sys.stderr)
        for error in report["errors"]:
            print(f"- {error}", file=sys.stderr)
        for warning in report["warnings"]:
            print(f"- warning: {warning}", file=sys.stderr)
        print("Run this script with --check for the complete JSON report.", file=sys.stderr)
        return 2

    try:
        config = load_runtime_config(args.config)
        command = build_whisper_command(config, whisper_args)
    except RuntimeConfigError as exc:
        print(f"VBS ASR configuration error: {exc}", file=sys.stderr)
        return 2
    return subprocess.run(command, env=runtime_environment(config), check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
