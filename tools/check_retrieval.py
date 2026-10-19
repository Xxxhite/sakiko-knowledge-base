"""Invariant checks for alias, evidence, layer, and continuity filtering."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
chunks=json.loads((ROOT/'data/retrieval_chunks.json').read_text(encoding='utf-8'))
def norm(s): return re.sub(r'\s+','',s).casefold()
def retrieve(query='',layers=('canon',),official=False,direct=False,continuity=None):
    ids=set()
    if query:
        for e in kb['entities']:
            if norm(query) in {norm(x) for x in [e['name_ja'],e['name_zh'],e['name_en'],*e['aliases']] if x}:
                ids.add(e['id'])
    return [c for c in chunks if c['layer'] in layers
            and (not official or c['official_only_eligible'])
            and (not direct or c['direct_only_eligible'])
            and (continuity is None or c['continuity']==continuity)
            and (not query or bool(ids.intersection(c['entity_ids'])) or norm(query) in norm(c['text']))]
def recs(rows): return {x['record_id'] for x in rows}
checks=[]
def check(name,condition):
    assert condition,name
    checks.append(dict(check=name,result='passed'))
check('Japanese Hatsune alias reaches official identity fact','F045' in recs(retrieve('三角初音')))
check('English Hatsune alias reaches same identity fact','F045' in recs(retrieve('Hatsune Misumi')))
check('default canon excludes genealogy inference','I004' not in recs(retrieve()))
check('inference opt in exposes genealogy reasoning','I004' in recs(retrieve(layers=('inference',))))
check('official only excludes cast retelling','F047' not in recs(retrieve(official=True)))
check('official and direct both keep browser identity fact','F045' in recs(retrieve(official=True,direct=True)))
check('direct only excludes indexed game class','F007' not in recs(retrieve(direct=True)))
check('TV filter excludes film snapshot fact','F054' not in recs(retrieve(continuity='tv_anime')))
check('film snapshot filter includes composer fact','F054' in recs(retrieve(continuity='film_profile_snapshot')))
check('empty fanon returns no records',not retrieve(layers=('fanon',)))
check('research queue and source issues stay outside factual retrieval',not any(x['record_id'].startswith(('Q','SC')) for x in retrieve()))
result={'status':'passed','scope':'Rule/metadata filtering checks; no language-model semantic evaluation.','checks':checks}
if '--write-report' in __import__('sys').argv:
    (ROOT/'validation/retrieval.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
