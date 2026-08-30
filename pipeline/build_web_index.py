from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
release_files = sorted((root/'data'/'releases').glob('*.json'))
if not release_files:
    raise SystemExit('no releases')

# newest lexical release id wins for manifest; all release rows are indexed.
all_reports=[]; all_evidence=[]; institutions={}; releases=[]
for path in release_files:
    p=json.loads(path.read_text(encoding='utf-8'))
    releases.append({'release_id':p['release_id'],'generated_at':p['generated_at'],'file':f'/data/releases/{path.name}'})
    for x in p['institutions']: institutions[x['institution_id']]=x
    all_reports.extend(p['reports'])
    all_evidence.extend(p['evidence'])

out=root/'web'/'public'/'data'
out.mkdir(parents=True,exist_ok=True)
manifest={
    'schema_version':'1',
    'releases':releases,
    'institution_count':len(institutions),
    'report_count':len(all_reports),
    'evidence_count':len(all_evidence),
}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'institutions.json').write_text(json.dumps(sorted(institutions.values(),key=lambda x:x.get('name','')),ensure_ascii=False,indent=2),encoding='utf-8')
(out/'reports.json').write_text(json.dumps(all_reports,ensure_ascii=False,indent=2),encoding='utf-8')

# Search index is intentionally denormalized for browser-side filtering.
search=[]
for e in all_evidence:
    search.append({
        'evidence_id':e['evidence_id'],'report_id':e['report_id'],'institution_id':e['institution_id'],
        'institution_name':e.get('institution_name'),'ticker':e.get('ticker'),'page_no':e['page_no'],
        'section_title':e.get('section_title'),'text':e['text'],'technology_groups':e.get('technology_groups',[]),
        'deployment_hits':e.get('deployment_hits',[]),'finance_hits':e.get('finance_hits',[]),'score':e.get('score'),
        'review_status':e.get('review_status'),'source_url':e.get('source_url')
    })
(out/'search-index.json').write_text(json.dumps(search,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
print(manifest)
