"""Dependency-free Chinese term/bigram retrieval over the collab story collection."""
from pathlib import Path
import json,re,math,argparse
ROOT=Path(__file__).resolve().parents[1]
ALIASES={'祐天寺にゃむ':'若麦','祐天寺若麥':'若麦','祐天寺若麦':'若麦','喵梦':'若麦','喵姆':'若麦','小祥':'祥子','大祥':'祥子','初音':'初华','モルフェス':'莫菲丝','morpheus':'莫菲丝','sakiko':'祥子','nyamu':'若麦','uika':'初华','umiri':'海铃','mutsumi':'睦'}
STOP={'祥子','丰川','川祥','什么','怎么','怎样','如何','为何','为什么','为什','么会','有没有','有没','没有','一下','的是','她的','她在','她是','这个','剧情','联动','游戏','明日','方舟','无忧','梦呓'}
ALIASES['战败']='行动失败'
def normalize(s):
    s=s.casefold()
    for a,b in ALIASES.items(): s=s.replace(a,b)
    return s
def tokens(s):
    s=normalize(s); result=[]
    for word in re.findall(r'[a-z0-9]+|[\u3400-\u9fff]+',s):
        result.extend(word[i:i+2] for i in range(len(word)-1)) if re.fullmatch(r'[\u3400-\u9fff]+',word) and len(word)>1 else result.append(word)
    return {x for x in result if x not in STOP}
def stage_rank(stage):
    if stage in ('SS-ST-1','SS-TR-1'): return 0
    match=re.fullmatch(r'SS-([1-8])-(BEG|END)',stage)
    if not match: raise ValueError('Stage must be SS-ST-1, SS-TR-1, or SS-1-BEG through SS-8-END')
    return int(match[1])*2-(match[2]=='BEG')
def search(query,limit=5,include_inference=False,max_rank=16,official=False,material=None):
    chunks=json.loads((ROOT/'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))
    rows=[r for r in chunks if (include_inference or r['layer']=='canon') and r['spoiler_rank']<=max_rank and (not official or r['official_only_eligible']) and (material is None or r['material_type']==material)]
    terms=tokens(query)
    if not terms or not rows: return []
    docs=[tokens(' '.join([r['text'],*r['keywords'],*r['query_examples']])) for r in rows]
    df={t:sum(t in d for d in docs) for t in terms}
    ranked=[]
    normalized=normalize(query)
    for row,doc in zip(rows,docs):
        matched=terms.intersection(doc)
        if not matched: continue
        score=sum(math.log(1+(len(rows)-df[t]+.5)/(df[t]+.5)) for t in matched)
        # Exact topic mentions help short names while bigrams handle ordinary prose.
        score+=sum(1.5 for k in row['keywords'] if len(k)>=2 and normalize(k) in normalized)
        score/=1+.001*len(doc)
        ranked.append((score,row))
    ranked.sort(key=lambda x:(-x[0],x[1]['record_id']))
    selected=[dict(score=round(score,4),**row) for score,row in ranked[:limit]]
    # Keep a source issue's companion wording beside its retrieved variant.
    required=list(dict.fromkeys(i for x in selected for i in x.get('required_context_record_ids',[])))
    for rid in required:
        if limit<2 or any(x['record_id']==rid for x in selected): continue
        related=next((r for r in rows if r['record_id']==rid),None)
        if related:
            context=dict(score=0.0,**related,retrieval_reason='required_source_issue_context')
            if len(selected)>=limit: selected[-1]=context
            else: selected.append(context)
    return selected
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Search Sakiko Arknights story evidence.')
    parser.add_argument('query'); parser.add_argument('--limit',type=int,default=5)
    parser.add_argument('--include-inference',action='store_true')
    parser.add_argument('--max-stage',default='SS-8-END'); parser.add_argument('--official-only',action='store_true')
    parser.add_argument('--material',choices=['main_story','operator_file','promotion_record','module_story','voice','event_letter','event_interface','outfit_description','item_description','operator_contract','interpretation'])
    args=parser.parse_args()
    if args.limit<1: parser.error('--limit must be positive')
    try: max_rank=stage_rank(args.max_stage)
    except ValueError as e: parser.error(str(e))
    rows=search(args.query,args.limit,args.include_inference,max_rank,args.official_only,args.material)
    print(json.dumps({'query':args.query,'results':rows,'source_note':'联动剧情证据为社区承载的游戏文本转录；客户端逐句对照待完成。'},ensure_ascii=False,indent=2))
