# Stage-specific dependencies

Run `python3 scripts/check_dependencies.py` from the installed Skill directory. Select only the needed stages using repeated `--require review|fetch|asr|burn`. This checks availability, not operational success.

- Review tools require Python 3.10+. They do not require Whisper or FFmpeg for text-only checks.
- URL acquisition requires the installed upstream JZSub Skill, yt-dlp, FFmpeg and ffprobe. Preserve the existing locally maintained JZSub installation. This repository does not depend on a fork under the VBS maintainer's account.
- ASR requires a usable Whisper implementation. Prefer the shared runtime described below. The check also recognizes the Whisper CLI or the Python modules whisper, mlx_whisper and faster_whisper in the selected interpreter. Model availability and decoding still need a real audio test.
- Burning requires FFmpeg/ffprobe, then a real check of libass and appropriate fonts before rendering.

JZSub source: https://github.com/pengchujin/jzsub

Inspect the upstream `skills/jzsub/SKILL.md` and installation instructions before a new installation. Use the host's Skill installer with repository `pengchujin/jzsub`, path `skills/jzsub`, and a verified commit or release. Record the source revision locally; do not automatically replace a working customized installation or silently track upstream main.

For an existing non-default installation, pass `--jzsub-dir <skill-directory>` or set `JZSUB_SKILL_DIR`. An invalid explicit path is reported as missing, not replaced by a guessed installation.

If JZSub is absent, URL acquisition is unavailable; existing local videos or user-provided subtitles can still use their applicable stages. Do not request Cookie/Token values. Do not auto-install dependencies during a read-only review.

## Shared MLX Whisper runtime

VBS looks for `VBS_RUNTIME_CONFIG`, then `~/.config/vbs/runtime.json`. This lets every local Codex conversation use one isolated Python and MLX Whisper environment without changing the system Python or relying on a previous job directory. When the default `python3` is older than 3.10, use the configured `python_executable` for VBS helper scripts as well as ASR.

The configuration schema is:

```json
{
  "schema_version": 1,
  "python_executable": "~/.local/share/vbs/.venv/bin/python",
  "python_version": "3.12",
  "mlx_whisper_cli": "~/.local/share/vbs/.venv/bin/mlx_whisper",
  "mlx_whisper_version": "0.4.3",
  "model_id": "mlx-community/whisper-large-v3-turbo",
  "model_revision": "replace-with-the-verified-commit",
  "model_path": "~/.local/share/vbs/models/whisper-large-v3-turbo",
  "weights_bytes": 0,
  "weights_sha256": "replace-with-the-verified-sha256",
  "hf_home": "~/.local/share/vbs/huggingface"
}
```

Paths may contain `~`; the runtime expands them locally. Keep machine-specific configuration outside the public repository.

Check the shared environment:

```bash
python3 <skill-dir>/scripts/run_asr.py --check
python3 <skill-dir>/scripts/run_asr.py --check --deep-check
python3 <skill-dir>/scripts/check_dependencies.py --require asr
```

Run transcription through the shared environment:

```bash
python3 <skill-dir>/scripts/run_asr.py audio.wav \
  --language en --output-format srt --output-dir output
```

`run_asr.py` injects the configured local model unless the caller explicitly supplies `--model`. The normal check validates the recorded weight size; `--deep-check` also hashes the complete weight file. It fails before transcription when the configuration, Python version, package version, CLI, or required model files do not match, and prints specific repair guidance. Availability checks do not replace a real audio transcription test.
