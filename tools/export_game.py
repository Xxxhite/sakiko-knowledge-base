"""Export collection mirrors, game retrieval and game reading views from kb.json.

The base retrieval_chunks file retains its separately curated indexing metadata.
Run this tool after editing kb.json; refresh SHA256SUMS.txt before validation.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def unique(values):
    return list(dict.fromkeys(values))


def save(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def main():
    kb = json.loads((ROOT / 'data/kb.json').read_text(encoding='utf-8'))
    evidence = {r['id']: r for r in kb['evidence']}
    sources = {r['id']: r for r in kb['sources']}
    localizations = {r['id']: r for r in kb.get('game_localization_checks', [])}
    rows = {r['id']: r for name in ('game_story_records', 'game_lore_records') for r in kb[name]}
    chunks = []

    def provenance(ids):
        eids = unique(ids)
        sids = unique(evidence[e]['source_id'] for e in eids)
        modes = unique(evidence[e]['verification_status'] for e in eids)
        return dict(evidence_ids=eids, source_ids=sids,
                    source_urls=[sources[s]['original_url'] for s in sids],
                    evidence_modes=modes,
                    direct_only_eligible=bool(eids) and all(evidence[e]['verification_status'] == 'direct_text_verified' for e in eids),
                    source_authorities=unique(sources[s]['authority'] for s in sids),
                    official_only_eligible=bool(sids) and all(sources[s]['authority'] == 'official' for s in sids))

    for collection in ('game_story_records', 'game_lore_records', 'game_interpretations'):
        for r in kb[collection]:
            interpretation = collection == 'game_interpretations'
            if interpretation:
                basis = [rows[i] for i in r['basis_record_ids']]
                eids = unique(e for row in basis for e in row['evidence_ids'])
                entity_ids = unique(e for row in basis for e in [row['subject_id'], *row['target_ids']])
                text = r['statement_zh'] + ' 推理：' + r['rationale'] + ' 其他理解：' + r['alternative_reading']
            else:
                eids = r['evidence_ids']
                entity_ids = unique([r['focus_entity_id'], r['subject_id'], *r['target_ids']])
                text = f"{r['stage']} {r['segment']}；场景层：{r['narrative_level']}；说话人：{r['speaker'] or '旁白'}。{r['statement_zh']}"
            chunk = dict(id='C_' + r['id'], record_id=r['id'], collection=collection,
                         layer=r['layer'], text=text, **provenance(eids),
                         phase='arknights_interpretation' if interpretation else f"arknights_{r['stage']}_{r['segment']}",
                         as_of=kb['metadata']['as_of'], evidence_status='curator_reasoning' if interpretation else r['evidence_status'],
                         entity_ids=entity_ids, continuity='arknights_collab',
                         keywords=r['keywords'], query_examples=r['query_examples'], spoiler_rank=r['spoiler_rank'],
                         stage=r.get('stage'), segment=r.get('segment'), narrative_level=r.get('narrative_level'),
                         speaker=r.get('speaker'), assertion_kind=r.get('assertion_kind'), client_cross_checked=False,
                         material_type='interpretation' if interpretation else r.get('material_type', 'main_story'))
            issues = [issue for issue in kb['source_issues'] if r['id'] in issue['affected_record_ids']]
            chunk['source_issue_ids'] = [issue['id'] for issue in issues]
            chunk['required_context_record_ids'] = unique(i for issue in issues for i in issue['affected_record_ids'] if i != r['id'])
            if r.get('context_record_ids'):
                chunk['context_record_ids'] = r['context_record_ids']
            for field in ('section_title', 'trigger_label', 'unlock_condition', 'voice_metadata',
                          'delivery_metadata', 'material_owner_id', 'server', 'language', 'localization_check_ids'):
                if field in r:
                    chunk[field] = r[field]
            if r.get('trigger_label'):
                chunk['text'] += f" 触发：{r['trigger_label']}；解锁：{r['unlock_condition']}。"
            chunk['localization_notes'] = [
                dict(check_id=lc['id'], assessment=lc['assessment'], note_zh=lc['note_zh'],
                     evidence_ids=lc['evidence_ids'],
                     source_urls=unique(sources[v['source_id']]['original_url'] for v in lc['variants']))
                for i in r.get('localization_check_ids', [])
                for lc in [localizations[i]] if lc['assessment'] != 'equivalent_core']
            chunks.append(chunk)

    for name, records in kb.items():
        if not isinstance(records, list):
            continue
        stem = {'facts': 'canon_facts', 'inferences': 'inference'}.get(name, name)
        save(ROOT / f'data/{stem}.json', records)
        (ROOT / f'jsonl/{stem}.jsonl').write_bytes(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records).encode('utf-8'))
    base = json.loads((ROOT / 'data/retrieval_chunks.json').read_text(encoding='utf-8'))
    for stem, records in [('game_retrieval_chunks', chunks), ('retrieval_combined', base + chunks)]:
        save(ROOT / f'data/{stem}.json', records)
        (ROOT / f'jsonl/{stem}.jsonl').write_bytes(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in records).encode('utf-8'))

    names = {'BEG': '行动前', 'END': '行动后', 'NBT': '幕间'}
    def order(r):
        stage = 0 if r['stage'] == 'SS-ST-1' else int(r['stage'].split('-')[1])
        return stage, {'NBT': 0, 'BEG': 1, 'END': 2}[r['segment']], r['scene_order']

    lines = [f"# 《无忧梦呓》祥子主线表现 · v{kb['metadata']['version']}\n",
             f"{len(kb['game_story_records'])}条按关卡排列的主线及关联背景记录。证据为社区承载文本，保留叙事层、说话人与客户端待核状态。SS-2行动前两条为若麦背景，祥子未出场。\n",
             '[覆盖审计](明日方舟_主线覆盖审计.md) · [开篇与行动脉络](明日方舟_开篇与行动脉络.md)\n']
    for r in sorted(kb['game_story_records'], key=order):
        lines += [f"## {r['id']} · {r['stage']} {names[r['segment']]}\n", r['statement_zh'] + '\n',
                  f"场景层：{r['narrative_level']}；类型：{r['assertion_kind']}；说话人：{r['speaker'] or '旁白'}。\n",
                  '定位：' + r['locator'] + '。证据：' + '；'.join(f"[{e}]({evidence[e]['original_url']})" for e in r['evidence_ids']) + '。\n']
        if r['quote_original']:
            lines.append('短引文：' + r['quote_original'] + '\n')
        if r['knowledge_change_zh']:
            lines.append('知情变化：' + r['knowledge_change_zh'] + '\n')
        if r.get('context_record_ids'):
            lines.append('关联背景：' + ', '.join(r['context_record_ids']) + '。\n')
    (ROOT / 'markdown/明日方舟_祥子剧情表现.md').write_bytes(('\n'.join(lines).rstrip() + '\n').encode('utf-8'))
    lines = [f"# 明日方舟剧情问答索引 · v{kb['metadata']['version']}\n", '默认使用canon；分析时另取inference。问答导航与覆盖审计不进入事实检索。\n', '| 问法 | 记录ID |', '| --- | --- |']
    lines += [f"| {r['question_zh']} | {', '.join(r['record_ids'])} |" for r in kb['game_question_index']]
    lines += ['\n[主线表现](明日方舟_祥子剧情表现.md) · [开篇与行动脉络](明日方舟_开篇与行动脉络.md) · [检索文件](../jsonl/game_retrieval_chunks.jsonl)\n']
    (ROOT / 'markdown/明日方舟_剧情问答索引.md').write_bytes(('\n'.join(lines).rstrip() + '\n').encode('utf-8'))
    lines = [f"# 《无忧梦呓》主线覆盖审计 · v{kb['metadata']['version']}\n",
             '覆盖序章、教学关和SS-1至SS-8行动前后，共18段。full_text_reviewed指所列文本全部阅读；character_passages_reviewed指已核对角色对话与相关叙述。客户端、配音与画面核对另行推进。\n',
             'absence按该段文本判断；记录数可以包含用于理解祥子行动的其他角色背景。原文不随仓库发布，text_assets保存固定版本URL对应的字节哈希及行数。\n',
             '| 顺序 | 段落 | 祥子出场 | 复核范围 | 收录记录 |', '| --- | --- | --- | --- | --- |']
    for r in kb['game_scene_coverage']:
        lines.append(f"| {r['reading_order']} | {r['stage']} {r['segment']} | {'有' if r['sakiko_presence']=='present_in_text' else '无'} | {'全文' if r['review_status']=='full_text_reviewed' else '角色相关段落'} | {', '.join(r['record_ids']) or '—'} |")
    for r in kb['game_scene_coverage']:
        lines += [f"\n## {r['id']} · {r['stage']} {r['segment']}\n", r['notes_zh'] + '\n',
                  '证据：' + '；'.join(f"[{e}]({evidence[e]['original_url']})" for e in r['evidence_ids']) + '。\n']
    (ROOT / 'markdown/明日方舟_主线覆盖审计.md').write_bytes(('\n'.join(lines).rstrip() + '\n').encode('utf-8'))
    export_supplements(kb, evidence, sources)
    from export_base import main as export_base
    export_base()
    print(f"Exported {sum(isinstance(v, list) for v in kb.values())} collections and {len(chunks)} game chunks.")


def export_supplements(kb, evidence, sources):
    """Keep supplementary reading views reproducible from the primary database."""
    version = kb['metadata']['version']
    localizations = {r['id']: r for r in kb.get('game_localization_checks', [])}
    def md(name, lines):
        (ROOT / 'markdown' / name).write_bytes(('\n'.join(lines).rstrip() + '\n').encode('utf-8'))
    def citations(row):
        return '；'.join(f"[{e}]({evidence[e]['original_url']})" for e in row['evidence_ids'])
    entities = {r['id']: r['name_zh'] for r in kb['entities']}
    lines = [f'# 档案、模组、语音与活动附加文本 · v{version}\n',
             '按材料记录游戏中的表现与评价；档案编者、爱丽丝、队友与祥子自己的说法分别保留归属。语音文本及标签已经核对，音频与客户端另行复核。\n']
    for r in kb['game_lore_records']:
        lines += [f"## {r['id']} · {r['section_title']}\n", r['statement_zh'] + '\n',
                  f"材料：{r['material_type']}；记录版本：{r['server']} / {r['language']}；所属角色：{entities.get(r.get('material_owner_id', r['subject_id']))}；叙事层：{r['narrative_level']}；说话人：{r['speaker'] or '旁白'}。\n",
                  f"解锁：{r['unlock_condition'] or '未指定'}；触发：{r['trigger_label'] or '不适用'}。定位：{r['locator']}。\n",
                  '证据：' + citations(r) + '。\n']
        if r.get('voice_metadata'):
            v = r['voice_metadata']
            lines.append(f"语音标识：{v['char_word_id']}；资源键：{v['voice_asset']}；触发位置：{v['place_type']}。\n")
        if r.get('delivery_metadata'):
            lines.append('国服现实活动送达时间：' + r['delivery_metadata']['local_time'] + '；剧情内日历日期未给出。\n')
        for i in r.get('localization_check_ids', []):
            lc=localizations[i]
            if lc['assessment'] != 'equivalent_core':
                lines.append(f"语言对照 {i}：{lc['note_zh']}\n")
    md('明日方舟_档案模组与语音.md', lines)
    voices = [r for r in kb['game_lore_records'] if r.get('voice_metadata')]
    lines = [f'# 祥子38项语音目录 · v{version}\n',
             '38项中日英文正文均已逐项阅读；触发名称、条件和资源键保留国服字段，各语言标签另见中日英文对照。资源键用作定位，音频播放复核待完成。\n',
             '| 语音ID | 触发标签 | 解锁条件 | 知识记录 |', '| --- | --- | --- | --- |']
    lines += [f"| {r['voice_metadata']['voice_id']} | {r['trigger_label']} | {r['unlock_condition']} | {r['id']} |" for r in sorted(voices, key=lambda r:r['voice_metadata']['voice_id'])]
    lines += ['\n信赖40%、100%、200%对应三项信赖提升后交谈。节庆语音的DIRECT是资源解锁类型，实际触发场合由place_type另行保存。\n',
              '[全部内容摘要与来源](明日方舟_档案模组与语音.md) · [材料覆盖审计](明日方舟_补充材料覆盖审计.md)\n']
    md('明日方舟_完整语音目录.md', lines)
    lines = [f'# 补充材料覆盖审计 · v{version}\n',
             'expected_slots与covered_slots记录已审阅目录；逐项阅读之后，按祥子剧情讨论价值提取摘要，具体选录范围见下。\n']
    for r in kb['game_material_coverage']:
        lines += [f"## {r['id']} · {r['title_zh']}\n", r['review_scope_zh'] + '\n',
                  f"审阅槽位：{len(r['covered_slots'])}/{len(r['expected_slots'])}；记录：{', '.join(r['record_ids'])}。\n"]
        for a in r['text_assets']:
            s = sources[a['source_id']]
            lines += [f"来源：[{s['id']}]({s['original_url']})；原始字节数：{a['byte_count']}；SHA-256：`{a['sha256']}`。\n"]
    md('明日方舟_补充材料覆盖审计.md', lines)
    content = {r['id']: r for key in ('game_story_records','game_lore_records') for r in kb[key]}
    phases = ['dream_encounter','castle_first_meeting','rhodes_island_daily_life','letter_support']
    phase_names = dict(zip(phases, ['梦中相遇','城堡外层初见及交谈','罗德岛日常','舞会来信支持']))
    lines = [f'# 关系阶段与行动脉络 · v{version}\n',
             '梦中相遇、城堡外层初见、罗德岛日常与活动来信分别组织。阶段内次序是阅读编排；档案、模组和语音之间未虚设精确日期。每一条关系只按其场景或具名发言生效。\n']
    for phase in phases:
        lines.append(f'## {phase_names[phase]}\n')
        for r in sorted((r for r in kb['game_relations'] if r.get('phase_group') == phase), key=lambda r:(r['thread_id'],r['order_within_thread'],r['id'])):
            basis = [content[i] for i in r['basis_record_ids']]
            lines += [f"### {entities[r['subject_id']]} → {entities[r['object_id']]} · {r['id']}\n",
                      ' '.join(x['statement_zh'] for x in basis) + '\n',
                      f"关系属性：{r['predicate']}；场景层：{r['narrative_level']}；依据：{', '.join(r['basis_record_ids'])}。\n",
                      '证据：' + citations(r) + '。\n']
    lines.append('## 主线关系记录\n')
    lines += [f"- {r['id']}：{entities[r['subject_id']]} → {entities[r['object_id']]}；{r['predicate']}；{r['stage']} {r['segment']}；依据 {', '.join(r['basis_record_ids'])}。" for r in kb['game_relations'] if not r.get('phase_group')]
    md('明日方舟_关系阶段时间线.md', lines)
    lines = [f'# 联动篇关系与自我认识 · v{version}\n',
             '[按阶段阅读关系](明日方舟_关系阶段时间线.md)\n',
             '| ID | 主体 → 对象 | 属性 | 场景层 | 依据 |', '| --- | --- | --- | --- | --- |']
    lines += [f"| {r['id']} | {entities[r['subject_id']]} → {entities[r['object_id']]} | {r['predicate']} | {r['stage']} {r['segment']} / {r['narrative_level']} | {', '.join(r['basis_record_ids'])} |" for r in kb['game_relations']]
    lines.append('\n## 剧情推断（inference）\n')
    for r in kb['game_interpretations']:
        lines += [f"### {r['id']}\n", r['statement_zh'] + '\n',
                  f"依据：{', '.join(r['basis_record_ids'])}。{r['rationale']}\n",
                  '其他理解：' + r['alternative_reading'] + '\n']
    md('明日方舟_关系与自我认识.md', lines)
    lines = [f'# 来源与证据 · v{version}\n',
             '来源保存原始URL与核验状态；证据保存所读定位与摘要。社区镜像的固定版本和材料范围另见覆盖审计。\n']
    for s in kb['sources']:
        lines += [f"## {s['id']} · {s['title']}\n", f"[{s['title']}]({s['original_url']})\n",
                  f"语言：{s['language']}；权威类别：{s['authority']}；取得状态：{s['verification_status']}；核验：{s['checked_on']}。\n", s['access_note'] + '\n']
        for e in (r for r in kb['evidence'] if r['source_id'] == s['id']):
            lines += [f"- {e['id']}（{e['language']}）：{e['locator']}。{e['support_summary_zh']}"]
    md('来源与证据.md', lines)
    lines = ['# 来源差异与处理\n']
    for r in kb['source_issues']:
        lines += [f"## {r['id']}\n", r['summary_zh'] + '\n', '处理：' + r['resolution_zh'] + '\n',
                  '证据：' + citations(r) + '。\n', '后续：' + r['next_action'] + '\n']
    md('来源差异表.md', lines)
    lines = [f'# 中日英文材料对照 · v{version}\n',
             '按语音槽位、角色档案章节、模组或信件ID对应；摘要为中文编录。equivalent_core表示所列命题核心相符，wording_variant为措辞差异，localized_addition为某语言多出的段落。客户端和音频状态单列。\n']
    for lc in kb.get('game_localization_checks', []):
        lines += [f"## {lc['id']} · {lc['lookup_key']}\n", lc['note_zh'] + '\n',
                  f"材料：{lc['material_type']}；判定：{lc['assessment']}；关联：{', '.join(lc['record_ids'])}。\n"]
        for v in lc['variants']:
            lines += [f"### {v['server']} / {v['language']} · {v['label']}\n", v['summary_zh'] + '\n',
                      f"证据：[{v['evidence_id']}]({sources[v['source_id']]['original_url']})；定位：{v['locator']}；来源字节SHA-256：`{v['asset_sha256']}`。\n"]
    md('明日方舟_中日英文对照.md', lines)
    lines = [f'# 多段剧情讨论导航 · v{version}\n',
             '以下提纲是编者组织已录记录的阅读导航，单列为game_discussion_guides，不进入canon事实片段。每一步回链具体记录；原始URL与证据定位可由context_game.py补取。\n',
             '运行示例：`python -X utf8 tools/context_game.py --guide AKD001`。自然问题可先不指定guide，结果会建议相关导航；选定后补取完整材料。\n']
    for g in kb['game_discussion_guides']:
        lines += [f"## {g['id']} · {g['question_zh']}\n", f"剧透等级：{g['spoiler_rank']}；提纲复核：{g['reviewed_on']}。\n"]
        for step in g['answer_outline']:
            lines.append(f"- {step['summary_zh']}（{', '.join(step['record_ids'])}）")
        for rid in g['record_ids']:
            r = content[rid]
            lines.append(f"\n证据 {rid}：{r['stage']} / {r['segment']}；{r['locator']}；{citations(r)}。\n")
    md('明日方舟_多段剧情讨论导航.md', lines)
    lines = [f'# 游戏文本问答验收 · v{version}\n',
             '本轮用12个讨论问题形成实际回答样本，并由同一编者对照已录正文、来源差异及固定文本逐句检查。supported为人工复核结论；自动检查复核引用、上下文和过滤边界。样本单列管理集合，不进入事实检索。\n']
    for review in kb['game_answer_reviews']:
        lines += [f"## {review['id']} · {review['question_zh']}\n"]
        for sentence in review['answer_sentences']:
            lines.append(sentence['text_zh'] + '（' + ', '.join(sentence['record_ids']) + '）\n')
        lines += ['复核：' + review['review_note_zh'] + '\n',
                  f"状态：{review['review_status']}；日期：{review['reviewed_on']}；导航：{review['guide_id']}。\n"]
        for rid in review['record_ids']:
            row = content[rid]
            lines.append(f"证据 {rid}：{row['stage']} / {row['segment']}；{row['locator']}；{citations(row)}。\n")
    md('明日方舟_问答验收.md', lines)


if __name__ == '__main__':
    main()
