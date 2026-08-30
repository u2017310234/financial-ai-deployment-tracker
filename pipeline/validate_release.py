from pathlib import Path
import json, sys

root = Path(__file__).resolve().parents[1]
release_dir = root / 'data' / 'releases'
files = sorted(release_dir.glob('*.json'))
if not files:
    raise SystemExit('no release JSON files found')

for path in files:
    payload = json.loads(path.read_text(encoding='utf-8'))
    for field in ['schema_version','release_id','generated_at','institutions','reports','evidence']:
        assert field in payload, f'{path}: missing {field}'
    institution_ids = {x['institution_id'] for x in payload['institutions']}
    report_ids = {x['report_id'] for x in payload['reports']}
    assert len(report_ids) == len(payload['reports']), f'{path}: duplicate report_id'
    for e in payload['evidence']:
        assert e['institution_id'] in institution_ids, (path, e['evidence_id'], 'unknown institution')
        assert e['report_id'] in report_ids, (path, e['evidence_id'], 'unknown report')
        assert int(e['page_no']) >= 1
        assert str(e.get('source_url') or '').startswith(('http://','https://'))
        assert '/work/' not in json.dumps(e, ensure_ascii=False), f'{path}: leaked Deepnote path'
    assert '/work/' not in path.read_text(encoding='utf-8'), f'{path}: leaked Deepnote path'
    print({'validated':str(path.relative_to(root)),'reports':len(payload['reports']),'evidence':len(payload['evidence'])})
