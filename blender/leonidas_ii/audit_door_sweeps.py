"""Actual saved door mesh vs actual saved in-room fixed meshes during swing.
Discrete angular samples are a regression screen, NOT continuous collision or
live avatar traversal. AABB-only and already-open-door routing missed this.
"""
import os,sys,json,math,hashlib,time
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from shipdesign.leonidas_ii import ROOMS
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
from audit_common import audit_inputs,current_generator_hashes,binding_mismatches

def tree(obs):
 """Triangulate actual saved polygons, retaining exact face-owner lookup."""
 vv=[];ff=[];owners=[]
 for ob in obs:
  ob.data.calc_loop_triangles();off=len(vv);vv.extend(ob.matrix_world@v.co for v in ob.data.vertices)
  for tri in ob.data.loop_triangles:
   ff.append(tuple(off+i for i in tri.vertices));owners.append(dict(object=ob.name,polygon=int(tri.polygon_index)))
 return (BVHTree.FromPolygons(vv,ff,all_triangles=True),owners) if ff else (None,[])

def sample_sweep(vv,ff,pivot,angle_deg,obstacle,interval=2):
 """Returns suspect intersections, NOT penetration depth or continuous proof."""
 pivot=Vector(pivot);vv=[Vector(p) for p in vv];bad=[]
 degrees=list(range(0,int(abs(angle_deg))+1,interval))
 if degrees[-1]!=abs(angle_deg):degrees.append(abs(angle_deg))
 for angle in degrees:
  a=math.radians(math.copysign(angle,angle_deg));rot=Matrix.Rotation(a,3,'Z');moved=[pivot+rot@(p-pivot) for p in vv]
  leaf=BVHTree.FromPolygons(moved,ff,all_triangles=True);overlap=leaf.overlap(obstacle) if obstacle else []
  if overlap:
   fi,oi=overlap[0];face=ff[fi];point=sum((moved[i] for i in face),Vector())/len(face)
   bad.append(dict(angle_deg=math.copysign(angle,angle_deg),surface_pair_count=len(overlap),first_obstacle_triangle=oi,representative_leaf_triangle_center=list(point)))
 return len(degrees),bad

def main():
 t=time.time();rows=[];issues=[];candidate=os.getenv('LII_DOOR_CANDIDATE')=='1';model_path,data_path=audit_inputs(candidate)
 data=json.loads(data_path.read_text());rmap={r['id']:r for r in ROOMS}
 start=current_generator_hashes();mismatches=binding_mismatches(start,data['source_files_sha256'])
 if not candidate:assert not mismatches,'Changed generator: rebuild before source-bound door screen.'
 bpy.context.view_layer.update()
 for d in data['doors']:
  ob=bpy.data.objects.get(d['name']);rid=d['id'];r=rmap[rid];assert ob is not None,(rid,'missing actual door')
  obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==rid and o.get('LII_kind') in ('furniture','navigation','steering','mover','wall','finish','ceiling','glazing','sign')]
  obstacle,owners=tree(obs);ob.data.calc_loop_triangles();vv=[ob.matrix_world@v.co for v in ob.data.vertices];ff=[tuple(p.vertices) for p in ob.data.loop_triangles]
  poses,bad=sample_sweep(vv,ff,d['hinge'],d['angle_deg'],obstacle)
  for b in bad:b['first_fixed_face']=owners[b['first_obstacle_triangle']]
  row=dict(room=rid,name=ob.name,angle_deg=d['angle_deg'],poses=poses,intersecting_poses=bad,status='SUSPECT_INTERSECTION' if bad else 'CLEAR_AT_SAMPLED_POSES');rows.append(row)
  if bad:issues.append(row)
  print('DOOR SWEEP',rid,row['status'],len(bad),flush=True)
 assert all(H(ROOT/f)==h for f,h in start.items()),'Generator changed while auditing.'
 report=dict(schema='victoria.leonidas-ii.door-finite-sweep/1.3',status='OLD_SAVED_MODEL_CANDIDATE_NOT_CURRENT_GENERATOR' if candidate else 'SAVED_SOURCE_BOUND_SCREEN',quality='GAME' if os.getenv('LII_GAME_DETAIL')=='1' else 'MASTER',source_file=str(model_path.relative_to(ROOT)),source_sha256=H(model_path),build_data_file=str(data_path.relative_to(ROOT)),build_data_sha256=H(data_path),auditor_sha256=H(__file__),generator_sha256=start,generator_binding_mismatches=mismatches,sample_interval_degrees=2,summary=dict(doors=len(rows),poses=sum(x['poses'] for x in rows),doors_with_intersections=len(issues)),doors=rows,seconds=round(time.time()-t,2),limits='Actual triangulated door/in-room furniture/navigation/steering/default-pose movers AND own wall/jamb/floor/ceiling/glazing/sign surface intersections at 2-degree poses, including real handles/hinges. No own-jamb or hinge exemption. Adjacent rooms remain outside this scoped screen. Not containment, continuous swept-volume proof, penetration-depth/clear-route certification or Roblox Studio acceptance. Representative triangle centres are NOT measured penetration points. Every intersection requires inspection.')
 out=ROOT/os.getenv('LII_DOOR_SWEEP_REPORT','docs/leonidas_ii/DOOR_SWEEP_GEOMETRY_AUDIT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('DOOR SWEEPS',json.dumps(report['summary']),flush=True)
 if os.getenv('LII_MICRO_REQUIRE_PASS')=='1' and (issues or mismatches):raise RuntimeError('Actual sampled door/furnishing intersections or stale generator bindings remain')

if __name__=='__main__':main()
