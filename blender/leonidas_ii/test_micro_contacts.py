"""Positive/negative regressions for the scoped micro-part and door screens.
Run separately in clean Blender for MASTER and LII_GAME_DETAIL=1. These tests
exercise screen sensitivity; they are not physical or visual ship acceptance.
"""
import sys,os,json,copy,hashlib,math
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from meshkit import Mesh,GAME_QUALITY
from audit_fittings import parts,contact,analyse,recipes,floor_screen,H
from audit_room_parts import analyse_room,face_hash,saved_face_hash
from audit_door_sweeps import sample_sweep
import furnishings as F
RESULTS=[]

def check(name,value,detail=None):
 RESULTS.append(dict(test=name,status='PASS' if value else 'FAIL',detail=detail));assert value,(name,detail)

def partbox(c,size):
 m=Mesh();m.box(c,size,'Iron');return parts(m)[0]

def bvh(m):return BVHTree.FromPolygons([Vector(v) for v in m.v],m.f)

def raw_object(name,m):
 me=bpy.data.meshes.new(name);me.from_pydata(m.v,[],m.f);me.update();ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);return ob

def triangles(ff):
 return [(f[0],f[i],f[i+1]) for f in ff for i in range(1,len(f)-1)]

def subset(m,keep):
 out=Mesh();start=0
 for gi,end in enumerate(m.groups):
  if gi in keep:
   ids=sorted({i for f in m.f[start:end] for i in f});remap={v:i for i,v in enumerate(ids)}
   assert len(set(m.tiles[start:end]))==1
   out.add([m.v[i] for i in ids],[tuple(remap[i] for i in f) for f in m.f[start:end]],m.tiles[start],False)
  start=end
 return out

def exposed_plane_overlaps(m,axis,plane,tolerance=1e-7):
 # Independent convex-polygon intersection in an explicitly EXPOSED plane.
 # Bounding-box overlap alone is insufficient for mitred/triangular rails.
 # Hidden butt-joint faces are not globally forbidden by this scoped test.
 axes=[k for k in range(3) if k!=axis];polys=[]
 def area(poly):return sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1]))/2 if len(poly)>2 else 0
 def cross(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
 for fi,f in enumerate(m.f):
  vv=[m.v[i] for i in f]
  if not all(abs(v[axis]-plane)<tolerance for v in vv):continue
  p=[(v[axes[0]],v[axes[1]]) for v in vv]
  if abs(area(p))<1e-12:continue
  if area(p)<0:p.reverse()
  polys.append((fi,p))
 hits=[]
 for j,(fa,a) in enumerate(polys):
  for fb,b in polys[:j]:
   poly=a[:]
   for p,q in zip(b,b[1:]+b[:1]):
    old=poly;poly=[]
    if not old:break
    last=old[-1];cl=cross(p,q,last)
    for v in old:
     cv=cross(p,q,v)
     if (cv>=-1e-12)!=(cl>=-1e-12):
      t=cl/(cl-cv);poly.append((last[0]+t*(v[0]-last[0]),last[1]+t*(v[1]-last[1])))
     if cv>=-1e-12:poly.append(v)
     last,cl=v,cv
   aa=abs(area(poly))
   if aa>1e-9:hits.append(dict(faces=[fa,fb],area_m2=aa))
 return hits

def main():
 from visual_design import clipped_finish_cells
 cells=list(clipped_finish_cells((0,4,0,4),[(1,3,1,3)]))
 area=sum((b-a)*(d-c) for (a,b,c,d),gold in cells)
 check('finish cells clip a true four-square-metre well without capping it',abs(area-12)<1e-9,area)
 check('no retained finish cell crosses the actual well',all(not(min(b,3)>max(a,1) and min(d,3)>max(c,1)) for (a,b,c,d),gold in cells))
 cells=list(clipped_finish_cells((0,4,0,4),inlays=[(1,2,0,4)]))
 check('flush inlay replaces four square metres, with no overlap layers',abs(sum((b-a)*(d-c) for (a,b,c,d),gold in cells)-16)<1e-9 and abs(sum((b-a)*(d-c) for (a,b,c,d),gold in cells if gold)-4)<1e-9)
 cps=parts(F.chair());feet=[p for p in cps if abs(p['lo'].z)<1e-6 and abs(p['hi'].z-.016)<1e-6 and ((p['lo']+p['hi'])/2).xy.length>.2]
 check('revolving chair has four ACTUAL floor-seated outer tip pads',len(feet)==4,len(feet))
 from period_detail import piano_stool
 stool=piano_stool();sps=parts(stool);tips=[p for p in sps if abs(p['lo'].z)<1e-6]
 check('piano stool has exactly three floor-seated outer wooden foot ends',len(tips)==3 and all(((p['lo']+p['hi'])/2).xy.length>.20 for p in tips),len(tips))
 check('piano stool central hub is clear of the floor',sps[0]['lo'].z>.10,float(sps[0]['lo'].z))
 # A vertical-to-elbow frame transition must preserve the tube's section
 # halfway between stations, not only at its authored circular rings.
 path=[Vector(p) for p in ((0,0,0),(0,0,2),(0,1,3),(0,2,3))]
 sweep=Mesh();sweep.tube(path,.1,'Iron',12);radial_count=len(sweep.v)//len(path)
 midpoint_radii=[(Vector(sweep.v[i*radial_count+j])+Vector(sweep.v[(i+1)*radial_count+j])-path[i]-path[i+1]).length/2 for i in range(len(path)-1) for j in range(radial_count)]
 check('transported elbow frames have no hourglass pinch',min(midpoint_radii)>.085,dict(minimum_midsection_radius=min(midpoint_radii)))
 check('transported tube remains one closed primitive',len(sweep.groups)==1 and sweep.groups[-1]==len(sweep.f))
 flipped=list(sweep.v);ring=flipped[radial_count:2*radial_count];flipped[radial_count:2*radial_count]=ring[radial_count//2:]+ring[:radial_count//2]
 bad_radii=[(Vector(flipped[j])+Vector(flipped[radial_count+j])-path[0]-path[1]).length/2 for j in range(radial_count)]
 check('reversed elbow section negative detects hourglass pinch',min(bad_radii)<.03)
 a=partbox((0,0,.5),(1,1,1));touch=partbox((0,0,1.10),(.8,.8,.20));gap=partbox((0,0,1.102),(.8,.8,.20))
 check('flat bearing positive',contact(a,touch));check('2mm floating flat negative',not contact(a,gap))
 check('contained closed solid positive',contact(a,partbox((0,0,.5),(.1,.1,.1))))
 m=Mesh();m.ring((0,0,0),.05,.01,'Brass',24,6);ring=parts(m)[0]
 check('empty torus bore is NOT solid contact',not contact(ring,partbox((0,0,0),(.01,.01,.01))))
 check('torus finite skin contact',contact(ring,partbox((.052,0,0),(.005,.005,.005))))
 from meshkit import flange
 bored=Mesh();flange(bored,(0,0,0),.16,bore=.08);bp=parts(bored)[0]
 check('actual bored flange has no hidden central cap',not contact(bp,partbox((0,0,0),(.03,.03,.01))))
 check('actual bored flange retains finite annular face',contact(bp,partbox((.12,0,0),(.02,.02,.01))))
 # Pixel review exposed coplanar square-corner overlaps despite otherwise
 # valid closed components. Check actual convex face intersections at the
 # top of the carom rail and retain a restored-overlap negative control.
 from period_detail import billiard_table
 railhits=exposed_plane_overlaps(billiard_table(),2,.925)
 check('pocketless carom rails have disjoint exposed top faces',not railhits,railhits[:8])
 oldrail=Mesh()
 for yy in (-.74,.74):oldrail.box((0,yy,.875),(3.,.16,.10),'Walnut',.025)
 for xx in (-1.43,1.43):oldrail.box((xx,0,.875),(.16,1.62,.10),'Walnut',.025)
 oldhits=exposed_plane_overlaps(oldrail,2,.925)
 check('restored crossed square rail corners trigger coplanar-face control',len(oldhits)>=4,oldhits[:4])
 check('actual carom rail is a single closed annular primitive',billiard_table().tags['SingleMitredCaromRail']==1)
 # Actual full staircase meshes: duplicated exposed side planes generated
 # black riser-end slits, although their separate solids were all manifold.
 import structure as ST
 from shipdesign.leonidas_ii import STAIRS
 captured_stairs={};old_emit=Mesh.emit
 def capture_stair(self,name,col,kind='furniture',**kwargs):
  if kind=='stair':captured_stairs[name]=self
  return []
 Mesh.emit=capture_stair
 try:ST.build_stairs()
 finally:Mesh.emit=old_emit
 for stair in STAIRS:
  actual_stair=captured_stairs['Stair_'+stair['id']]
  for sign in (-1,1):
   hits=exposed_plane_overlaps(actual_stair,1,stair['y']+sign*stair['width']/2)
   check('actual stair exposed side has no riser/tread coplanar overlap '+stair['id']+' '+str(sign),not hits,hits[:4])
 oldstep=Mesh();oldstep.box((.15,0,.145),(.315,1.8,.07),'Oak');oldstep.box((0,0,.09),(.030,1.8,.186),'Oak')
 check('restored full-width riser triggers exposed-side overlap control',bool(exposed_plane_overlaps(oldstep,1,.9)))
 # Real templates: every recipe is checked as authored, then one non-anchor
 # primitive is displaced far away without changing its elevation.
 for label,m in recipes():
  base=analyse(label,m);check('recipe positive '+label,not base['detached_clusters'],dict(parts=base['primitive_parts']))
  ps=parts(m)
  if label.startswith('ceiling_'):
   highest=max(p['hi'].z for p in ps);eligible=[i for i,p in enumerate(ps) if p['hi'].z<highest-.002]
  else:
   lowest=min(p['lo'].z for p in ps);eligible=[i for i,p in enumerate(ps) if p['lo'].z>lowest+.002]
  check('non-anchor available '+label,bool(eligible))
  j=eligible[len(eligible)//2];start=0 if j==0 else m.groups[j-1];ids={i for f in m.f[start:m.groups[j]] for i in f};bad=copy.deepcopy(m)
  for i in ids:x,y,z=bad.v[i];bad.v[i]=(x+20,y,z)
  result=analyse(label,bad);check('displaced actual primitive negative '+label,bool(result['detached_clusters']),dict(part=j))
 bed=F.bed();ps=parts(bed);remove={i for i,p in enumerate(ps) if set(p['tiles'])=={'Oak'}}
 check('seven real bed slats identified',len(remove)==7,sorted(remove))
 check('missing mattress slats negative',bool(analyse('bed_missing_slats',subset(bed,set(range(len(ps)))-remove))['detached_clusters']))
 context=Mesh();context.box((0,0,-.05),(3,3,.10),'Iron');fixed=bvh(context);r=dict(id='REGRESSION')
 placed=copy.deepcopy(F.service_setting());check('actual crockery and flatware surface positive',not analyse_room(r,placed,fixed)['detached_clusters'])
 bad=Mesh();bad.append(placed,(0,0,.002));check('actual crockery 2mm floating negative',bool(analyse_room(r,bad,fixed)['detached_clusters']))
 # A real saved-object extraction/raycast test, including its sample count.
 finish=raw_object('Finish_REGRESSION',context);finish['LII_room']='REGRESSION'
 furniture=raw_object('Furniture_REGRESSION',F.chair());furniture['LII_room']='REGRESSION'
 def datum():
  bpy.context.view_layer.update();vv=[furniture.matrix_world@v.co for v in furniture.data.vertices];lo=[min(v[k] for v in vv) for k in range(3)];hi=[max(v[k] for v in vv) for k in range(3)]
  return dict(fixtures=[dict(label='RegressionChair',room='REGRESSION',bounds=[lo,hi],position=list(furniture.location))])
 f=floor_screen(datum());check('saved actual floor rays positive',f['fixtures_tested']==1 and f['floating_count']==0,f)
 furniture.location.z=.015;f=floor_screen(datum());check('saved actual floor rays 15mm negative',f['fixtures_tested']==1 and f['floating_count']==1,f)
 furniture.location.z=0;furniture.location.x=5;f=floor_screen(datum());check('feet over actual floor void negative is NOT skipped',f['fixtures_tested']==1 and f['missing_support_count']==1 and f['support_flags']==1,f)
 furniture.location.x=0;furniture.location.z=-.005;f=floor_screen(datum());check('actual floor 5mm excessive penetration negative',f['penetration_count']==1 and f['support_flags']==1,f)
 furniture.location.z=0;f=floor_screen(datum());check('saved actual floor restored positive',f['support_flags']==0 and f['sole_patches_tested']>=5,f)
 furniture.location.x=1.5;f=floor_screen(datum());check('one outer foot over a real floor edge negative',f['missing_support_count']==1 and f['support_flags']==1,f)
 furniture.location.x=0;datum()
 # A finite foot may bridge a 2mm board/grout joint. Probe points must
 # remain INSIDE that actual sole, rather than searching outside the foot.
 foot=Mesh();foot.box((0,0,.025),(.04,.04,.05),'Iron');fo=raw_object('Furniture_GROOVE_TEST',foot);fo['LII_room']='GROOVE_TEST'
 for sign in (-1,1):
  slab=Mesh();slab.box((sign*.5005,0,-.05),(.999,2,.10),'Iron');ob=raw_object('Finish_GROOVE_TEST_'+str(sign),slab);ob['LII_room']='GROOVE_TEST'
 bpy.context.view_layer.update();g=floor_screen(dict(fixtures=[dict(label='RegressionFoot',room='GROOVE_TEST',bounds=[[-.02,-.02,0],[.02,.02,.05]],position=[0,0,0])]))
 check('finite actual sole correctly bridges a narrow 2mm joint',g['support_flags']==0 and g['sole_patches_tested']==1,g)
 # Real rounded tyres have point contacts, not planar shoes. Preserve the
 # actual three-wheel count, including a raised SINGLE wheel negative.
 wheel=Mesh();wheel.ring((0,0,.04),.032,.008,'Iron',16,8,(1,0,0));wheels=[]
 for j,(x,y) in enumerate(((-.5,0),(.5,0),(0,.5))):
  ob=raw_object('Furniture_CASTER_REGRESSION_'+str(j),wheel);ob['LII_room']='CASTER_REGRESSION';ob.location=(x,y,0);wheels.append(ob)
 base=raw_object('Finish_CASTER_REGRESSION',context);base['LII_room']='CASTER_REGRESSION'
 def wheel_datum():
  bpy.context.view_layer.update();vv=[ob.matrix_world@v.co for ob in wheels for v in ob.data.vertices]
  return dict(fixtures=[dict(label='Pianoforte',room='CASTER_REGRESSION',position=[0,0,0],bounds=[[min(v[k] for v in vv) for k in range(3)],[max(v[k] for v in vv) for k in range(3)]])])
 g=floor_screen(wheel_datum());check('three actual rounded caster extremes bear on actual floor',g['support_flags']==0 and len(g['curved_bearing_fixtures'][0]['actual_extreme_contact_points'])==3,g)
 wheels[0].location.z=.015;g=floor_screen(wheel_datum());check('one lifted rounded caster is not hidden by two seated ones',g['missing_support_count']==1 and g['support_flags']==1,g)
 for ob in wheels:ob.location.z=.015
 g=floor_screen(wheel_datum());check('all rounded casters lifted 15mm negative',g['floating_count']==1 and g['support_flags']==1,g)
 # All three actual stool feet, independently: a lifted foot must not hide
 # behind the two remaining soles or a central floor-contacting pedestal.
 stool_ob=raw_object('Furniture_STOOL_REGRESSION',stool);stool_ob['LII_room']='STOOL_REGRESSION'
 stool_base=raw_object('Finish_STOOL_REGRESSION',context);stool_base['LII_room']='STOOL_REGRESSION'
 def stool_datum():
  bpy.context.view_layer.update();vv=[stool_ob.matrix_world@v.co for v in stool_ob.data.vertices]
  return dict(fixtures=[dict(label='ThreeFootPianoStool',room='STOOL_REGRESSION',position=[0,0,0],bounds=[[min(v[k] for v in vv) for k in range(3)],[max(v[k] for v in vv) for k in range(3)]])])
 g=floor_screen(stool_datum());check('all three actual piano stool soles on floor positive',g['support_flags']==0 and g['sole_patches_tested']==3,g)
 first_foot={i for f in stool.f[stool.groups[1]:stool.groups[2]] for i in f}
 for i in first_foot:stool_ob.data.vertices[i].co.z+=.015
 stool_ob.data.update();g=floor_screen(stool_datum());check('one lifted actual piano stool foot negative',g['missing_support_count']==1 and g['support_flags']==1,g)
 # Polygon identity must survive vertex reordering but reject millimetre drift.
 check('saved/generated polygon identity positive',face_hash(context.v,context.f)==saved_face_hash([finish]))
 rounded=Mesh();rounded.box((-4.0004499,-7.44,9.9175),(.064,.18,.02),'Iron');rounded_ob=raw_object('Float32_Boundary_Regression',rounded)
 check('polygon identity reproduces actual float32 storage at 0.1mm bin boundaries',face_hash(rounded.v,rounded.f)==saved_face_hash([rounded_ob]))
 origin=(-31.456789,.234567,3.123456);local=Mesh();local.v=[tuple(Vector(v)-Vector(origin)) for v in rounded.v];local.f=rounded.f
 mover_ob=raw_object('Float32_Mover_Regression',local);mover_ob.location=origin;bpy.context.view_layer.update()
 check('polygon identity reproduces local-origin mover serialization',face_hash(rounded.v,rounded.f,origin)==saved_face_hash([mover_ob]))
 shifted=copy.deepcopy(rounded);shifted.v[0]=(shifted.v[0][0]+.002,*shifted.v[0][1:])
 check('local-origin polygon identity still rejects real 2mm displacement',face_hash(shifted.v,shifted.f,origin)!=saved_face_hash([mover_ob]))
 changed=copy.deepcopy(context);changed.v[0]=(changed.v[0][0]+.002,*changed.v[0][1:]);check('polygon identity displacement negative',face_hash(changed.v,changed.f)!=saved_face_hash([finish]))
 # Door tests use a finite actual leaf mesh, not its overall AABB. Obstacles
 # exist only inside each signed sweep and are absent at the closed pose.
 leaf=Mesh();leaf.box((.5,0,1),(1,.045,2),'Oak');ff=triangles(leaf.f)
 clear=partbox((2,2,1),(.1,.1,.3))['bvh'];n,bad=sample_sweep(leaf.v,ff,(0,0,0),90,clear)
 check('sampled door clear positive',n==46 and not bad)
 for sign in (-1,1):
  block=partbox((.50,sign*.50,1),(.12,.12,.4))['bvh'];n,bad=sample_sweep(leaf.v,ff,(0,0,0),sign*90,block)
  check('signed sampled door obstruction negative '+str(sign),bool(bad) and all(b['angle_deg']*sign>0 for b in bad),dict(intersecting_poses=len(bad)))
  _,opposite=sample_sweep(leaf.v,ff,(0,0,0),-sign*90,block);check('opposite door swing does not false-hit '+str(sign),not opposite)
 # Actual authored leaves/frames on all FOUR wall orientations. This is
 # independent of the room-furniture sweep and has NO own-jamb exemption.
 import interiors as I
 from shipdesign.leonidas_ii import ROOMS
 for wall in ('x0','x1','y0','y1'):
  r=next(r for r in ROOMS if r['kind']!='machinery' and r['door_wall']==wall);captured=[];original_emit=Mesh.emit
  def collect(self,name,col,kind='furniture',**kwargs):captured.append((name,kind,self));return []
  Mesh.emit=collect
  try:I.surfaces(r)
  finally:Mesh.emit=original_emit
  actual=next(m for name,kind,m in captured if kind=='door');jamb=next(m for name,kind,m in captured if name=='Joinery_'+r['id']);door=I.DOORS[-1];af=triangles(actual.f)
  _,hits=sample_sweep(actual.v,af,door['hinge'],door['angle_deg'],bvh(jamb))
  check('actual leaf/own jamb sampled clearance '+wall,not hits,dict(room=r['id'],poses_with_intersections=len(hits)))
  check('actual cranked leaf hinge straps are physically connected '+wall,not analyse('door_leaf_'+wall,actual)['detached_clusters'])
  lifted=[(x,y,z+.010) for x,y,z in actual.v];_,hits=sample_sweep(lifted,af,door['hinge'],0,bvh(jamb))
  check('actual door 10mm header penetration negative '+wall,bool(hits))
  pin=Mesh();hx,hy,hz=door['hinge'];pin.cylinder((hx,hy,hz+.95),.013,1.90,'Iron',20)
  _,hits=sample_sweep(actual.v,af,door['hinge'],0,bvh(pin));check('actual oversized hinge pin interference negative '+wall,bool(hits))
 # Actual first-class cabinet crowns with both mirrored door signs,
 # on long and short cabins. The deliberately restored old wider crown
 # must fail, otherwise a frame-only sweep would silently miss it again.
 from audit_room_parts import regenerate
 for rid in ('A001','A002','U001','U002','B_First098','B_First099'):
  r=next(r for r in ROOMS if r['id']==rid);captured=[];original_emit=Mesh.emit
  Mesh.emit=collect
  try:I.surfaces(r)
  finally:Mesh.emit=original_emit
  actual=next(m for name,kind,m in captured if kind=='door');door=I.DOORS[-1];furniture=regenerate(r)
  _,hits=sample_sweep(actual.v,triangles(actual.f),door['hinge'],door['angle_deg'],bvh(furniture))
  check('actual cabin door clears actual furniture/cabinet crown '+rid,not hits,dict(poses_with_intersections=len(hits)))
  if rid=='A001':
   old_wardrobe=I.wardrobe
   def wider_crown(width=.62,height=1.98):return old_wardrobe(.62 if width==.54 else width,height)
   I.wardrobe=wider_crown
   try:bad_furniture=regenerate(r)
   finally:I.wardrobe=old_wardrobe
   _,hits=sample_sweep(actual.v,triangles(actual.f),door['hinge'],door['angle_deg'],bvh(bad_furniture))
   check('restored old wide actual cabinet crown interference negative',bool(hits),dict(poses_with_intersections=len(hits)))
 out=ROOT/os.getenv('LII_MICRO_TEST_REPORT','docs/leonidas_ii/inspection/MICRO_CONTACT_REGRESSIONS_'+('GAME' if GAME_QUALITY else 'MASTER')+'.json')
 report=dict(schema='victoria.leonidas-ii.micro-contact-regressions/1.0',quality='GAME' if GAME_QUALITY else 'MASTER',tests=RESULTS,summary=dict(pass_count=len(RESULTS),fail_count=0),test_sha256=H(__file__),auditors_sha256={p.name:H(p) for p in (HERE/'audit_fittings.py',HERE/'audit_room_parts.py',HERE/'audit_door_sweeps.py')},generator_sha256={p.name:H(p) for p in sorted(HERE.glob('*.py'))},limits='Screen regressions only, including synthetic/altered actual templates. Not assembled-ship visual, universal connectivity or continuous-sweep certification.')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('MICRO CONTACT REGRESSIONS',report['quality'],report['summary'],flush=True)

if __name__=='__main__':main()
