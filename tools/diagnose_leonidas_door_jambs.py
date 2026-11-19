"""Generated door-vs-own-wall/jamb diagnostic; never saved-source acceptance.
Uses full leaf/handles/hinges and all actual authored own-room wall primitives.
No jamb/hinge contact exclusions. Discrete 2-degree poses, not continuous QA.
"""
from pathlib import Path
import sys,json,bisect,time
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'blender/leonidas_ii'),str(ROOT)]
from meshkit import Mesh
from shipdesign.leonidas_ii import ROOMS
from audit_common import current_generator_hashes
from audit_door_sweeps import sample_sweep
from audit_fittings import parts,H
import interiors as I


def triangulate(m):
    me=bpy.data.meshes.new('DoorJambDiagnostic');me.from_pydata(m.v,[],m.f);me.update();me.calc_loop_triangles()
    vv=[v.co.copy() for v in me.vertices];ff=[tuple(t.vertices) for t in me.loop_triangles];owner=[int(t.polygon_index) for t in me.loop_triangles];bpy.data.meshes.remove(me)
    return vv,ff,owner


def main():
    start=current_generator_hashes();original=Mesh.emit;rows=[];t=time.time()
    for r in ROOMS:
        if r['kind']=='machinery':continue
        captured=[]
        def collect(self,name,col,kind='furniture',**kwargs):
            captured.append(dict(name=name,mesh=self,kind=kind));return []
        Mesh.emit=collect
        try:I.surfaces(r)
        finally:Mesh.emit=original
        leaf=next(a['mesh'] for a in captured if a['kind']=='door');wall=next(a['mesh'] for a in captured if a['name']=='Joinery_'+r['id']);d=I.DOORS[-1]
        vv,ff,owner=triangulate(wall);obs=BVHTree.FromPolygons(vv,ff,all_triangles=True);lv,lf,_=triangulate(leaf)
        n,bad=sample_sweep(lv,lf,d['hinge'],d['angle_deg'],obs)
        if bad:
            ps=parts(wall)
            for b in bad:
                polygon=owner[b['first_obstacle_triangle']];part=bisect.bisect_right(wall.groups,polygon);p=ps[part]
                b.update(wall_polygon=polygon,wall_primitive=part,tiles=p['tiles'],primitive_low=list(p['lo']),primitive_high=list(p['hi']))
            print('OWN WALL/JAMB',r['id'],len(bad),'first',bad[0],flush=True)
        rows.append(dict(room=r['id'],poses=n,intersections=bad))
    assert start==current_generator_hashes(),'Source changed during diagnostic.'
    report=dict(schema='victoria.leonidas-ii.generated-own-jamb-diagnostic/1.0',status='GENERATED_DIAGNOSTIC_NOT_SAVED_SOURCE_ACCEPTANCE',generator_sha256=start,driver_sha256=H(__file__),summary=dict(doors=len(rows),poses=sum(r['poses'] for r in rows),doors_with_intersections=sum(bool(r['intersections']) for r in rows)),rows=rows,seconds=round(time.time()-t,2),limits=__doc__)
    p=ROOT/'docs/leonidas_ii/inspection/MICRO_GENERATED_DOOR_JAMBS.json';p.write_text(json.dumps(report,indent=2)+'\n');print('OWN WALL/JAMBS',report['summary'],report['seconds'],flush=True)

if __name__=='__main__':main()
