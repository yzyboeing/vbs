# Checkpoints and artifacts

## State order

`ingested` → `english-draft-ready` → `english-approved` → `bilingual-draft-ready` → `bilingual-approved` → `review-burn-ready` → `final-approved` → `delivered`

Initialize once, then record each completed checkpoint:

```bash
python3 <skill-dir>/scripts/checkpoint.py record <job-dir> \
  --stage english-draft-ready \
  --artifact english_review=english-review.srt \
  --artifact review_notes=english-review-notes.tsv
```

Approval checkpoints require a concise note recording the user's explicit approval of the exact version, including a corrected replacement explicitly designated for continuation. Receiving a corrected file alone is not approval; unchanged approved versions do not require repeated approval:

```bash
python3 <skill-dir>/scripts/checkpoint.py record <job-dir> \
  --stage english-approved \
  --artifact english_approved=english-approved.srt \
  --approval-note "User explicitly approved the corrected English SRT."
```

Before continuing in a later turn:

```bash
python3 <skill-dir>/scripts/checkpoint.py status <job-dir>
python3 <skill-dir>/scripts/checkpoint.py verify <job-dir>
```

Review-draft checkpoints are intentionally mutable because the user may edit those files. Approval checkpoints are immutable and hash-enforced. Save an approved file under its distinct `*-approved.srt` name; never point an approval checkpoint at the still-editable review filename.

If an approved upstream artifact changes, do not record a downstream stage. Invalidate first:

```bash
python3 <skill-dir>/scripts/checkpoint.py invalidate <job-dir> --from english
python3 <skill-dir>/scripts/checkpoint.py invalidate <job-dir> --from bilingual
python3 <skill-dir>/scripts/checkpoint.py invalidate <job-dir> --from review
python3 <skill-dir>/scripts/checkpoint.py invalidate <job-dir> --from final
```

English invalidation returns the job to `english-draft-ready` and removes every later checkpoint. Bilingual invalidation returns it to `bilingual-draft-ready` while retaining the approved English checkpoint. Review invalidation returns to `bilingual-approved` when the burned review must be rebuilt. Final invalidation returns to `final-approved` when a delivered file fails final verification but the approved review remains valid.

## Required names

Use stable names so the user and a resumed agent can distinguish drafts from approved inputs:

- `english-source-original.<ext>` — immutable downloaded, embedded, or supplied source
- `english-review.srt` — editable English draft
- `english-transcript.txt`
- `english-review-notes.tsv`
- `english-approved.srt` — exact approved English authority
- `chinese-review.srt`
- `bilingual-review.srt`
- `bilingual-transcript.txt`
- `translation-review-notes.tsv`
- `chinese-approved.srt`
- `bilingual-approved.srt`
- `<title> [REVIEW] bilingual.mp4`
- `burn-qa-report.json`
- `<title> bilingual FINAL.mp4`

Do not overwrite an approved artifact in place. If a correction arrives, save the new review artifact, invalidate the affected checkpoint, and record approval again after the user confirms it.
