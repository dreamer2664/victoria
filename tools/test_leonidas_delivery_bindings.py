"""Regression-test delivered/fresh byte-binding modes in isolated COPIED fixtures.

Never edits canonical sources/audits/receipt/kit and never runs Blender. A small,
explicitly synthetic GAME byte fixture exercises the saved-source-positive path;
that fixture is NOT a model, a geometry audit, or an actual export. The real kit
archive and its contents are checked separately by check_leonidas_delivery.py.
"""
from pathlib import Path
import collections
import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import check_leonidas_micro_delivery as checker

DOC = ROOT / 'docs/leonidas_ii'
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
REPORT = 'docs/leonidas_ii/MICRO_DELIVERY_VALIDATION.json'
RECEIPT = 'docs/leonidas_ii/EXPORT_INPUT_IDENTITY.json'
KIT = 'exports/leonidas_ii/IMPORT_KIT_MANIFEST.json'
rows = []


def main():
    rows.clear()
    relatives = set(checker.INPUT_PATHS.values()) - {
        checker.INPUT_PATHS['game'], checker.INPUT_PATHS['game_data']}
    relatives.update(str(p.relative_to(ROOT)) for p in (ROOT / 'blender/leonidas_ii').glob('*.py'))
    relatives.update({RECEIPT, KIT, 'exports/leonidas_ii/game_manifest.json',
                      'tools/record_leonidas_export_inputs.py'})
    relatives.update(f'docs/leonidas_ii/{family}_{quality}.json'
                     for family in checker.FAMILIES for quality in ('MASTER', 'GAME'))
    relatives.update(f'docs/leonidas_ii/inspection/MICRO_CONTACT_REGRESSIONS_{quality}.json'
                     for quality in ('MASTER', 'GAME'))
    before = {p: H(ROOT / p) for p in sorted(relatives)}
    parent = DOC / 'build'
    parent.mkdir(parents=True, exist_ok=True)
    original_globals = checker.ROOT, checker.DOC, checker.HERE
    try:
        with tempfile.TemporaryDirectory(prefix='delivery-binding-fixtures-', dir=parent) as tmp:
            fixture = Path(tmp)
            for rel in sorted(relatives):
                target = fixture / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
            checker.ROOT = fixture
            checker.DOC = fixture / 'docs/leonidas_ii'
            checker.HERE = fixture / 'blender/leonidas_ii'
            changed = {}

            def remember(rel):
                if rel not in changed:
                    p = fixture / rel
                    changed[rel] = p.read_bytes() if p.is_file() else None

            def write(rel, blob):
                remember(rel)
                p = fixture / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(blob)

            def remove(rel):
                remember(rel)
                (fixture / rel).unlink()

            def alter(rel, fn):
                d = json.loads((fixture / rel).read_text())
                fn(d)
                write(rel, (json.dumps(d, indent=2) + '\n').encode())

            def reset():
                for rel, blob in changed.items():
                    p = fixture / rel
                    if blob is None:
                        p.unlink(missing_ok=True)
                    else:
                        p.write_bytes(blob)
                changed.clear()

            def rebind_receipt_to_fixture_kit():
                alter(KIT, lambda d: d.update(export_input_receipt_sha256=H(fixture / RECEIPT)))

            def rebind_fixture_audit(rel, fn):
                # Even self-consistently updated fixture hashes cannot excuse a
                # nonzero scoped result, wrong source/quality or missing generator.
                alter(rel, fn)
                def update_receipt(d):
                    for row in d['audit_reports']:
                        if row['file'] == rel:
                            row['sha256'] = H(fixture / rel)
                alter(RECEIPT, update_receipt)
                rebind_receipt_to_fixture_kit()

            def synthetic_saved_game():
                game = checker.INPUT_PATHS['game']
                data = checker.INPUT_PATHS['game_data']
                write(game, b'SYNTHETIC GAME BYTE-BINDING UNIT FIXTURE. NOT A BLENDER MODEL.\n')
                write(data, (fixture / checker.INPUT_PATHS['master_data']).read_bytes())
                for family in checker.FAMILIES:
                    rel = f'docs/leonidas_ii/{family}_GAME.json'
                    alter(rel, lambda a: a.update(source_sha256=H(fixture / game),
                                                   build_data_sha256=H(fixture / data)))
                def update_receipt(d):
                    for key in ('game', 'game_data'):
                        p = fixture / checker.INPUT_PATHS[key]
                        d['inputs'][key].update(sha256=H(p), bytes=p.stat().st_size)
                    for row in d['audit_reports']:
                        row['sha256'] = H(fixture / row['file'])
                alter(RECEIPT, update_receipt)
                alter(KIT, lambda d: d.update(game_source_sha256=H(fixture / game),
                                             game_build_data_sha256=H(fixture / data),
                                             export_input_receipt_sha256=H(fixture / RECEIPT)))

            def case(name, mutation=None, accept=False, fresh=False, assertion=None):
                result = {}
                try:
                    if mutation:
                        mutation()
                    (fixture / REPORT).unlink(missing_ok=True)
                    with contextlib.redirect_stdout(io.StringIO()):
                        code = checker.main() if fresh is None else checker.main(require_saved_sources=fresh)
                    result = json.loads((fixture / REPORT).read_text())
                    okay = code == 0 and result.get('summary') == {'PASS': 42} if accept else code != 0 and result.get('summary', {}).get('FAIL', 0) > 0
                    if assertion:
                        okay = okay and assertion(result)
                    detail = dict(exit_code=code, validation_summary=result.get('summary'),
                                  mode=result.get('mode'), absent_inputs=result.get('receipt_only_absent_inputs'))
                except Exception as exc:
                    okay = False
                    detail = dict(unexpected_exception=type(exc).__name__, message=str(exc)[:300])
                finally:
                    reset()
                row = dict(test=name, status='PASS' if okay else 'FAIL', detail=detail)
                rows.append(row)
                print(row['status'], name, flush=True)

            case('Explicit delivered-package mode checks all 42 gates with GAME scratch absent', accept=True,
                 assertion=lambda r: r['receipt_only_absent_inputs'] == ['game', 'game_data'] and
                 not r['input_verification']['GAME']['fresh_saved_source_and_data_bytes_checked'] and
                 r['mode'] == 'DELIVERED_FROZEN_EXPORT_AND_CANONICAL_AUDIT_BINDINGS')
            case('Default fresh-source mode rejects absent saved GAME bytes', fresh=None,
                 assertion=lambda r: r['mode'] == 'REQUIRE_ACTUAL_SAVED_SOURCES' and
                 any(c['status'] == 'FAIL' and 'actual saved source/build data required' in c['check'] for c in r['checks']))
            case('Explicit strict flag semantics reject absent saved GAME bytes', fresh=True)
            case('Synthetic retained saved-source fixture passes the strict positive path', synthetic_saved_game,
                 accept=True, fresh=True,
                 assertion=lambda r: all(v['fresh_saved_source_and_data_bytes_checked'] for v in r['input_verification'].values()) and not r['receipt_only_absent_inputs'])
            case('Synthetic retained saved-source fixture also passes explicit package mode', synthetic_saved_game,
                 accept=True, assertion=lambda r: not r['receipt_only_absent_inputs'])

            for quality in ('MASTER', 'GAME'):
                for family in checker.FAMILIES:
                    rel = f'docs/leonidas_ii/{family}_{quality}.json'
                    case(f'Exact frozen hash rejects whitespace-only change in {family}_{quality}',
                         lambda rel=rel: write(rel, (fixture / rel).read_bytes() + b'\n'))

            game_audit = 'docs/leonidas_ii/MICRO_GEOMETRY_GAME.json'
            case('A missing canonical GAME audit is not waived with absent scratch', lambda: remove(game_audit))
            case('An empty frozen canonical-audit list is rejected',
                 lambda: alter(RECEIPT, lambda d: d.update(audit_reports=[])))
            case('An omitted canonical-audit identity is rejected',
                 lambda: alter(RECEIPT, lambda d: d['audit_reports'].pop()))
            case('A duplicated canonical-audit identity cannot replace a family',
                 lambda: alter(RECEIPT, lambda d: d['audit_reports'].__setitem__(-1, d['audit_reports'][0])))
            case('Absent GAME source still requires its exact original frozen identity',
                 lambda: alter(RECEIPT, lambda d: d['inputs']['game'].update(sha256='f' * 64)))
            case('Absent GAME build-data still requires its exact original frozen identity',
                 lambda: alter(RECEIPT, lambda d: d['inputs']['game_data'].update(sha256='e' * 64)))
            case('A missing frozen GAME input record is rejected',
                 lambda: alter(RECEIPT, lambda d: d['inputs'].pop('game')))
            case('Changed retained MASTER cannot use a receipt fallback',
                 lambda: write(checker.INPUT_PATHS['master'], (fixture / checker.INPUT_PATHS['master']).read_bytes() + b'changed'))
            case('Changed retained MASTER data cannot use a receipt fallback',
                 lambda: write(checker.INPUT_PATHS['master_data'], (fixture / checker.INPUT_PATHS['master_data']).read_bytes() + b'\n'))
            case('Changed exporter is rejected',
                 lambda: write(checker.INPUT_PATHS['exporter'], (fixture / checker.INPUT_PATHS['exporter']).read_bytes() + b'\n'))
            case('An added current generator key is rejected',
                 lambda: write('blender/leonidas_ii/Unexpected_New_Generator.py', b'# synthetic negative\n'))
            case('An omitted current generator is rejected', lambda: remove('blender/leonidas_ii/working_detail.py'))

            def stale_game():
                synthetic_saved_game()
                p = checker.INPUT_PATHS['game']
                write(p, (fixture / p).read_bytes() + b'altered after freeze')
            case('Changed retained GAME cannot silently fall back to frozen identity', stale_game)

            def stale_game_data():
                synthetic_saved_game()
                p = checker.INPUT_PATHS['game_data']
                write(p, (fixture / p).read_bytes() + b'\n')
            case('Changed retained GAME data cannot silently fall back to frozen identity', stale_game_data)

            def partial_game():
                synthetic_saved_game()
                remove(checker.INPUT_PATHS['game_data'])
            case('Partial saved-source retention is explicitly identified in package mode', partial_game,
                 accept=True, assertion=lambda r: r['receipt_only_absent_inputs'] == ['game_data'] and
                 not r['input_verification']['GAME']['fresh_saved_source_and_data_bytes_checked'])
            case('Strict mode rejects even partially absent GAME saved inputs', partial_game, fresh=True)

            nonzero = {'MICRO_GEOMETRY': 'floor_floating_count',
                       'ROOM_PART_GEOMETRY': 'saved_geometry_mismatches',
                       'PLANT_PART_GEOMETRY': 'saved_geometry_mismatches',
                       'EXTERIOR_PART_GEOMETRY': 'saved_geometry_mismatches',
                       'DOOR_SWEEP_GEOMETRY': 'doors_with_intersections',
                       'SHAFT_CLEARANCE': 'intersecting_poses'}
            for family, key in nonzero.items():
                rel = f'docs/leonidas_ii/{family}_GAME.json'
                case(f'{family} nonzero geometry result is rejected even with rebound fixture hashes',
                     lambda rel=rel, key=key: rebind_fixture_audit(rel, lambda a: a['summary'].__setitem__(key, 1)))
            case('Wrong GAME audit quality rejected even with rebound fixture hashes',
                 lambda: rebind_fixture_audit(game_audit, lambda a: a.update(quality='OLD')))
            case('Wrong GAME audit source rejected even with rebound fixture hashes',
                 lambda: rebind_fixture_audit(game_audit, lambda a: a.update(source_sha256='d' * 64)))
            case('Missing GAME audit generator coverage rejected with rebound fixture hashes',
                 lambda: rebind_fixture_audit(game_audit, lambda a: a['generator_sha256'].pop(next(iter(a['generator_sha256'])))))
            case('Expanded GAME fitting tolerance is rejected with rebound fixture hashes',
                 lambda: rebind_fixture_audit(game_audit, lambda a: a.update(tolerance_m=.001)))

            regression = 'docs/leonidas_ii/inspection/MICRO_CONTACT_REGRESSIONS_GAME.json'
            case('Duplicate regression names cannot inflate a passing total',
                 lambda: alter(regression, lambda a: a['tests'].__setitem__(-1, a['tests'][0])))
            def insufficient_regressions(a):
                a['tests'] = a['tests'][:343]
                a['summary']['pass_count'] = 343
            case('Fewer than the complete current 344 regressions is rejected',
                 lambda: alter(regression, insufficient_regressions))
            case('Wrong regression generator binding is rejected',
                 lambda: alter(regression, lambda a: a.update(generator_sha256={})))
            case('Wrong import-kit GAME source binding is rejected',
                 lambda: alter(KIT, lambda a: a.update(game_source_sha256='a' * 64)))
            case('Wrong import-kit frozen-receipt binding is rejected',
                 lambda: alter(KIT, lambda a: a.update(export_input_receipt_sha256='b' * 64)))
            case('Changed game manifest is rejected',
                 lambda: write('exports/leonidas_ii/game_manifest.json', (fixture / 'exports/leonidas_ii/game_manifest.json').read_bytes() + b'\n'))
            case('A pending rather than completed frozen exporter receipt is rejected',
                 lambda: alter(RECEIPT, lambda a: a.update(status='PENDING')))
            case('A changed original export recorder is rejected',
                 lambda: write('tools/record_leonidas_export_inputs.py', (fixture / 'tools/record_leonidas_export_inputs.py').read_bytes() + b'\n'))
    finally:
        checker.ROOT, checker.DOC, checker.HERE = original_globals

    unchanged = before == {p: H(ROOT / p) for p in before}
    rows.append(dict(test='All original canonical source/data/audit/receipt/manifest bytes remain unchanged',
                     status='PASS' if unchanged else 'FAIL'))
    summary = dict(collections.Counter(r['status'] for r in rows))
    result = dict(schema='victoria.leonidas-ii.delivery-binding-tests/1.0',
                  runner_sha256=H(Path(__file__)), checker_sha256=H(ROOT / 'tools/check_leonidas_micro_delivery.py'),
                  source_sha256=H(ROOT / checker.INPUT_PATHS['master']),
                  export_input_receipt_sha256=H(ROOT / RECEIPT),
                  mode='ISOLATED_COPIED_METADATA_AND_SYNTHETIC_SAVED_BYTE_FIXTURES_NOT_GEOMETRY_VALIDATION',
                  original_inputs_unchanged=unchanged, tests=rows, summary=summary, limits=__doc__)
    (DOC / 'DELIVERY_BINDING_TESTS.json').write_text(json.dumps(result, indent=2) + '\n')
    print('DELIVERY BINDING TESTS', summary, flush=True)
    return 1 if summary.get('FAIL') else 0


if __name__ == '__main__':
    raise SystemExit(main())
