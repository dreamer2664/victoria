"""Executed regression audit of ACTUAL master mesh vertices/triangles.
Blender -b models/leonidas_ii/Aurelian_1889.blend --python-exit-code 1 -P this.py

Scope: three internal framing groups versus the analytical design envelope
AND actual lower-shell side rays below 6m (no shell openings in this band);
actual-component contact path stern shoe -> post / forward keel; full-radius
propeller swept-disc clearance from the actual stern-frame triangle surfaces,
plus continuous axially resolved rotational-envelope clearance from the shell.
Not a Boolean, watertight-shell, scantling, stiffness or strength certificate.
"""
from pathlib import Path
import sys,json,hashlib,datetime,math
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import hb,keel_z,deck_z,SHAFT_Z
MASTER=ROOT/'models/leonidas_ii/Aurelian_1889.blend'
DOC=ROOT/'docs/leonidas_ii';DOC.mkdir(exist_ok=True,parents=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def actual(ob):
 ob.data.calc_loop_triangles()
 return [ob.matrix_world@v.co for v in ob.data.vertices],[tuple(t.vertices) for t in ob.data.loop_triangles]
checks=[]
def check(name,ok,detail):
 checks.append(dict(check=name,status='PASS' if ok else 'FAIL',detail=detail));print(checks[-1]['status'],name,flush=True)

hull=bpy.data.objects['Hull_Shell_New'];hv,ht=actual(hull);hull_bvh=BVHTree.FromPolygons(hv,ht,all_triangles=True)
rows=[]
for prefix in ('Rolled_Frames_ReverseAngles','Floors_And_DeckBeams','Keelsons'):
 count=outside=actual_count=actual_outside=0;minimum=actual_minimum=float('inf');examples=[];actual_examples=[]
 for ob in bpy.context.scene.objects:
  if ob.type!='MESH' or not ob.name.startswith(prefix):continue
  vv,_=actual(ob)
  for v in vv:
   x,y,z=map(float,v);margins=(z-keel_z(x),deck_z(x)-z,hb(x,z)-abs(y));margin=min(margins);minimum=min(minimum,margin);count+=1
   if margin<-.003:
    outside+=1
    if len(examples)<12:examples.append(dict(point=[x,y,z],minimum_axis_margin_m=margin))
   # Below 6m there are no modeled shell openings. A side ray intersects
   # the actual outer loft before its inner surface; this catches members
   # inside the ideal curve but OUTSIDE the coarse physical bilge chord.
   if z<=6.0:
    side=1 if y>=0 else -1;hit=hull_bvh.ray_cast(Vector((x,side*12.,z)),Vector((0,-side,0)),24.)
    outer=side*float(hit[0].y) if hit[0] is not None else 0.;am=outer-abs(y)
    actual_count+=1;actual_minimum=min(actual_minimum,am)
    if am<-.003:
     actual_outside+=1
     if len(actual_examples)<12:actual_examples.append(dict(point=[x,y,z],actual_outer_half_breadth_m=outer,margin_m=am))
 row=dict(group=prefix,vertices=count,outside_design_envelope_3mm=outside,minimum_axis_margin_m=minimum if count else None,examples=examples,actual_lower_hull_vertices_tested=actual_count,outside_actual_lower_shell_3mm=actual_outside,minimum_actual_lateral_margin_m=actual_minimum if actual_count else None,actual_lower_shell_examples=actual_examples);rows.append(row)
check('Internal framing fits analytical envelope AND actual lower loft',all(r['vertices'] and not r['outside_design_envelope_3mm'] and r['actual_lower_hull_vertices_tested'] and not r['outside_actual_lower_shell_3mm'] for r in rows),rows)

obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Keel_Stem_SternFrame')]
assert len(obs)==1,'Expected one explicit keel/stern-frame assembly'
verts,triangles=actual(obs[0]);parent=list(range(len(verts)))
def find(a):
 while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
 return a
for a,b,c in triangles:
 for j in (b,c):
  x,y=find(a),find(j)
  if x!=y:parent[y]=x
by={}
for t in triangles:by.setdefault(find(t[0]),[]).append(t)
components=[]
for tt in by.values():
 ids=sorted({i for t in tt for i in t});remap={v:i for i,v in enumerate(ids)};vv=[verts[i] for i in ids];ff=[tuple(remap[i] for i in t) for t in tt]
 bounds=([min(v[k] for v in vv) for k in range(3)],[max(v[k] for v in vv) for k in range(3)])
 components.append(dict(vertices=vv,faces=ff,bounds=bounds,tree=BVHTree.FromPolygons(vv,ff,all_triangles=True,epsilon=1e-5)))
# Triangles intersecting (or vertices within 2mm of another surface) make
# an observed contact edge. A mere overlap of bounding boxes does NOT count.
graph={i:set() for i in range(len(components))};edges=[]
for i,a in enumerate(components):
 for j in range(i):
  b=components[j]
  if any(a['bounds'][0][k]>b['bounds'][1][k]+.002 or b['bounds'][0][k]>a['bounds'][1][k]+.002 for k in range(3)):continue
  contact=bool(a['tree'].overlap(b['tree']));method='triangle_intersection'
  if not contact:
   method='surface_distance_le_2mm'
   contact=any(b['tree'].find_nearest(v)[3]<=.002 for v in a['vertices']) or any(a['tree'].find_nearest(v)[3]<=.002 for v in b['vertices'])
  if contact:graph[i].add(j);graph[j].add(i);edges.append(dict(a=i,b=j,method=method))
shoe=[i for i,c in enumerate(components) if abs((c['bounds'][1][0]-c['bounds'][0][0])-2.70)<.02 and abs(c['bounds'][0][2]-.05)<.02 and abs(c['bounds'][1][2]-.27)<.02]
posts=[i for i,c in enumerate(components) if abs((c['bounds'][0][0]+c['bounds'][1][0])/2+79.2)<.02 and c['bounds'][1][2]>8.6]
forward=[i for i,c in enumerate(components) if c['bounds'][1][0]>-70 and -73.3<c['bounds'][0][0]<-69.5]
seen=set(shoe);queue=list(shoe)
while queue:
 for j in graph[queue.pop()]:
  if j not in seen:seen.add(j);queue.append(j)
contact_detail=dict(components=len(components),observed_contact_edges=len(edges),shoe_components=shoe,after_post_components=posts,forward_keel_components=forward,reachable_from_shoe=sorted(seen),contact_edges=edges)
check('Actual stern shoe contacts after post and forward rising keel',len(shoe)==1 and bool(set(posts)&seen) and bool(set(forward)&seen),contact_detail)

prop=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Propeller_4Blade')]
assert prop,'Propeller mesh missing'
pv=[];pt=[]
for ob in prop:
 vv,tt=actual(ob);off=len(pv);pv+=vv;pt += [tuple(i+off for i in t) for t in tt]
prop_r=max(math.hypot(v.y,v.z-SHAFT_Z) for v in pv);xmin=min(v.x for v in pv)-.020;xmax=max(v.x for v in pv)+.020

def clip(poly,bound,positive):
 if not poly:return []
 out=[]
 for a,b in zip(poly,[*poly[1:],poly[0]]):
  ai=(a[0]>=bound) if positive else (a[0]<=bound);bi=(b[0]>=bound) if positive else (b[0]<=bound)
  if ai:out.append(a)
  if ai!=bi:
   t=(bound-a[0])/(b[0]-a[0]);out.append(a+(b-a)*t)
 return out

def radial_distance(poly):
 pp=[np.array([v[1],v[2]-SHAFT_Z]) for v in poly];cross=[];result=float('inf')
 for a,b in zip(pp,[*pp[1:],pp[0]]):
  d=b-a;den=float(np.dot(d,d));t=max(0.,min(1.,-float(np.dot(a,d))/den)) if den>1e-20 else 0.
  result=min(result,float(np.linalg.norm(a+d*t)));cross.append(float(a[0]*b[1]-a[1]*b[0]))
 if abs(sum(cross))>1e-12 and (min(cross)>=-1e-12 or max(cross)<=1e-12):return 0.
 return result
min_r=float('inf');tested=0
for t in triangles:
 poly=clip(clip([np.array(verts[i],dtype=float) for i in t],xmin,True),xmax,False)
 if len(poly)<3:continue
 tested+=1;min_r=min(min_r,radial_distance(poly))
clearance=min_r-prop_r
intersection_pairs=len(BVHTree.FromPolygons(verts,triangles,all_triangles=True).overlap(BVHTree.FromPolygons(pv,pt,all_triangles=True)))
# A pitched blade does not occupy its maximum tip radius at every X. Check
# the shell against conservative continuous rotational envelopes in <=10mm
# axial intervals, not just a finite set of stopped blade angles. Clipping
# each source triangle to an interval is exact; a convex polygon's maximum
# radius is at a vertex. The shell's minimum projected radius is measured on
# its clipped polygon. Expand the propeller interval by 20mm at both ends.
# Using independent minima/maxima throughout each interval is conservative.
htri=np.asarray(hv,dtype=float)[np.asarray(ht,dtype=int)]
htri=htri[(htri[:,:,0].max(axis=1)>=xmin)&(htri[:,:,0].min(axis=1)<=xmax)]
ptri=np.asarray(pv,dtype=float)[np.asarray(pt,dtype=int)]
intervals=np.linspace(xmin,xmax,math.ceil((xmax-xmin)/.010)+1);shell_bounds=[]
for lo,hi in zip(intervals,intervals[1:]):
 hs=htri[(htri[:,:,0].max(axis=1)>=lo)&(htri[:,:,0].min(axis=1)<=hi)]
 ps=ptri[(ptri[:,:,0].max(axis=1)>=lo-.020)&(ptri[:,:,0].min(axis=1)<=hi+.020)]
 if not len(hs) or not len(ps):continue
 sr=float('inf');pr=0.
 for tri in hs:
  poly=clip(clip(list(tri),lo,True),hi,False)
  if len(poly)>=3:sr=min(sr,radial_distance(poly))
 for tri in ps:
  poly=clip(clip(list(tri),lo-.020,True),hi+.020,False)
  if len(poly)>=3:pr=max(pr,max(math.hypot(v[1],v[2]-SHAFT_Z) for v in poly))
 if math.isfinite(sr) and pr>0:shell_bounds.append(dict(axial_interval_m=[float(lo),float(hi)],minimum_shell_radius_m=sr,maximum_guarded_propeller_radius_m=pr,conservative_radial_gap_m=sr-pr))
shell_gap=min((r['conservative_radial_gap_m'] for r in shell_bounds),default=-1.)
tightest=min(shell_bounds,key=lambda r:r['conservative_radial_gap_m']) if shell_bounds else None
check('Actual stern frame AND shell clear complete propeller rotation envelope',tested>0 and clearance>.040 and intersection_pairs==0 and shell_gap>.040,dict(actual_propeller_radius_m=prop_r,axial_slab_with_20mm_guard_m=[xmin,xmax],clipped_frame_triangles=tested,minimum_frame_radial_distance_m=min_r,swept_disc_frame_clearance_m=clearance,rest_pose_frame_triangle_intersection_pairs=intersection_pairs,shell_envelope=dict(method='Continuous conservative radial bound: clipped actual triangles in <=10mm axial intervals, propeller interval expanded by 20mm each end; not sampled stopped poses or minimum Euclidean surface distance.',clipped_shell_triangles=len(htri),axial_intervals=len(shell_bounds),minimum_radial_gap_bound_m=shell_gap,tightest_interval=tightest)))
report=dict(schema='victoria.leonidas-ii.structural-geometry-audit/1.2',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(MASTER),auditor_sha256=sha(Path(__file__)),hull_spec_sha256=sha(ROOT/'shipdesign/leonidas_ii.py'),checks=checks,summary={s:sum(c['status']==s for c in checks) for s in ('PASS','FAIL')},limitations=['Analytical envelope vertices plus actual lower-shell side rays below 6m; not exact shell Boolean containment, every upper opening or every hidden surface.','Contact graph demonstrates observed assembly contacts, not welded/manifold union, scantling or structural strength.','Rotational-envelope tests cover keel/stern-frame and actual shell only. Shell result is a conservative radial separation bound, not minimum Euclidean tip clearance. Hydrodynamic, elastic and pressure-vessel behaviour unverified.'])
(DOC/'STRUCTURE_GEOMETRY_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print('STRUCTURAL GEOMETRY AUDIT',report['summary'],flush=True)
if report['summary']['FAIL']:raise RuntimeError('Actual structural regression gate failed; inspect report before export/publication')
