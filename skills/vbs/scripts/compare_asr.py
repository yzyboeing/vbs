#!/usr/bin/env python3
import argparse
import difflib
import json
import re
from pathlib import Path

TIMING = re.compile(r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s+-->\s+(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")
TOKEN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?%?")


def seconds(parts: tuple[str, ...]) -> float:
    h, m, s, ms = map(int, parts)
    return h * 3600 + m * 60 + s + ms / 1000


def parse_tokens(path: Path) -> list[dict]:
    records = []
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip())
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        match = TIMING.match(lines[1].strip())
        if not match:
            continue
        start = seconds(match.groups()[:4])
        end = seconds(match.groups()[4:])
        for token in TOKEN.findall(" ".join(lines[2:])):
            records.append({"raw": token, "norm": token.casefold(), "start": start, "end": end})
    return records


def clean_tsv(value: str) -> str:
    return value.replace("\t", " ").replace("\n", " ")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two ASR SRT passes and report token-level differences.")
    parser.add_argument("pass_a")
    parser.add_argument("pass_b")
    parser.add_argument("--json-report")
    args = parser.parse_args()

    a = parse_tokens(Path(args.pass_a))
    b = parse_tokens(Path(args.pass_b))
    matcher = difflib.SequenceMatcher(a=[item["norm"] for item in a], b=[item["norm"] for item in b], autojunk=False)
    differences = []
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            continue
        relevant = a[a0:a1] + b[b0:b1]
        start = min((item["start"] for item in relevant), default=0.0)
        end = max((item["end"] for item in relevant), default=start)
        differences.append({
            "operation": tag,
            "start": start,
            "end": end,
            "pass_a": " ".join(item["raw"] for item in a[a0:a1]),
            "pass_b": " ".join(item["raw"] for item in b[b0:b1]),
        })

    print("operation\tstart_seconds\tend_seconds\tpass_a\tpass_b\treview_reason")
    for item in differences:
        reason = "possible omission" if item["operation"] in {"delete", "insert"} else "wording mismatch"
        print(
            f"{item['operation']}\t{item['start']:.3f}\t{item['end']:.3f}\t"
            f"{clean_tsv(item['pass_a'])}\t{clean_tsv(item['pass_b'])}\t{reason}"
        )

    report = {
        "pass_a_tokens": len(a),
        "pass_b_tokens": len(b),
        "difference_groups": len(differences),
        "differences": differences,
    }
    if args.json_report:
        Path(args.json_report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
