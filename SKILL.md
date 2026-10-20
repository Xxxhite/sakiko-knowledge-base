---
name: sakiko-knowledge-base
description: 检索丰川祥子（豊川祥子／Togawa Sakiko）在 BanG Dream! MyGO!!!!!、Ave Mujica 原作及《明日方舟》联动《无忧梦呓》中的剧情、台词语境、人物关系和来源。讨论祥子的行动、动机、关系变化或跨作品表现时使用，区分 canon、inference、fanon；也支持用户明确要求的本库维护。
---

# 丰川祥子剧情知识库

使用随Skill提供的结构化资料回答问题，以记录、场景和原始来源支持回答。范围和版本见[README](README.md)，缺口见[原作进度](markdown/原作_补充进度.md)。普通问答从下表选择入口；维护本库时再读AGENTS.md。

## 定位资料并检索

以本文件所在目录为Skill根目录。下列命令在该目录运行；从其他目录调用时使用工具的绝对路径。工具按自身位置读取data/，检索仅依赖Python标准库。在知识库Git仓库维护时，以当前仓库的SKILL.md和data/为准。安装副本是独立快照，版本比较与刷新见[安装与更新](docs/Skill安装与更新.md)。

| 问题范围 | 入口 | 按需阅读 |
| --- | --- | --- |
| MyGO、Ave 原作行动、对白、关系 | `tools/search_base.py` | [问答导航](markdown/原作_剧情问答索引.md)、[实际回答](markdown/原作_问答验收.md)、[逐话索引](markdown/后段逐话索引.md) |
| 《无忧梦呓》场景、档案或语音 | `tools/search_game.py` | [游戏问答](markdown/明日方舟_剧情问答索引.md) |
| 联动动机、成长、多场景比较、来源差异 | `tools/context_game.py` | [联动检索规则](docs/明日方舟检索使用规则.md) |
| 原作与联动比较 | 分别运行原作、游戏入口 | 按世界线分别引用 |

```text
python -B -X utf8 tools/search_base.py "Ave第一话父亲向祥子扔了东西吗"
python -B -X utf8 tools/search_base.py "第三话睦深层世界持伞的画面" --phase ave_ep03
python -B -X utf8 tools/search_base.py "睦是唯一知道祥子境遇的人是谁的推测" --include-inference
python -B -X utf8 tools/search_game.py "她怎样向博士学习" --material voice
python -B -X utf8 tools/context_game.py "祥子为什么没有立刻带睦离开"
python -B -X utf8 tools/context_game.py --record AKL009 --material module_story --limit 1
```

原作可用 `--phase mygo_ep08`、`--phase ave_ep07` 区分同号话数；游戏可用 `--max-stage SS-7-END` 控制进度。原作有整体剧透，按用户已看范围选择 phase 并核对返回记录的剧情阶段。

先检索相关片段，再读关联记录。结果较弱时换用别名、明确行动或关卡关键词，并按 record_id 查主记录。关键词命中用于发现资料，逐条检查是否回答当前问题；按需读取分集合 JSON，避免一次载入整个总库。

## 回答与证据

- 默认只取 **canon**。分析动机时显式加入 **inference**，保留解读者、依据与推测强度。**fanon**当前为空，用户自定设定按独立世界线处理。问答样本是已复核的组织示例，引用仍指向正文记录与证据。
- 先回答谁在什么场景做了什么、向谁说了什么，再按问题解释变化。对其他角色的指责、猜测、计划和评价保留说话人。
- 引用给记录 ID、作品及集数／关卡、场景定位和原始 URL。结果中的 citations 或 evidence_ids 可回溯到 [证据](data/evidence.json) 和 [来源](data/sources.json)。
- `official_explicit` 为官方明示，`primary_interview_explicit` 为署名主创／声优对已播事件的明确复述；个人解释在 inference。`game_text_transcription` 为社区承载的游戏文本转录，保留来源属性。
- `direct_text_verified` 表示已读正文，`indexed_text_verified` 表示只核检索索引；原片、客户端、音频和时间码的复核状态分别按数据填写。需要官方来源时用 `--official-only`；需要已读正文时用 `--direct-only`（原作），并据结果说明覆盖范围。
- 原作`tv_anime`、电影档案`film_profile_snapshot`、联动`arknights_collab`分别使用；联动保留narrative_level，区分家庭梦、队友梦、回放、梦中人物和后续罗德岛。原作如ave_ep03_inner_world，在回答中保留深层世界画面语境。
- 联动片段带 `required_context_record_ids` 或 `source_issue_ids` 时补取上下文。`context_game.py` 会闭合必要关联，检查 `blocked_context` 与 `missing_required_context_ids`。赠礼需并读 AKL009／AKL016，日服晋升新增按 SC005 读取。

缺口集中说明一次，给出当前证据支持的内容及待核项。补充外部资料时核对原始来源，区别已入库记录与本次新查资料；完整原文、候选和导航按各自用途使用。

## 用户要求更新知识库时

先读[AGENTS.md](AGENTS.md)，按主数据、稳定ID、分层和导出验证流程维护。普通剧情问答直接检索并回答；资料更新、安装副本刷新、提交及推送分别按用户授权办理。
