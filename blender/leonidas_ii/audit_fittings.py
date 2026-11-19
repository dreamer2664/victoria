"""Independent finite-part support screens, beyond whole-prefab AABBs.

Prototype parts are the actual emitted primitive surfaces, not proxy boxes.
A graph uses BVH surface intersections, nearest-vertex/surface distance and
closed-mesh containment. This is a conservative joint screen, not a load or
universal Boolean proof. Every flagged cluster needs source/visual inspection.
The saved-master floor screen raycasts actual Finish_ meshes from saved lowest sole patches;
it never treats a nominal furniture origin as the finished floor. The tub
uses its four actual cast feet, not the below-floor plumbing tail, as datum.
"""
import os,sys,json,math,hashlib,time
from pathlib import Path
from collections import Counter,defaultdict
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
import furnishings as F
import period_detail as P
import service_fittings as S
import working_detail as W
from meshkit import Mesh,GAME_QUALITY

TOL=.0006
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def inside(bvh,p):
    # Surface crossings in a non-axis-aligned direction; only used AFTER
    # the surface-intersection and distance tests for fully nested parts.
    direction=Vector((.734713,.442193,.512781)).normalized();origin=Vector(p);count=0
    for _ in range(96):
        loc,normal,index,distance=bvh.ray_cast(origin,direction,200.)
        if loc is None:break
        count+=1;origin=loc+direction*.000013
    return bool(count%2)


def parts(mesh):
    out=[];start=0
    for end in mesh.groups:
        faces=mesh.f[start:end];ids=sorted({i for f in faces for i in f});remap={v:i for i,v in enumerate(ids)}
        vv=[Vector(mesh.v[i]) for i in ids];ff=[tuple(remap[i] for i in f) for f in faces]
        lo=Vector(tuple(min(v[k] for v in vv) for k in range(3)));hi=Vector(tuple(max(v[k] for v in vv) for k in range(3)))
        out.append(dict(vertices=vv,faces=ff,lo=lo,hi=hi,bvh=BVHTree.FromPolygons(vv,ff,epsilon=0.0),tiles=dict(Counter(mesh.tiles[start:end]))))
        start=end
    assert start==len(mesh.f)
    return out


def contact(a,b):
    if any(a['hi'][k]+TOL<b['lo'][k] or b['hi'][k]+TOL<a['lo'][k] for k in range(3)):return False
    if a['bvh'].overlap(b['bvh']):return True
    # Nearest vertices on either actual surface detect most flat/nested
    # contact patches. They are NOT an all-triangle minimum-distance proof.
    for first,second in ((a,b),(b,a)):
        for v in first['vertices']:
            loc,n,i,d=second['bvh'].find_nearest(v,TOL)
            if loc is not None and d<=TOL:return True
    if inside(a['bvh'],b['vertices'][0]) or inside(b['bvh'],a['vertices'][0]):return True
    return False


def analyse(label,mesh):
    ps=parts(mesh);parent=list(range(len(ps)))
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(a,b):parent[root(a)]=root(b)
    pairs=0
    for i,a in enumerate(ps):
        for j in range(i):
            if contact(a,ps[j]):union(i,j);pairs+=1
    clusters=defaultdict(list)
    for i in range(len(ps)):clusters[root(i)].append(i)
    lowest=min(p['lo'].z for p in ps)
    # Separate external floor/surface gap from internal disconnected parts.
    if label.startswith('ceiling_'):
        highest=max(p['hi'].z for p in ps);anchor_ids={root(i) for i,p in enumerate(ps) if p['hi'].z>=highest-TOL}
    else:anchor_ids={root(i) for i,p in enumerate(ps) if p['lo'].z<=lowest+TOL}
    detached=[]
    for r,ids in clusters.items():
        if r in anchor_ids:continue
        lo=[min(ps[i]['lo'][k] for i in ids) for k in range(3)];hi=[max(ps[i]['hi'][k] for i in ids) for k in range(3)]
        tiles=Counter()
        for i in ids:tiles.update(ps[i]['tiles'])
        detached.append(dict(parts=ids,low=lo,high=hi,tiles=dict(tiles)))
    return dict(recipe=label,primitive_parts=len(ps),actual_contact_pairs=pairs,clusters=len(clusters),lowest_z=lowest,detached_clusters=detached)


def recipes():
    for style in ('dining','writing','armchair'):yield 'chair_'+style,F.chair(style)
    for length in (1.82,2.1,2.65):yield 'sofa_'+str(length),F.sofa(length)
    for length,width,cloth in ((2.7,1.02,True),(2.25,.86,False),(6.0,1.4,False)):
        yield 'table_'+str((length,width,cloth)),F.table(length,width,cloth)
    for name in ('service_setting','washstand','wc','bathtub','range_unit'):
        yield name,getattr(F,name)()
    for style in ('first','hospital'):yield 'bed_'+style,F.bed(style)
    for variant in range(3):yield 'bunk_'+str(variant),F.bunk(variant)
    for side in (-1,1):yield 'bunk_aisle_ladder_'+str(side),F.bunk(0,ladder_side=side)
    for width in (.62,1.5):yield 'wardrobe_'+str(width),F.wardrobe(width)
    for width in (1.2,1.6):yield 'desk_'+str(width),F.desk(width)
    yield 'bookcase',F.bookcase()
    for kind in ('pantry','linen'):
        for variant in range(3):yield 'shelving_'+kind+'_'+str(variant),F.shelving(kind,variant)
    for name in ('round_table','plain_chair','utility_table','plain_bench','low_bookcase','book_stack','billiard_table','grand_piano','piano_stool'):
        yield name,getattr(P,name)()
    yield 'plain_bench_backless',P.plain_bench(back=False)
    for name in ('chart_table','mail_cubby','drinks_rack','ice_chest','cargo_crate','staved_barrel','medicine_cabinet','barber_chair','iron_safe','medical_trolley','provision_rack','folded_deckchair'):
        yield name,getattr(S,name)()
    yield 'bake_oven',W.bake_oven()
    for name in ('tea_tray','game_board','paper_and_ink'):
        m=Mesh();getattr(P,name)(m,0,0,0);yield name,m
    from meshkit import guarded_lamp
    m=Mesh();guarded_lamp(m,0,0,0);yield 'ceiling_guarded_lamp',m
    for w,h in ((.38,.41),(.48,.34),(1.35,.62),(1.70,.66)):
        m=Mesh();P.framed_panel(m,0,0,0,w,h);yield 'framed_panel_'+str((w,h)),m
    m=Mesh();P.wall_clock(m,0,0,0);yield 'wall_clock',m
    m=Mesh();P.reading_sconce(m,{},0,0,0);yield 'reading_sconce',m
    from shipdesign.leonidas_ii import ROOMS
    r=next(r for r in ROOMS if r['id']=='S_Music')
    for style in ('cabin','opal','chandelier','club','reading','marine'):
        m=Mesh();P.ceiling_fixture(m,r,-18,0,style);yield 'ceiling_fixture_'+style,m
    from meshkit import flange,handwheel
    from machinery import gauge
    for direction,axis in (('longitudinal',(1,0,0)),('transverse',(0,1,0)),('vertical',(0,0,1))):
        m=Mesh();flange(m,(0,0,0),.16,axis);yield 'flange_'+direction,m
        m=Mesh();flange(m,(0,0,0),.16,axis,bore=.08);yield 'bored_flange_'+direction,m
        m=Mesh();handwheel(m,(0,0,0),.14,axis);yield 'handwheel_'+direction,m
        m=Mesh();gauge(m,(0,0,0),.13,axis);yield 'gauge_'+direction,m


def floor_screen(data):
    """Actual saved planar sole patches, not arbitrary extreme vertices.

    A finite foot may correctly bridge a 2mm board/grout joint; demanding
    floor below every outer corner false-flags it. Probe three INTERIOR
    points on EACH actual lowest sole face instead. Missing whole soles,
    millimetre lift and penetration still fail; no tolerance increase.
    """
    import numpy as np
    room_soles=defaultdict(list);room_vertices=defaultdict(list);finish_geometry={};finish={}
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH':continue
        if ob.name.startswith('Furniture_'):
            arr=np.empty(len(ob.data.vertices)*3,dtype=np.float64);ob.data.vertices.foreach_get('co',arr);arr=arr.reshape(-1,3);matrix=np.array(ob.matrix_world);arr=arr@matrix[:3,:3].T+matrix[:3,3]
            room_vertices[ob.get('LII_room','')].append((ob.name,arr))
            for polygon in ob.data.polygons:
                normal=ob.matrix_world.to_3x3()@polygon.normal
                if normal.z>-.99:continue
                vv=arr[list(polygon.vertices)]
                if np.ptp(vv[:,2])>.00015:continue
                room_soles[ob.get('LII_room','')].append(dict(z=float(vv[0,2]),lo=vv.min(0),hi=vv.max(0),vertices=[Vector(v) for v in vv],object=ob.name,polygon=polygon.index))
        elif ob.name.startswith('Finish_'):
            vv,ff=finish_geometry.setdefault(ob.get('LII_room',''),([],[]));off=len(vv)
            vv.extend(ob.matrix_world@v.co for v in ob.data.vertices);ff.extend(tuple(off+i for i in p.vertices) for p in ob.data.polygons)
    for rid,(vv,ff) in finish_geometry.items():finish[rid]=BVHTree.FromPolygons(vv,ff)
    summary=Counter();issues=[];curved=[];tested=0;patches_tested=0;missing=0;penetrating=0;floating=0
    for f in data['fixtures']:
        if f['label']=='PlaceSetting':continue
        rid=f['room'];low,high=f['bounds'];bearing_z=f.get('floor_bearing_z',low[2])
        def issue(reason,**details):
            summary[f['label']]+=1;issues.append(dict(room=rid,label=f['label'],position=f['position'],reason=reason,**details))
        if rid not in finish:
            missing+=1;issue('NO_ACTUAL_FINISH_CONTEXT');continue
        soles=[p for p in room_soles[rid] if abs(p['z']-bearing_z)<.00015 and all(p['lo'][k]>=low[k]-.00015 and p['hi'][k]<=high[k]+.00015 for k in (0,1))]
        tested+=1
        if f['label']=='ThreeFootPianoStool' and len(soles)!=3:
            missing+=1;issue('MISSING_ACTUAL_PIANO_STOOL_FOOT_SOLES',expected=3,actual=len(soles));continue
        if not soles:
            # Rounded caster tyres have actual point/line contacts, not a
            # planar shoe. Test their SAVED extreme vertices exactly; never
            # invent a wide pad or search outside the real wheel footprint.
            extreme={}
            for object_name,arr in room_vertices[rid]:
                mask=(np.abs(arr[:,2]-bearing_z)<.00015)&(arr[:,0]>=low[0]-.00015)&(arr[:,0]<=high[0]+.00015)&(arr[:,1]>=low[1]-.00015)&(arr[:,1]<=high[1]+.00015)
                for vertex in np.flatnonzero(mask):
                    point=Vector(arr[vertex]);key=tuple(round(v,5) for v in point)
                    extreme[key]=dict(z=point.z,vertices=[point],object=object_name,polygon=None,actual_vertex=int(vertex),curved_extreme=True)
            soles=list(extreme.values())
            # Known actual wheel families must retain ALL three/four contact
            # points; a raised single wheel cannot hide behind another one.
            expected={'Pianoforte':3,'MedicalInstrumentTrolley':4}.get(f['label'])
            if expected is not None and len(soles)!=expected:
                missing+=1;issue('MISSING_EXPECTED_ACTUAL_CASTER_CONTACTS',expected=expected,actual=len(soles));continue
        if not soles:
            missing+=1;issue('NO_MATCHING_ACTUAL_LOWEST_CONTACT_GEOMETRY');continue
        if soles[0].get('curved_extreme'):curved.append(dict(room=rid,label=f['label'],actual_extreme_contact_points=[list(p['vertices'][0]) for p in soles]))
        bad=[]
        for sole in soles:
            vv=sole['vertices'];c=sum(vv,Vector())/len(vv)
            samples=[c] if sole.get('curved_extreme') else [c*.65+vv[j*len(vv)//3]*.35 for j in range(3)];gaps=[];patches_tested+=1
            for point in samples:
                loc,n,index,distance=finish[rid].ray_cast(point+Vector((0,0,.02)),Vector((0,0,-1)),.4)
                if loc is not None:gaps.append(float(point.z-loc.z))
            why=None
            if not gaps:why='ACTUAL_SOLE_PATCH_OVER_FLOOR_VOID'
            elif min(gaps)<-TOL:why='ACTUAL_SOLE_PATCH_PENETRATES_FLOOR'
            elif not any(abs(gap)<=TOL for gap in gaps):why='ACTUAL_SOLE_PATCH_ABOVE_FLOOR'
            if why:bad.append(dict(reason=why,object=sole['object'],polygon=sole['polygon'],actual_vertex=sole.get('actual_vertex'),probes=len(samples),rays_with_floor=len(gaps),gaps_m=gaps))
        if bad:
            if any('PENETRATES' in b['reason'] for b in bad):penetrating+=1
            elif any('VOID' in b['reason'] for b in bad):missing+=1
            else:floating+=1
            issue('ACTUAL_LOW_SOLE_PATCH_SUPPORT_FLAG',actual_sole_patches=len(soles),flagged_patches=bad)
    return dict(fixtures_tested=tested,sole_patches_tested=patches_tested,interior_probes_per_planar_patch=3,curved_bearing_fixtures=curved,floating_count=floating,missing_support_count=missing,penetration_count=penetrating,support_flags=len(issues),by_label=dict(summary),issues=issues)


def main():
    t=time.time();fixture_only=os.getenv('LII_FITTINGS_FIXTURE_ONLY')=='1';model_path=None;data_path=None
    if not fixture_only:
        from audit_common import audit_inputs,current_generator_hashes,binding_mismatches
        model_path,data_path=audit_inputs(False);data=json.loads(data_path.read_text())
        assert not binding_mismatches(current_generator_hashes(),data['source_files_sha256']),'Rebuild changed generator before certifying saved-model support.'
    rows=[]
    for label,mesh in recipes():
        row=analyse(label,mesh);rows.append(row);print('FINITE PART SCREEN',label,'clusters',row['clusters'],'detached',len(row['detached_clusters']),'base_mm',round(row['lowest_z']*1000,3),flush=True)
    floor=floor_screen(data) if not fixture_only else None
    summary=dict(recipes=len(rows),recipes_with_detached_clusters=sum(bool(r['detached_clusters']) for r in rows),detached_clusters=sum(len(r['detached_clusters']) for r in rows),floor_floating_count=floor['floating_count'] if floor else None,floor_support_flags=floor['support_flags'] if floor else None)
    r=dict(schema='victoria.leonidas-ii.finite-fitting-screen/1.2',scope='ISOLATED_ACTUAL_PRIMITIVE_CONTACT_SCREEN'+(' + SAVED_MODEL_ACTUAL_FLOOR_RAYS' if floor else ''),quality='GAME' if GAME_QUALITY else 'MASTER',auditor_sha256=H(__file__),source_file=str(model_path.relative_to(ROOT)) if model_path else None,source_sha256=H(model_path) if model_path else None,build_data_sha256=H(data_path) if data_path else None,generator_sha256={str(p.relative_to(ROOT)):H(p) for p in sorted(HERE.glob('*.py'))},tolerance_m=TOL,recipes=rows,saved_model_floor=floor,summary=summary,seconds=round(time.time()-t,2),limits='Conservative actual-surface graph and scoped actual-lowest-sole interior-patch floor rays (three per saved planar sole, exact extreme-point rays for rounded casters with three/four-contact count guards; finite flat feet may bridge 2mm joints); not all-triangle minimum-distance, universal Boolean connectivity, every assembled accessory placement, structural strength, visual or Studio acceptance. A pass never substitutes for individual image/source review.')
    out=ROOT/os.getenv('LII_FITTING_REPORT','docs/leonidas_ii/MICRO_GEOMETRY_AUDIT.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n');print('FINITE FITTING SCREEN',json.dumps(summary),flush=True)
    if os.getenv('LII_MICRO_REQUIRE_PASS')=='1' and (summary['detached_clusters'] or (floor and floor['support_flags'])):raise RuntimeError('Unsupported finite parts, actual floor gaps/voids or excessive penetration remain')

if __name__=='__main__':main()
