# Stage-specific dependencies

Run `python3 scripts/check_dependencies.py` from the installed Skill directory. Select only the needed stages using repeated `--require review|fetch|asr|burn`. This checks availability, not operational success.

- Review tools require Python 3.10+. They do not require Whisper or FFmpeg for text-only checks.
- URL acquisition requires the installed upstream JZSub Skill, yt-dlp, FFmpeg and ffprobe. Preserve the existing locally maintained JZSub installation. This repository does not depend on a fork under the VBS maintainer's account.
- ASR requires a usable Whisper implementation; the check recognizes the Whisper CLI or the Python modules whisper, mlx_whisper and faster_whisper in the selected interpreter. Model availability and decoding still need to be tested.
- Burning requires FFmpeg/ffprobe, then a real check of libass and appropriate fonts before rendering.

JZSub source: https://github.com/pengchujin/jzsub

Inspect the upstream `skills/jzsub/SKILL.md` and installation instructions before a new installation. Use the host's Skill installer with repository `pengchujin/jzsub`, path `skills/jzsub`, and a verified commit or release. Record the source revision locally; do not automatically replace a working customized installation or silently track upstream main.

For an existing non-default installation, pass `--jzsub-dir <skill-directory>` or set `JZSUB_SKILL_DIR`. An invalid explicit path is reported as missing, not replaced by a guessed installation.

If JZSub is absent, URL acquisition is unavailable; existing local videos or user-provided subtitles can still use their applicable stages. Do not request Cookie/Token values. Do not auto-install dependencies during a read-only review.
