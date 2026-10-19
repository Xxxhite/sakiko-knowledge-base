from pathlib import Path
import json,sys
from search_game import search,stage_rank
ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
records={x['id']:x for x in kb['game_story_records']}
inferences={x['id']:x for x in kb['game_interpretations']}
lore={x['id']:x for x in kb['game_lore_records']}
all_content={**records,**lore}
entities={x['id'] for x in kb['entities']}
sources={x['id']:x for x in kb['sources']}
evidence={x['id']:x for x in kb['evidence']}
chunks=json.loads((ROOT/'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))
checks=[]
def check(name,yes):
    assert yes,name
    checks.append(dict(check=name,result='passed'))
def recs(rows): return {x['record_id'] for x in rows}
check('Story actor/target and evidence references',all(r['subject_id'] in entities and all(x in entities for x in r['target_ids']) and all(x in evidence for x in r['evidence_ids']) for r in records.values()))
check('Transcripts retain community source qualification',all(sources[evidence[e]['source_id']]['source_type']=='game_script_transcription' and sources[evidence[e]['source_id']]['authority']=='secondary' for r in records.values() for e in r['evidence_ids']))
check('Game canon kept apart from evidence acquisition status',all(r['layer']=='canon' and r['evidence_status']=='game_text_transcription' and not r['client_cross_checked'] for r in records.values()))
check('Morpheus attack stays attributed character claim',records['AK013']['assertion_kind']=='other_character_claim' and records['AK013']['speaker']=='莫菲丝' and records['AK013']['subject_id']=='ak_morpheus')
check('Dream mother separated from historical mother',records['AK025']['subject_id']=='ak_dream_mother' and records['AK017']['target_ids']==['mother'])
check('Quoted dream Mutsumi actor preserved',records['AK012']['subject_id']=='ak_dream_mutsumi_voice' and records['AK012']['narrative_level']=='mutsumi_dream')
check('Dream reveal gate uses later disclosure',records['AK003']['spoiler_rank']==stage_rank('SS-1-END'))
check('Interpretation basis and spoiler dependency',all(all(x in all_content for x in r['basis_record_ids']) and r['spoiler_rank']>=max(all_content[x]['spoiler_rank'] for x in r['basis_record_ids']) for r in inferences.values()))
check('Question index references story or inference',all(all(x in records or x in inferences or x in lore for x in r['record_ids']) for r in kb['game_question_index']))
check('Scene relationship reference and context',all(r['subject_id'] in entities and r['object_id'] in entities and all(x in records for x in r['basis_record_ids']) and r['narrative_level']==records[r['basis_record_ids'][0]]['narrative_level'] for r in kb['game_relations']))
check('Game retrieval coverage and aliases',len(chunks)==len(records)+len(inferences)+len(lore) and all(c['continuity']=='arknights_collab' and not c['official_only_eligible'] for c in chunks))
check('Default excludes game inference',all(r['layer']=='canon' for r in search('成长 音乐 责任',limit=100)))
check('Opt in includes game inference','AKI001' in recs(search('责任 成长',limit=100,include_inference=True)))
check('Official-only does not promote copied scripts',search('母亲',official=True)==[])
check('Progress filter excludes late story',all(r['spoiler_rank']<=14 for r in search('母亲 结局',limit=100,max_rank=stage_rank('SS-7-END'))))
check('Initial dream disclosure stays hidden before reveal',not recs(search('生日',max_rank=stage_rank('SS-1-BEG'))))

cases=[
('为何答应造梦者的挑战','AK004'),
('给安过生日时弹的是什么','AK003'),
('小祥把喵梦当战友吗','AK019'),
('她觉得海铃可靠不可靠','AK020'),
('岛上的初音与祥子是否错过','AK009'),
('是谁把她推到悬崖下面','AK012'),
('造梦者骂她自私的那段','AK013'),
('明明清醒却舍不得妈妈','AK024'),
('最后有没有向伙伴道歉','AK031'),
('她为何说自己不了解成员内心','AK034'),
('她重新见到队友时开不开心','AK032'),
('演奏如何影响人偶丝线','AK030')]
outcomes=[]
for query,expected in cases:
    found=[x['record_id'] for x in search(query,limit=5)]
    outcomes.append(dict(query=query,expected=expected,top5=found,passed=expected in found))
check('Natural Chinese retrieval cases',all(x['passed'] for x in outcomes))
result=dict(status='passed',checks=checks,cases=outcomes,scope='Local term/bigram ranking, attribution and metadata checks; no embedding or language-model answer evaluation.')
if '--write-report' in sys.argv:
    (ROOT/'validation/game_retrieval.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
