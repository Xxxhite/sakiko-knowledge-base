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
        '当前收录Ave Mujica第4、6、9—13话。官方预告梗概、主创复述和原片核验分别记录；文件沿用后段逐话索引.md路径。\n',
        '第9—13话的授权关系据TV官网，链接与分钟标示据Bandai Channel公开目录。此前实际打开第12话正文时显示登录提示，见[访问审计](访问审计.md)的A001；其他集读取范围为目录。\n',
        '第12话的官方剧情仍为短预告梗概；候选场景单独管理，待办见[逐场景复核清单](逐场景复核清单.md)。\n']
    for row in sorted(kb['episode_catalog'],key=lambda r:r['episode']):
        lines += [f"## {row['id']} · {row['title']}\n",
            f"公告播出：{row['announced_broadcast_date']}；新闻稿：{row['press_release_date']}；正文范围：{row['plot_evidence_level']}。\n",
            '关联：'+(', '.join(row['related_record_ids']) or '该梗概仅作下一轮原片定位')+'。\n',
            '证据：'+citations(row['evidence_ids'])+'。\n']
        if row['official_playback_url']:
            lines.append(f"官方播放目录：[入口]({row['official_playback_url']})；目录分钟数：{row['catalog_duration_minutes']}。\n")
            lines.append('目录证据：'+citations(row['playback_link_evidence_ids'])+'；访问审计：'+', '.join(row['access_audit_ids'])+'。\n')
        else:
            lines.append('播放目录与时长：待核验。\n')
        lines.append('原片完整核验：'+('已完成' if row['full_episode_reviewed'] else '待完成')+'；字幕版本与时间码按实际取得情况填写。\n')
    (ROOT/'markdown/后段逐话索引.md').write_bytes(('\n'.join(lines).rstrip()+'\n').encode())
    print('Exported original fact and episode reading views.')


if __name__=='__main__':
    main()
