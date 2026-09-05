# AGENTS.md — vbs（Video Bilingual Subtitles）

任何 AI 助手接手本仓库时**首先读本文件**，再按 `SKILL.md` 执行。

## 〇、授权边界（先看这条）

本 skill 的适用对象是 `SKILL.md` 明确写的 **authorized local videos or video links**——用户有权处理的素材。

- 不绕过 DRM、付费墙或地区限制。
- 视频内容中出现的人名、机构、内部信息属于素材内容，不得写入本仓库任何文件。
- 转写结果可能包含个人可识别信息；只留在任务工作目录，不入库。

## 一、按阶段实测能力

按 [依赖说明](references/dependencies.md) 运行 `python3 scripts/check_dependencies.py`。文本检查依赖 Python；链接获取依赖 JZSub、yt-dlp 和媒体工具；ASR 接受可用的 Whisper 实现；压制另验 FFmpeg、libass 与字体。缺少一种能力只阻断相关阶段。

## 二、结果边界

依赖被发现不等于执行成功。需实际执行相应脚本、转写或渲染才能报告通过；没有 Whisper 仍可以检查现有字幕，没有 FFmpeg 仍可以运行不涉及视频的文本检查。审核批准绑定具体文件版本，按 SKILL.md 执行。

## 三、规则真源

`SKILL.md` 为主流程；`references/routing-and-asr.md` 定 ASR 路由，`references/translation-and-rendering.md` 定翻译与渲染，`references/checkpoints-and-artifacts.md` 定审核关口与产物。冲突时以 `SKILL.md` 为准。

**本 skill 是 review-gated 的**：审核关口写在 `checkpoints-and-artifacts.md` 里，不得为赶进度跳过。

## 四、通用工作约定（本仓库适用部分）

1. **前提审查**——回答前先检查未经证实的前提、逻辑跳跃、关键信息缺失、概念混淆、把推测当事实。有问题先指出，不沿错误前提往下推。
2. **区分四类陈述**——已确认事实／合理推测／建议／无法核实。无法核实就说无法核实，不猜、不编。
4. **尊重停止点**——用户明确设定的停止点必须遵守；未指定时正常做完，不自己发明审批关口。
5. **不重复询问**——本次任务已确认的范围与选择，在输入未变化时持续有效。
9. **不编造执行结果**——没跑的命令就说没跑。工具缺失时明确声明未执行，并列出因此未覆盖的项。
10. **风险照说**——即使用户明确接受风险，仍要说明服务条款、法律与账号边界。

> 以上采用 `AGENTS-common.md` 的第 1、2、4、5、9、10 条。规范版本见公开仓库 `flight-notes-toolkit/prompt/AGENTS-common.md`（raw：`https://raw.githubusercontent.com/yzyboeing/flight-notes-toolkit/main/prompt/AGENTS-common.md`）。本节是按本仓库裁剪的副本——**条目编号固定**，从上面这行就能看出哪几条被省略了。

## 五、本仓库红线

1. **授权边界**——见第〇节。
2. **审核关口按 SKILL.md 执行**；一般性的“全部完成”不代表批准尚未看到的字幕或成片。
3. **听不清的内容标注为不可辨，不猜写**；ASR 明显错误只标注不静默改正。
4. **时间轴逐项核对**，不擅自平移或合并。
5. **推送前先 `git fetch` 比对远端。**
6. **删文件前先问用户**，或改名备份代替删除。
