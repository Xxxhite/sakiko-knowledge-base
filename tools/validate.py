"""Recheck the delivered knowledge base using Python standard library only."""
from pathlib import Path
import json, hashlib, argparse

ROOT=Path(__file__).resolve().parents[1]

def load(p):
    def unique_pairs(pairs):
        result={}
        for k,v in pairs:
            assert k not in result, f'duplicate JSON key: {k}'
            result[k]=v
        return result
    return json.loads(p.read_text(encoding='utf-8'),object_pairs_hook=unique_pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))

def validate():
    checks=[]
    # Inspect project data, never installed dependencies or local editor settings.
    json_paths=[p for directory in ('data','schema') for p in (ROOT/directory).rglob('*.json')]
    json_paths.extend(ROOT/name for name in ('package.json','package-lock.json') if (ROOT/name).is_file())
    for p in json_paths: load(p)
    checks.append({'check':'strict_json_parse','result':'passed','files':len(json_paths)})
    kb=load(ROOT/'data/kb.json')
    mapping={'entities':'entities','sources':'sources','evidence':'evidence','facts':'canon_facts',
             'relations':'relations','timeline':'timeline','inferences':'inference','fanon':'fanon','research_queue':'research_queue','episode_catalog':'episode_catalog','source_issues':'source_issues','candidate_claims':'candidate_claims','scene_reviews':'scene_reviews','access_audit':'access_audit','game_story_records':'game_story_records','game_interpretations':'game_interpretations','game_question_index':'game_question_index','game_relations':'game_relations','game_lore_records':'game_lore_records'}
    mapping['game_scene_coverage']='game_scene_coverage'
    mapping['game_material_coverage']='game_material_coverage'
    mapping['game_localization_checks']='game_localization_checks'
    mapping['game_discussion_guides']='game_discussion_guides'
    mapping['game_answer_reviews']='game_answer_reviews'
    for key,stem in mapping.items():
        assert kb[key]==load(ROOT/f'data/{stem}.json'), f'JSON mirror mismatch {key}'
        lines=(ROOT/f'jsonl/{stem}.jsonl').read_text(encoding='utf-8').splitlines()
        assert all(line.strip() for line in lines), f'empty row {stem}'
        parsed=[json.loads(line) for line in lines]
        assert parsed==kb[key], f'JSONL mirror mismatch {key}'
    checks.append({'check':'json_jsonl_mirrors','result':'passed','collections':len(mapping)})
    index={}
    for key in mapping:
        for r in kb[key]:
            assert r['id'] not in index, f'duplicate record ID {r["id"]}'
            index[r['id']]=r
    ents={x['id'] for x in kb['entities']}; es={x['id']:x for x in kb['evidence']}; ss={x['id']:x for x in kb['sources']}
    for key in mapping:
        for r in kb[key]:
            for eid in r.get('evidence_ids',[]): assert eid in es, f'unknown evidence {eid}'
            for field in ['subject_id','object_id']:
                if field in r: assert r[field] in ents, f'unknown entity {r[field]}'
            for rid in r.get('basis_record_ids',[])+r.get('record_ids',[])+r.get('context_record_ids',[]): assert rid in index, f'unknown record {rid}'
            if r.get('group_context'): assert r['group_context'] in ents
            if r.get('material_owner_id'): assert r['material_owner_id'] in ents
            for eid in r.get('voice_metadata',{}).get('localization_evidence_ids',[]): assert eid in es
            for asset in r.get('text_assets',[]): assert asset['source_id'] in ss
            for lid in r.get('localization_check_ids',[]):
                assert lid in index and r['id'] in index[lid]['record_ids']
            for variant in r.get('variants',[]):
                assert variant['source_id'] in ss and variant['evidence_id'] in es
                assert es[variant['evidence_id']]['source_id']==variant['source_id']
                assert ss[variant['source_id']]['language']==variant['language']
    for e in es.values():
        assert e['source_id'] in ss
        s=ss[e['source_id']]
        assert e['original_url']==s['original_url']
        assert e['verification_status']==s['verification_status']
    checks.append({'check':'unique_ids_and_foreign_keys','result':'passed','records':len(index)})
    for key in ['facts','relations','timeline']:
        for r in kb[key]:
            assert r['layer']=='canon' and r['evidence_status'] in ('official_explicit','primary_interview_explicit')
            assert r['evidence_ids']
            allowed={'official'} if r['evidence_status']=='official_explicit' else {'official','creator_first_person'}
            assert all(ss[es[e]['source_id']]['authority'] in allowed for e in r['evidence_ids'])
    for r in kb['inferences']:
        assert r['layer']=='inference' and r['rationale'] and r['basis_record_ids'] and r['alternative_reading']
    for r in kb['fanon']: assert r['layer']=='fanon' and r['worldline_id'] and r['author']
    assert kb['metadata']['fanon_count']==len(kb['fanon'])
    for r in kb['source_issues']:
        assert all(s in ss for s in r['source_ids'])
        assert all(i in index for i in r['affected_record_ids'])
    for r in kb['episode_catalog']:
        assert all(i in index for i in r['related_record_ids'])
        if not r['full_episode_reviewed']:
            assert r['timecode_start'] is None and r['timecode_end'] is None
    checks.append({'check':'canon_inference_fanon_separation','result':'passed'})
    timeline={x['id']:x for x in kb['timeline']}
    def visit(i,stack):
        assert i not in stack, 'timeline cycle'
        for prev in timeline[i]['story_time']['after_event_ids']:
            assert prev in timeline
            visit(prev,stack|{i})
    for tid in timeline: visit(tid,set())
    checks.append({'check':'timeline_references_and_acyclic_order','result':'passed'})
    chunks=load(ROOT/'data/retrieval_chunks.json')
    rows=[json.loads(x) for x in (ROOT/'jsonl/retrieval_chunks.jsonl').read_text(encoding='utf-8').splitlines()]
    assert chunks==rows
    assert len(chunks)==sum(len(kb[k]) for k in ['facts','relations','timeline','inferences'])
    for c in chunks:
        r=index[c['record_id']]
        assert c['layer']==r['layer'] and c['evidence_ids']==r['evidence_ids']
        assert c['evidence_status']==r['evidence_status']
        assert all(i in ents for i in c['entity_ids'])
        assert c['official_only_eligible']==all(ss[es[e]['source_id']]['authority']=='official' for e in r['evidence_ids'])
        source_ids=list(dict.fromkeys(es[x]['source_id'] for x in r['evidence_ids']))
        assert c['source_ids']==source_ids
        assert c['source_urls']==[ss[x]['original_url'] for x in source_ids]
        assert c['direct_only_eligible']==all(es[x]['verification_status']=='direct_text_verified' for x in r['evidence_ids'])
    checks.append({'check':'retrieval_provenance','result':'passed','chunks':len(chunks)})
    checksum_path=ROOT/'SHA256SUMS.txt'
    if checksum_path.exists():
        entries=checksum_path.read_text(encoding='utf-8').splitlines()
        for line in entries:
            expected,rel=line.split('  ',1)
            target=(ROOT/rel).resolve()
            assert target.is_relative_to(ROOT.resolve())
            assert hashlib.sha256(target.read_bytes()).hexdigest()==expected, f'checksum mismatch {rel}'
        checks.append({'check':'sha256_manifest','result':'passed','files':len(entries)})
    return {'status':'passed','checks':checks,'counts':{k:len(kb[k]) for k in mapping},'schema_validation':'Run validate_schema.js for Draft-07 validation.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--write-report',action='store_true'); args=parser.parse_args()
    result=validate()
    if args.write_report:
        (ROOT/'validation').mkdir(exist_ok=True)
        (ROOT/'validation/integrity.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
