"""Synthetic-fixture tests ONLY; never read/approve actual ship render pixels.

Exercises the curated helper in a disposable excluded workspace. Real output
is a small, explicitly scoped test report. No ship review register is written.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'tools/make_leonidas_refinement.py'
spec = importlib.util.spec_from_file_location('synthetic_curated_helper', HELPER)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
passed = []


def mark(label):
    passed.append(dict(test=label, status='PASS'))
    print('PASS', label)


(ROOT / '.cache').mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='leonidas-curated-test-',
                                 dir=ROOT / '.cache') as folder:
    temp = Path(folder)
    m.ROOT, m.DOC, m.OUT = temp, temp / 'docs/leonidas_ii', temp / 'renders/leonidas_ii/refinement'
    m.REVIEW = m.DOC / 'DETAIL_VISUAL_REVIEW.json'

    def put(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def js(path, value):
        put(path, (json.dumps(value, indent=2) + '\n').encode())

    for relative in ('models/leonidas_ii/Aurelian_1889.blend',
                     'blender/leonidas_ii/render.py', 'shipdesign/leonidas_ii.py',
                     'blender/leonidas_ii/audit_details.py',
                     'blender/leonidas_ii/audit_structure.py',
                     'blender/leonidas_ii/audit_ladders.py'):
        put(temp / relative, ('Synthetic fixture, NOT ship evidence: ' + relative).encode())
    data = dict(fixture_mounts=[{}]*7, rigging_feet=[{}]*3, rigging_lines=[{}]*3,
                access_ladders=[{}]*5, counts=dict(physical_compartments=5))
    js(temp / 'exports/leonidas_ii/build_data.json', data)
    source = m.sha(temp / 'models/leonidas_ii/Aurelian_1889.blend')
    renderer = m.sha(temp / 'blender/leonidas_ii/render.py')
    for name, count, auditor in (('DETAIL_GEOMETRY_AUDIT', 7, 'audit_details.py'),
                                 ('STRUCTURE_GEOMETRY_AUDIT', 3, 'audit_structure.py')):
        audit = dict(source_sha256=source, auditor_sha256=m.sha(temp / 'blender/leonidas_ii' / auditor),
                     checks=[dict(check='Synthetic unit gate', status='PASS',
                                  count=7 if i == 0 else 3) for i in range(count)])
        if count == 7:
            audit.update(build_data_sha256=m.sha(temp / 'exports/leonidas_ii/build_data.json'),
                         ladder_auditor_sha256=m.sha(temp / 'blender/leonidas_ii/audit_ladders.py'),
                         access_ladders=dict(summary=dict(ladders=5, failures=0,
                                                          rung_ends=330, frame_mounts=44)))
        else:
            audit['hull_spec_sha256'] = m.sha(temp / 'shipdesign/leonidas_ii.py')
        js(m.DOC / (name + '.json'), audit)
    primary, closeups, images = [], [], []
    for name in sorted(m.EXPECTED):
        interior = name.startswith('Interior_')
        size = (1600, 1000) if interior else (1120, 700)
        path = (temp / 'renders/leonidas_ii' / (name+'.jpg') if interior else
                temp / 'scratch' / (name+'.jpg'))
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', size, (120, 100, 40)).save(path)
        row = dict(file=str(path.relative_to(temp)), title='Synthetic unit fixture',
                   source_sha256=source, renderer_sha256=renderer, sha256=m.sha(path),
                   pixels=list(size), cycles_samples=12 if interior else 24,
                   cutaway=name == 'Interior_Grand_Stair')
        (primary if interior else closeups).append(row)
        images.append(dict(image=name, sha256=row['sha256'],
                           status='REVIEWED_WITH_LIMITATIONS', inspection_method='OPENED_FINAL_JPG',
                           observation='Synthetic unit text; this does not review any actual ship model.',
                           limitations='Synthetic fixtures only; no real image or model is certified.'))
    pr, cr = temp / 'scratch/primary.json', temp / 'scratch/closeups.json'
    js(pr, primary)
    js(cr, closeups)
    review = dict(schema='victoria.leonidas-ii.focused-visual-review/1.1',
                  status='FOCUSED_REVIEW_COMPLETE_FULL_EVIDENCE_SEPARATE',
                  source_sha256=source, renderer_sha256=renderer,
                  render_register=str((m.OUT / 'camera_register.json').relative_to(temp)),
                  primary_render_register=str(pr.relative_to(temp)),
                  detail_render_register=str(cr.relative_to(temp)), images=images,
                  blocking_issues=[])
    for name in ('DETAIL_GEOMETRY_AUDIT', 'STRUCTURE_GEOMETRY_AUDIT'):
        review[name.lower() + '_sha256'] = m.sha(m.DOC / (name+'.json'))
    js(m.REVIEW, review)
    m.validate()
    mark('Synthetic complete 19-full-resolution / 6-close-up plan validates')

    def reject(label, change):
        altered = copy.deepcopy(review)
        change(altered)
        js(m.REVIEW, altered)
        try:
            m.validate()
        except (ValueError, KeyError, FileNotFoundError):
            mark(label)
        else:
            raise AssertionError('Did not reject: ' + label)
        js(m.REVIEW, review)

    reject('Refuses missing planned image', lambda r: r['images'].pop())
    reject('Refuses duplicate replacing a planned view', lambda r: r['images'].__setitem__(0, r['images'][1]))
    reject('Refuses stale master', lambda r: r.__setitem__('source_sha256', 'bad'))
    reject('Refuses stale renderer', lambda r: r.__setitem__('renderer_sha256', 'bad'))
    reject('Refuses stale audit identity', lambda r: r.__setitem__('detail_geometry_audit_sha256', 'bad'))
    reject('Refuses an unopened final JPG', lambda r: r['images'][0].__setitem__('inspection_method', 'AUTOMATIC'))
    reject('Refuses wrong opened-pixel identity', lambda r: r['images'][0].__setitem__('sha256', 'bad'))
    reject('Refuses an unscoped release status', lambda r: r.__setitem__('status', 'APPROVED'))
    reject('Refuses an empty observation', lambda r: r['images'][0].__setitem__('observation', ''))
    reject('Refuses unresolved visual blockers', lambda r: r['blocking_issues'].append('Unfixed geometry'))
    stair = next(r for r in primary if Path(r['file']).stem == 'Interior_Grand_Stair')
    stair['cutaway'] = False
    js(pr, primary)
    reject('Refuses mislabeled wall-removed stair', lambda r: None)
    stair['cutaway'] = True
    js(pr, primary)
    row = next(r for r in primary if Path(r['file']).stem == 'Interior_Music')
    path = temp / row['file']
    original_bytes, original_row = path.read_bytes(), copy.deepcopy(row)
    Image.new('RGB', (1120, 700), (120, 100, 40)).save(path)
    row.update(pixels=[1120, 700], cycles_samples=24, sha256=m.sha(path))
    js(pr, primary)
    reject('Refuses pilot dimensions substituted for a full-resolution interior',
           lambda r: next(i for i in r['images'] if i['image'] == 'Interior_Music').__setitem__('sha256', row['sha256']))
    path.write_bytes(original_bytes)
    row.clear()
    row.update(original_row)
    row['cycles_samples'] = 6
    js(pr, primary)
    reject('Refuses insufficient full-resolution samples', lambda r: None)
    row['cycles_samples'] = 12
    js(pr, primary)
    m.main()
    assert len(list(m.OUT.glob('*.jpg'))) == 6
    assert len(list((temp / 'renders/leonidas_ii').glob('Interior_*.jpg'))) == 19
    mark('Copies only six scratch close-ups; reuses nineteen durable main JPGs')
    pr.unlink()
    cr.unlink()
    m.main()
    mark('Durable mixed register regenerates page with no scratch registers')
    page = (m.DOC / 'DETAIL_REFINEMENT.html').read_text()
    assert '<b>7</b>' in page and '<b>3</b>' in page and '<b>5</b>' in page and '<b>286</b>' not in page and '@@' not in page
    mark('Displayed contact/space metrics derive from audit/data')

report = dict(schema='victoria.leonidas-ii.refinement-helper-tests/1.0',
              scope='SYNTHETIC FIXTURES ONLY; no real render opened or approved',
              runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              helper_sha256=hashlib.sha256(HELPER.read_bytes()).hexdigest(),
              tests=passed, summary=dict(PASS=len(passed), FAIL=0))
(ROOT / 'docs/leonidas_ii/REFINEMENT_HELPER_TESTS.json').write_text(json.dumps(report, indent=2)+'\n')
print('ALL', len(passed), 'SYNTHETIC TESTS PASSED; NO SHIP REVIEW CREATED')
