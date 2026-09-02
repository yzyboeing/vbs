# Routing and ASR

## Decision order

1. Inspect the input before choosing a method.
2. Use a matching user-supplied or manual English subtitle as the source.
3. If only platform automatic English captions exist, preserve them and use the hybrid audit route when practical.
4. If no usable English captions exist, download or retain the source master and run Whisper.

For local files, inspect subtitle streams, audio streams, duration, frame rate, dimensions, HDR/color metadata, and codecs with `ffprobe`. Extract an embedded English track without changing its bytes when possible; otherwise retain both the raw extraction and the converted review SRT.

For links, use JZSub to probe and acquire the best source. Public links are tried anonymously first. Browser authentication may be used only when access is authorized; Cookie contents must never be exported, displayed, logged, or placed in a job artifact.

## Whisper quality strategy

Use a local Apple-Silicon implementation such as MLX Whisper on compatible Macs; otherwise choose an available accurate Whisper implementation. Prefer a high-accuracy model for technical material when time, memory, and disk permit. Record the exact implementation, model, language option, and meaningful decoding settings.

Prepare a lossless 16 kHz mono analysis WAV while preserving the source audio unchanged. Check mean/peak level and silence regions; normalization or voice isolation is optional and must produce a separate derivative rather than replace the master.

Run two passes when feasible:

- Pass A: stable sentence/segment transcription without forced word timestamps.
- Pass B: word timestamps or meaningfully different decoding settings for timing and omission detection.

A domain glossary may bias one pass, but never both. Treat glossary-induced text as suspect until supported by the audio or the independent pass. Avoid promoting an initial prompt into transcript text. For long videos, chunk at silence boundaries with overlap and reconcile the overlap before producing the review SRT.

Compare passes:

```bash
python3 <skill-dir>/scripts/compare_asr.py pass-a.srt pass-b.srt \
  --json-report asr-differences.json > english-review-notes.tsv
```

Manually inspect every non-equal difference that could change meaning, especially:

- missing or repeated short words;
- negatives, modality, quantities, units, decimal points, percentages, and engine/aircraft identifiers;
- acronyms spoken as letters or sounds, such as N1 and FCOM;
- proper names and specialized terms;
- speech adjacent to music, cuts, silence, or the end of the file;
- implausibly long gaps inside detected speech and captions continuing after speech ends.

The English review SRT is a clean candidate, not a raw model dump. Put uncertainty in `english-review-notes.tsv` with timestamp, alternatives, reason, and recommended user check. Do not insert bracketed guesses into the subtitle unless the user asks.

## Route changes

Change from JZSub to Whisper when the caption track is absent, wrong-language, machine-translated, clearly incomplete, badly desynchronized, or rejected by the user. Keep the rejected source unchanged for audit.

Change from Whisper to a manual source only after verifying that it matches the same video edit and duration. A subtitle from another cut is not authoritative merely because its text is better.
