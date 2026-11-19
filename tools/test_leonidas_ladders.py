"""Blender-only isolated regression for the exterior-ladder contact auditor.

Run serially, without loading/writing the editable master:
  blender -b -t 2 --python-exit-code 1 -P tools/test_leonidas_ladders.py
Repeat with LII_GAME_DETAIL=1. Reports explicitly concern this generated
fixture subset, NOT every part of the saved model or Studio climbing.
"""
import hashlib
import json
import os
from pathlib import Path
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / 'blender/leonidas_ii'
sys.path[:0] = [str(HERE), str(ROOT)]
from meshkit import materials, ACCESS_LADDERS
import structure
import topsides
import weather_detail
from audit_ladders import inspect_access_ladders


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


bpy.ops.wm.read_factory_settings(use_empty=True)
materials()
structure.build_decks()
topsides.funnels_and_casings()
topsides.masts_and_rig()
weather_detail.crown_roof('After_DeckCabin_Continuous_CrownedRoof',
                          (-54.35, -25.30, -3.65, 3.65), 19.88, .13)
bpy.context.view_layer.update()
data = {'access_ladders': ACCESS_LADDERS}
positive = inspect_access_ladders(data)
assert positive['summary'] == dict(ladders=5, rung_ends=330, frame_mounts=44, failures=0)
frames = [o for o in bpy.context.scene.objects
          if o.name.startswith('Climbing_Ladder_Mast_Fore_Frame')]
assert frames
for ob in frames:
    ob.location.x += .15
bpy.context.view_layer.update()
displaced = inspect_access_ladders(data)
assert any(v.get('issue') == 'Rung/frame joint' for v in displaced['issues'])
for ob in frames:
    ob.location.x -= .15
bpy.context.view_layer.update()
assert not inspect_access_ladders(data)['issues']
for ob in frames:
    bpy.data.objects.remove(ob, do_unlink=True)
missing = inspect_access_ladders(data)
assert any(v.get('issue') == 'Missing separate emitted frame/rungs' for v in missing['issues'])
quality = 'GAME' if os.getenv('LII_GAME_DETAIL') == '1' else 'MASTER'
report = dict(
    schema='victoria.leonidas-ii.ladder-audit-regression/1.0',
    scope='ISOLATED_GENERATOR_FIXTURE_ONLY; no saved ship mesh is modified or comprehensively certified',
    quality=quality,
    runner_sha256=sha(Path(__file__)),
    auditor_sha256=sha(HERE / 'audit_ladders.py'),
    generator_sha256={str((HERE/f).relative_to(ROOT)): sha(HERE/f)
                      for f in ('access_detail.py', 'meshkit.py', 'topsides.py',
                                'structure.py', 'weather_detail.py')},
    tests=[
        dict(test='Five generated climbing ladders have all recorded actual contacts',
             status='PASS', detail=positive['summary']),
        dict(test='Existing foremast frame displaced by 150mm fails actual rung-contact rays',
             status='PASS', rejected_joint_count=sum(v.get('issue') == 'Rung/frame joint'
                                                     for v in displaced['issues'])),
        dict(test='Completely removed actual foremast frame is rejected', status='PASS'),
    ],
    limits='The full saved-master ladder gate is separately recorded in DETAIL_GEOMETRY_AUDIT.json. '
           'These tests do not certify universal joint connectivity, nest hatches, '
           'load rating, Humanoid climbing or Studio acceptance.',
)
path = ROOT / 'docs/leonidas_ii' / ('LADDER_AUDIT_REGRESSION_' + quality + '.json')
path.write_text(json.dumps(report, indent=2) + '\n')
print('ISOLATED LADDER REGRESSION', quality, '3 PASS;', positive['summary'], flush=True)
