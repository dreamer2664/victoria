"""Source/saved-bound exterior finite-part support screen.

Covers structural decks/stairs, topsides, weather roofs/planks, ladders, navigation,
rigging and the separately emitted galley flue. Static contact paths and
internal rigid mover joints are separate. Not strength, rope/chain dynamics,
every clash, moving interfaces or live walking/climbing/boat acceptance.
"""
import os,sys,re,json,time,gc
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from meshkit import Mesh,GAME_QUALITY
from audit_common import audit_inputs,current_generator_hashes,binding_mismatches
from audit_fittings import analyse,H,TOL
from audit_room_parts import analyse_room,face_hash,saved_face_hash,mesh_tree
import topsides
import structure
import interiors
from shipdesign.leonidas_ii import ROOMS


def capture():
    emitted=[];original=Mesh.emit
    def collect(self,name,col,kind='furniture',deck='',room='',origin=None,mover=None,material='atlas',**kwargs):
        assert self.groups and self.groups[-1]==len(self.f),(name,'Untracked raw primitive faces')
        emitted.append(dict(name=name,mesh=self,kind=kind,room=room,origin=origin,mover=mover,material=material));return []
    Mesh.emit=collect
    try:
        structure.build_decks()
        structure.build_stairs()
        topsides.build()
        # This is the ONLY direct service emission outside room furniture.
        r=next(r for r in ROOMS if r['id']=='S_Galley')
        interiors.CURRENT_ROOM=r['id'];interiors.fit_service(Mesh(),r)
    finally:Mesh.emit=original
    assert sum(a['name']=='Galley_Exterior_CommonFlue' for a in emitted)==1
    return emitted


def main():
    t=time.time();candidate=os.getenv('LII_EXTERIOR_CANDIDATE')=='1';model_path,data_path=audit_inputs(candidate)
    data=json.loads(data_path.read_text());start=current_generator_hashes();mismatches=binding_mismatches(start,data['source_files_sha256'])
    if not candidate:assert not mismatches,'Changed generator: rebuild first.'
    bpy.context.view_layer.update();captured=capture();static=Mesh();owner=[];binding=[];moving=[];captured_names=set()
    for a in captured:
        m=a['mesh'];pattern=re.compile(re.escape(a['name'])+r'(?:_\d+)?$');obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and pattern.fullmatch(o.name)]
        captured_names.update(o.name for o in obs)
        generated=face_hash(m.v,m.f,a['origin']);saved=saved_face_hash(obs)
        binding.append(dict(name=a['name'],kind=a['kind'],mover=a['mover'],generated_faces_sha256=generated,saved_faces_sha256=saved,match=generated==saved,saved_objects=[o.name for o in obs]))
        if not candidate:assert generated==saved,(a['name'],'Generated primitive polygons differ from saved geometry')
        if a['mover']:
            row=analyse(a['name'],m);row['role']='RIGID_INTERNAL_JOINTS_ONLY_NOT_RUNNING_INTERFACES';moving.append(row)
        else:
            static.append(m);owner.extend([a['name']]*len(m.groups))
    # NEVER let an old copy of a recaptured assembly anchor its corrected
    # version. This also excludes recaptured decks/pillars/weather roofs.
    context_obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in captured_names and o.get('LII_kind') in ('shell','structure','deck','bulkhead','wall','finish','ceiling','stair')]
    assert not captured_names.intersection(o.name for o in context_obs)
    context=mesh_tree(context_obs);row=analyse_room(dict(id='ALL_STATIC_EXTERIOR'),static,context)
    for issue in row['detached_clusters']:
        issue['assemblies']=sorted({owner[i] for i in issue['parts']})
        print('EXTERIOR DETACHED',issue['assemblies'],issue['low'],issue['high'],issue['tiles'],flush=True)
    assert all(H(ROOT/f)==h for f,h in start.items()),'Generator changed during audit.'
    summary=dict(captured_assemblies=len(captured),rigid_static_parts=row['primitive_parts'],static_detached_clusters=len(row['detached_clusters']),mover_assemblies=len(moving),mover_internal_detached_clusters=sum(len(r['detached_clusters']) for r in moving),saved_geometry_mismatches=sum(not b['match'] for b in binding))
    report=dict(schema='victoria.leonidas-ii.exterior-finite-part-screen/1.0',status='CANDIDATE_GENERATOR_NOT_DELIVERED_SOURCE' if candidate else 'SAVED_SOURCE_BOUND_SCREEN',quality='GAME' if GAME_QUALITY else 'MASTER',source_file=str(model_path.relative_to(ROOT)),source_sha256=H(model_path),build_data_file=str(data_path.relative_to(ROOT)),build_data_sha256=H(data_path),auditor_sha256=H(__file__),generator_sha256=start,generator_binding_mismatches=mismatches,tolerance_m=TOL,summary=summary,rigid_static=row,movers=moving,geometry_binding=binding,structural_context=[o.name for o in context_obs],seconds=round(time.time()-t,2),limits='Finite primitive surface/nearest-vertex/containment support paths to real structure; old copies of recaptured assemblies excluded as anchors. Rigid mover-internal contact screened separately. Does not establish absence of deep intersections, credible foundations/fastening/load/strength, chain/rope kinematics, continuous/adjacent-room sweeps, climbing, boat contact, visual inspection or Studio acceptance. All flags require physical/source examination; zero flags are not global approval.')
    out=ROOT/os.getenv('LII_EXTERIOR_PART_REPORT','docs/leonidas_ii/EXTERIOR_PART_GEOMETRY_AUDIT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
    print('EXTERIOR PARTS',json.dumps(summary),round(time.time()-t,2),flush=True)
    if os.getenv('LII_MICRO_REQUIRE_PASS')=='1' and (summary['static_detached_clusters'] or summary['mover_internal_detached_clusters'] or summary['saved_geometry_mismatches'] or mismatches):raise RuntimeError('Exterior finite-part joints or source binding still flagged')

if __name__=='__main__':main()
