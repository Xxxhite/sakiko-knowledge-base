"""Validate language alignment without promoting localized words across versions."""
from pathlib import Path
import json
import re
import sys
from search_game import search

ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
rows={r['id']:r for r in kb['game_lore_records']}
sources={r['id']:r for r in kb['sources']}
es={r['id']:r for r in kb['evidence']}
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(dict(check=name,result='passed'))

lc=kb['game_localization_checks']
byid={r['id']:r for r in lc}
chunks=json.loads((ROOT/'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))
chunk_byid={r['record_id']:r for r in chunks}
check('66 alignment units across four materials',len(lc)==66 and {t:sum(r['material_type']==t for r in lc) for t in ['voice','operator_file','promotion_record','module_story','event_letter']} == dict(voice=41,operator_file=15,promotion_record=2,module_story=3,event_letter=5))
check('Three different regions and languages per check',all({(v['server'],v['language']) for v in r['variants']}=={('CN','zh-Hans'),('JP','ja'),('Global','en')} for r in lc))
check('All variant evidence binds source and locator',all(v['source_id'] in sources and v['evidence_id'] in es and es[v['evidence_id']]['source_id']==v['source_id'] and es[v['evidence_id']]['locator']==v['locator'] and es[v['evidence_id']]['language']==v['language'] for r in lc for v in r['variants']))
check('Cross-language sources use immutable revisions',all(re.search(r'/[0-9a-f]{40}/(?:jp|en)/gamedata/excel/',sources[v['source_id']]['original_url']) for r in lc for v in r['variants'] if v['server']!='CN'))
check('Public mirrors retain community authority',all(sources[v['source_id']]['authority']=='secondary' and not r['client_cross_checked'] and not r['audio_reviewed'] for r in lc for v in r['variants']))
check('Bidirectional comparison links',all(all(i in rows and r['id'] in rows[i]['localization_check_ids'] for i in r['record_ids']) for r in lc) and all(all(i in byid and r['id'] in byid[i]['record_ids'] for i in r.get('localization_check_ids',[])) for r in rows.values()))
check('Comparison tables stay outside factual chunks',not any(r['collection']=='game_localization_checks' for r in chunks))
check('Chinese and Japanese record languages follow region',all({'CN':'zh-Hans','JP':'ja','Global':'en'}[r['server']]==r['language'] for r in rows.values()))
new=rows['AKL091']
check('Localized forgetting passage stays Japanese and attributed',new['server']=='JP' and new['language']=='ja' and new['subject_id']=='ak_iris' and new['speaker']=='爱丽丝' and new['assertion_kind']=='archive_assessment' and all(es[e]['language']=='ja' for e in new['evidence_ids']))
check('No localized passage automatically changes original canon',rows['AKL061']['server']=='CN' and rows['AKL061']['language']=='zh-Hans' and '真正的遗忘' not in rows['AKL061']['statement_zh'])
check('Localized passage requires paired context',set(chunk_byid['AKL091']['required_context_record_ids'])=={'AKL061'} and 'AKL091' in chunk_byid['AKL061']['required_context_record_ids'])
check('Differences are accessible in retrieval',all(chunk_byid[rid]['localization_notes'] and any(v['check_id'] in rows[rid]['localization_check_ids'] for v in chunk_byid[rid]['localization_notes']) for rid in ['AKL047','AKL068','AKL061','AKL091']))
check('Variant evidence is not mixed into Chinese claims',all(not any(v['evidence_id'] in rows[i]['evidence_ids'] for v in r['variants'] if v['server']!='CN') for r in lc if r['assessment']!='equivalent_core' for i in r['record_ids'] if i!='AKL091'))
check('All 38 own voice texts now verified in three languages',sum(r.get('voice_metadata',{}).get('text_languages_verified')==['zh-Hans','ja','en'] for r in rows.values())==38)
check('Gift difference retained across all three languages',all({'zh-Hans','ja','en'}.issubset({es[e]['language'] for e in rows[i]['evidence_ids']}) for i in ['AKL009','AKL016']) and next(r for r in kb['source_issues'] if r['id']=='SC004')['affected_record_ids']==['AKL009','AKL016'])
check('Mutsumi knowledge wording stays CN-scoped',rows['AKL068']['server']=='CN' and '些微' in rows['AKL068']['statement_zh'] and next(r for r in kb['source_issues'] if r['id']=='SC006')['affected_record_ids']==['AKL068'])
check('Anonymous listener remains a guess and future plan',rows['AKL010']['assertion_kind']=='character_guess' and rows['AKL008']['assertion_kind']=='future_plan' and next(r for r in kb['entities'] if r['id']=='ak_anonymous_listener')['name_zh']=='未具名的听众')
check('Research follows both remaining game questions',all(any(term in r['topic'] for r in kb['research_queue']) for term in ['匿名听众','赠送过程']))
check('Letter dates retain original CN scope',all(r['delivery_metadata']['server']=='CN' and r['server']=='CN' and r['event_calendar_date'] is None for r in rows.values() if r['material_type']=='event_letter'))
cases=[
    ('日服爱丽丝说真正的遗忘是什么','AKL091','promotion_record'),
    ('为什么说忘却是把困难变成自己的养分','AKL091','promotion_record'),
    ('日文晋升记录多出的那段勇气','AKL091','promotion_record'),
    ('日英文的生日曲是否可能困扰母亲','AKL047','voice'),
    ('祥子对睦的痛苦有多少了解','AKL068','operator_file'),
    ('New Friends 祥子知道朋友是谁','AKL074','module_story'),
    ('A Silent Pact 匿名听众','AKL010','module_story'),
    ('Talk after Trust Increase 3 娃娃','AKL016','voice'),
    ('夢のお城からの録音 道歉','AKL083','event_letter'),
    ('日文额外训练里的祥子怎么回应海铃','AKL075','module_story'),
]
outcomes=[]
for query,rid,material in cases:
    found=[r['record_id'] for r in search(query,limit=5,material=material)]
    outcomes.append(dict(query=query,expected=rid,material=material,top5=found,passed=rid in found))
if any(not x['passed'] for x in outcomes):
    print(json.dumps([x for x in outcomes if not x['passed']],ensure_ascii=False,indent=2))
check('Language-context queries',all(x['passed'] for x in outcomes))
check('New localized paragraph respects ending gate',not any(r['record_id']=='AKL091' for r in search('遗忘 勇气',limit=100,max_rank=14)))
result=dict(status='passed',checks=checks,cases=outcomes,scope='Localized text, provenance and retrieval; audio and client remain separate review tasks.')
if '--write-report' in sys.argv:
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/v17_retrieval.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
