"""Assemble cited records for a discussion, preserving scope and missing context."""
from pathlib import Path
import argparse
import json
from search_game import search, stage_rank, tokens

ROOT = Path(__file__).resolve().parents[1]


def assemble(query='', guide_id=None, record_ids=None, limit=5, max_rank=16,
             include_inference=False, official=False, material=None, max_records=40):
    if limit < 1 or max_records < 1:
        raise ValueError('limit and max_records must be positive')
    kb = json.loads((ROOT/'data/kb.json').read_text(encoding='utf-8'))
    chunks = {r['record_id']: r for r in json.loads((ROOT/'data/game_retrieval_chunks.json').read_text(encoding='utf-8'))}
    guides = {r['id']: r for r in kb['game_discussion_guides']}
    if guide_id and guide_id not in guides:
        raise ValueError('Unknown guide: '+guide_id)
    guide = guides.get(guide_id)
    seeds = list(dict.fromkeys((record_ids or []) + (guide['record_ids'] if guide else [])))
    if not seeds:
        seeds = [r['record_id'] for r in search(query, limit, include_inference, max_rank, official, material)]
    for rid in seeds:
        if rid not in chunks:
            raise ValueError('Unknown game content record: '+rid)
    selected, blocked, links = {}, {}, []
    queue = [(rid, 'selected_guide' if guide else 'query_or_explicit_record', None, 0) for rid in seeds]
    for rid, reason, parent, depth in queue:
        if parent:
            links.append(dict(from_record_id=parent, to_record_id=rid, reason=reason))
        if rid in selected:
            continue
        if rid in blocked:
            if blocked[rid]['reason'] == 'material_filter' and reason == 'required_source_issue_context':
                del blocked[rid]
            else:
                continue
        row = chunks.get(rid)
        issue = None
        if row is None: issue = 'unknown_record'
        elif row['spoiler_rank'] > max_rank: issue = 'spoiler_filter'
        elif row['layer'] != 'canon' and not include_inference: issue = 'layer_filter'
        elif official and not row['official_only_eligible']: issue = 'official_filter'
        # Source-issue companions may cross material boundaries, never other filters.
        elif material and row['material_type'] != material and reason != 'required_source_issue_context': issue = 'material_filter'
        elif len(selected) >= max_records: issue = 'record_budget'
        if issue:
            blocked[rid] = dict(record_id=rid, reason=issue, requested_by=parent)
            continue
        selected[rid] = dict(row, retrieval_reason=reason)
        for target in row.get('required_context_record_ids', []):
            queue.append((target, 'required_source_issue_context', rid, depth))
        # One story-background hop; source-issue links always close transitively.
        if depth == 0:
            for target in row.get('context_record_ids', []):
                queue.append((target, 'story_background', rid, 1))
    evidence = {r['id']:r for r in kb['evidence']}
    for row in selected.values():
        row['citations'] = [dict(evidence_id=e, source_id=evidence[e]['source_id'],
            original_url=evidence[e]['original_url'], locator=evidence[e]['locator'],
            language=evidence[e]['language'], verification_status=evidence[e]['verification_status'])
            for e in row['evidence_ids']]
    required = {rid for r in selected.values() for rid in r.get('required_context_record_ids', [])}
    missing = sorted(required-set(selected))
    suggestions = []
    query_terms = tokens(query)
    if query_terms:
        def guide_terms(g):
            # Use the linked records' existing topic vocabulary for paraphrases.
            text = [g['question_zh'], *g['keywords'], *(s['summary_zh'] for s in g['answer_outline'])]
            for rid in g['record_ids']:
                text.extend(chunks[rid]['keywords'])
                text.extend(chunks[rid]['query_examples'])
            return tokens(' '.join(text))
        ranked = sorted(((len(query_terms & guide_terms(g)),g)
                         for g in guides.values() if g['spoiler_rank'] <= max_rank), key=lambda x:(-x[0],x[1]['id']))
        suggestions = [dict(guide_id=g['id'], question_zh=g['question_zh']) for score,g in ranked[:3] if score]
    # An outline is visible only when every cited record passed all filters/budgets.
    guide_complete = bool(guide) and all(rid in selected for rid in guide['record_ids'])
    return dict(query=query, guide_id=guide_id, guide_complete=guide_complete,
        answer_outline=guide['answer_outline'] if guide_complete else [],
        outline_kind='curator_navigation', results=list(selected.values()),
        context_links=links, blocked_context=list(blocked.values()),
        missing_required_context_ids=missing, required_context_complete=not missing,
        suggested_guides=suggestions,
        filters=dict(max_spoiler_rank=max_rank, include_inference=include_inference,
                     official_only=official, material=material, max_records=max_records),
        source_note='正文证据为社区游戏文本转录；讨论提纲为编者导航。关联来源差异可跨材料补取，进度、分层与官方来源过滤始终生效。')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('query', nargs='?', default='')
    p.add_argument('--guide')
    p.add_argument('--record', action='append', default=[])
    p.add_argument('--limit', type=int, default=5)
    p.add_argument('--max-records', type=int, default=40)
    p.add_argument('--max-stage', default='SS-8-END')
    p.add_argument('--include-inference', action='store_true')
    p.add_argument('--official-only', action='store_true')
    p.add_argument('--material', choices=['main_story','operator_file','promotion_record','module_story','voice',
        'event_letter','event_interface','outfit_description','item_description','operator_contract','interpretation'])
    args = p.parse_args()
    if not args.query and not args.guide and not args.record:
        p.error('Provide a question, --guide or --record.')
    try:
        result = assemble(args.query, args.guide, args.record, args.limit, stage_rank(args.max_stage),
                          args.include_inference, args.official_only, args.material, args.max_records)
    except ValueError as error:
        p.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
