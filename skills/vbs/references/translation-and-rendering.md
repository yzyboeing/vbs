# Translation and rendering

## Translation

Translate from complete source sentences while retaining the approved cue timing and cue order. Each bilingual review cue must contain exactly two semantic lines: approved English first, Simplified Chinese second. Do not use surrounding cues to add information absent from the source.

The approved English cue boundary is part of translation quality. Before English approval, replace mechanical chunks with complete sentences or self-contained clauses; avoid orphan words and incomplete phrases that require the next screen to make sense. A long cue may wrap visually without changing its timestamp. If readability requires a timing split, return to English review and split at a natural clause boundary before translation.

For technical material:

- preserve numbers, units, aircraft/engine identifiers, limitations, conditions, warnings, and modality;
- keep established acronyms such as N1 and FCOM when translating them would reduce precision;
- prefer the domain-correct term, but use concise ordinary wording when it does not change the technical meaning;
- record genuinely ambiguous terms and alternatives in `translation-review-notes.tsv` instead of silently guessing;
- do not validate or correct the speaker's technical claim unless separately asked to verify it against authoritative sources.

Chinese subtitle punctuation may be compact, but punctuation removal must not create ambiguity. Do not merge, split, or retime cues during the review translation stage. Rendering may visually wrap a line without changing the SRT text.

## Rendering

Use aspect-ratio-aware styles. Default to a bottom-anchored English-over-Chinese stack with high contrast, outlines, and a bounded translucent background. Inspect the source frames before fixing the placement; move the stack within the safe area if it hides essential instruments, labels, faces, or demonstrations.

Target no more than two visual lines per language. If a cue requires more, return to the bilingual review stage and obtain approval for a new cue split rather than shrinking text until unreadable. Maintain visible margins on landscape, portrait, and square video.

Prefer the highest-quality master and one final video encode. Preserve frame rate, dimensions, aspect ratio, audio channel layout, and audio codec when compatible. Use the source video as the timing authority. With a sparse image overlay, avoid shortest-stream behavior that can stop a few frames early; compare the output video-stream duration and frame count with the source. Do not promise HDR or Dolby Vision preservation through an SDR compatibility encode.

Use the `[REVIEW]` filename as the normal review marker instead of burning a visible watermark. If a visible watermark is required, its later removal creates a new render: rebuild the final from the source master and approved subtitles and repeat media and visual QA.

## Burn QA

Required automated checks:

- approved artifact hashes still match the workflow manifest;
- cue indices and times are valid, ordered, non-overlapping, and within video duration;
- bilingual cues contain both languages;
- output duration, dimensions, frame rate, audio presence, and expected codecs are confirmed with `ffprobe`;
- the complete output decodes without FFmpeg errors.

Required visual checks use rendered frames, not only metadata. Inspect first and last captions, the longest cue, multi-line cues, numbers/acronyms, different scene types, a cue boundary, and a subtitle-free interval. Reject clipped glyphs, overlap, bad wrapping, unreadable contrast, captions outside the safe area, obvious desynchronization, and lingering text after cue end.
