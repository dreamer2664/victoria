"""Independent saved-stair exposed-side/correspondence screen.
Run serially in Blender, once opening each canonical MASTER/GAME source.
It reads actual saved polygons, compares them to regenerated primitive faces
at the existing 0.1 mm storage grid, and tests actual convex exposed side
faces for positive-area coplanar overlap. Does not save or alter the source.
Not an all-surface Boolean, strength, headroom or walking certification.
"""
from pathlib import Path
import sys,os,json,hashlib,re
import bpy
HERE=Path(__file__).resolve().parents[1]/'blender/leonidas_ii';ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from meshkit import Mesh,GAME_QUALITY
from shipdesign.leonidas_ii import STAIRS
from audit_common import audit_inputs,current_generator_hashes,binding_mismatches
from audit_room_parts import face_hash,saved_face_hash
from test_micro_contacts import exposed_plane_overlaps
import structure
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
model,datafile=audit_inputs(False);data=json.loads(datafile.read_text());generator=current_generator_hashes()
assert not binding_mismatches(generator,data['source_files_sha256']),'Generator changed after source build'
quality='GAME' if GAME_QUALITY else 'MASTER';captured={};original=Mesh.emit

def capture(self,name,col,kind='furniture',**kwargs):
 if kind=='stair':captured[name]=self
 return []
Mesh.emit=capture
try:structure.build_stairs()
finally:Mesh.emit=original
bpy.context.view_layer.update();rows=[]
for s in STAIRS:
 name='Stair_'+s['id'];expected=captured[name]
 # Only actual two-digit Mesh.emit chunks, not a different flight whose
 # ID extends this one (After_Orlop versus After_Orlop_Starboard).
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_kind')=='stair' and (o.name==name or re.fullmatch(re.escape(name)+r'_\d{2}',o.name))]
 assert obs,(name,'Missing saved stair')
 actual=Mesh()
 for ob in obs:
  off=len(actual.v);actual.v.extend(tuple(ob.matrix_world@v.co) for v in ob.data.vertices);actual.f.extend(tuple(off+i for i in p.vertices) for p in ob.data.polygons)
 generated_hash=face_hash(expected.v,expected.f);saved_hash=saved_face_hash(obs);sides=[]
 for sign in (-1,1):
  plane=s['y']+sign*s['width']/2;tolerance=.000002
  faces=sum(all(abs(actual.v[i][1]-plane)<tolerance for i in f) for f in actual.f)
  overlaps=exposed_plane_overlaps(actual,1,plane,tolerance)
  sides.append(dict(sign=sign,plane_y_m=plane,float32_plane_tolerance_m=tolerance,actual_faces_in_plane=faces,overlapping_face_pairs=len(overlaps),overlaps=overlaps[:12],status='PASS' if faces>=2 and not overlaps else 'FAIL'))
 rows.append(dict(stair=s['id'],objects=[o.name for o in obs],actual_vertices=len(actual.v),actual_faces=len(actual.f),generated_faces_sha256=generated_hash,saved_faces_sha256=saved_hash,saved_geometry_match=generated_hash==saved_hash,sides=sides,status='PASS' if generated_hash==saved_hash and all(v['status']=='PASS' for v in sides) else 'FAIL'))
old=Mesh();old.box((.15,0,.145),(.315,1.8,.07),'Oak');old.box((0,0,.09),(.030,1.8,.186),'Oak')
negative=exposed_plane_overlaps(old,1,.9)
summary=dict(stairs=len(rows),sides=sum(len(r['sides']) for r in rows),saved_geometry_mismatches=sum(not r['saved_geometry_match'] for r in rows),exposed_overlap_pairs=sum(s['overlapping_face_pairs'] for r in rows for s in r['sides']),flags=sum(r['status']!='PASS' for r in rows),restored_old_full_width_riser_negative_detected=bool(negative))
assert current_generator_hashes()==generator,'Generator changed during read-only audit'
report=dict(schema='victoria.leonidas-ii.saved-stair-joinery/1.0',quality=quality,status='SAVED_SOURCE_BOUND_SCREEN',source_file=str(model.relative_to(ROOT)),source_sha256=H(model),build_data_sha256=H(datafile),auditor_sha256=H(__file__),convex_plane_tester_sha256=H(HERE/'test_micro_contacts.py'),generator_sha256=generator,rows=rows,summary=summary,limits=__doc__)
out=ROOT/'docs/leonidas_ii'/f'STAIR_JOINERY_{quality}.json';out.write_text(json.dumps(report,indent=2)+'\n');print('SAVED STAIR JOINERY',quality,summary,flush=True)
assert summary['stairs']==len(STAIRS) and summary['sides']==2*len(STAIRS) and not(summary['flags'] or summary['saved_geometry_mismatches'] or summary['exposed_overlap_pairs']) and summary['restored_old_full_width_riser_negative_detected'],summary
