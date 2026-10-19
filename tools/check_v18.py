"""Check discussion navigation, source closure and filters on assembled context."""
from pathlib import Path
import json
import sys
from context_game import assemble

ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
content={r['id']:r for n in ('game_story_records','game_lore_records') for r in kb[n]}
chunks=json.loads((ROOT/'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))
checks=[]
def check(name, condition):
    assert condition, name
    checks.append(dict(check=name,result='passed'))
guides=kb['game_discussion_guides']
check('Twelve curated navigation guides',len(guides)==12 and all(g['guide_kind']=='curator_navigation' and not g['default_retrieval_eligible'] for g in guides))
check('Navigation is not a fact chunk',not any(c['collection']=='game_discussion_guides' for c in chunks))
for g in guides:
    refs={rid for step in g['answer_outline'] for rid in step['record_ids']}
    check(g['id']+' linked outline',refs==set(g['record_ids']) and all(rid in content for rid in refs))
    check(g['id']+' spoiler gate',g['spoiler_rank']==max(content[r]['spoiler_rank'] for r in refs))
    result=assemble(guide_id=g['id'])
    check(g['id']+' full context',result['guide_complete'] and result['required_context_complete'] and all(r['citations'] for r in result['results']))

# Independent paraphrases exercise discovery, then explicitly select a guide.
cases=[
 ('明明知道家里是假的，她为何舍不得妈妈又愿意出门','AKD001'),
 ('睦想在聚会上唱歌时，小祥有没有先听她自己的想法','AKD002'),
 ('跟莫菲丝打赌以前她有没有先设法唤醒伙伴','AKD003'),
 ('莫菲丝说她怕被抛下，祥子后来又为什么为对方难过','AKD004'),
 ('最初罗德岛里遇见的爱丽丝和后来正式见面的是什么情况','AKD005'),
 ('贝娜还是爱丽丝送的洋娃娃，两处文本分别写什么','AKD006'),
 ('匿名听众是小提琴手这句话是谁猜的，合奏实现了吗','AKD007'),
 ('日文晋升里说的遗忘与中文留下勇气有什么联系','AKD008'),
 ('她请罗德岛减轻睦的压力，那对睦了解多少','AKD009'),
 ('庭院新朋友的名字祥子听清了吗，海铃走神时她又怎么做','AKD010'),
 ('她弹琴让丝线松开时的道歉，和最后牵手登台有什么先后','AKD011'),
 ('上舰以后她干了哪些活，创作想法与舞会收到的支持呢','AKD012'),
]
outcomes=[]
for query,gid in cases:
    result=assemble(query)
    found=[r['guide_id'] for r in result['suggested_guides']]
    outcomes.append(dict(query=query,expected_guide=gid,top3=found,passed=gid in found))
if not all(r['passed'] for r in outcomes):
    print(json.dumps([r for r in outcomes if not r['passed']],ensure_ascii=False,indent=2))
check('Twelve natural discussion questions discover their guides',all(r['passed'] for r in outcomes))
gift=assemble(record_ids=['AKL009'],limit=1,material='module_story')
check('A one-record selection expands its cross-material gift companion',{'AKL009','AKL016'}.issubset({r['record_id'] for r in gift['results']}) and gift['required_context_complete'])
check('Cross-material guide companion retries an earlier material exclusion',assemble(guide_id='AKD006',material='module_story')['guide_complete'])
small=assemble(record_ids=['AKL009'],max_records=1)
check('Budget exhaustion exposes missing companion',not small['required_context_complete'] and small['missing_required_context_ids']==['AKL016'] and any(r['reason']=='record_budget' for r in small['blocked_context']))
limited=assemble(guide_id='AKD001',max_rank=10)
check('Spoiler filter hides guide prose and later records',not limited['guide_complete'] and not limited['answer_outline'] and all(r['spoiler_rank']<=10 for r in limited['results']))
official=assemble(guide_id='AKD006',official=True)
check('Official filter also applies to linked records',not official['results'] and not official['answer_outline'] and all(r['reason']=='official_filter' for r in official['blocked_context']))
check('Inference disabled by default',not assemble(record_ids=['AKI001'])['results'])
check('Inference can be explicitly requested',assemble(record_ids=['AKI001'],include_inference=True)['results'][0]['layer']=='inference')
check('Story background is supplied',any(r['record_id']=='AK067' for r in assemble(record_ids=['AK001'])['results']))
for result in [gift,small,limited,official,assemble(guide_id='AKD008')]:
    ids=[r['record_id'] for r in result['results']]
    check('Unique context '+str(len(checks)),len(ids)==len(set(ids)))
check('Localized distinction remains paired',{'AKL061','AKL091'}.issubset({r['record_id'] for r in assemble(record_ids=['AKL091'])['results']}))
result=dict(status='passed',checks=checks,cases=outcomes,
 scope='Curator-reviewed outlines and context retrieval; no generated-answer evaluation is claimed.')
if '--write-report' in sys.argv:
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/v18_discussion.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
