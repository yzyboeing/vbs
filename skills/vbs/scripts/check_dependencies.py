#!/usr/bin/env python3
"""Report stage-specific capabilities without reading credentials or media."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys


def locate_jzsub(explicit=None):
    if explicit:
        candidates = [Path(explicit).expanduser()]
    else:
        candidates = [Path.home() / '.codex/skills/jzsub', Path.home() / '.agents/skills/jzsub']
    return next((p for p in candidates if (p / 'SKILL.md').is_file() and (p / 'scripts/fetch_video.py').is_file()), None)


def stage_status(python_ok, fetcher, ffmpeg, ffprobe, ytdlp, asr):
    return {
        'review': python_ok,
        'fetch': python_ok and fetcher and ffmpeg and ffprobe and ytdlp,
        'asr': python_ok and ffmpeg and ffprobe and asr,
        'burn': python_ok and ffmpeg and ffprobe,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jzsub-dir', default=os.environ.get('JZSUB_SKILL_DIR'))
    parser.add_argument('--require', choices=('review', 'fetch', 'asr', 'burn'), action='append', default=[])
    args = parser.parse_args()
    jzsub = locate_jzsub(args.jzsub_dir)
    bins = {name: bool(shutil.which(name)) for name in ('ffmpeg', 'ffprobe', 'yt-dlp')}
    asr = bool(shutil.which('whisper')) or any(importlib.util.find_spec(name) is not None for name in ('whisper', 'mlx_whisper', 'faster_whisper'))
    stages = stage_status(sys.version_info >= (3, 10), bool(jzsub), bins['ffmpeg'], bins['ffprobe'], bins['yt-dlp'], asr)
    report = {
        'stages': stages, 'tools': bins, 'jzsub_found': bool(jzsub),
        'asr_implementation_found': asr,
        'scope': 'availability only; model downloads, libass, fonts, execution and media QA not verified',
    }
    print(json.dumps(report, indent=2))
    return int(any(not stages[stage] for stage in args.require))


if __name__ == '__main__':
    raise SystemExit(main())
