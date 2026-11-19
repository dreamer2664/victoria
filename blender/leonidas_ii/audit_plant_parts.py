"""Reconstruct actual plant primitives; screen rigid joints against real structure.
Internal rigid mover joints are screened separately from deliberate running
bearing clearances. This is not force/load, every interference or motion QA.
"""
import os,sys,json,math,time,re,gc
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from meshkit import Mesh,GAME_QUALITY
from audit_fittings import analyse,H
from audit_room_parts import analyse_room,face_hash,saved_face_hash,mesh_tree
import machinery
from audit_common import audit_inputs,current_generator_hashes,binding_mismatches

def capture():
 emitted=[];original=Mesh.emit
 def collect(self,name,col,kind='furniture',deck='',room='',origin=None,mover=None,material='atlas',**kwargs):
  emitted.append(dict(name=name,mesh=self,kind=kind,room=room,origin=origin,mover=mover,material=material));return []
 Mesh.emit=collect
 try:machinery.build()
 finally:Mesh.emit=original
 return emitted

def main():
 t=time.time();candidate=os.getenv('LII_PLANT_CANDIDATE')=='1';model_path,data_path=audit_inputs(candidate)
 data=json.loads(data_path.read_text());start=current_generator_hashes();mismatches=binding_mismatches(start,data['source_files_sha256'])
 if not candidate:assert not mismatches,'Changed generator: rebuild first.'
 bpy.context.view_layer.update();captured=capture();static=Mesh();owner=[];binding=[];moving=[]
 excluded_kinds={'wall','finish','ceiling','sign','glazing','door'}
 for a in captured:
  m=a['mesh'];pattern=re.compile(re.escape(a['name'])+r'(?:_\d+)?$');obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and pattern.fullmatch(o.name)]
  generated=face_hash(m.v,m.f,a['origin']);saved=saved_face_hash(obs);binding.append(dict(name=a['name'],kind=a['kind'],mover=a['mover'],generated_faces_sha256=generated,saved_faces_sha256=saved,match=generated==saved,saved_objects=[o.name for o in obs]))
  if not candidate:assert generated==saved,(a['name'],'Captured source does not match saved mesh')
  if a['mover']:
   row=analyse(a['name'],m);row['role']='RIGID_INTERNAL_JOINTS_ONLY_NOT_RUNNING_INTERFACES';moving.append(row);print('PLANT MOVER INTERNAL',a['name'],'detached',len(row['detached_clusters']),flush=True)
  elif a['kind'] not in excluded_kinds:
   static.append(m);owner.extend([a['name']]*len(m.groups))
 # Only actual hull, tank/deck structure and the actual local steering/
 # shaft-alley enclosure may anchor plant. Never use old machinery meshes
 # as surrogate supports for a changed candidate.
 context_obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.get('LII_kind') in ('shell','structure','deck','bulkhead') or o.get('LII_room') in ('E_Alley','S_Steering') and o.get('LII_kind') in ('wall','finish','ceiling'))]
 context=mesh_tree(context_obs);row=analyse_room(dict(id='ALL_STATIC_PLANT'),static,context)
 for issue in row['detached_clusters']:
  issue['assemblies']=sorted({owner[i] for i in issue['parts']})
  print('PLANT DETACHED',issue['assemblies'],'bounds',issue['low'],issue['high'],'materials',issue['tiles'],flush=True)
 assert all(H(ROOT/f)==h for f,h in start.items()),'Generator changed during audit.'
 summary=dict(captured_assemblies=len(captured),rigid_static_parts=row['primitive_parts'],static_detached_clusters=len(row['detached_clusters']),mover_assemblies=len(moving),mover_internal_detached_clusters=sum(len(r['detached_clusters']) for r in moving),saved_geometry_mismatches=sum(not b['match'] for b in binding))
 report=dict(schema='victoria.leonidas-ii.plant-finite-part-screen/1.0',status='CANDIDATE_GENERATOR_NOT_DELIVERED_SOURCE' if candidate else 'SAVED_SOURCE_BOUND_SCREEN',quality='GAME' if GAME_QUALITY else 'MASTER',source_file=str(model_path.relative_to(ROOT)),source_sha256=H(model_path),build_data_file=str(data_path.relative_to(ROOT)),build_data_sha256=H(data_path),auditor_sha256=H(__file__),generator_sha256=start,generator_binding_mismatches=mismatches,summary=summary,rigid_static=row,movers=moving,geometry_binding=binding,structural_context=[o.name for o in context_obs],seconds=round(time.time()-t,2),limits='Primitive surface/nearest vertex/containment graph anchored to actual hull/decks/frames and local enclosures, plus separate rigid mover-internal graphs. Running bearing gaps between different movers/static plant are deliberately not rigid-joint tests. Not every collision, shaft bore, sweep, mechanical functioning, pressure/load/strength, visual inspection or Studio acceptance. Surface connectivity via a pipe does not by itself establish a credible equipment foundation; source and eye-level examination remain necessary.')
 out=ROOT/os.getenv('LII_PLANT_PART_REPORT','docs/leonidas_ii/PLANT_PART_GEOMETRY_AUDIT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PLANT PARTS',json.dumps(summary),round(time.time()-t,2),flush=True)
 if os.getenv('LII_MICRO_REQUIRE_PASS')=='1' and (summary['static_detached_clusters'] or summary['mover_internal_detached_clusters'] or summary['saved_geometry_mismatches'] or mismatches):raise RuntimeError('Plant support/internal joints or source binding still flagged')

if __name__=='__main__':main()
