"""Validate provenance, references and retrieval exclusion for unverified material."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
kb=json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
chunks=json.loads((ROOT/'data/retrieval_chunks.json').read_text(encoding='utf-8'))
entities={x['id'] for x in kb['entities']}
sources={x['id']:x for x in kb['sources']}
evidence={x['id']:x for x in kb['evidence']}
episodes={x['id']:x for x in kb['episode_catalog']}
candidates={x['id']:x for x in kb['candidate_claims']}
scenes={x['id']:x for x in kb['scene_reviews']}
audits={x['id']:x for x in kb['access_audit']}
all_records={x['id']:x for rows in kb.values() if isinstance(rows,list) for x in rows}
checks=[]
def check(name,condition):
    assert condition,name
    checks.append({'check':name,'result':'passed'})

check('Candidate and workflow rows excluded from retrieval',not {c['record_id'] for c in chunks}.intersection(set(candidates)|set(scenes)|set(audits)))
check('Candidate evidence comes from secondary sources',all(sources[evidence[e]['source_id']]['authority']=='secondary' for x in candidates.values() for e in x['evidence_ids']))
check('Candidates keep pending evidence and no established layer',all('layer' not in x and x['candidate_layer']=='canon' and x['evidence_status']=='secondary_only' and not x['default_retrieval_eligible'] for x in candidates.values()))
check('All candidate references exist',all(x['episode_id'] in episodes and all(e in evidence for e in x['evidence_ids']) and all(r in all_records for r in x['corroborating_record_ids']) for x in candidates.values()))
check('Scene references and canonical entities exist',all(x['episode_id'] in episodes and all(i in entities for i in x['entity_ids']) and all(i in evidence for i in x['evidence_ids']) and all(i in all_records for i in x['related_record_ids']) and all(i in candidates for i in x['candidate_claim_ids']) for x in scenes.values()))
check('Every pending claim has a scene review task',set(candidates).issubset({i for s in scenes.values() for i in s['candidate_claim_ids']}))
check('Candidate and task episode references agree',all(candidates[i]['episode_id']==s['episode_id'] for s in scenes.values() for i in s['candidate_claim_ids']))
check('Unreviewed scene positions remain null',all(not x['full_episode_reviewed'] and x['subtitle_version'] is None and x['timecode_start'] is None and x['timecode_end'] is None for x in scenes.values()))
check('Scene playback links match verified catalog',all(x['official_playback_url']==episodes[x['episode_id']]['official_playback_url'] for x in scenes.values()))
check('Access audit source and evidence references exist',all(x['source_id'] in sources and x['url']==sources[x['source_id']]['original_url'] and all(i in evidence for i in x['evidence_ids']) and all(i in episodes for i in x['episode_ids']) for x in audits.values()))
check('Episode playback evidence and audit references exist',all(all(i in evidence for i in x['playback_link_evidence_ids']) and all(i in audits for i in x['access_audit_ids']) for x in episodes.values()))
check('Film management and support facts remain in film continuity',all(x['continuity']=='film_profile_snapshot' for x in kb['facts'] if x['id'] in ['F059','F061']))
result={'status':'passed','scope':'Provenance/reference/isolation checks; original episode scenes remain pending.','checks':checks}
if '--write-report' in sys.argv:
    (ROOT/'validation/review_workflow.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
