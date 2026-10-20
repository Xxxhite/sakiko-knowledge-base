// Ajv 6 supports the delivered JSON Schema Draft-07.
const fs = require('fs');
const path = require('path');
const Ajv = require('ajv');
const root = path.resolve(__dirname, '..');
const schema = JSON.parse(fs.readFileSync(path.join(root, 'schema/kb.schema.json'), 'utf8'));
const kb = JSON.parse(fs.readFileSync(path.join(root, 'data/kb.json'), 'utf8'));
const ajv = new Ajv({allErrors:true, schemaId:'auto'});
if (!ajv.validateSchema(schema)) throw new Error(JSON.stringify(ajv.errors));
const validate = ajv.compile(schema);
if (!validate(kb)) throw new Error(JSON.stringify(validate.errors, null, 2));
// Verify that incorrect layers, a missing source URL, and a missing relation phase are rejected.
for (const mutate of [
  x => { x.facts[0].layer = 'fanon'; },
  x => { delete x.sources[0].original_url; },
  x => { delete x.relations[0].valid_time; },
  x => { x.candidate_claims[0].default_retrieval_eligible = true; },
  x => { x.scene_reviews[0].full_episode_reviewed = true; },
  x => { x.game_story_records[0].evidence_status = 'official_explicit'; },
  x => { delete x.game_story_records[0].narrative_level; },
  x => { x.game_story_records[0].client_cross_checked = true; },
  x => { x.game_interpretations[0].layer = 'canon'; },
  x => { x.game_lore_records[0].material_type = 'main_story'; },
  x => { delete x.game_lore_records[0].section_title; },
  x => { delete x.game_lore_records.find(r => r.voice_metadata).voice_metadata.voice_id; },
  x => { x.game_lore_records.find(r => r.voice_metadata).voice_metadata.audio_reviewed = true; },
  x => { x.game_lore_records.find(r => r.delivery_metadata).delivery_metadata.date_kind = 'story_calendar'; },
  x => { x.game_material_coverage[0].client_cross_checked = true; },
  x => { x.game_material_coverage[0].text_assets[0].sha256 = 'invalid'; },
  x => { x.game_lore_records.find(r => r.id === 'AKL091').server = 'CN'; },
  x => { x.game_localization_checks[0].variants.pop(); },
  x => { x.game_localization_checks[0].audio_reviewed = true; },
  x => { x.game_localization_checks[0].variants[0].asset_sha256 = 'invalid'; },
  x => { x.game_discussion_guides[0].default_retrieval_eligible = true; },
  x => { delete x.game_discussion_guides[0].answer_outline[0].record_ids; },
  x => { x.game_answer_reviews[0].default_retrieval_eligible = true; },
  x => { delete x.game_answer_reviews[0].answer_sentences[0].record_ids; },
  x => { x.episode_catalog.find(r => r.id === 'EP04').catalog_duration_minutes = 24; },
  x => { delete x.episode_catalog[0].work_id; },
  x => { x.episode_catalog.find(r => r.id === 'MYGO13').work_id = 'bang_dream_ave_mujica'; },
  x => { x.episode_catalog.find(r => r.id === 'EP13').work_id = 'bang_dream_its_mygo'; },
  x => { x.original_question_index[0].default_retrieval_eligible = true; },
  x => { delete x.original_question_index.find(r => r.answer_review).answer_review.answer_sentences[0].record_ids; },
  x => { x.original_question_index.find(r => r.answer_review).answer_review.answer_sentences[0].layer = 'fanon'; },
  x => { x.original_question_index.find(r => r.answer_review).answer_review.review_method = 'independent_full_work_review'; },
  x => { x.original_question_index.find(r => r.answer_review).answer_review.answer_sentences[0].review_result = 'unchecked'; }
]) {
  const bad = JSON.parse(JSON.stringify(kb)); mutate(bad);
  if (validate(bad)) throw new Error('Negative schema check unexpectedly accepted invalid record.');
}
const result = {status:'passed', schema_draft:'Draft-07', engine:'Ajv '+require('ajv/package.json').version,
  schema_meta_validation:'passed', total_database_validation:'passed', negative_checks:33};
if (process.argv.includes('--write-report')) {
  fs.mkdirSync(path.join(root, 'validation'), {recursive:true});
  fs.writeFileSync(path.join(root, 'validation/schema.json'), JSON.stringify(result,null,2)+'\n');
}
console.log(JSON.stringify(result,null,2));
