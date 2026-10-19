---
name: sakiko-knowledge-base
description: 检索丰川祥子（豊川祥子／Togawa Sakiko）在 BanG Dream! MyGO!!!!!、Ave Mujica 原作及《明日方舟》联动《无忧梦呓》中的剧情、台词语境、人物关系和证据来源。讨论祥子的行动、动机、关系变化或跨作品表现时使用；区分 canon、inference、fanon。
---

# 丰川祥子剧情知识库

使用随 Skill 安装的结构化资料回答剧情问题，以记录、场景和原始来源支持回答。当前范围和版本见 [README](README.md)，具体缺口见 [补充进度](markdown/原作_补充进度.md)。

## 定位资料并检索

以本文件所在目录为 Skill 根目录。下列命令在该目录运行；从其他目录调用时使用工具的绝对路径。工具以自身位置定位 data/，无需把当前项目设为知识库仓库。Python 3.9 及以上即可检索，无需 Python 第三方依赖。

| 问题范围 | 入口 | 按需阅读 |
| --- | --- | --- |
| MyGO、Ave 原作行动、对白、关系 | `tools/search_base.py` | [原作问答](markdown/原作_剧情问答索引.md)、[逐话索引](markdown/后段逐话索引.md) |
| 《无忧梦呓》场景、档案或语音 | `tools/search_game.py` | [游戏问答](markdown/明日方舟_剧情问答索引.md) |
| 联动动机、成长、多场景比较、来源差异 | `tools/context_game.py` | [联动检索规则](docs/明日方舟检索使用规则.md) |
| 原作与联动比较 | 分别运行原作、游戏入口 | 按世界线分别引用 |

```text
python -B -X utf8 tools/search_base.py "第8话祥子向爽世的最后通告"
python -B -X utf8 tools/search_base.py "监督如何理解旧团重聚和告别" --include-inference
python -B -X utf8 tools/search_game.py "她怎样向博士学习" --material voice
python -B -X utf8 tools/context_game.py "祥子为什么没有立刻带睦离开"
python -B -X utf8 tools/context_game.py --record AKL009 --material module_story --limit 1
```

原作可用 `--phase mygo_ep08`、`--phase ave_ep07` 区分同号话数；游戏可用 `--max-stage SS-7-END` 控制进度。原作有整体剧透，按用户已看范围选择 phase 并核对返回记录的剧情阶段。

先检索相关片段，再读关联记录。结果较弱时换用别名、明确行动或关卡关键词，并按 record_id 查主记录。关键词命中用于发现资料，逐条检查是否回答当前问题；按需读取分集合 JSON，避免一次载入整个总库。

## 回答与证据

- 默认只取 **canon**。分析动机时显式加入 **inference**，保留编者或受访者姓名、推测语气和依据。**fanon** 当前为空，用户自定设定按独立世界线处理。
- 先回答谁在什么场景做了什么、向谁说了什么，再按问题解释变化。对其他角色的指责、猜测、计划和评价保留说话人。
- 引用给记录 ID、作品及集数／关卡、场景定位和原始 URL。结果中的 citations 或 evidence_ids 可回溯到 [证据](data/evidence.json) 和 [来源](data/sources.json)。
- `official_explicit` 为官方明示，`primary_interview_explicit` 为署名主创／声优对已播事件的明确复述；个人解释在 inference。`game_text_transcription` 为社区承载的游戏文本转录，保留来源属性。
- `direct_text_verified` 表示已读正文，`indexed_text_verified` 表示只核检索索引；原片、客户端、音频和时间码的复核状态分别按数据填写。需要官方来源时用 `--official-only`；需要已读正文时用 `--direct-only`（原作），并据结果说明覆盖范围。
- 原作 `tv_anime`、电影档案 `film_profile_snapshot`、联动 `arknights_collab` 分别使用；联动保留 narrative_level，区分家庭梦、队友梦、回放、梦中人物和后续罗德岛。
- 联动片段带 `required_context_record_ids` 或 `source_issue_ids` 时补取上下文。`context_game.py` 会闭合必要关联，检查 `blocked_context` 与 `missing_required_context_ids`。赠礼需并读 AKL009／AKL016，日服晋升新增按 SC005 读取。

缺口集中说明一次，给出当前证据支持的内容及待核项。补充外部资料时核对原始来源，区别已入库记录与本次新查资料；完整原文、候选和导航按各自用途使用。

## 用户要求更新知识库时

先读 [AGENTS.md](AGENTS.md)，按主数据、稳定 ID、分层和导出验证流程维护。普通剧情问答直接检索；入库、提交和推送按用户更新请求执行。安装副本是指定版本快照，后续内容维护在 Git 仓库进行，再更新安装版本。
