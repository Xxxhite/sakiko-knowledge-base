"""Check opening context, coverage, linked records and retrieval provenance."""
from pathlib import Path
import json
import re
import sys
from search_game import search, stage_rank

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


kb = load('data/kb.json')
stories = {r['id']: r for r in kb['game_story_records']}
content = {**stories, **{r['id']: r for r in kb['game_lore_records']},
           **{r['id']: r for r in kb['game_interpretations']}}
evidence = {r['id']: r for r in kb['evidence']}
sources = {r['id']: r for r in kb['sources']}
chunks = load('data/game_retrieval_chunks.json')
coverage = kb['game_scene_coverage']
checks = []


def check(name, condition):
    assert condition, name
    checks.append(dict(check=name, result='passed'))


expected = {('SS-ST-1', 'NBT'), ('SS-TR-1', 'TUTORIAL')} | {
    (f'SS-{n}', segment) for n in range(1, 9) for segment in ('BEG', 'END')}
check('Coverage contains all 18 entry/tutorial/main segments', len(coverage) == 18 and {(r['stage'], r['segment']) for r in coverage} == expected)
check('Coverage order is unique', sorted(r['reading_order'] for r in coverage) == list(range(1, 19)))
for row in coverage:
    check('Coverage references ' + row['id'],
          all(e in evidence for e in row['evidence_ids']) and
          all(asset['source_id'] in sources for asset in row['text_assets']) and
          row['record_ids'] == [r['id'] for r in kb['game_story_records'] if (r['stage'], r['segment']) == (row['stage'], row['segment'])])
    if row['sakiko_presence'] == 'absent_in_text':
        check('Absent character is not the actor ' + row['id'], row['sakiko_speaking_lines'] == 0 and all(stories[i]['subject_id'] != 'sakiko' for i in row['record_ids']))
    for asset in row['text_assets']:
        check('Source version pinned ' + asset['source_id'], bool(re.search(r'/[0-9a-f]{40}/zh_CN/gamedata/story/', sources[asset['source_id']]['original_url'])))

check('SS-2 before operation retains Nyamu-only background', all(stories[i]['subject_id'] == 'nyamu' and stories[i]['speaker'] == '祐天寺若麦' for i in ('AK075', 'AK076')))
check('Dream employment and illness remain dream-scoped', all(stories[i]['narrative_level'] == 'initial_sakiko_dream' and stories[i]['spoiler_rank'] >= 2 for i in ('AK063', 'AK064', 'AK065', 'AK066', 'AK067')))
check('Opening street montage remains separate', all(stories[f'AK{i:03d}']['narrative_level'] == 'opening_street_vision' for i in range(59, 63)))
for row in stories.values():
    check('Context progress ' + row['id'], all(i in stories and stories[i]['spoiler_rank'] <= row['spoiler_rank'] for i in row.get('context_record_ids', [])))

check('Coverage stays outside factual retrieval', not any(c['collection'] == 'game_scene_coverage' or c['record_id'].startswith('AKC') for c in chunks))
check('Combined retrieval is the exact ordered union', load('data/retrieval_combined.json') == load('data/retrieval_chunks.json') + chunks)
for stem in ('game_retrieval_chunks', 'retrieval_combined'):
    lines = (ROOT / f'jsonl/{stem}.jsonl').read_text(encoding='utf-8').splitlines()
    check('Retrieval JSONL mirror ' + stem, load(f'data/{stem}.json') == [json.loads(line) for line in lines])

for chunk in chunks:
    row = content[chunk['record_id']]
    ids = list(dict.fromkeys(e for i in row.get('basis_record_ids', []) for e in content[i]['evidence_ids'])) if chunk['layer'] == 'inference' else row['evidence_ids']
    sids = list(dict.fromkeys(evidence[e]['source_id'] for e in ids))
    check('Game retrieval provenance ' + row['id'],
          chunk['evidence_ids'] == ids and chunk['source_ids'] == sids and
          chunk['source_urls'] == [sources[i]['original_url'] for i in sids] and
          chunk['direct_only_eligible'] == all(evidence[i]['verification_status'] == 'direct_text_verified' for i in ids) and
          chunk['official_only_eligible'] == all(sources[i]['authority'] == 'official' for i in sids) and
          chunk.get('context_record_ids', []) == row.get('context_record_ids', []))

check('Prologue progress accepts the new checkpoint', stage_rank('SS-ST-1') == 0 and stage_rank('SS-TR-1') == 0)
check('Prologue progress hides later dream disclosure', all(r['record_id'] in {'AK059','AK060','AK061','AK062'} for r in search('序章 梦 祥子 罗德岛', limit=100, max_rank=0)))
cases = [
    ('序章为什么强调站姿', 'AK059'),
    ('小祥为什么不让喵梦煽动睦', 'AK060'),
    ('新曲为什么没让若麦听到', 'AK061'),
    ('序章路口她怎么哭了', 'AK062'),
    ('刚醒来的她认得那四个女生吗', 'AK063'),
    ('梦里她怎么会安置病人', 'AK064'),
    ('梦里为什么想对抗矿石病', 'AK065'),
    ('她怎么认识爱丽丝和贝娜', 'AK066'),
    ('爱丽丝为什么急着找安', 'AK067'),
    ('她一开始希望安留在美梦吗', 'AK068'),
    ('护梦项链第一次谁给她', 'AK069'),
    ('什么时候在城堡醒来', 'AK070'),
    ('赌约前被绑她怎么冷静', 'AK072'),
    ('明知男人可疑为什么付钱', 'AK077'),
    ('劝海铃时为什么提琴盒', 'AK078'),
    ('为什么觉得梦中睦不是本人', 'AK080'),
    ('她想写一首怎样的新歌', 'AK082'),
    ('把梦中爱丽丝的话说回给本人', 'AK084'),
]
outcomes = []
for query, expected_id in cases:
    found = [r['record_id'] for r in search(query, limit=5)]
    outcomes.append(dict(query=query, expected=expected_id, top5=found, passed=expected_id in found))
check('Opening and action context natural queries', all(r['passed'] for r in outcomes))
result = dict(status='passed', checks=checks, cases=outcomes,
              scope='Text coverage, attribution, provenance, progress and local retrieval; client review tracked separately.')
if '--write-report' in sys.argv:
    (ROOT / 'validation').mkdir(exist_ok=True)
    (ROOT / 'validation/v15_retrieval.json').write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
print(json.dumps(result, ensure_ascii=False, indent=2))
