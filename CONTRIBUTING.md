# Contributing

欢迎提交问题报告、字幕工作流案例和改进建议。

## 提交修改前

1. 不得在测试数据、日志或提交中包含视频平台 Cookie、Token、密码、私钥或个人字幕素材。
2. 保留三个强制人工审核停点，除非变更明确增强而不是绕过人工确认。
3. 新增或修改脚本时仅使用必要依赖，并补充能够验证实际行为的测试。
4. 修改 Skill 后运行：

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/vbs
```

## 问题报告建议内容

- 输入类型：本地文件或链接；
- 字幕来源：人工、平台自动或无字幕；
- 采用路线：`jzsub-source`、`hybrid-audit` 或 `whisper-asr`；
- 实际停留阶段；
- 已脱敏的错误信息和最小复现步骤。

不要上传无权公开的视频、音频、字幕或账号信息。
