# 2026-09-05 — Dependency portability

- Add stage-specific dependency discovery, upstream JZSub installation guidance and failure tests.
- Preserve artifact review gates; missing ASR does not block text-only checks or approved-subtitle burning.

# Changelog

## Unreleased

- 英文审核前按完整句或自足语义单元重分段，禁止把孤立残词或未完成短语留到下一画面；视觉换行不再等同于时间轴切分。
- `[REVIEW]` 文件名默认承担审片标记，不再默认烧录可见水印；若审片版确有可见水印，最终版必须从源片移除水印后重渲染并重复媒体 QA。
- 最终渲染以源视频时间戳和帧数为基准，避免稀疏字幕图层因 shortest-stream 规则截掉尾帧；检查点新增 `--from review` 与 `--from final` 精确回退。
- 新增任务后受控复盘：任务交付后主动把经实际产物、用户纠正或验证结果证实的通用经验写回 Skill，并排除私密素材、个案数据和未经验证的猜测；提交、推送与发布仍需单独授权。
- 支持通过 `VBS_RUNTIME_CONFIG` 或 `~/.config/vbs/runtime.json` 自动发现跨对话共享的 MLX Whisper 环境。
- 新增 `run_asr.py`，在转写前核验 Python、MLX Whisper、命令行和本地模型，并自动使用已配置模型。
- 依赖检查现在会报告当前解释器与共享 ASR 环境的独立状态和明确故障原因。
- 锁定 MLX Whisper 运行时依赖为 `0.4.3`，并增加共享运行时回归测试。
- 将 GitHub Actions 更新到 Node.js 24 兼容的 `actions/checkout@v7` 和 `actions/setup-python@v7`。

## 0.1.1 — 2026-09-05

- 收紧两处审核关口的「批准」定义：**收到修正文件本身不再视为批准**。继续执行需要用户明确批准该具体版本，或提供修正文件并明确指示按该版本继续。
- 批准绑定到具体文件版本；版本未变化时不重复请求批准。
- 新增 `skills/vbs/AGENTS.md`：AI 助手入口，含授权边界、经实机验证的能力自检命令、完整／受限档位对照、规则真源与仓库红线。

## 0.1.0 — 2026-09-02

- 首次公开版本。
- 支持 JZSub、Whisper 和混合审计三种输入路线。
- 增加英文、双语和 REVIEW 成片三个人工审核停点。
- 增加批准件哈希锁定和下游失效机制。
- 增加 SRT 结构校验与双次 ASR 差异检测工具。
- 明确感谢 JZSub 项目。
