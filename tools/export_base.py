"""Refresh original-work fact and episode reading views from kb.json."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]


def main():
    kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
    names={r['id']:r['name_zh'] for r in kb['entities']}
    evidence={r['id']:r for r in kb['evidence']}
    def citations(ids):
        return '；'.join(f"[{i}]({evidence[i]['original_url']})（{evidence[i]['locator']}，{evidence[i]['verification_status']}）" for i in ids)
    lines=['# 丰川祥子：基础事实库\n','所有条目层级为 **canon**；档案适用媒介和剧情阶段逐项保留。\n']
    for row in kb['facts']:
        lines += [f"## {row['id']} · {row['statement_zh']}\n",
            '- 主体：'+names[row['subject_id']],
            f"- 字段：`{row['predicate']}`；值：`{json.dumps(row['value'],ensure_ascii=False)}`",
            f"- 阶段：{row['valid_time']['phase']}；媒介：{row['continuity']}",
            '- 证据：'+citations(row['evidence_ids'])+'\n']
        if row['notes']:
            lines.append('说明：'+row['notes']+'\n')
    (ROOT/'markdown/基础事实库.md').write_bytes(('\n'.join(lines).rstrip()+'\n').encode())
    lines=[f"# 原作逐话索引 · v{kb['metadata']['version']}\n",
        '按work_id和episode分别编目MyGO与Ave Mujica，已覆盖话数见下列条目。文件沿用后段逐话索引.md路径。官方梗概、一手访谈和原片核验分别记录。\n',
        '第9—13话的授权关系据TV官网，链接与分钟标示据Bandai Channel公开目录。此前实际打开第12话正文时显示登录提示，见[访问审计](访问审计.md)的A001；其他集读取范围为目录。\n',
        'Ave Mujica第12话的官方剧情仍为短预告梗概；候选场景单独管理，待办见[逐场景复核清单](逐场景复核清单.md)。\n']
    works={'bang_dream_its_mygo':'It’s MyGO!!!!!','bang_dream_ave_mujica':'Ave Mujica'}
    for row in sorted(kb['episode_catalog'],key=lambda r:(r['work_id'],r['episode'])):
        lines += [f"## {row['id']} · {works[row['work_id']]} 第{row['episode']}话 · {row['title']}\n",
            f"公告播出：{row['announced_broadcast_date'] or '待核验'}；新闻稿：{row['press_release_date'] or '未设定（见各来源发布日期）'}；正文范围：{row['plot_evidence_level']}。\n",
            '关联：'+(', '.join(row['related_record_ids']) or '该梗概仅作下一轮原片定位')+'。\n',
            '证据：'+citations(row['evidence_ids'])+'。\n']
        if row['official_playback_url']:
            lines.append(f"官方播放目录：[入口]({row['official_playback_url']})；目录分钟数：{row['catalog_duration_minutes']}。\n")
            lines.append('目录证据：'+citations(row['playback_link_evidence_ids'])+'；访问审计：'+', '.join(row['access_audit_ids'])+'。\n')
        else:
            lines.append('播放目录与时长：待核验。\n')
        lines.append('原片完整核验：'+('已完成' if row['full_episode_reviewed'] else '待完成')+'；字幕版本与时间码按实际取得情况填写。\n')
    (ROOT/'markdown/后段逐话索引.md').write_bytes(('\n'.join(lines).rstrip()+'\n').encode())
    def md(name,lines):
        (ROOT/'markdown'/name).write_bytes(('\n'.join(lines).rstrip()+'\n').encode())
    lines=['# 丰川祥子：人物关系库\n',
        '层级均为canon。symmetric互向关系只存一边；valence保存关系属性，未定时为unspecified。关系仅适用于列明的阶段与场景。\n',
        '| ID | 主体 | 属性 | 对象 | 方向 | 阶段 | 关系性质 |','| --- | --- | --- | --- | --- | --- | --- |']
    for row in kb['relations']:
        lines.append(f"| {row['id']} | {names[row['subject_id']]} | {row['predicate']} | {names[row['object_id']]} | {row['direction']} | {row['valid_time']['phase']} | {row['valence']} |")
    for row in kb['relations']:
        lines += [f"\n## {row['id']}\n",row['statement_zh']+'\n',
            f"证据类别：{row['evidence_status']}；范围：{row['narrative_scope']}；证据：{citations(row['evidence_ids'])}。\n"]
        if row['notes']:lines.append('说明：'+row['notes']+'\n')
    md('人物关系库.md',lines)
    lines=['# 关系阶段与职责对照\n','各边按所列阶段与证据资格使用；film_profile_snapshot为电影官网档案，TV集数另核。\n',
        '| ID | 主体 → 对象 | 关系属性 | 阶段 | 证据类型 |','| --- | --- | --- | --- | --- |']
    for row in kb['relations']:
        lines.append(f"| {row['id']} | {names[row['subject_id']]} → {names[row['object_id']]} | {row['predicate']} | {row['valid_time']['phase']} | {row['evidence_status']} |")
    lines.append('\n逐条证据和方向见[人物关系库](人物关系库.md)；身份待核任务见[逐场景复核清单](逐场景复核清单.md)。\n')
    md('关系阶段对照.md',lines)
    lines=['# 时间线\n','display_order是阅读排序，after_event_ids才是明确先后约束；剧情内日期、披露集数和新闻稿日期分别保存。\n']
    for row in sorted(kb['timeline'],key=lambda r:(r['display_order'],r['id'])):
        lines += [f"## {row['id']} · {row['title_zh']}\n",
            f"阶段：{row['story_time']['phase']}；披露：{row['reveal']['work']} / {row['reveal']['episode'] if row['reveal']['episode'] is not None else '未指定集数'}；时间码：{row['reveal']['timecode'] or '待核验'}。\n",
            '明确晚于：'+(', '.join(row['story_time']['after_event_ids']) or '未设定')+'；关联：'+', '.join(row['record_ids'])+'。\n',
            '证据：'+citations(row['evidence_ids'])+'。\n',row['notes']+'\n']
    md('时间线.md',lines)
    lines=['# 剧情推断库 · inference\n','编者及署名主创的剧情理解单列；默认事实检索关闭，保留依据、推理与替代阅读。\n']
    for row in kb['inferences']:
        lines += [f"## {row['id']} · {row['statement_zh']}\n",
            '解读者：'+row.get('interpretation_author','编者')+'；依据：'+', '.join(row['basis_record_ids'])+'。\n',
            '推理：'+row['rationale']+'\n','其他阅读：'+row['alternative_reading']+'\n',
            f"强度：{row['strength']}；阶段：{row['valid_time']['phase']}。\n",'证据：'+citations(row['evidence_ids'])+'。\n']
    md('剧情推断库.md',lines)
    lines=[f"# 原作剧情问答导航 · v{kb['metadata']['version']}\n",'以下为查询导航，排除事实片段；分析动机时可显式打开inference。\n',
        '| ID | 问题 | 正文记录 |','| --- | --- | --- |']
    for row in kb['original_question_index']:
        lines.append(f"| {row['id']} | {row['question_zh']} | {', '.join(row['record_ids'])} |")
    md('原作_剧情问答索引.md',lines)
    reviewed = [r for r in kb['original_question_index'] if r.get('answer_review')]
    lines = [f"# 原作问答验收 · v{kb['metadata']['version']}\n",
        f"{len(reviewed)}个实际回答、{sum(len(r['answer_review']['answer_sentences']) for r in reviewed)}句逐句复核。样本保存在original_question_index.answer_review，随JSON／JSONL导出，排除事实检索。\n",
        '方法：同一编者对照所引记录及证据定位，检查人物、阶段、发言人与分层；程序检查引用闭合和来源资格。含原作整体剧透，按各句所列作品与阶段使用。\n',
        '核验范围：既有记录及本轮取得的日文正文；原片、字幕和时间码沿用证据的实际状态。场景缺口统一见[下一步清单](下一步补充清单.md)。\n']
    content = {r['id']: r for name in ('facts','relations','timeline','inferences') for r in kb[name]}
    for row in reviewed:
        review = row['answer_review']
        lines += [f"## {row['id']} · {row['question_zh']}\n"]
        for number, sentence in enumerate(review['answer_sentences'], 1):
            ids = sentence['record_ids']
            eids = list(dict.fromkeys(e for rid in ids for e in content[rid]['evidence_ids']))
            lines += [f"{number}. **{sentence['layer']}**：{sentence['text_zh']}（依据：{', '.join(ids)}）\n",
                      '   来源：'+citations(eids)+'。\n']
        lines += [f"复核：{review['review_status']}；{review['reviewed_on']}；{review['review_method']}。\n",
                  review['review_note_zh']+'\n']
    md('原作_问答验收.md',lines)
    print('Exported original facts, relations, timeline, interpretations, episodes and question views.')


if __name__=='__main__':
    main()
