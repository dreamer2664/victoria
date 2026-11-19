"""Focused actual-surface shaft/carrier interference regression.

Only crankshaft vs its stationary engine casting, and tailshaft/couplings/
thrust collars vs their stationary shaft carriers. 15-degree poses and two
injected failures per pair. NOT every engine mover, connecting rod, bearing
load/strength, fluid passage, all running clearances or continuous motion QA.
"""
import os,sys,re,json,math,time
from pathlib import Path
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from meshkit import Mesh,MOVERS,GAME_QUALITY
from audit_common import audit_inputs,current_generator_hashes,binding_mismatches
from audit_plant_parts import capture
from audit_room_parts import face_hash,saved_face_hash
from audit_fittings import H


def tris(m):
    me=bpy.data.meshes.new('TemporaryClearanceTriangulation');me.from_pydata(m.v,[],m.f);me.update();me.calc_loop_triangles()
    vv=[v.co.copy() for v in me.vertices];ff=[tuple(t.vertices) for t in me.loop_triangles];bpy.data.meshes.remove(me)
    return vv,ff


def collisions(vv,ff,pivot,angle,obstacle,shift=(0,0,0)):
    pivot=Vector(pivot);rot=Matrix.Rotation(math.radians(angle),3,'X');delta=Vector(shift)
    moved=[pivot+rot@(v-pivot)+delta for v in vv]
    return len(BVHTree.FromPolygons(moved,ff,all_triangles=True).overlap(obstacle))


def main():
    t=time.time();candidate=os.getenv('LII_SHAFT_CANDIDATE')=='1';model_path,data_path=audit_inputs(candidate)
    data=json.loads(data_path.read_text());start=current_generator_hashes();mismatches=binding_mismatches(start,data['source_files_sha256'])
    if not candidate:assert not mismatches,'Rebuild changed source first.'
    bpy.context.view_layer.update();captured={a['name']:a for a in capture()};rows=[];bindings=[]
    for moving,fixed,journal in (('Crankshaft_3Throws','Engine_Bed_Standards_Cylinders',(-26,0,3)),('Tailshaft_And_Couplings','Shaft_Bearings_SternTube_Pintles',(-66.1,0,3))):
        for name in (moving,fixed):
            a=captured[name];pattern=re.compile(re.escape(name)+r'(?:_\d+)?$');obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and pattern.fullmatch(o.name)]
            generated=face_hash(a['mesh'].v,a['mesh'].f);saved=saved_face_hash(obs);bindings.append(dict(name=name,generated_faces_sha256=generated,saved_faces_sha256=saved,match=generated==saved))
            if not candidate:assert generated==saved,(name,'Source/saved mesh mismatch')
        rotor=captured[moving]['mesh'];stator=captured[fixed]['mesh'];vv,ff=tris(rotor);sv,sf=tris(stator);obstacle=BVHTree.FromPolygons(sv,sf,all_triangles=True)
        pivot=next(m['origin'] for m in MOVERS if m['name']==moving);poses=[]
        for angle in range(0,360,15):
            hit=collisions(vv,ff,pivot,angle,obstacle);poses.append(dict(degrees=angle,surface_pairs=hit))
        # Reproduce the original defect with a real solid cap, rather than
        # checking only nominal cylinder radii or a synthetic overall AABB.
        cap=Mesh();cap.cylinder(journal,.40,.10,'Iron',48,(1,0,0));cv,cf=tris(cap);plug=BVHTree.FromPolygons(cv,cf,all_triangles=True)
        cap_negative=collisions(vv,ff,pivot,0,plug)>0
        displacement_negative=collisions(vv,ff,pivot,0,obstacle,shift=(0,.025,0))>0
        rows.append(dict(moving=moving,fixed=fixed,pivot=pivot,poses=poses,intersecting_poses=sum(p['surface_pairs']>0 for p in poses),negative_solid_journal_cap_detected=cap_negative,negative_25mm_radial_displacement_detected=displacement_negative))
        print('SHAFT/CARRIER',moving,'intersecting poses',rows[-1]['intersecting_poses'],'negatives',cap_negative,displacement_negative,flush=True)
    assert start==current_generator_hashes(),'Generator changed during audit.'
    summary=dict(pairs=len(rows),poses=sum(len(r['poses']) for r in rows),intersecting_poses=sum(r['intersecting_poses'] for r in rows),negative_controls_passed=sum(r['negative_solid_journal_cap_detected']+r['negative_25mm_radial_displacement_detected'] for r in rows),negative_controls_expected=2*len(rows),saved_geometry_mismatches=sum(not b['match'] for b in bindings))
    report=dict(schema='victoria.leonidas-ii.shaft-carrier-screen/1.0',status='CANDIDATE_GENERATOR_NOT_DELIVERED_SOURCE' if candidate else 'SAVED_SOURCE_BOUND_SCREEN',quality='GAME' if GAME_QUALITY else 'MASTER',source_file=str(model_path.relative_to(ROOT)),source_sha256=H(model_path),build_data_file=str(data_path.relative_to(ROOT)),build_data_sha256=H(data_path),auditor_sha256=H(__file__),generator_sha256=start,generator_binding_mismatches=mismatches,summary=summary,pairs=rows,geometry_binding=bindings,seconds=round(time.time()-t,2),limits=__doc__)
    out=ROOT/os.getenv('LII_SHAFT_CLEARANCE_REPORT','docs/leonidas_ii/SHAFT_CLEARANCE_AUDIT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('SHAFT CLEARANCE',json.dumps(summary),flush=True)
    if os.getenv('LII_MICRO_REQUIRE_PASS')=='1' and (summary['intersecting_poses'] or summary['negative_controls_passed']!=summary['negative_controls_expected'] or summary['saved_geometry_mismatches'] or mismatches):raise RuntimeError('Shaft carrier intersections, failed negatives or source/saved mismatch remain')

if __name__=='__main__':main()
