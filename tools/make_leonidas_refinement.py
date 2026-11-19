"""Curate current-source refinement evidence; never infer manual approval.

Exactly 19 individually opened full-resolution interior JPGs plus six opened
close-up diagnostics. Both sets must use the same actual master/renderer.
Only the six scratch close-ups are copied; full interiors already have their
own durable files. This is a curated subset, not the full 256-view acceptance.
"""
from pathlib import Path
import base64
import hashlib
import html
import io
import json
import shutil

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/leonidas_ii'
OUT = ROOT / 'renders/leonidas_ii/refinement'
REVIEW = DOC / 'DETAIL_VISUAL_REVIEW.json'
EXPECTED = {
    'Interior_Dining_First', 'Interior_Library', 'Interior_Smoking',
    'Interior_Music', 'Interior_Writing', 'Interior_Grand_Stair',
    'Interior_Dining_Second', 'Interior_Second_Lounge', 'Interior_Cabin_First',
    'Interior_Cabin_Second', 'Interior_Captain', 'Interior_Officer',
    'Interior_Galley', 'Interior_Bakery', 'Interior_Pantry',
    'Interior_Hospital', 'Interior_Barber', 'Interior_Crew',
    'Interior_Wheelhouse', 'Detail_Exterior_Bridge',
    'Detail_Exterior_Promenade', 'Detail_Promenade_Bench',
    'Detail_Mast_Ladder', 'Detail_Funnel_Ladder', 'Detail_Lifebuoy_Hook',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def esc(value):
    return html.escape(str(value), quote=True)


def workspace_path(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT.resolve()), 'Path is outside repository')
    return path


def validate():
    review = load(REVIEW)
    source = sha(ROOT / 'models/leonidas_ii/Aurelian_1889.blend')
    renderer = sha(ROOT / 'blender/leonidas_ii/render.py')
    require(review.get('schema') == 'victoria.leonidas-ii.focused-visual-review/1.1',
            'Missing current curated manual-review schema')
    require(review.get('status') == 'FOCUSED_REVIEW_COMPLETE_FULL_EVIDENCE_SEPARATE',
            'Curated review is not explicitly complete')
    require(review.get('source_sha256') == source and
            review.get('renderer_sha256') == renderer,
            'Stale master or renderer in curated manual review')
    images = review.get('images', [])
    require(len(images) == len(EXPECTED) and
            {i.get('image') for i in images} == EXPECTED,
            'Exactly all 25 planned curated views must be individually reviewed')
    require(not review.get('blocking_issues'), 'Unresolved curated visual blockers')
    audits = {}
    for name, count, auditor in (
        ('DETAIL_GEOMETRY_AUDIT', 7, 'audit_details.py'),
        ('STRUCTURE_GEOMETRY_AUDIT', 3, 'audit_structure.py'),
    ):
        path = DOC / (name + '.json')
        audit = load(path)
        require(review.get(name.lower() + '_sha256') == sha(path),
                'Manual review is not bound to current ' + name)
        require(audit.get('source_sha256') == source and
                audit.get('auditor_sha256') == sha(ROOT / 'blender/leonidas_ii' / auditor),
                'Stale source or auditor in ' + name)
        require(len(audit.get('checks', [])) == count and
                all(c.get('status') == 'PASS' for c in audit['checks']),
                'Missing or failing geometry gates in ' + name)
        audits[name] = audit
    detail = audits['DETAIL_GEOMETRY_AUDIT']
    require(detail.get('build_data_sha256') ==
            sha(ROOT / 'exports/leonidas_ii/build_data.json'), 'Stale detail-audit data')
    require(detail.get('ladder_auditor_sha256') ==
            sha(ROOT / 'blender/leonidas_ii/audit_ladders.py'), 'Stale ladder auditor')
    require(audits['STRUCTURE_GEOMETRY_AUDIT'].get('hull_spec_sha256') ==
            sha(ROOT / 'shipdesign/leonidas_ii.py'), 'Stale structure contract')
    data = load(ROOT / 'exports/leonidas_ii/build_data.json')
    require(detail['checks'][0]['count'] == len(data['fixture_mounts']) and
            detail['checks'][4]['count'] == len(data['rigging_feet']) ==
            len(data['rigging_lines']), 'Audit/display contact totals do not match build data')
    ladder = detail['access_ladders']['summary']
    require(ladder['ladders'] == len(data['access_ladders']) == 5 and
            ladder['failures'] == 0, 'Incomplete exterior-ladder audit coverage')
    durable_register = workspace_path(review['render_register'])
    require(durable_register == OUT / 'camera_register.json',
            'Durable curated camera register must be in the handoff folder')
    if durable_register.exists():
        rows = load(durable_register)
    else:
        # Interior pilot pixels must NOT replace their full-resolution main
        # views. Select interiors only from the main register, and close-ups
        # only from the separately source-bound diagnostic register.
        primary = load(workspace_path(review['primary_render_register']))
        closeups = load(workspace_path(review['detail_render_register']))
        rows = [r for r in primary if Path(r['file']).stem in EXPECTED and
                Path(r['file']).stem.startswith('Interior_')]
        rows += [r for r in closeups if Path(r['file']).stem in EXPECTED and
                 Path(r['file']).stem.startswith('Detail_')]
    by_name = {Path(r['file']).stem: r for r in rows}
    require(len(by_name) == len(rows), 'Duplicate selected camera-register stems')
    verified = []
    for opened in images:
        name = opened['image']
        require(name in by_name, 'Missing current camera registration: ' + name)
        entry = by_name[name]
        path = workspace_path(entry['file'])
        require(path.suffix == '.jpg' and path.is_file(), 'Not a final JPG: ' + name)
        require(entry.get('source_sha256') == source and
                entry.get('renderer_sha256') == renderer, 'Stale image source: ' + name)
        require(sha(path) == entry.get('sha256') == opened.get('sha256'),
                'Exact opened/final-JPG identity does not match: ' + name)
        interior = name.startswith('Interior_')
        expected_pixels = [1600, 1000] if interior else [1120, 700]
        minimum_samples = 12 if interior else 24
        with Image.open(path) as image:
            require(list(image.size) == entry.get('pixels') == expected_pixels,
                    'Wrong full-resolution/close-up pixel dimensions: ' + name)
        require(entry.get('cycles_samples', 0) >= minimum_samples,
                'Insufficient recorded samples: ' + name)
        if interior:
            require(path.parent == ROOT / 'renders/leonidas_ii',
                    'Curated interiors must use durable main full-resolution files')
        require(entry.get('cutaway') is (name == 'Interior_Grand_Stair'),
                'Cutaway/enclosure label mismatch: ' + name)
        require(opened.get('inspection_method') == 'OPENED_FINAL_JPG',
                'Final JPG has not been explicitly opened: ' + name)
        require(opened.get('status') in (
            'REVIEWED_WITH_LIMITATIONS', 'REVISION_VERIFIED_IN_VIEW'),
            'Missing explicit limited-scope review status: ' + name)
        require(isinstance(opened.get('observation'), str) and
                len(opened['observation'].strip()) >= 40 and
                isinstance(opened.get('limitations'), str) and
                len(opened['limitations'].strip()) >= 30,
                'Substantive observation/limitations required: ' + name)
        verified.append((entry, opened, path))
    return review, source, audits, data, verified


PAGE = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SS Aurelian · physical detail refinement</title><style>
*{box-sizing:border-box}body{margin:0;background:#f0ede5;color:#233a42;font:16px/1.55 system-ui,Arial,sans-serif}header{background:#152f38;color:#f4f0e6;padding:52px max(24px,6vw) 38px}header small{color:#d3b67d;letter-spacing:.16em}h1{font:500 clamp(36px,5vw,66px)/1.08 Georgia,serif;max-width:1000px;margin:18px 0}header p{max-width:970px;color:#c8d5d6}.status{display:inline-block;border:1px solid #a68c58;color:#f2dcb1;padding:6px 11px;font-size:12px}main{padding:32px max(24px,6vw) 60px}.intro{max-width:1040px}h2{font:600 24px/1.25 Georgia,serif;margin:10px 0}.metrics{display:flex;gap:34px;flex-wrap:wrap;margin-top:28px}.metrics b{font-size:27px;display:block;color:#fff}.metrics span{font-size:12px;color:#b7c9ce}.hash{font-size:11px;overflow-wrap:anywhere}.note{background:#e5e1d4;border-left:4px solid #9e824e;padding:18px 22px;margin:25px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(430px,1fr));gap:24px;margin-top:32px}article{background:#fffdf8;border:1px solid #d7d5cb;border-radius:4px;overflow:hidden}article img{display:block;width:100%;aspect-ratio:1.6;object-fit:contain;background:#56666b}article>div{padding:18px 22px 24px}small{font-size:10px;font-weight:700;letter-spacing:.08em;color:#8f712f}p{margin:12px 0}.limit{font-size:13px;color:#687778}code{font-size:10px;overflow-wrap:anywhere}li{margin:7px 0}footer{background:#dce2dd;padding:25px 6vw;color:#4c6265;font-size:12px}@media(max-width:600px){.grid{grid-template-columns:1fr}header{padding-top:32px}.metrics{gap:20px}}
</style><header><small>OPERATION VICTORIA / LEONIDAS-II</small>
<h1>SS Aurelian<br>Physical detail &amp; room identity</h1>
<span class="status">CURATED REFINEMENT REVIEW — FULL EVIDENCE / STUDIO ACCEPTANCE ARE SEPARATE</span>
<p>New Cycles views of the revised geometry: attached lamps, purpose-specific room plans, coordinated cabins, working fittings and supported exterior detail. Not concept images, a texture-only restyle or simulated gameplay.</p>
<div class="metrics"><div><b>@@INTERIORS@@ + @@CLOSEUPS@@</b><span>full-resolution interiors + close-ups</span></div><div><b>@@MOUNTS@@</b><span>ceiling contacts ray-checked</span></div><div><b>@@FEET@@</b><span>deck-fastened rigging landings</span></div><div><b>@@ROOMS@@</b><span>physical spaces retained</span></div></div>
<p class="hash">REVIEWED MASTER SHA-256 · @@SOURCE@@</p></header>
<main><section class="intro"><h2>Changes in the model</h2>
<p>Separate first- and second-class dining plans, a shared library table and low window bookcases, perimeter writing secretaires, and distinct billiards, music and games arrangements. Five coordinated cabin schemes, frame-supported bunk ladders and purpose-specific sanitary/working fittings replace generic layouts and isolated details.</p>
<p>Ceiling fittings have real backplates; low bodies were shortened after the clearance check found six failures. Joinery rails butt between stiles instead of overlapping coplanar corner faces. Window reveals, catches and brackets are dimensional; pictures and instruments are upright. Crowned roofs, eaves, fascia, finite weather planks, benches, hooked lifebuoy brackets, actual grab-rope bridles and deck-fastened stays add physical detail without moving the boat sockets. Mast/funnel ladders have continuous rails and finite carrier supports.</p>
<div class="note"><strong>Evidence boundary.</strong> These @@IMAGES@@ individually opened files are one same-source curated subset: @@INTERIORS@@ interiors at 1600 × 1000, plus @@CLOSEUPS@@ close-ups at 1120 × 700. The stair view explicitly removes walls. Other enclosed views retain their room enclosure while omitting unrelated occluders as described by the renderer. This subset does not replace the separate 51-major / 203-survey / 2-supplementary full-evidence review. The old 256-image / 47-pass checkpoint belongs to published <code>6a9ee98</code>. Current geometry/format/runtime checks do not imply Studio acceptance.</div>
<h2>Executed geometry checks</h2><ul>@@CHECKS@@</ul>
<p>Actual-shell/stern/propeller regression: @@STRUCTURE_COUNT@@ PASS. Room/rigging/exterior-ladder checks: @@DETAIL_COUNT@@ PASS. The ladder gate checks @@RUNG_ENDS@@ actual rung ends and @@LADDER_MOUNTS@@ carrier interfaces across five exterior ladders. These are not universal internal connectivity, welded union, strength, finite-radius rigging clearance or continuous avatar-walking certification. Nest-platform access openings and live exterior climbing are not implemented.</p>
<p>Accommodation remains <strong>628 passenger positions + 117 crew</strong>. First class includes 114 permanent beds + 114 modeled convertible settee positions; live conversion is unimplemented. Dining remains 96 / 48 seats. Three boat sockets are not a complete lifesaving inventory. Hydrostatics, world fit, multiplayer carry and measured FPS remain unverified.</p>
</section><section class="grid">@@CARDS@@</section></main>
<footer>Actual model and authored PBR maps. Adaptive Cycles sample caps are at least 12 for the full-resolution interiors / 24 for close-ups; individual pixels may converge earlier. Two diffuse/glossy bounces, a temporary 1K rendering cache and conventional tiled OIDN leave softness/noise; delivered maps remain 2K. Embedded thumbnails are reduced; the separate JPGs retain their recorded dimensions. Features are verified only where visible, not on hidden surfaces. Manual identities: docs/leonidas_ii/DETAIL_VISUAL_REVIEW.json. Source: models/leonidas_ii/Aurelian_1889.blend. No user aesthetic approval or playable-release claim is implied.</footer></html>'''


def main():
    review, source, audits, data, verified = validate()
    OUT.mkdir(parents=True, exist_ok=True)
    entries, cards = [], []
    for entry, opened, path in verified:
        interior = path.stem.startswith('Interior_')
        dest = path if interior else OUT / path.name
        if path.resolve() != dest.resolve():
            shutil.copy2(path, dest)
        published = {**entry, 'file': str(dest.relative_to(ROOT)),
                     'focused_refinement': True,
                     'evidence_role': 'full_resolution_interior' if interior else 'closeup_diagnostic'}
        entries.append(published)
        with Image.open(dest) as original:
            image = original.convert('RGB')
        image.thumbnail((960, 600), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=86, optimize=True)
        uri = 'data:image/jpeg;base64,' + base64.b64encode(buffer.getvalue()).decode()
        label = ('WALL-REMOVED STAIR DIAGNOSTIC' if entry['cutaway'] else
                 'FULL-RESOLUTION ENCLOSED ROOM' if interior
                 else 'ACTUAL EXTERIOR CLOSE-UP')
        cards.append('<article><img src="' + uri + '" alt="' + esc(entry['title']) +
                     '"><div><small>' + label + '</small><h2>' + esc(entry['title']) +
                     '</h2><p>' + esc(opened['observation']) +
                     '</p><p class="limit">' + esc(opened['limitations']) +
                     '</p><code>' + esc(published['file']) + ' · ' +
                     str(entry['pixels'][0]) + ' × ' + str(entry['pixels'][1]) +
                     ' · ' + str(entry['cycles_samples']) +
                     ' adaptive samples</code></div></article>')
    detail, structure = audits['DETAIL_GEOMETRY_AUDIT'], audits['STRUCTURE_GEOMETRY_AUDIT']
    interiors = sum(e['evidence_role'] == 'full_resolution_interior' for e in entries)
    values = {
        'IMAGES': len(entries), 'INTERIORS': interiors, 'CLOSEUPS': len(entries)-interiors,
        'MOUNTS': detail['checks'][0]['count'], 'FEET': detail['checks'][4]['count'],
        'ROOMS': data['counts']['physical_compartments'], 'SOURCE': source,
        'DETAIL_COUNT': len(detail['checks']), 'STRUCTURE_COUNT': len(structure['checks']),
        'RUNG_ENDS': detail['access_ladders']['summary']['rung_ends'],
        'LADDER_MOUNTS': detail['access_ladders']['summary']['frame_mounts'],
        'CHECKS': ''.join('<li>' + esc(c['check']) + '</li>' for c in detail['checks']),
        'CARDS': '\n'.join(cards),
    }
    page = PAGE
    for key, value in values.items():
        page = page.replace('@@' + key + '@@', str(value))
    require('@@' not in page, 'Unresolved page template marker')
    (OUT / 'camera_register.json').write_text(json.dumps(entries, indent=2) + '\n')
    (DOC / 'DETAIL_REFINEMENT.html').write_text(page)
    print('Saved curated handoff:', interiors, 'full-resolution interiors +',
          len(entries)-interiors, 'close-ups; full/Studio acceptance is separate.')


if __name__ == '__main__':
    main()
