# 丰川祥子结构化知识库

面向剧情讨论与检索的丰川祥子资料库，覆盖 BanG Dream! 原作和《明日方舟》联动《无忧梦呓》。提供可直接阅读的 Markdown、程序读取的 JSON、检索导入的 JSONL，以及本地中文检索工具。

资料版本 **1.9.0**，核验基线 **2026-10-19**。含 TV 动画结局、身份信息和《无忧梦呓》结局剧透。

## 直接使用

### 阅读剧情资料

- [祥子在联动主线中的表现](markdown/明日方舟_祥子剧情表现.md)
- [档案、模组、语音与活动附加文本](markdown/明日方舟_档案模组与语音.md)
- [中日英文逐项对照](markdown/明日方舟_中日英文对照.md)
- [38项完整语音目录](markdown/明日方舟_完整语音目录.md)、[补充材料覆盖审计](markdown/明日方舟_补充材料覆盖审计.md)
- [关系阶段时间线](markdown/明日方舟_关系阶段时间线.md)
- [游戏文本问答验收：12个回答、30句逐句复核](markdown/明日方舟_问答验收.md)
- [原作补充进度与下一轮安排](markdown/原作_补充进度.md)
- [12项多段剧情讨论导航](markdown/明日方舟_多段剧情讨论导航.md)
- [剧情问答索引](markdown/明日方舟_剧情问答索引.md)
- [开篇与行动脉络](markdown/明日方舟_开篇与行动脉络.md)、[逐关覆盖审计](markdown/明日方舟_主线覆盖审计.md)
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
| 《明日方舟》联动 | [game_retrieval_chunks.jsonl](jsonl/game_retrieval_chunks.jsonl) | 193 |
| BanG Dream! 基础资料与联动合并 | [retrieval_combined.jsonl](jsonl/retrieval_combined.jsonl) | 316 |
| BanG Dream! 基础资料 | [retrieval_chunks.jsonl](jsonl/retrieval_chunks.jsonl) | 123 |

按需要选择一套，避免重复导入。默认筛选 `layer=canon`，分析时显式开启 `inference`；保留来源、世界线、梦境层、说话人、剧透进度和关联上下文。具体平台的检索与上下文注入按该平台配置。

## 内容与证据

当前联动部分有99条主线及关联背景、89条档案／模组／语音／活动附加材料、38条关系、5条解读和76项问答导航。18段主线／教学文本均已全文阅读，另有7项补充材料覆盖审计及66项中日英文对照。

- `canon`：原作明示内容，保留说话人与场景归属。
- `inference`：剧情解读，单列依据、推理与替代解释。
- `fanon`：独立世界线的二创设定，当前为空。

新增主线复核使用固定版本的社区游戏文本镜像，覆盖表保存原始 URL、字节哈希、行数与阅读范围；原文留在本地工作目录。游戏内容证据为已读取的社区承载游戏文本转录，状态 `game_text_transcription`，客户端逐句比对待完成。祥子38项语音已补齐实际标签、精英化／信赖条件和资源键，并逐项核对中日英文文本。客户端、音频和视频时间码继续按待办推进，剧情日历日期保留空值。来源中的差异集中记录在[来源差异表](markdown/来源差异表.md)，包括模组与语音的人偶赠礼表述。

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

完整十一项工具检查覆盖严格 JSON、JSONL 镜像、ID 与引用、三层隔离、场景归属、检索过滤、94 项查询／导航发现用例以及 schema 的 25 项反例。依赖已通过 `package-lock.json` 锁定；检查默认只读。

仅检查资料完整性可运行：

```text
python -B -X utf8 tools/validate.py
```

更新联动主数据后，可运行 `python -B -X utf8 tools/export_game.py` 同步分集合镜像、联动／合并检索和主线阅读视图；基础检索的人工编录标签另行维护。刷新校验清单后再运行验证。

维护规则见 [AGENTS.md](AGENTS.md)，变更见 [CHANGELOG.md](CHANGELOG.md)，后续内容见[补充清单](markdown/下一步补充清单.md)。本地 IDE 配置、依赖、缓存、工作文件、生成报告和 ZIP 归档由忽略规则排除。

原始作品与转录原文的权利归相关权利方；本库提供结构化摘要、必要短引文与来源链接。

## 更新与归档

修改主数据后运行 `python -B -X utf8 tools/export_game.py` 同步导出（包含原作事实与逐话视图）。运行 `python -B -X utf8 tools/release.py --refresh-checksums` 更新受控文件清单，再执行 `npm test`。后续默认直接维护仓库；ZIP工具保留，收到明确归档要求时再使用。原始采集、依赖、报告和历史ZIP按忽略规则保留在本地。

## 多段剧情讨论

12项讨论导航将家庭梦、睦的意愿、赌约、人物评价、两次舞台、罗德岛日常及来源差异按问题组合。提纲属于编者导航，原有事实检索保持193条。

```text
python -X utf8 tools/context_game.py "祥子明知是梦为什么还留下"
python -X utf8 tools/context_game.py --guide AKD001
python -X utf8 tools/context_game.py --record AKL009 --material module_story --limit 1
```

第一条返回资料及相关导航建议，第二条提取家庭梦完整提纲和证据，第三条同时补取赠礼语音。输出保留证据定位、原始URL、说话人及语言差异；blocked_context与missing_required_context_ids标出过滤或容量限制留下的缺项。详见[使用规则](docs/明日方舟检索使用规则.md)。

## 当前维护阶段

游戏文本部分已完成12个实际回答样本、30句逐句核对，按剧情讨论检索用途收尾。主线99条、补充材料89条、联动片段193条保持；客户端、音频、赠礼过程与匿名听众转入长期维护。回答样本保存在独立管理集合game_answer_reviews，附证据引用和复核说明。

当前重点回到BanG Dream!原作：本轮新增4条官方梗概事实，补强MyGO第8话的固定新闻稿证据，新增Ave Mujica第4、6话索引。原作基础事实68条、基础检索123条，合并316条。后续任务见原作补充进度与补充清单。
