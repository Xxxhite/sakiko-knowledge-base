"""Check MyGO supplementation, work identity and original retrieval."""
from pathlib import Path
import json
import sys
from search_base import search, normalize_original

ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
chunks=json.loads((ROOT/'data/retrieval_chunks.json').read_text(encoding='utf-8'))
byid={r['record_id']:r for r in chunks}
facts={r['id']:r for r in kb['facts']}
sources={r['id']:r for r in kb['sources']}
evidence={r['id']:r for r in kb['evidence']}
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(dict(check=name,result='passed'))
check('Episode work and number are unique',len({(r['work_id'],r['episode']) for r in kb['episode_catalog']})==len(kb['episode_catalog']))
check('MyGO and Ave episode 13 are different entries',{r['work_id'] for r in kb['episode_catalog'] if r['episode']==13}=={'bang_dream_its_mygo','bang_dream_ave_mujica'})
check('Old EP IDs remain Ave Mujica',all(r['work_id']=='bang_dream_ave_mujica' for r in kb['episode_catalog'] if r['id'].startswith('EP')))
check('MyGO unreviewed playback and positions stay empty',all(not r['full_episode_reviewed'] and r['official_playback_url'] is None and r['subtitle_version'] is None and r['timecode_start'] is None and r['timecode_end'] is None for r in kb['episode_catalog'] if r['id'].startswith('MYGO')))
for fid in ['F069','F070','F071','F072','F073','F074']:
    row=facts[fid]
    check(fid+' attributed primary retelling',row['evidence_status']=='primary_interview_explicit' and row['epistemic_scope']=='attributed_plot_report' and all(sources[evidence[e]['source_id']]['authority']=='creator_first_person' and evidence[e]['verification_status']=='direct_text_verified' for e in row['evidence_ids']))
check('Writer interpretation remains separately attributed',next(r for r in kb['inferences'] if r['id']=='I007')['interpretation_author'].startswith('绫奈') and byid['I007']['layer']=='inference')
for fid in ['F075','F076','F077','F078','F079']:
    row=facts[fid]
    check(fid+' primary retelling and direct evidence',row['evidence_status']=='primary_interview_explicit' and row['epistemic_scope']=='attributed_plot_report' and all(sources[evidence[e]['source_id']]['authority']=='creator_first_person' and evidence[e]['verification_status']=='direct_text_verified' for e in row['evidence_ids']))
for fid in ['F080','F081','F082','F083']:
    row=facts[fid]
    check(fid+' explicit cast retelling',row['layer']=='canon' and row['evidence_status']=='primary_interview_explicit' and row['valid_time']['phase']=='mygo_ep03' and all(evidence[e]['source_id']=='S117' for e in row['evidence_ids']))
for sid,url in [('S117','https://www.lisani.jp/0000233447/'),('S118','https://www.lisani.jp/0000234940/')]:
    check(sid+' actual reading and upstream URLs are both retained',sources[sid]['original_url'].startswith('https://news.livedoor.com/article/detail/') and sources[sid]['resolved_url']==sources[sid]['original_url'] and url in sources[sid]['access_note'] and '实际读取' in sources[sid]['access_note'])
check('Notebook song is a character action, not real production duration',facts['F080']['subject_id']=='sakiko' and facts['F080']['predicate']=='set_notebook_words_to_song' and '30' not in facts['F080']['statement_zh'])
check('Downhill corroboration retains the episode anchor',set(facts['F073']['evidence_ids'])=={'E425','E445'} and facts['F073']['valid_time']['phase']=='mygo_ep04' and '未标集数' in facts['F073']['notes'])
maracas=next(r for r in kb['inferences'] if r['id']=='I010')
check('Maracas explanation remains an attributed tentative reading',maracas['interpretation_author'].startswith('林鼓子') and maracas['strength']=='limited' and byid['I010']['layer']=='inference' and all('E444' not in r['evidence_ids'] for r in kb['facts']))
check('Two spring-song performances retain different groups and episodes',facts['F081']['subject_id']=='crychic' and facts['F081']['valid_time']['phase']=='mygo_ep03' and facts['F078']['valid_time']['phase']=='mygo_ep07')
check('Chinese and Arabic episode phrases normalize equivalently',normalize_original('第三集')==normalize_original('第3话') and normalize_original('第十三話')==normalize_original('第13集') and normalize_original('第十四集')=='第十四集')
check('A paginated interview is one source with actual page locations',sources['S119']['published_on']=='2025-03-06' and '&p=2' in sources['S119']['access_note'] and '&p=3' in sources['S119']['access_note'] and all(evidence[e]['source_id']=='S119' for e in ['E446','E447','E448','E449','E450']))
check('Recruitment action is separate from director motive',facts['F084']['evidence_ids']==['E446'] and next(r for r in kb['inferences'] if r['id']=='I011')['evidence_ids']==['E448'] and byid['I011']['layer']=='inference')
check('Ring denial retains its speaker and scene',facts['F085']['subject_id']=='sakiko' and facts['F085']['predicate']=='uttered_denial_after_video' and 'RiNG' in facts['F085']['statement_zh'] and '监督复述' in facts['F085']['statement_zh'] and '发言人：祥子' in byid['F085']['text'])
check('Denial leaves the established childhood relationship intact',facts['F039']['predicate']=='childhood_friend' and next(r for r in kb['relations'] if r['id']=='R005')['direction']=='symmetric' and next(r for r in kb['relations'] if r['id']=='R042')['predicate']=='uttered_denial_about')
check('Unspecified recruitment episode stays unspecified',next(r for r in kb['timeline'] if r['id']=='T023')['reveal']['episode'] is None and not any('F085' in r['related_record_ids'] for r in kb['episode_catalog']))
check('Episode-eight corroboration preserves older evidence',set(facts['F072']['evidence_ids'])=={'E426','E430','E450','E459'} and 'E450' in next(r for r in kb['episode_catalog'] if r['id']=='MYGO08')['evidence_ids'])
check('Corrected interview version is identifiable',sources['S115']['original_url']=='https://animageplus.jp/news/detail/96' and sources['S115']['published_on']=='2024-12-20' and '订正版' in sources['S115']['access_note'])
check('Song composition has a diegetic scope',facts['F077']['predicate']=='diegetic_composed_song' and facts['F077']['continuity']=='tv_anime' and '剧中' in facts['F077']['statement_zh'])
check('Father-line update preserves scriptwriter and earlier cast evidence',set(facts['F074']['evidence_ids'])=={'E429','E439','E455'} and '绫奈' in facts['F074']['statement_zh'] and '高尾' in facts['F074']['statement_zh'])
check('Episode twelve utterance has an explicit cast episode anchor',facts['F086']['valid_time']['phase']=='mygo_ep12' and facts['F086']['evidence_ids']==['E452'] and next(r for r in kb['timeline'] if r['id']=='T024')['reveal']['episode']==12 and next(r for r in kb['relations'] if r['id']=='R043')['object_id']=='nyamu')
check('Episode twelve title keeps its indexed evidence separate',next(r for r in kb['episode_catalog'] if r['id']=='MYGO12')['evidence_ids']==['E452','E454'] and evidence['E454']['verification_status']=='indexed_text_verified' and evidence['E452']['verification_status']=='direct_text_verified')
check('Broadcast date is separate from story calendar',next(r for r in kb['episode_catalog'] if r['id']=='MYGO13')['announced_broadcast_date']=='2023-09-14' and evidence['E456']['source_id']=='S122' and 'E456' not in facts['F074']['evidence_ids'] and facts['F074']['valid_time']['calendar_date'] is None)
check('Forgetting expression retains the question-answer distinction',facts['F087']['valid_time']['phase']=='mygo_haruhikage_aftermath' and '提问' in facts['F087']['notes'] and not any('F087' in r['related_record_ids'] for r in kb['episode_catalog']))
check('Mutsumi reading remains attributed and optional',next(r for r in kb['inferences'] if r['id']=='I013')['interpretation_author'].startswith('渡瀬') and byid['I013']['layer']=='inference' and all('E457' not in r['evidence_ids'] for r in kb['facts']))
check('Ultimatum and plea retain opposite actor directions',facts['F088']['subject_id']=='sakiko' and facts['F089']['subject_id']=='soyo' and {(r['subject_id'],r['object_id']) for r in kb['relations'] if r['id'] in ['R044','R045']}=={('sakiko','soyo'),('soyo','sakiko')})
check('Cast retelling does not invent the full ultimatum dialogue',facts['F088']['evidence_ids']==['E458'] and evidence['E458']['source_id']=='S123' and '逐句' in facts['F088']['notes'] and sources['S123']['original_url']=='https://news.livedoor.com/article/detail/24798231/' and 'https://www.lisani.jp/0000236253/' in sources['S123']['access_note'])
check('Hope for reunion remains cast interpretation',next(r for r in kb['inferences'] if r['id']=='I014')['interpretation_author'].startswith('小日向') and byid['I014']['layer']=='inference' and all('E460' not in r['evidence_ids'] for r in kb['facts']))
check('Audience absence preserves the earlier reunion evidence',set(facts['F051']['evidence_ids'])=={'E36','E461'} and '没有观众' in facts['F051']['statement_zh'] and set(next(r for r in kb['timeline'] if r['id']=='T012')['evidence_ids'])=={'E36','E461'})
check('Farewell meaning stays separate from performance conditions',byid['I015']['layer']=='inference' and evidence['E462']['source_id']=='S119' and 'E462' not in facts['F051']['evidence_ids'] and next(r for r in kb['inferences'] if r['id']=='I015')['interpretation_author'].startswith('柿本'))
check('Two episode sevens keep distinct works and evidence',next(r for r in kb['episode_catalog'] if r['id']=='EP07')['work_id']=='bang_dream_ave_mujica' and next(r for r in kb['episode_catalog'] if r['id']=='MYGO07')['work_id']=='bang_dream_its_mygo' and evidence['E463']['verification_status']=='indexed_text_verified')
check('Only-me question remains Soyo utterance',facts['F090']['subject_id']=='soyo' and facts['F090']['predicate']=='asked_if_only_she_wanted_reunion' and facts['F090']['value']=='どうして……？私だけなの……？' and evidence['E464']['source_id']=='S124')
check('Early singing and later encouragement keep distinct phases',facts['F091']['valid_time']['phase']=='crychic_beginning' and facts['F070']['valid_time']['phase']=='mygo_ep07' and next(r for r in kb['timeline'] if r['id']=='T026')['reveal']['episode'] is None)
check('Final memory line keeps its actual speaker and addressee',facts['F092']['subject_id']=='soyo' and facts['F092']['valid_time']['phase']=='mygo_ep13' and '向灯' in facts['F092']['statement_zh'] and evidence['E466']['source_id']=='S124')
check('Song reading remains tentative and attributed',next(r for r in kb['inferences'] if r['id']=='I016')['strength']=='limited' and next(r for r in kb['inferences'] if r['id']=='I016')['interpretation_author'].startswith('林鼓子') and all('E467' not in r['evidence_ids'] for r in kb['facts']))
check('Early Ave catalog preserves synopsis evidence while adding primary scenes',{'E468','E42','E482','E483','E484'}.issubset(next(r for r in kb['episode_catalog'] if r['id']=='EP01')['evidence_ids']) and next(r for r in kb['episode_catalog'] if r['id']=='EP03')['plot_evidence_level']=='primary_interview_retelling' and next(r for r in kb['episode_catalog'] if r['id']=='EP05')['plot_evidence_level']=='official_synopsis' and all(evidence[i]['verification_status']=='indexed_text_verified' for i in ['E468','E469','E470']))
interpretations={r['id']:r for r in kb['inferences']}
check('Director and actor readings keep separate authors',interpretations['I008']['interpretation_author'].startswith('柿本') and interpretations['I009']['interpretation_author'].startswith('高尾') and all(byid[r]['layer']=='inference' and '解读者：' in byid[r]['text'] for r in ['I008','I009']))
check('Founding and departure have directed phase-specific edges',all(next(r for r in kb['relations'] if r['id']==rid)['subject_id']=='sakiko' and next(r for r in kb['relations'] if r['id']==rid)['object_id']=='crychic' for rid in ['R037','R038']) and next(r for r in kb['relations'] if r['id']=='R037')['valid_time']['phase']!=next(r for r in kb['relations'] if r['id']=='R038')['valid_time']['phase'])
check('Question navigation references only original chunks',all(not r['default_retrieval_eligible'] and all(rid in byid for rid in r['record_ids']) for r in kb['original_question_index']))
check('Question navigation excluded from fact chunks',not any(r['record_id'].startswith('BQ') for r in chunks))
check('Related old views gain fixed episode 8 evidence',all('E423' in next(r for r in kb[n] if r['id']==rid)['evidence_ids'] for n,rid in [('relations','R024'),('timeline','T004')]))
cases=[
 ('旧团第一次演出完，小祥跟灯说了什么','F069',False),
 ('第3话为什么要照镜子','F069',False),
 ('祥子怎样给碧天伴走应援','F070',False),
 ('灯说歌是心的呐喊，这句话跟祥子什么关系','F071',False),
 ('素世在第八集最后抓住谁','F072',False),
 ('爽世在校门打招呼后为什么追上去','F073',False),
 ('十三话里她怎么称呼父亲','F074',False),
 ('くそ親父','F074',False),
 ('小祥在旧乐队是弹什么和写什么','F018',False),
 ('初华还喜欢星星吗','F067',False),
 ('祥子流泪以后约了谁','F042',False),
 ('编剧如何理解祥子的眼泪以及组建新乐队','I007',True),
 ('旧团CRYCHIC最初是谁发起的','F075',False),
 ('小祥后来离开了原来的乐队吗','F076',False),
 ('春日影在故事里是谁写的曲','F077',False),
 ('剧情里春日影的创作者','F077',False),
 ('第7集祥子看到了什么现场演唱','F078',False),
 ('她在现场听到了MyGO演唱的哪首歌','F078',False),
 ('Oblivionis这个名字从哪里来','F079',False),
 ('忘却之湖和祥子的艺名有什么关联','F079',False),
 ('监督怎样解释遗忘和新身份保护自己','I008',True),
 ('高尾怎样演绎祥子外在愤怒内在悲伤','I009',True),
 ('祥子是怎样把灯写在本子上的话变成歌的','F080',False),
 ('人間になりたいうた是谁串起了笔记里的文字','F080',False),
 ('第三集旧团舞台上唱的是哪一首曲子','F081',False),
 ('CRYCHIC那次春日影演出，灯伸手时小祥做了什么','F082',False),
 ('祥子有没有在演出中点头回应灯','F082',False),
 ('旧乐队大家一起去KTV是哪个回忆','F083',False),
 ('灯为什么在卡拉OK拿沙槌，林鼓子怎么猜的','I010',True),
 ('羊宫提到过素世追小祥下坡的场景吗','F073',False),
 ('她怎么和喵梦谈妥加入乐队的','F084',False),
 ('组团时小祥和若麦有过交换条件的交涉吗','F084',False),
 ('看了Mortis爆红视频后她在RiNG门前说了什么','F085',False),
 ('睦など、知りません是谁说的','F085',False),
 ('祥子说不认识睦，那青梅竹马关系的依据呢','F039',False),
 ('监督觉得喵梦从祥子的衣着看出了什么','I011',True),
 ('柿本如何解释祥子睦爽世的心理距离变化','I012',True),
 ('MyGO第八话抓住祥子的互动，导演也提过吗','F072',False),
 ('第十二集祥子跟喵梦说的双利手是怎么回事','F086',False),
 ('あなた両利きですわね','F086',False),
 ('小祥对若麦提到左右手的那句在第几话','F086',False),
 ('米澤提到了第12话哪个问句','F086',False),
 ('忘れさせて这句话是谁用过的','F087',False),
 ('高尾谈到祥子让我忘记的措辞','F087',False),
 ('渡瀬怎么理解睦夹在祥子和爽世中间的处境','I013',True),
 ('第13话最后关于父亲的话高尾也提过吗','F074',False),
 ('第八集祥子对素世下了最后通告吗','F088',False),
 ('第8话她给爽世最后通告是谁复述的','F088',False),
 ('爽世如何恳求小祥让旧团回来','F089',False),
 ('抓住祥子请求复活CRYCHIC','F089',False),
 ('第8话是谁向祥子恳求回到旧乐队','R045',False),
 ('第8话谁认为旧团大家都想回来','I014',True),
 ('爽世以为灯立希也想回CRYCHIC是谁解读的','I014',True),
 ('Ave第7话旧团重聚现场有观众吗','F051',False),
 ('监督如何理解第7话旧团重聚和告别','I015',True),
 ('灯在最后一次CRYCHIC演出怎么理解祥子','I015',True),
 ('どうして私だけなの','F090',False),
 ('爽世第八集为什么问只有我一个','F090',False),
 ('这句只有我吗是祥子还是素世说的','F090',False),
 ('灯最初怎么在小祥带领下开始唱歌','F091',False),
 ('羊宫回顾谁引领她在CRYCHIC唱歌','F091',False),
 ('第13话素世对灯说忘不了旧团','F092',False),
 ('最终话她说一辈子忘不了CRYCHIC','F092',False),
 ('林鼓子如何解读迷路日々中灯无意伤到祥子','I016',True),
 ('歌曲里双方受伤的解释是谁的理解','I016',True),
 ('CRYCHIC刚开始的引领和第7话应援有什么区别','R046',False),
 ('第五话解散以后成员回到什么生活','F093',False),
 ('全国巡演中断后各自的生活','F093',False),
 ('监督怎么理解人間になりたいうたⅡ与祥子','I017',True),
 ('灯不了解祥子却想继续思考她','I017',True),
 ('立希珍惜旧团却不愿再和小祥组团是谁的理解','I018',True),
 ('柿本如何解释立希对祥子的别扭与自我保护','I018',True),
 ('小祥识别他人才能的审美眼光与成长环境','I019',True),
 ('高尾认为祥子在顺境逆境中如何寄托情感','I020',True),
 ('MyGO第十三话新乐队唱的同名曲','F094',False),
 ('MyGO第13集Ave Mujica舞台歌曲','F094',False),
 ('第十话灯在星象馆见到谁','F095',False),
 ('第10话灯和初华在哪里相遇','F095',False),
 ('初华跟灯说歌能传达心意是哪一段','F096',False),
 ('天文馆那段是谁向灯谈超越言语的表达','F096',False),
 ('林鼓子如何解释立希对祥子的憧憬','I021',True),
 ('作曲时想到祥子并为比较而烦恼是谁的理解','I021',True),
 ('初华役佐々木也复述了祥子祖父关系吗','F047',False),
 ('佐佐木关于初华父亲是定治的家系旁证','F048',False),
 ('Ave第一话父亲向祥子扔了东西吗','F097',False),
 ('她爸爸对她投掷物品的场景','R048',False),
 ('退出CRYCHIC之后她哭了是哪段回顾','F098',False),
 ('高尾说退团直后的哭泣在哪一话披露','T029',False),
 ('母亲去世的场景定位在哪一集','T031',False),
 ('睦拿伞站在大哭祥子身后是哪层画面','F099',False),
 ('第三话睦深层世界持伞的画面','F099',False),
 ('高尾为何觉得她不想给别人添麻烦而难开口','I022',True),
 ('睦是唯一知道祥子境遇的人是谁的推测','I023',True),
 ('渡瀬怎么理解睦知道她退团心情和伞的关系','I023',True),
]
outcomes=[]
for query,rid,inference in cases:
    found=[r['record_id'] for r in search(query,include_inference=inference)]
    outcomes.append(dict(query=query,expected=rid,top5=found,passed=rid in found))
if not all(r['passed'] for r in outcomes):print(json.dumps([r for r in outcomes if not r['passed']],ensure_ascii=False,indent=2))
check('Original-work natural queries',all(r['passed'] for r in outcomes))
check('Default search keeps interpretation off',all(r['layer']=='canon' for r in search('编剧 泪水 结成',limit=100)))
check('Default reunion search keeps attributed inner readings off',not {'I014','I015'}&{r['record_id'] for r in search('旧团 回来 理解 告别',limit=1000)})
check('Official filter excludes interview-only facts',not {'F069','F070','F071','F072','F073','F074'}&{r['record_id'] for r in search('祥子',limit=1000,official=True)})
check('Official fixed synopsis remains searchable','F067' in {r['record_id'] for r in search('初华 星星',official=True,direct=True)})
check('Direct-only retains actually read interviews','F069' in {r['record_id'] for r in search('初演 表情 镜子',direct=True)})
phase_rows=search('照镜子',phase='mygo_ep03')
check('Phase filter separates the two episode threes','F069' in {r['record_id'] for r in phase_rows} and all(r['phase'].startswith('mygo_ep03') for r in phase_rows) and 'F031' not in {r['record_id'] for r in phase_rows})
check('Planetarium utterance keeps Uika as speaker and Tomori as listener',facts['F096']['subject_id']=='uika' and facts['F096']['value']=='tomori' and next(r for r in kb['relations'] if r['id']=='R047')['subject_id']=='uika' and next(r for r in kb['relations'] if r['id']=='R047')['object_id']=='tomori')
check('Planetarium official index and attributed dialogue keep distinct evidence modes',facts['F095']['evidence_status']=='official_explicit' and evidence['E480']['verification_status']=='indexed_text_verified' and facts['F096']['evidence_status']=='primary_interview_explicit' and all(evidence[e]['verification_status']=='direct_text_verified' for e in facts['F096']['evidence_ids']))
check('New family corroboration retains earlier evidence and genealogy inference',all({'E32','E479'}.issubset(next(r for r in kb[n] if r['id']==rid)['evidence_ids']) for n,rid in [('facts','F047'),('facts','F048'),('relations','R025'),('relations','R026')]) and byid['I004']['layer']=='inference' and 'E479' in byid['I004']['evidence_ids'])
check('Voice actor reading remains opt in',next(r for r in kb['inferences'] if r['id']=='I021')['interpretation_author'].startswith('林鼓子') and 'I021' not in {r['record_id'] for r in search('立希 祥子 憧憬',limit=1000)})
check('Family scene retains father-to-daughter direction',facts['F097']['subject_id']=='father' and facts['F097']['value']=='sakiko' and next(r for r in kb['relations'] if r['id']=='R048')['object_id']=='sakiko')
check('Umbrella scene retains inner-world scope',facts['F099']['valid_time']['phase']=='ave_ep03_inner_world' and '深层世界' in byid['F099']['text'] and byid['F099']['layer']=='canon')
check('Exclusive knowledge is an attributed tentative reading',interpretations['I023']['strength']=='limited' and interpretations['I023']['interpretation_author'].startswith('渡瀬') and all('E487' not in r['evidence_ids'] for r in kb['facts']) and 'I023' not in {r['record_id'] for r in search('睦 唯一 知情',limit=1000)})
check('Official death fact preserves its own evidence qualification',facts['F023']['evidence_ids']==['E14'] and facts['F023']['evidence_status']=='official_explicit' and next(r for r in kb['timeline'] if r['id']=='T031')['evidence_ids']==['E482'])
identity_rows=search('祥子',limit=100)
check('A pure character-name query returns cited records',bool(identity_rows) and all(r['citations'] and all(c['locator'] and c['original_url']==sources[c['source_id']]['original_url'] for c in r['citations']) for r in identity_rows))
result=dict(status='passed',checks=checks,cases=outcomes,scope='Primary interview attribution, distinct work episode identities and original-work local retrieval.')
if '--write-report' in sys.argv:
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/v110_original.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
