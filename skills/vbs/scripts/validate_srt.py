#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from pathlib import Path

TIMING = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")
CJK = re.compile(r"[\u3400-\u9fff]")


def seconds(parts: tuple[str, ...]) -> float:
    h, m, s, ms = map(int, parts)
    return h * 3600 + m * 60 + s + ms / 1000


def parse(path: Path) -> list[dict]:
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    cues = []
    for block_number, block in enumerate(blocks, 1):
        lines = [line.rstrip() for line in block.splitlines()]
        if len(lines) < 3:
            raise ValueError(f"block {block_number} has fewer than three lines")
        try:
            index = int(lines[0].strip())
        except ValueError as exc:
            raise ValueError(f"block {block_number} has an invalid index") from exc
        match = TIMING.match(lines[1].strip())
        if not match:
            raise ValueError(f"block {block_number} has an invalid timing line")
        cues.append({
            "index": index,
            "start": seconds(match.groups()[:4]),
            "end": seconds(match.groups()[4:]),
            "lines": lines[2:],
        })
    return cues


def video_duration(path: Path) -> float:
    output = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True)
    return float(output.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate structural and review properties of an SRT file.")
    parser.add_argument("srt")
    parser.add_argument("--mode", choices=["english", "chinese", "bilingual"], default="english")
    parser.add_argument("--video")
    parser.add_argument("--json-report")
    args = parser.parse_args()

    errors = []
    warnings = []
    try:
        cues = parse(Path(args.srt))
    except (OSError, ValueError) as exc:
        cues = []
        errors.append(str(exc))

    duration = video_duration(Path(args.video)) if args.video else None
    for position, cue in enumerate(cues, 1):
        if cue["index"] != position:
            errors.append(f"cue {position}: index is {cue['index']}")
        if cue["start"] >= cue["end"]:
            errors.append(f"cue {position}: start is not before end")
        if position > 1 and cue["start"] < cues[position - 2]["end"]:
            errors.append(f"cue {position}: overlaps cue {position - 1}")
        if not any(line.strip() for line in cue["lines"]):
            errors.append(f"cue {position}: empty text")
        if duration is not None and cue["end"] > duration + 0.1:
            errors.append(f"cue {position}: ends after video duration")
        cue_duration = cue["end"] - cue["start"]
        char_count = sum(len(line.strip()) for line in cue["lines"])
        if cue_duration < 0.8:
            warnings.append(f"cue {position}: very short duration {cue_duration:.3f}s")
        if cue_duration > 8.0:
            warnings.append(f"cue {position}: long duration {cue_duration:.3f}s")
        if cue_duration > 0 and char_count / cue_duration > (34 if args.mode == "bilingual" else 24):
            warnings.append(f"cue {position}: high reading speed {char_count / cue_duration:.1f} chars/s")
        if args.mode == "bilingual":
            if len(cue["lines"]) != 2:
                errors.append(f"cue {position}: bilingual review cue must have exactly two semantic lines")
            elif not CJK.search(cue["lines"][1]):
                errors.append(f"cue {position}: second line has no Chinese characters")
        elif args.mode == "chinese" and not CJK.search("".join(cue["lines"])):
            warnings.append(f"cue {position}: no Chinese characters detected")

    report = {
        "file": str(Path(args.srt).resolve()),
        "mode": args.mode,
        "cue_count": len(cues),
        "video_duration": duration,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_report:
        Path(args.json_report).write_text(rendered + "\n", encoding="utf-8")
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
