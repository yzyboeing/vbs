#!/usr/bin/env python3
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

STAGES = [
    "ingested",
    "english-draft-ready",
    "english-approved",
    "bilingual-draft-ready",
    "bilingual-approved",
    "review-burn-ready",
    "final-approved",
    "delivered",
]
APPROVAL_STAGES = {"english-approved", "bilingual-approved", "final-approved"}
MUTABLE_STAGES = {"english-draft-ready", "bilingual-draft-ready"}
MANIFEST = "workflow-manifest.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_path(job_dir: str) -> Path:
    return Path(job_dir).expanduser().resolve() / MANIFEST


def load(job_dir: str) -> tuple[Path, dict]:
    path = manifest_path(job_dir)
    if not path.is_file():
        raise SystemExit(f"Missing manifest: {path}")
    return path, json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_artifacts(job: Path, values: list[str]) -> dict:
    artifacts = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Artifact must be name=path: {value}")
        name, raw_path = value.split("=", 1)
        path = Path(raw_path).expanduser()
        if not path.is_absolute():
            path = job / path
        path = path.resolve()
        if not path.is_file():
            raise SystemExit(f"Artifact does not exist: {path}")
        artifacts[name] = {"path": str(path), "size": path.stat().st_size, "sha256": sha256(path)}
    return artifacts


def cmd_init(args: argparse.Namespace) -> None:
    job = Path(args.job_dir).expanduser().resolve()
    job.mkdir(parents=True, exist_ok=True)
    path = job / MANIFEST
    if path.exists():
        raise SystemExit(f"Manifest already exists: {path}")
    parsed = urlparse(args.source)
    source = {"value": args.source, "kind": "url" if parsed.scheme in {"http", "https"} else "local"}
    if source["kind"] == "local":
        local = Path(args.source).expanduser().resolve()
        if not local.is_file():
            raise SystemExit(f"Local source does not exist: {local}")
        source.update({"value": str(local), "size": local.stat().st_size, "sha256": sha256(local)})
    recorded_at = now()
    data = {
        "schema_version": 1,
        "created_at": recorded_at,
        "updated_at": recorded_at,
        "route": args.route,
        "source": source,
        "current_stage": "ingested",
        "checkpoints": {"ingested": {"recorded_at": recorded_at, "artifacts": {}}},
    }
    save(path, data)
    print(path)


def cmd_record(args: argparse.Namespace) -> None:
    path, data = load(args.job_dir)
    current = data["current_stage"]
    expected_index = STAGES.index(current) + 1
    if expected_index >= len(STAGES) or STAGES[expected_index] != args.stage:
        raise SystemExit(f"Illegal transition: {current} -> {args.stage}")
    if args.stage in APPROVAL_STAGES and not args.approval_note:
        raise SystemExit(f"--approval-note is required for {args.stage}")
    job = path.parent
    data["checkpoints"][args.stage] = {
        "recorded_at": now(),
        "approval_note": args.approval_note,
        "artifacts": parse_artifacts(job, args.artifact),
    }
    data["current_stage"] = args.stage
    data["updated_at"] = now()
    save(path, data)
    print(args.stage)


def cmd_verify(args: argparse.Namespace) -> None:
    _, data = load(args.job_dir)
    errors = []
    source = data.get("source", {})
    if source.get("kind") == "local":
        source_path = Path(source["value"])
        if not source_path.is_file() or sha256(source_path) != source.get("sha256"):
            errors.append("source file is missing or changed")
    for stage, checkpoint in data.get("checkpoints", {}).items():
        for name, artifact in checkpoint.get("artifacts", {}).items():
            artifact_path = Path(artifact["path"])
            if not artifact_path.is_file():
                errors.append(f"{stage}:{name} is missing")
            elif stage not in MUTABLE_STAGES and (
                artifact_path.stat().st_size != artifact["size"] or sha256(artifact_path) != artifact["sha256"]
            ):
                errors.append(f"{stage}:{name} changed after recording")
    result = {"stage": data["current_stage"], "valid": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(3)


def cmd_status(args: argparse.Namespace) -> None:
    path, data = load(args.job_dir)
    summary = {
        "manifest": str(path),
        "route": data["route"],
        "current_stage": data["current_stage"],
        "recorded_stages": [stage for stage in STAGES if stage in data.get("checkpoints", {})],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def cmd_invalidate(args: argparse.Namespace) -> None:
    path, data = load(args.job_dir)
    targets = {
        "english": "english-draft-ready",
        "bilingual": "bilingual-draft-ready",
        "review": "bilingual-approved",
        "final": "final-approved",
    }
    target = targets[args.from_stage]
    target_index = STAGES.index(target)
    if STAGES.index(data["current_stage"]) < target_index:
        raise SystemExit(f"Cannot invalidate {args.from_stage} from stage {data['current_stage']}")
    data["checkpoints"] = {
        stage: checkpoint
        for stage, checkpoint in data["checkpoints"].items()
        if STAGES.index(stage) <= target_index
    }
    data["current_stage"] = target
    data["updated_at"] = now()
    save(path, data)
    print(target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and verify review-gated subtitle workflow checkpoints.")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("job_dir")
    init.add_argument("--source", required=True)
    init.add_argument("--route", required=True, choices=["jzsub-source", "hybrid-audit", "whisper-asr"])
    init.set_defaults(func=cmd_init)

    record = sub.add_parser("record")
    record.add_argument("job_dir")
    record.add_argument("--stage", required=True, choices=STAGES[1:])
    record.add_argument("--artifact", action="append", default=[])
    record.add_argument("--approval-note")
    record.set_defaults(func=cmd_record)

    verify = sub.add_parser("verify")
    verify.add_argument("job_dir")
    verify.set_defaults(func=cmd_verify)

    status = sub.add_parser("status")
    status.add_argument("job_dir")
    status.set_defaults(func=cmd_status)

    invalidate = sub.add_parser("invalidate")
    invalidate.add_argument("job_dir")
    invalidate.add_argument(
        "--from",
        dest="from_stage",
        required=True,
        choices=["english", "bilingual", "review", "final"],
    )
    invalidate.set_defaults(func=cmd_invalidate)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
