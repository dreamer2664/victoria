"""Independent actual-mesh contact check for revised decorative fixtures.
It ray-tests the emitted ceiling AND emitted fixture meshes, not just the
nominal room-top number. This is not universal collision/Studio acceptance.
"""
import sys,json,hashlib,math,collections
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from shipdesign.leonidas_ii import ROOMS
D=json.loads((ROOT/'exports/leonidas_ii/build_data.json').read_text());R={r['id']:r for r in ROOMS}

def tree(objects):
 vv=[];ff=[]
 for ob in objects:
  me=ob.data;me.calc_loop_triangles();off=len(vv);vv.extend(tuple(ob.matrix_world@v.co) for v in me.vertices);ff.extend(tuple(off+k for k in t.vertices) for t in me.loop_triangles)
 return BVHTree.FromPolygons(vv,ff,all_triangles=True) if ff else None

def meshes(rid,kind):return [o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==rid and o.get('LII_kind')==kind]
ceil={};furn={};mounts=[]
for a in D.get('fixture_mounts',[]):
 rid=a['room'];x,y,z=a['position']
 if rid not in ceil:
  ceil[rid]=tree(meshes(rid,'ceiling'));furn[rid]=tree(meshes(rid,'steering') if rid=='S_Steering' else meshes(rid,'furniture'))
 hit=ceil[rid].ray_cast(Vector((x,y,z-.04)),Vector((0,0,1)),.30) if ceil[rid] else (None,None,None,None)
 plate=furn[rid].ray_cast(Vector((x+.055,y,z+.015)),Vector((0,0,-1)),.10) if furn[rid] else (None,None,None,None)
 gap=float(hit[0].z-z) if hit[0] is not None else None
 overlap=float(plate[0].z-hit[0].z) if plate[0] is not None and hit[0] is not None else None
 okay=gap is not None and abs(gap)<.001 and overlap is not None and -.001<=overlap<=.012
 mounts.append(dict(room=rid,style=a['style'],position=a['position'],ceiling_hit_z=float(hit[0].z) if hit[0] is not None else None,backplate_hit_z=float(plate[0].z) if plate[0] is not None else None,surface_datum_error_m=gap,backplate_overlap_m=overlap,standing_clearance_m=a['bottom']-R[rid]['z'],over_table=a['over_table'],status='PASS' if okay else 'FAIL'))
# Recompute fixed-prefab envelope/pair diagnostics from final build data.
outside=[];pairs=[];by=collections.defaultdict(list)
for f in D['fixtures']:
 r=R[f['room']];lo,hi=f['bounds'];over=max(r['x0']-lo[0],hi[0]-r['x1'],r['y0']-lo[1],hi[1]-r['y1'],hi[2]-r['top'])
 if over>.10:outside.append(dict(room=r['id'],fixture=f['label'],over_m=over))
 by[f['room']].append(f)
for rid,ff in by.items():
 for i,a in enumerate(ff):
  for b in ff[i+1:]:
   delta=[min(a['bounds'][1][k],b['bounds'][1][k])-max(a['bounds'][0][k],b['bounds'][0][k]) for k in range(3)]
   if min(delta[:2])>.035 and delta[2]>.18:pairs.append(dict(room=rid,a=a['label'],b=b['label'],overlap_m=delta))
checks=[dict(check='Actual ceiling/backplate contact at every revised room fixture',status='PASS' if mounts and all(a['status']=='PASS' for a in mounts) else 'FAIL',count=len(mounts)),dict(check='Fixed prefab bounds remain within room envelope (100mm tolerance)',status='PASS' if not outside else 'FAIL',issues=outside),dict(check='No substantial inter-prefab AABB overlap suspects',status='PASS' if not pairs else 'FAIL',issues=pairs)]
low=[a for a in mounts if not a['over_table'] and a['standing_clearance_m']<2.0]
checks.append(dict(check='Revised non-table fixture bounding bottoms >= 2.0m above deck',status='PASS' if not low else 'FAIL',issues=low))
# Free room-specific BVHs before testing the exterior assembly, keeping
# this independent final-mesh audit usable on the small build host.
ceil.clear();furn.clear()
import gc;gc.collect()
feet=[];deck_trees={};anchor_trees={}
for a in D.get('rigging_feet',[]):
 x,y,z=a['position'];dk=a['deck'];prefix=a['anchor_object_prefix']
 if dk not in deck_trees:deck_trees[dk]=tree([o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_kind')=='deck' and o.get('LII_deck')==dk])
 if prefix not in anchor_trees:anchor_trees[prefix]=tree([o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefix)])
 support=deck_trees[dk].ray_cast(Vector((x,y,z+.08)),Vector((0,0,-1)),.22) if deck_trees[dk] else (None,None,None,None)
 sole=anchor_trees[prefix].ray_cast(Vector((x,y,z-.05)),Vector((0,0,1)),.15) if anchor_trees[prefix] else (None,None,None,None)
 embed=float(support[0].z-sole[0].z) if support[0] is not None and sole[0] is not None else None
 feet.append(dict(id=a['id'],deck=dk,deck_hit_z=float(support[0].z) if support[0] is not None else None,sole_hit_z=float(sole[0].z) if sole[0] is not None else None,sole_embed_m=embed,status='PASS' if embed is not None and -.001<=embed<=.026 else 'FAIL'))
checks.append(dict(check='All standing-rigging chainplate soles contact actual deck meshes',status='PASS' if feet and all(v['status']=='PASS' for v in feet) else 'FAIL',count=len(feet),issues=[v for v in feet if v['status']!='PASS']))
architecture=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_kind') in ('wall','ceiling','superstructure','deck','skylight','bulkhead') and max((o.matrix_world@Vector(v)).z for v in o.bound_box)>11.70]
obstacles=tree(architecture);crossings=[]
for a in D.get('rigging_lines',[]):
 A=Vector(a['top']);B=Vector(a['bottom']);direction=(B-A).normalized();length=(B-A).length-.40
 hit=obstacles.ray_cast(A+direction*.20,direction,length) if obstacles else (None,None,None,None)
 if hit[0] is not None:crossings.append(dict(id=a['id'],hit_position=list(hit[0]),distance_from_upper_end_m=float(hit[3])+.20))
checks.append(dict(check='Standing cable centrelines do not pierce emitted deckhouse/deck/casing architecture',status='PASS' if D.get('rigging_lines') and not crossings else 'FAIL',count=len(D.get('rigging_lines',[])),issues=crossings))
# The room AABB/contact gates missed internally unsupported climbing rungs.
# Test separate final rung/frame meshes and actual mast/shell/deck carriers.
obstacles=None;deck_trees.clear();anchor_trees.clear();gc.collect()
from audit_ladders import inspect_access_ladders
ladder_audit=inspect_access_ladders(D)
checks.append(dict(check='All five exterior ladders: actual rung/frame joints and carrier supports',status='PASS' if not ladder_audit['issues'] else 'FAIL',**ladder_audit['summary'],issues=ladder_audit['issues']))
report=dict(schema='victoria.leonidas-ii.detail-geometry-audit/1.2',source_sha256=hashlib.sha256((ROOT/'models/leonidas_ii/Aurelian_1889.blend').read_bytes()).hexdigest(),build_data_sha256=hashlib.sha256((ROOT/'exports/leonidas_ii/build_data.json').read_bytes()).hexdigest(),auditor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),checks=checks,mounts=mounts,rigging_feet=feet,access_ladders=ladder_audit,ladder_auditor_sha256=hashlib.sha256((HERE/'audit_ladders.py').read_bytes()).hexdigest(),limits=['Standing-rigging rays test straight cable centrelines, excluding 200mm at the intended end fittings. They are not finite-radius cable/rail contact or strength/load certification.','Fixture contact rays inspect the actual room ceiling and backplate separately. They do not certify all hidden component-to-component contacts.','AABB placement is conservative; no Boolean union, continuous avatar walk, door swing, multiplayer physics or Studio FPS acceptance is implied.'])
(ROOT/'docs/leonidas_ii/DETAIL_GEOMETRY_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
for c in checks:print(c['status'],c['check'],len(c.get('issues',[])),flush=True)
print('FIXTURE MOUNT CONTACT FAILURES',json.dumps([m for m in mounts if m['status']=='FAIL']),flush=True)
if any(c['status']=='FAIL' for c in checks):raise RuntimeError('Actual detail-geometry gate failed; inspect the source-bound report before export/publication')
