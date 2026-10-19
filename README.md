# 丰川祥子结构化知识库

面向剧情讨论与检索的丰川祥子资料库，覆盖 BanG Dream! 原作和《明日方舟》联动《无忧梦呓》。提供可直接阅读的 Markdown、程序读取的 JSON、检索导入的 JSONL，以及本地中文检索工具。

资料版本 **1.4.0**，核验基线 **2026-10-19**。含 TV 动画结局、身份信息和《无忧梦呓》结局剧透。

## 直接使用

### 阅读剧情资料

- [祥子在联动主线中的表现](markdown/明日方舟_祥子剧情表现.md)
- [档案、模组与语音](markdown/明日方舟_档案模组与语音.md)
- [剧情问答索引](markdown/明日方舟_剧情问答索引.md)
- [关系与自我认识](markdown/明日方舟_关系与自我认识.md)
- [基础事实](markdown/基础事实库.md)、[人物关系](markdown/人物关系库.md)、[时间线](markdown/时间线.md)

这些文件可在 GitHub 上直接阅读，也可下载仓库后离线使用。

### 本地检索

准备 Python 3.9 或更新版本，无需安装 Python 第三方依赖。在仓库目录运行：

```text
python -X utf8 tools/search_game.py "她为什么不马上带睦离开"
python -X utf8 tools/search_game.py "祥子在罗德岛做什么" --material operator_file
python -X utf8 tools/search_game.py "匿名听众" --material module_story
python -X utf8 tools/search_game.py "她怎样向博士学习" --material voice
python -X utf8 tools/search_game.py "尊重睦的意愿" --include-inference
python -X utf8 tools/search_game.py "母亲" --max-stage SS-7-END
```

按系统环境，也可将 `python` 换成 `python3` 或 `py -3`。结果为 JSON，包含命中内容、记录 ID、材料类型、剧情进度及来源。本地工具使用关键词和中文双字片段排序。

### 导入聊天知识库或检索系统

| 使用范围 | 导入文件 | 片段数 |
| --- | --- | ---: |
| 《明日方舟》联动 | [game_retrieval_chunks.jsonl](jsonl/game_retrieval_chunks.jsonl) | 83 |
| BanG Dream! 基础资料与联动合并 | [retrieval_combined.jsonl](jsonl/retrieval_combined.jsonl) | 202 |
| BanG Dream! 基础资料 | [retrieval_chunks.jsonl](jsonl/retrieval_chunks.jsonl) | 119 |

按需要选择一套，避免重复导入。默认筛选 `layer=canon`，分析时显式开启 `inference`；保留来源、世界线、梦境层、说话人、剧透进度和关联上下文。具体平台的检索与上下文注入按该平台配置。

## 内容与证据

当前联动部分有 58 条主线场景、20 条档案／晋升／模组／语音材料、15 条场景关系、5 条解读和 30 项问答导航。

- `canon`：原作明示内容，保留说话人与场景归属。
- `inference`：剧情解读，单列依据、推理与替代解释。
- `fanon`：独立世界线的二创设定，当前为空。

游戏内容证据为已读取的社区承载游戏文本转录，状态 `game_text_transcription`，客户端逐句比对待完成。语音触发标签、剧情日历日期和视频时间码按核验进度保留空值。来源中的差异集中记录在[来源差异表](markdown/来源差异表.md)，包括模组与语音的人偶赠礼表述。

详见[覆盖与来源](markdown/明日方舟_覆盖与来源.md)、[字段字典](docs/字段字典.md)、[联动检索规则](docs/明日方舟检索使用规则.md)和[检索与导入](docs/检索与导入.md)。

## 目录

| 目录或文件 | 用途 |
| --- | --- |
| `data/` | 总库 `kb.json`、分集合 JSON、派生检索片段 |
| `jsonl/` | 与 JSON 对应的导入文件 |
| `markdown/` | 可阅读的事实、关系、剧情和来源文档 |
| `schema/` | Draft-07 JSON Schema |
| `docs/` | 编录、核验、字段及使用规则 |
| `tools/` | 检索与验证工具 |
| `AGENTS.md` | 维护说明和后续工作交接 |
| `SHA256SUMS.txt` | 仓库交付文件的 SHA-256 校验清单 |

## 维护与验证

普通阅读、导入和本地检索只需上面的文件或 Python。维护者执行完整验证时，另需 Node.js 和 npm：

```text
npm ci
npm test
```

完整检查覆盖严格 JSON、JSONL 镜像、ID 与引用、三层隔离、场景归属、检索过滤、24 项中文查询以及 schema 的 11 项反例。依赖已通过 `package-lock.json` 锁定；检查默认只读。

仅检查资料完整性可运行：

```text
python -B -X utf8 tools/validate.py
```

维护规则见 [AGENTS.md](AGENTS.md)，变更见 [CHANGELOG.md](CHANGELOG.md)，后续内容见[补充清单](markdown/下一步补充清单.md)。本地 IDE 配置、依赖、缓存、工作文件、生成报告和 ZIP 归档由忽略规则排除。

原始作品与转录原文的权利归相关权利方；本库提供结构化摘要、必要短引文与来源链接。
