"""Check voice inventory, material attribution, event dates and relationship phases."""
from pathlib import Path
import json
import sys
from search_game import search

ROOT = Path(__file__).resolve().parents[1]
kb = json.loads((ROOT / 'data/kb.json').read_text(encoding='utf-8'))
lore = {r['id']: r for r in kb['game_lore_records']}
rows = {r['id']: r for name in ('game_story_records', 'game_lore_records') for r in kb[name]}
evidence = {r['id']: r for r in kb['evidence']}
sources = {r['id']: r for r in kb['sources']}
chunks = json.loads((ROOT / 'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))
checks = []


def check(name, condition):
    assert condition, name
    checks.append(dict(check=name, result='passed'))


voices = [r for r in lore.values() if r.get('material_owner_id') == 'sakiko' and r['material_type'] == 'voice']
expected = {f'CN_{i:03d}' for i in [*range(1, 15), *range(17, 35), 36, 37, 38, 42, 43, 44]}
check('All 38 distinct Sakiko voice slots', len(voices) == 38 and {r['voice_metadata']['voice_id'] for r in voices} == expected)
by_voice = {r['voice_metadata']['voice_id']: r for r in voices}
check('Original voice record IDs retained', all(by_voice[voice]['id'] == rid for voice, rid in {
    'CN_001':'AKL011','CN_002':'AKL012','CN_004':'AKL018','CN_005':'AKL013','CN_006':'AKL014',
    'CN_007':'AKL015','CN_008':'AKL019','CN_009':'AKL016','CN_010':'AKL017','CN_014':'AKL020'}.items()))
check('Trust requirements 40 100 200', [by_voice[v]['voice_metadata']['unlock_params'] for v in ['CN_007','CN_008','CN_009']] == [[40],[100],[200]])
check('Promotion voice phase mapping', [by_voice[v]['voice_metadata']['unlock_params'] for v in ['CN_005','CN_006','CN_013','CN_014']] == [[1,1],[2,1],[1,1],[2,1]])
check('Seasonal placement is separate from direct unlock', all(by_voice[v]['voice_metadata']['place_type'] == place and by_voice[v]['voice_metadata']['unlock_type'] == 'DIRECT' for v,place in [('CN_038','NEW_YEAR'),('CN_043','BIRTHDAY'),('CN_044','ANNIVERSARY')]))
check('All voices have source label and exact resource key', all(r['trigger_label'] and r['unlock_condition'] and r['voice_metadata']['char_word_id'] == 'char_4182_oblvns_' + r['voice_metadata']['voice_id'] and r['voice_metadata']['voice_asset'] == 'char_4182_oblvns/' + r['voice_metadata']['voice_id'] for r in voices))
check('Bilingual text status does not promote audio review', all({'zh-Hans','ja'}.issubset(r['voice_metadata']['text_languages_verified']) and not r['voice_metadata']['audio_reviewed'] and any(evidence[e]['language'] == 'ja' for e in r['voice_metadata']['localization_evidence_ids']) for r in voices))
check('Voice trigger and unlock fields reach retrieval', all(next(c for c in chunks if c['record_id'] == r['id'])['voice_metadata'] == r['voice_metadata'] and next(c for c in chunks if c['record_id'] == r['id'])['trigger_label'] == r['trigger_label'] for r in voices))
material_pairs = {'operator_file':('OPERATOR_FILE','FILE'), 'promotion_record':('OPERATOR_FILE','FILE'),
                  'voice':('VOICE','VOICE'), 'event_letter':('EVENT_LETTER','LETTER'),
                  'event_interface':('EVENT_HALL','INTERFACE'), 'outfit_description':('OUTFIT','OUTFIT'),
                  'item_description':('ITEM','ITEM'), 'operator_contract':('CONTRACT','CONTRACT')}
check('Supplement stages agree with material', all((r['stage'],r['segment']) == material_pairs[r['material_type']] if r['material_type'] != 'module_story' else r['stage'] in ('MODULE_LOR_Y','MODULE_OTHER') and r['segment'] == 'MODULE' for r in lore.values()))
letters = [r for r in lore.values() if r['material_type'] == 'event_letter']
check('Five letters and signed authors', len(letters) == 5 and [r['speaker'] for r in letters] == ['可露希尔','红豆','温米','爱丽丝','莫菲丝'])
check('Delivery times do not become story dates', all(r['event_calendar_date'] is None and r['delivery_metadata']['date_kind'] == 'real_world_event_delivery' and r['delivery_metadata']['server'] == 'CN' and r['delivery_metadata']['local_time'].endswith('+08:00') for r in letters))
check('Dream costume scoped to its descriptive material', lore['AKL088']['material_type'] == 'outfit_description' and lore['AKL088']['narrative_level'] == 'dream_costume_description')
check('Teammate file actor and owner preserved', lore['AKL067']['subject_id'] == 'sakiko' and lore['AKL067']['material_owner_id'] == 'mutsumi' and lore['AKL072']['subject_id'] == 'uika' and lore['AKL072']['speaker'] == '爱丽丝')
check('Module narrator knowledge separate from Sakiko knowledge', '未弄清' in lore['AKL074']['statement_zh'] and lore['AKL074']['material_owner_id'] == 'mutsumi')
check('All story segments fully read as text', len(kb['game_scene_coverage']) == 18 and all(r['review_status'] == 'full_text_reviewed' and not r['client_cross_checked'] for r in kb['game_scene_coverage']))
check('Supplement inventories complete within declared scope', len(kb['game_material_coverage']) == 7 and all(r['expected_slots'] == r['covered_slots'] and all(i in lore for i in r['record_ids']) for r in kb['game_material_coverage']))
check('Inventories excluded from factual retrieval', not any(c['record_id'].startswith('AKMC') for c in chunks))
check('Relationship phases reference same source scope', all(all(i in rows for i in r['basis_record_ids']) and r['narrative_level'] == rows[r['basis_record_ids'][0]]['narrative_level'] and set(r['evidence_ids']).issubset({e for i in r['basis_record_ids'] for e in rows[i]['evidence_ids']}) for r in kb['game_relations']))
check('Doctor learning and Vigna letter relationship available', any(r['object_id'] == 'ak_doctor' and r.get('phase_group') == 'rhodes_island_daily_life' for r in kb['game_relations']) and any(r['subject_id'] == 'ak_vigna' and r.get('phase_group') == 'letter_support' for r in kb['game_relations']))
check('Gift conflict retains fixed CN sources and Japanese wording', all(e in next(r for r in kb['source_issues'] if r['id'] == 'SC004')['evidence_ids'] for e in lore['AKL009']['evidence_ids'] + lore['AKL016']['evidence_ids']))
check('All new material remains attributed community text', all(r['evidence_status'] == 'game_text_transcription' and not r['client_cross_checked'] and all(sources[evidence[e]['source_id']]['authority'] == 'secondary' for e in r['evidence_ids']) for r in lore.values()))

cases = [
    ('她喜欢把不同饮料混在一起喝吗','AKL021','voice'),
    ('精英化时她怎么评价自己的队长能力','AKL024','voice'),
    ('她在战败的时候说什么','AKL040','voice'),
    ('她给博士过生日会弹什么','AKL047','voice'),
    ('她的新年第一句问候是什么','AKL045','voice'),
    ('她邀请博士坐贵宾席参加舞会','AKL046','voice'),
    ('信赖触摸会怎样回应','AKL043','voice'),
    ('她的生日和身高写在哪里','AKL049','operator_file'),
    ('她的血液源石结晶密度公开了吗','AKL050','operator_file'),
    ('父亲遭诈骗后她为什么打零工','AKL055','operator_file'),
    ('她害怕自己的选择给同伴带来痛苦','AKL059','promotion_record'),
    ('祥子嘱托罗德岛别给睦太多压力','AKL067','operator_file'),
    ('初华和祥子晚上在甲板做什么','AKL070','operator_file'),
    ('睦的新朋友身份祥子知道吗','AKL074','module_story'),
    ('海铃走神她会追问到底吗','AKL075','module_story'),
    ('若麦认为谁适合做指挥','AKL078','voice'),
    ('莫菲丝事后有道歉和送布景吗','AKL083','event_letter'),
    ('红豆有没有提议以后一起合奏','AKL080','event_letter'),
    ('爱丽丝为她们舞会送了什么','AKL082','event_letter'),
    ('五封来信齐了以后演出有什么变化','AKL085','event_interface'),
    ('旋律的主人是在梦中出现的服装吗','AKL088','outfit_description'),
    ('通常放在钢琴上的信物是什么','AKL089','item_description'),
    ('招聘合同怎么评价她的责任','AKL090','operator_contract'),
    ('她看见安家里的醉酒男人什么反应','AK087','main_story'),
    ('她核查海铃被指控时追问有没有亲眼看见','AK052','main_story'),
    ('错过初华的船她还想追上去吗','AK099','main_story'),
    ('家庭梦第一次返程邀请她犹豫了吗','AK018','main_story'),
    ('五个人醒来她向谁问回家的办法','AK036','main_story'),
    ('最后她抓住队友伸来的手登台','AK038','main_story'),
    ('她如何配合红豆寻找安','AK001','main_story'),
]
outcomes = []
for query, expected_id, material in cases:
    found = [r['record_id'] for r in search(query, limit=5, material=material)]
    outcomes.append(dict(query=query, expected=expected_id, material=material, top5=found, passed=expected_id in found))
if any(not r['passed'] for r in outcomes):
    print(json.dumps([r for r in outcomes if not r['passed']],ensure_ascii=False,indent=2))
check('Voice file teammate letter and transition queries', all(r['passed'] for r in outcomes))
check('Letter material filter preserves paired gift context obligation', all(c['material_type'] == 'event_letter' for c in search('舞会 帮忙', material='event_letter',limit=100)))
check('Ending gate excludes letters and costumes', not any(c['material_type'] in ('event_letter','outfit_description','event_interface') for c in search('舞会 梦境',max_rank=14,limit=100)))
result = dict(status='passed', checks=checks, cases=outcomes,
              scope='Inventory and evidence-aware local retrieval; audiovisual review remains separately tracked.')
if '--write-report' in sys.argv:
    (ROOT / 'validation').mkdir(exist_ok=True)
    (ROOT / 'validation/v16_retrieval.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result,ensure_ascii=False,indent=2))
