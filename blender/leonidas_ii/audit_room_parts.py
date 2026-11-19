"""Whole-compartment small-part contact screen against ACTUAL saved finishes.

Reconstructs authored primitive boundaries (lost after chunked mesh emission),
then verifies that their vertex/polygon multiset is exactly the saved furniture.
Only then screens their finite-part graph against saved walls/floor/ceiling.
Flags require source/visual examination; no claim of universal solid/physics QA.
"""
import os,sys,json,hashlib,time,math,gc
from pathlib import Path
from collections import defaultdict,Counter
import bpy
import numpy as np
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
import interiors as I
from meshkit import Mesh,GAME_QUALITY
from shipdesign.leonidas_ii import ROOMS
from audit_fittings import parts,contact,TOL,H
from audit_common import audit_inputs,current_generator_hashes,binding_mismatches

def mesh_tree(obs):
 vv=[];ff=[]
 for ob in obs:
  off=len(vv);vv.extend(ob.matrix_world@v.co for v in ob.data.vertices);ff.extend(tuple(off+k for k in p.vertices) for p in ob.data.polygons)
 return BVHTree.FromPolygons(vv,ff) if ff else None

def face_hash(vv,ff,origin=None):
 # Reproduce Blender's ACTUAL float32 vertex serialization before the
 # unchanged 0.1mm hash grid. Double->float rounding at a grid boundary
 # otherwise changed 46 M_Entrance face bins despite identical vertices.
 # Movers also pass through the same local-origin subtraction/world-matrix
 # round trip as Mesh.emit and saved_face_hash; no tolerance is enlarged.
 if origin is None:vv=np.asarray(vv,dtype=np.float32)
 else:
  origin=Vector(origin);matrix=Matrix.Translation(origin)
  vv=[matrix@(Vector(v)-origin) for v in vv]
 # Emission can reorder vertices and recalculate winding. Compare the
 # multiset of unordered polygon corners, explicitly quantised to 0.1mm.
 faces=[]
 for f in ff:
  corners=sorted(tuple(round(float(vv[i][k]),4) for k in range(3)) for i in f)
  faces.append(tuple(corners))
 return hashlib.sha256(repr(sorted(faces)).encode()).hexdigest()

def saved_face_hash(obs):
 vv=[];ff=[]
 for ob in obs:
  off=len(vv);vv.extend(ob.matrix_world@v.co for v in ob.data.vertices);ff.extend(tuple(off+k for k in p.vertices) for p in ob.data.polygons)
 return face_hash(vv,ff)

def regenerate(r):
 I.CURRENT_ROOM=r['id'];m=Mesh();kind=r['kind'];original_emit=Mesh.emit
 # fit_service also emits ONE exterior flue, explicitly outside this
 # furniture-only reconstruction. Do not duplicate it into the saved scene.
 # Refuse any new, silently omitted direct emission introduced in future.
 def no_exterior_emit(self,name,col,kind='furniture',**kwargs):
  assert name=='Galley_Exterior_CommonFlue' and kind=='superstructure',(name,kind,'Unexpected direct emission during furniture reconstruction')
  return []
 Mesh.emit=no_exterior_emit
 try:
  if kind.startswith('cabin'):I.fit_cabin(m,r)
  elif kind.startswith('dorm'):I.fit_dorm(m,r)
  elif kind in ('dining','dining_second','library','music','smoking','writing','lounge_second','mess'):I.fit_public(m,r)
  else:I.fit_service(m,r)
 finally:Mesh.emit=original_emit
 return m

def analyse_room(r,m,context):
 ps=parts(m);parent=list(range(len(ps)))
 def root(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 cells=defaultdict(list);pairs=0;tested=0
 for i,a in enumerate(ps):
  lo=[math.floor((v-TOL)/.5) for v in a['lo']];hi=[math.floor((v+TOL)/.5) for v in a['hi']]
  keys=[(x,y,z) for x in range(lo[0],hi[0]+1) for y in range(lo[1],hi[1]+1) for z in range(lo[2],hi[2]+1)]
  candidates=set()
  for key in keys:candidates.update(cells[key])
  for j in candidates:
   if root(i)==root(j):continue
   tested+=1
   if contact(a,ps[j]):parent[root(i)]=root(j);pairs+=1
  for key in keys:cells[key].append(i)
 rooted=set();bearing_parts=0
 for i,p in enumerate(ps):
  rr=root(i)
  if rr in rooted:continue
  okay=bool(p['bvh'].overlap(context)) if context else False
  if not okay and context:
   for v in p['vertices']:
    hit=context.find_nearest(v,TOL)
    if hit[0] is not None and hit[3]<=TOL:okay=True;break
  if okay:rooted.add(rr);bearing_parts+=1
 clusters=defaultdict(list)
 for i in range(len(ps)):clusters[root(i)].append(i)
 issues=[]
 for rr,ids in clusters.items():
  if rr in rooted:continue
  low=[min(ps[i]['lo'][k] for i in ids) for k in range(3)];high=[max(ps[i]['hi'][k] for i in ids) for k in range(3)];tiles=Counter()
  for i in ids:tiles.update(ps[i]['tiles'])
  issues.append(dict(parts=ids,low=low,high=high,tiles=dict(tiles)))
 return dict(room=r['id'],primitive_parts=len(ps),clusters=len(clusters),rooted_clusters=len(rooted),detached_clusters=issues,contact_unions=pairs,broadphase_candidates_tested=tested)

def stairhall_bearings(r,m):
 # A column attached at its capital could pass the rigid graph while its
 # foot hung over a well. Test BOTH actual extreme faces independently.
 ps=[p for p in parts(m) if set(p['tiles'])=={'Oak'} and p['hi'].z-p['lo'].z>2 and max(p['hi'].x-p['lo'].x,p['hi'].y-p['lo'].y)<.36]
 assert len(ps)==4,(r['id'],'Expected four actual turned columns',len(ps))
 floor=mesh_tree([o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==r['id'] and o.get('LII_kind')=='finish'])
 ceiling=mesh_tree([o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==r['id'] and o.get('LII_kind')=='ceiling']);rows=[]
 for p in ps:
  readings={}
  for name,zz,context,direction in (('foot',p['lo'].z,floor,Vector((0,0,-1))),('capital',p['hi'].z,ceiling,Vector((0,0,1)))):
   vv=[v for v in p['vertices'] if abs(v.z-zz)<.00015];c=sum(vv,Vector())/len(vv);probes=[c]+[c*.65+vv[j*len(vv)//4]*.35 for j in range(4)];gaps=[]
   for v in probes:
    hit=context.ray_cast(v-direction*.02,direction,.20) if context else (None,None,None,None)
    if hit[0] is not None:gaps.append(float((hit[0]-v).dot(direction)))
   readings[name]=dict(actual_extreme_z=zz,probe_count=len(probes),gaps_m=gaps,finite_bearing=any(abs(g)<=TOL for g in gaps))
  rows.append(dict(x=(p['lo'].x+p['hi'].x)/2,y=(p['lo'].y+p['hi'].y)/2,**readings,status='PASS' if all(v['finite_bearing'] for v in readings.values()) else 'FAIL'))
 return rows


def main():
 candidate=os.getenv('LII_MICRO_CANDIDATE')=='1';model_path,data_path=audit_inputs(candidate)
 data=json.loads(data_path.read_text());t=time.time();rows=[]
 start=current_generator_hashes();mismatches=binding_mismatches(start,data['source_files_sha256'])
 if not candidate:assert not mismatches,'Changed generator: rebuild first.'
 bpy.context.view_layer.update()
 only=os.getenv('LII_MICRO_ROOMS','').split(',') if os.getenv('LII_MICRO_ROOMS') else None
 for r in ROOMS:
  if r['kind'] in ('machinery','steering') or only and r['id'] not in only:continue
  m=regenerate(r);obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==r['id'] and o.get('LII_kind')=='furniture'];fh=face_hash(m.v,m.f);sh=saved_face_hash(obs)
  if not candidate:assert fh==sh,(r['id'],'Reconstructed primitive polygons differ from saved emitted geometry',fh,sh)
  context=mesh_tree([o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==r['id'] and o.get('LII_kind') in ('wall','finish','ceiling')]);row=analyse_room(r,m,context);row.update(generated_faces_sha256=fh,saved_faces_sha256=sh,saved_geometry_match=fh==sh)
  if r['kind']=='stairhall':row['stair_column_bearings']=stairhall_bearings(r,m)
  rows.append(row)
  print('ROOM FINITE PARTS',r['id'],row['primitive_parts'],'detached',len(row['detached_clusters']),'saved-match',fh==sh,flush=True);del m,context;gc.collect()
 summary=dict(rooms=len(rows),parts=sum(r['primitive_parts'] for r in rows),rooms_with_detached=sum(bool(r['detached_clusters']) for r in rows),detached_clusters=sum(len(r['detached_clusters']) for r in rows),saved_geometry_mismatches=sum(not r['saved_geometry_match'] for r in rows),stair_columns=sum(len(r.get('stair_column_bearings',[])) for r in rows),stair_column_bearing_flags=sum(c['status']!='PASS' for r in rows for c in r.get('stair_column_bearings',[])))
 assert all(H(ROOT/f)==h for f,h in start.items()),'Generator changed while auditing.'
 report=dict(generator_sha256=start,generator_binding_mismatches=mismatches,build_data_file=str(data_path.relative_to(ROOT)),build_data_sha256=H(data_path),schema='victoria.leonidas-ii.room-finite-part-screen/1.2',status='CANDIDATE_GENERATOR_NOT_DELIVERED_SOURCE' if candidate else 'SAVED_SOURCE_BOUND_SCREEN',source_file=str(model_path.relative_to(ROOT)),source_sha256=H(model_path),quality='GAME' if GAME_QUALITY else 'MASTER',auditor_sha256=H(__file__),part_auditor_sha256=H(HERE/'audit_fittings.py'),tolerance_m=TOL,rooms=rows,summary=summary,seconds=round(time.time()-t,2),limits='Finite primitive surface intersections/nearest sampled vertices/closed-part containment, plus exact generated/saved face correspondence rounded to 0.1mm, anchored to saved room walls/floor/ceiling. Not universal Boolean connectivity, all-triangle distance, load/strength, visual inspection, door sweeps, every machinery/exterior component, humanoid walking or Studio acceptance.')
 out=ROOT/os.getenv('LII_ROOM_PART_REPORT','docs/leonidas_ii/ROOM_PART_GEOMETRY_AUDIT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('ROOM PART SCREEN',json.dumps(summary),round(time.time()-t,2),flush=True)
 if os.getenv('LII_MICRO_REQUIRE_PASS')=='1' and (summary['detached_clusters'] or summary['saved_geometry_mismatches'] or summary['stair_column_bearing_flags']):raise RuntimeError('Detached room parts, column foot/capital bearing flags or generated/saved mesh mismatch remain')

if __name__=='__main__':main()
