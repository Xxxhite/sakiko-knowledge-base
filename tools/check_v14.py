from pathlib import Path
import json,sys
from search_game import search
ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
lore={x['id']:x for x in kb['game_lore_records']}
entities={x['id'] for x in kb['entities']}
es={x['id']:x for x in kb['evidence']}; ss={x['id']:x for x in kb['sources']}
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(dict(check=name,result='passed'))
check('Supplementary actor/entity/evidence references',all(x['subject_id'] in entities and all(i in entities for i in x['target_ids']) and all(e in es for e in x['evidence_ids']) for x in lore.values()))
check('Supplementary text remains source-qualified',all(x['layer']=='canon' and x['evidence_status']=='game_text_transcription' and not x['client_cross_checked'] and all(ss[es[e]['source_id']]['authority']=='secondary' for e in x['evidence_ids']) for x in lore.values()))
check('File/module/voice records stay outside dream scenes',all(x['narrative_level']=='post_castle_rhodes_island' and x['spoiler_rank']==16 for x in lore.values()))
check('Iris assessment has attributed author',lore['AKL005']['speaker']=='爱丽丝' and lore['AKL005']['assertion_kind']=='archive_assessment')
check('Listener instrument kept as character guess',lore['AKL010']['assertion_kind']=='character_guess')
check('Meeting and duet retained as future plan',lore['AKL008']['assertion_kind']=='future_plan')
check('Unverified voice triggers left null',all(x['trigger_label'] is None and x['unlock_condition'] is None for x in lore.values() if x['material_type']=='voice'))
issue=next(x for x in kb['source_issues'] if x['id']=='SC004')
check('Gift attribution keeps both source records',set(issue['affected_record_ids'])=={'AKL009','AKL016'} and set(issue['evidence_ids'])=={'E75','E76'})
check('Material filter returns only requested type',all(x['material_type']=='module_story' for x in search('匿名听众 弹琴',limit=100,material='module_story')))
check('Pre-ending progress excludes later archive',not any(x['record_id'].startswith('AKL') for x in search('罗德岛 工作',limit=100,max_rank=14)))
cases=[
('她有没有把决定权交给睦','AK043',None),
('不忍打断睦的幸福演奏那段','AK045',None),
('海铃被说背叛后她怎么查证','AK052',None),
('祥子骑单车下坡怎么样了','AK054',None),
('她当时明知是假母亲还走过去','AK049',None),
('罗德岛有哪些搬运保洁工作','AKL002','operator_file'),
('是谁偷偷留字条给她加油','AKL007','module_story'),
('她对匿名听众身份做了什么','AKL008','module_story'),
('跟博士学习决策的台词','AKL011','voice'),
('初华让她不要熬夜的提醒','AKL017','voice'),
('重新认识泰拉后想写什么歌','AKL014','voice'),
('初次见红豆时为何落寞','AKL015','voice')]
outcomes=[]
for query,expected,material in cases:
    found=[x['record_id'] for x in search(query,limit=5,material=material)]
    outcomes.append(dict(query=query,expected=expected,material=material,top5=found,passed=expected in found))
check('New natural language retrieval cases',all(x['passed'] for x in outcomes))
gift=search('贝娜送的洋娃娃',limit=5)
check('One gift wording retrieves paired provenance',{'AKL009','AKL016'}.issubset({x['record_id'] for x in gift}))
result=dict(status='passed',checks=checks,cases=outcomes,scope='Supplementary text, attribution, progress/material filters and retrieval; no language-model answer evaluation.')
if '--write-report' in sys.argv: (ROOT/'validation/v14_retrieval.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
