# AGENTS.md — vbs（Video Bilingual Subtitles）

任何 AI 助手接手本仓库时**首先读本文件**，再按 `SKILL.md` 执行。

## 〇、授权边界（先看这条）

本 skill 的适用对象是 `SKILL.md` 明确写的 **authorized local videos or video links**——用户有权处理的素材。

- 不绕过 DRM、付费墙或地区限制。
- 视频内容中出现的人名、机构、内部信息属于素材内容，不得写入本仓库任何文件。
- 转写结果可能包含个人可识别信息；只留在任务工作目录，不入库。

## 一、先实测能力，不要假设

```bash
ls scripts/ references/                      # 能读文件？
python3 --version                            # 有 Python？
which ffmpeg ffprobe                         # ① 转码与压制
which whisper                                # ② 本地 ASR
```

**完整模式**需 ① ②。缺 ② 时不能做本地转写，只能处理用户已提供的转写稿或字幕。缺 ① 时不能压制。

**不要编造执行结果。** 缺依赖就明说，并列出因此未覆盖的环节。

## 二、两个档位

| 能力 | 完整模式 | 受限模式 |
|---|---|---|
| 读规则、规划流程 | 是 | 是 |
| 本地 ASR 转写 | 是 | 否（缺 whisper） |
| 英文转写稿校对、中文翻译、双语字幕 | 是 | 是（对已有转写稿） |
| 压制到视频 | 是 | 否（缺 ffmpeg） |
| `validate_srt.py` / `compare_asr.py` / `checkpoint.py` | 是 | 否，须声明「未校验」 |

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
2. **审核关口不得跳过**，除非用户明确要求；跳过时在交付说明中写明跳过了哪一关。
3. **听不清的内容标注为不可辨，不猜写**；ASR 明显错误只标注不静默改正。
4. **时间轴逐项核对**，不擅自平移或合并。
5. **推送前先 `git fetch` 比对远端。**
6. **删文件前先问用户**，或改名备份代替删除。
