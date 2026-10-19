"""Search original-work records with layers, sources and phase filters."""
from pathlib import Path
import argparse
import json
import math
import re
from search_game import normalize, tokens

ROOT=Path(__file__).resolve().parents[1]
EPISODE_NUMBERS={name:str(i) for i,name in enumerate(['一','二','三','四','五','六','七','八','九','十','十一','十二','十三'],1)}


def normalize_original(text):
    text=normalize(text).replace('素世','爽世').replace('燈','灯')
    def episode(match):
        value=match.group(1)
        number=EPISODE_NUMBERS.get(value,value)
        return '第'+str(int(number))+'话' if number.isdigit() and 1<=int(number)<=13 else match.group(0)
    return re.sub(r'第\s*([一二三四五六七八九十]+|[0-9]+)\s*[话話集]',episode,text)


def search(query,limit=5,include_inference=False,official=False,direct=False,continuity=None,phase=None):
    if limit<1:raise ValueError('limit must be positive')
    kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
    chunks=json.loads((ROOT/'data/retrieval_chunks.json').read_text(encoding='utf-8'))
    norm=normalize_original
    query=norm(query)
    entities={r['id']:r for r in kb['entities']}
    rows=[r for r in chunks if (include_inference or r['layer']=='canon')
        and (not official or r['official_only_eligible']) and (not direct or r['direct_only_eligible'])
        and (continuity is None or r['continuity']==continuity) and (phase is None or r['phase'].startswith(phase))]
    terms=tokens(query)
    if not terms:
        terms={'@'+eid for eid,ent in entities.items() if len(query)>=2 and any(query in norm(n) for n in [ent['name_zh'],ent['name_ja'] or '',ent['name_en'] or '',*ent['aliases']] if n)}
    if not terms or not rows:return []
    navigation={r['record_id']:[] for r in rows}
    for item in kb['original_question_index']:
        for rid in item['record_ids']:
            if rid in navigation:navigation[rid].extend([item['question_zh'],*item['keywords']])
    docs=[]
    for row in rows:
        text=[row['text'],row['phase'],*navigation[row['record_id']]]
        for eid in row['entity_ids']:
            ent=entities[eid]
            text.extend([ent['name_zh'],ent['name_ja'] or '',ent['name_en'] or '',*ent['aliases']])
        docs.append(tokens(norm(' '.join(text)))|{'@'+eid for eid in row['entity_ids']})
    df={t:sum(t in d for d in docs) for t in terms}
    ranked=[]
    for row,doc in zip(rows,docs):
        matched=terms&doc
        if not matched:continue
        score=sum(math.log(1+(len(rows)-df[t]+.5)/(df[t]+.5)) for t in matched)/(1+.001*len(doc))
        ranked.append((score,row))
    ranked.sort(key=lambda item:(-item[0],item[1]['record_id']))
    evidence={r['id']:r for r in kb['evidence']}
    return [dict(row,score=round(score,4),citations=[dict(evidence_id=e,source_id=evidence[e]['source_id'],
        original_url=evidence[e]['original_url'],locator=evidence[e]['locator'],language=evidence[e]['language'],
        verification_status=evidence[e]['verification_status']) for e in row['evidence_ids']]) for score,row in ranked[:limit]]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('query');p.add_argument('--limit',type=int,default=5)
    p.add_argument('--include-inference',action='store_true');p.add_argument('--official-only',action='store_true')
    p.add_argument('--direct-only',action='store_true');p.add_argument('--continuity');p.add_argument('--phase')
    args=p.parse_args()
    try:rows=search(args.query,args.limit,args.include_inference,args.official_only,args.direct_only,args.continuity,args.phase)
    except ValueError as error:p.error(str(error))
    print(json.dumps(dict(query=args.query,results=rows,source_note='保留官方材料与一手访谈复述的不同证据资格；推断显式开启，原片核验范围见逐话索引。'),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
