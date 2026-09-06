---
name: vbs
description: "Create English and bilingual subtitles and burned videos with mandatory English, bilingual, and review-video approval gates. Supports local videos and authorized links."
---

# Video Bilingual Subtitles

Process one authorized, decodable video per job directory. Reuse JZSub for links and trustworthy source captions; use Whisper when no usable English captions exist. Never claim that every video is supported: do not bypass DRM, paywalls, CAPTCHAs, safety interstitials, unsupported codecs, or missing access.

## Non-negotiable review gates

Treat this as a staged workflow even when the user initially requests an end-to-end result. A request to complete the whole job is not approval of unseen subtitles.

1. Deliver the English review package and stop. Do not translate or burn.
2. Continue only after the user explicitly approves the English SRT or supplies a corrected replacement with an explicit instruction to continue with that version.
3. Deliver the Chinese and bilingual review package and stop. Do not burn.
4. Continue only after the user explicitly approves the bilingual subtitles or supplies corrected replacements with an explicit instruction to continue with those versions.
5. Deliver a `[REVIEW]` burned video and the QA report, then stop.
6. Export the unmarked final video only after the user explicitly approves that review video.

If the user changes approved English, invalidate every translation and video derived from it. If the user changes approved Chinese, invalidate every rendered or burned video derived from it. Never infer approval from silence, general praise, or a request that still mentions unresolved errors.

Receiving a corrected file alone is not approval. If the user explicitly says to continue with that version, record approval without asking again. Approval binds to the exact artifact version; unchanged approved versions do not require repeated approval.

Use `scripts/checkpoint.py` for every job so approval state and artifact hashes survive across turns. Start each resumed turn with `checkpoint.py status` and `checkpoint.py verify`.

## Stage 0 — Ingest and select the route

Read [dependencies](references/dependencies.md) and run `scripts/check_dependencies.py`. Check only the stages required by the selected route. Prefer the shared Python and ASR runtime discovered from `VBS_RUNTIME_CONFIG` or `~/.config/vbs/runtime.json` when the default `python3` is older than 3.10 or lacks Whisper. Only for an ASR route, run `scripts/run_asr.py --check`, then use `scripts/run_asr.py` for both Whisper passes. Missing ASR does not block review of provided subtitles or burning approved subtitles.

Create a new empty job directory. Inspect local inputs with `ffprobe`; probe links with the installed JZSub fetcher before downloading when practical. Confirm the audio language when detection is ambiguous. If the audio is not English, ask whether the user still wants an English translation transcript; do not mislabel non-English ASR as an English transcript.

Choose and report one route:

- `jzsub-source`: a manual English caption track or user-supplied English subtitle is available and matches the video.
- `hybrid-audit`: only automatic/platform English captions are available; extract them unchanged, then audit them against Whisper when feasible.
- `whisper-asr`: no usable English captions exist, or the user explicitly requests a fresh transcription.

Prefer manual original-language captions over automatic captions. Do not choose a translated platform track as the English source. For URL acquisition, use the installed JZSub scripts and keep Cookie access local and silent. The review gates in this Skill override JZSub's default instruction to continue through translation and burning.

Read [references/routing-and-asr.md](references/routing-and-asr.md) when selecting or running an ASR route.

Initialize state:

```bash
python3 <skill-dir>/scripts/checkpoint.py init <job-dir> \
  --source "<local-path-or-url>" --route <route>
```

## Stage 1 — English review package

Preserve downloaded or embedded source captions byte-for-byte as `english-source-original.*`. Never overwrite them. Create a separate, editable `english-review.srt`.

For Whisper, use at least two independently decoded passes when resources permit. One pass must prioritize stable segment transcription; the other must provide timing or alternate decoding. Do not combine a terminology prompt with the only timing pass. Compare the passes with `scripts/compare_asr.py` and inspect suspected insertions, deletions, replacements, long speech gaps, low-confidence words, numerals, acronyms, names, and the beginning and end of the audio. Do not silently fill words that were not heard.

Deliver only:

- `english-review.srt`
- `english-transcript.txt`
- `english-review-notes.tsv`
- `english-source-original.*` when one exists
- a short method report stating caption kind or Whisper model, detected language, and unresolved uncertainties

Validate `english-review.srt` with `scripts/validate_srt.py`, record `english-draft-ready`, deliver the package, and stop. After explicit approval of the exact file, including a corrected replacement explicitly designated for continuation, save the exact approved file as `english-approved.srt`, record `english-approved`, and do not edit it in later stages.

Read [references/checkpoints-and-artifacts.md](references/checkpoints-and-artifacts.md) for filenames and approval recording.

## Stage 2 — Chinese and bilingual review package

Use only `english-approved.srt` as semantic and timing authority. Translate with the active session model unless the user explicitly requests another service. Preserve cue count, cue IDs, timestamps, numerals, units, names, URLs, modality, and technical meaning. Do not repair English during translation; return to Stage 1 if an English error is found.

Create and validate:

- `chinese-review.srt`
- `bilingual-review.srt`, with English first and Chinese second in every cue
- `bilingual-transcript.txt`
- `translation-review-notes.tsv` for genuine terminology or meaning uncertainties

Record `bilingual-draft-ready`, deliver the package, and stop. After explicit approval of the exact files, including corrected replacements explicitly designated for continuation, save `chinese-approved.srt` and `bilingual-approved.srt`, validate them, record `bilingual-approved`, and do not edit their text during rendering.

Read [references/translation-and-rendering.md](references/translation-and-rendering.md) before translating aviation or other technical material and before rendering.

## Stage 3 — Review burn and QA

Burn only from the highest-quality source master and `bilingual-approved.srt`. Re-encode video once; copy the original audio when container-compatible. Prefer ASS/libass with an installed validated font. A deterministic transparent-overlay fallback is acceptable when libass is unavailable, but it must preserve both languages, safe margins, and cue timing.

Name this output `<title> [REVIEW] bilingual.mp4`; never give it the final name yet. Run structural subtitle validation, full media decode, `ffprobe` comparison, and representative rendered-frame inspection. Include the first and last cues, the longest cue, multi-line cues, technical numerals, scene changes, and a subtitle-free interval. Check for clipped glyphs, language overlap, unreadable contrast, hidden key content, audio loss, duration drift, and stray captions after speech ends. Warn before processing HDR/Dolby Vision when the compatibility path may not preserve it.

Record `review-burn-ready`, deliver the review video and QA report, and stop.

## Stage 4 — Final delivery

After explicit approval of the review video, record `final-approved`. If no subtitle or rendering change is requested, promote the byte-identical review video to `<title> bilingual FINAL.mp4`; otherwise invalidate the affected checkpoint and repeat the necessary stage. Verify the promoted file matches the QA-approved review video by hash and verify checkpoint integrity; repeat media QA only if content or rendering changed. Record `delivered`, and report actual duration, resolution, frame rate, codecs, subtitle route, caption kind, ASR model when used, authentication use without account details, and remaining verification limits.

Do not describe the video's technical claims as externally validated unless the user separately requested and received source verification.
