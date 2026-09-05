# Changelog

## [0.1.1] - 2026-09-05

### Changed
- Tightened the approval semantics at both review gates: receiving a corrected
  file alone no longer counts as approval. Continuation now requires the user's
  explicit approval of the exact version, or a corrected replacement that the
  user explicitly designates for continuation. Approval binds to the exact
  artifact version; unchanged approved versions do not require repeated approval.
  (`skills/vbs/SKILL.md`, `skills/vbs/references/checkpoints-and-artifacts.md`)

### Added
- `skills/vbs/AGENTS.md` — entry point for AI assistants: authorization
  boundary, capability self-check with commands verified on a real machine,
  full vs. limited tier matrix, rule sources, and repository red lines.

## 0.1.0 — 2026-09-02

- 首次公开版本。
- 支持 JZSub、Whisper 和混合审计三种输入路线。
- 增加英文、双语和 REVIEW 成片三个人工审核停点。
- 增加批准件哈希锁定和下游失效机制。
- 增加 SRT 结构校验与双次 ASR 差异检测工具。
- 明确感谢 JZSub 项目。
