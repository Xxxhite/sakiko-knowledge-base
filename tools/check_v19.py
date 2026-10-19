"""Verify reviewed game answers and the first original-work supplementation."""
from pathlib import Path
import json
import sys
from context_game import assemble

ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
content={r['id']:r for n in ('game_story_records','game_lore_records') for r in kb[n]}
guides={r['id']:r for r in kb['game_discussion_guides']}
sources={r['id']:r for r in kb['sources']}
evidence={r['id']:r for r in kb['evidence']}
facts={r['id']:r for r in kb['facts']}
reviews=kb['game_answer_reviews']
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(dict(check=name,result='passed'))
check('Twelve reviewed answers',len(reviews)==12 and {r['guide_id'] for r in reviews}==set(guides))
maintenance=kb['metadata']['maintenance']
check('Maintenance handoff names actual answer reviews',set(maintenance['game_answer_review_ids'])=={r['id'] for r in reviews} and maintenance['active_focus']=='bang_dream_original' and maintenance['game_text_status']=='text_reference_complete' and maintenance['delivery_mode']=='repository_only')
for review in reviews:
    refs={rid for sentence in review['answer_sentences'] for rid in sentence['record_ids']}
    check(review['id']+' sentence references',refs==set(review['record_ids']) and refs==set(guides[review['guide_id']]['record_ids']))
    check(review['id']+' manual review identity',review['review_method']=='single_editor_evidence_check' and review['review_status']=='passed' and not review['default_retrieval_eligible'])
    check(review['id']+' spoiler gate',review['spoiler_rank']==max(content[r]['spoiler_rank'] for r in refs))
    context=assemble(review['question_zh'],guide_id=review['guide_id'])
    selected={r['record_id']:r for r in context['results']}
    check(review['id']+' complete cited context',refs.issubset(selected) and context['required_context_complete'])
    check(review['id']+' evidence locators',all(c['locator'] and c['original_url']==sources[c['source_id']]['original_url'] for rid in refs for c in selected[rid]['citations']))
check('All answer statements retain canon text backing',all(content[r]['layer']=='canon' for review in reviews for r in review['record_ids']))
all_text=''.join(s['text_zh'] for r in reviews for s in r['answer_sentences'])
check('Speaker and version distinctions checked in samples',all(t in all_text for t in ['莫菲丝对她的评价','凭感觉','未来计划','日服','中文档案编者','梦中母亲']))
check('New original facts use directly read Japanese official sources',all(sources[evidence[e]['source_id']]['authority']=='official' and evidence[e]['verification_status']=='direct_text_verified' and evidence[e]['language']=='ja' for fid in ['F065','F066','F067','F068'] for e in facts[fid]['evidence_ids']))
check('Episode 8 old stable ID gets a fixed original source','E423' in facts['F042']['evidence_ids'])
eps={r['id']:r for r in kb['episode_catalog']}
check('New episode metadata keeps unreviewed positions empty',all(eps[r]['official_playback_url'] is None and eps[r]['catalog_duration_minutes'] is None and eps[r]['runtime_precision']=='not_reviewed' and not eps[r]['full_episode_reviewed'] for r in ['EP04','EP06']))
base=json.loads((ROOT/'data/retrieval_chunks.json').read_text(encoding='utf-8'))
game=json.loads((ROOT/'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))
check('Answer reviews excluded from factual retrieval',not any(r['record_id'].startswith('AKA') for r in base+game))
check('Retrieval inventory matches content counts',len(base)==sum(len(kb[n]) for n in ('facts','relations','timeline','inferences')) and len(game)==193)
check('Original additions remain in original continuity',all(r['continuity']=='tv_anime' for r in base if r['record_id'] in ['F065','F066','F067','F068']))
result=dict(status='passed',checks=checks,reviewed_answers=len(reviews),reviewed_sentences=sum(len(r['answer_sentences']) for r in reviews),
    semantic_review='Single editor compared generated samples with cited records, source differences and selected fixed text; automated checks cover structure and context availability.')
if '--write-report' in sys.argv:
    (ROOT/'validation').mkdir(exist_ok=True)
    (ROOT/'validation/v19_answer_review.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(result,ensure_ascii=False,indent=2))
