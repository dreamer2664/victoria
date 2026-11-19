"""New shell, structural members, decks, cutouts and real stair flights."""
import math
import numpy as np
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from meshkit import *
from shipdesign.leonidas_ii import *

# Shell apertures: rings are part of the shell surface, not dark discs.
PORT_X=[float(x) for x in np.arange(-64.8,69,2.72)]
PORT_Z=(6.65,9.95)
SHELL_PORTS=[]
_HULL_TREE=None

def hull_tree():
 global _HULL_TREE
 if _HULL_TREE is None:
  ob=bpy.data.objects['Hull_Shell_New'];ob.data.calc_loop_triangles()
  _HULL_TREE=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[tuple(t.vertices) for t in ob.data.loop_triangles],all_triangles=True)
 return _HULL_TREE


def actual_outer_breadth(x,z):
 # Intersect the ACTUAL lofted/shell-thickened triangles, not merely the
 # ideal half-breadth curve. A coarse bilge chord is inside that curve.
 hit=hull_tree().ray_cast(Vector((x,12.,z)),Vector((0,-1,0)),24.)
 return max(0.,float(hit[0].y)) if hit[0] is not None else 0.


def actual_min_breadth(x0,x1,z):
 return min(actual_outer_breadth(float(x),z) for x in np.linspace(x0,x1,5))

def build_hull():
 m=Mesh();xs=sorted(set([-83.,83.]+[round(float(x),5) for x in np.linspace(-82.5,82.5,167)]+[round(x+d,5) for x in PORT_X for d in (-.28,.28)] +[-2.85,-1.15]))
 levels=[.08,.20,.60,1.2,2.,3.,4.,5.,5.7,6.37,6.93,7.25,8.1,8.8,9.67,10.23,10.65,10.95,11.5,11.78,12.3,13.1]
 # Do not subdivide the aperture column itself, keeping annulus outer edges
 # shared exactly with neighbouring shell quads.
 intervals=[(round(x-.28,5),round(x+.28,5),x) for x in PORT_X]
 xs=[x for x in xs if not any(a+1e-5<x<b-1e-5 for a,b,_ in intervals) and not -2.85+1e-5<x<-1.15-1e-5]
 verts=[];faces=[];tiles=[];vmap={}
 def vertex(p):
  key=tuple(round(float(a),6) for a in p)
  if key not in vmap:vmap[key]=len(verts);verts.append(key)
  return vmap[key]
 def point(x,z,side):
  zz=max(keel_z(x),min(z,deck_z(x)));return (x,side*hb(x,zz),zz)
 def face(points,tile):
  ii=[]
  for p in points:
   k=vertex(p)
   if k not in ii:ii.append(k)
  if len(ii)>=3:
   a,b,c=[Vector(verts[j]) for j in ii[:3]]
   if (b-a).cross(c-a).length>1e-8:faces.append(tuple(ii));tiles.append(tile)
 for side in (-1,1):
  for a,b in zip(xs,xs[1:]):
   pc=next((xc for aa,bb,xc in intervals if abs(a-aa)<1e-5 and abs(b-bb)<1e-5),None)
   for lo,hi in zip(levels,levels[1:]):
    if hi<min(keel_z(a),keel_z(b)) or lo>max(deck_z(a),deck_z(b)):continue
    tile='Oxide' if hi<6.37 else 'Ivory' if lo>=6.37 and hi<=6.93 else 'Hull'
    holez=next((z for z in PORT_Z if abs(lo-(z-.28))<1e-5 and abs(hi-(z+.28))<1e-5),None)
    # Full-size shell boarding door with a real clear opening.
    boarding=abs(a+2.85)<1e-5 and abs(b+1.15)<1e-5 and lo>=8.8 and hi<=10.95
    if boarding:continue
    if pc is not None and holez is not None and min(hb(pc-.28,holez),hb(pc+.28,holez))>1.2 and holez>max(keel_z(pc-.28),keel_z(pc+.28))+.5:
     # Four outer corners, 16 inner circle vertices, 20-triangle annulus.
     outer=[point(b,hi,side),point(a,hi,side),point(a,lo,side),point(b,lo,side)]
     inner=[point(pc+.22*math.cos(math.pi/4+j*math.tau/16),holez+.22*math.sin(math.pi/4+j*math.tau/16),side) for j in range(16)]
     for k in range(4):
      for j in range(4):face([outer[k],inner[(k*4+j)%16],inner[(k*4+j+1)%16]],tile)
      face([outer[k],inner[(k*4+4)%16],outer[(k+1)%4]],tile)
     SHELL_PORTS.append(dict(x=pc,y=side*hb(pc,holez),z=holez,side=side))
    else:face([point(a,lo,side),point(b,lo,side),point(b,hi,side),point(a,hi,side)],tile)
 # Flat of bottom. At fine ends the same vertices collapse to a centreline.
 for a,b in zip(xs,xs[1:]):
  face([point(a,keel_z(a),-1),point(b,keel_z(b),-1),point(b,keel_z(b),1),point(a,keel_z(a),1)],'Oxide')
 # Close the vertical stem/counter ends. Open top is intentionally a rim.
 for x in (-83,83):
  for lo,hi in zip(levels,levels[1:]):face([point(x,lo,-1),point(x,hi,-1),point(x,hi,1),point(x,lo,1)],'Hull')
 m.v=verts;m.f=faces;m.tiles=tiles;m.smooth=[True]*len(faces);m.tags['NewLoftedShell']=1
 ob=m.emit('Hull_Shell_New',collection('Hull'),kind='shell',maxtris=150000)[0]
 # Recalculate / weld before real 24 mm shell thickness. Solidify supplies
 # porthole and boarding-door reveals, rather than sealing the holes.
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 # Check chosen winding outward at broadside; bmesh component may choose either.
 broad=[p for p in ob.data.polygons if abs(p.center.x)<30 and p.center.y>7 and p.center.z>4]
 if broad and sum(p.normal.y for p in broad)<0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Actual 24mm shell','SOLIDIFY');mod.thickness=.024;mod.offset=-1;mod.use_even_offset=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 # Porthole bronze rims, inside deadlight rings and glass in the actual bore.
 rims=Mesh();glass=Mesh()
 for p in SHELL_PORTS:
  c=(p['x'],p['y']+p['side']*.016,p['z']);rims.ring(c,.235,.022,'Brass',16,6,(0,1,0));bolts(rims,c,.27,8,(0,1,0),.010,'Brass')
  glass.cylinder((p['x'],p['y']-p['side']*.009,p['z']),.215,.009,'Ivory',16,(0,1,0))
 rims.emit('Porthole_Rims',collection('Hull'),kind='fitting');glass.emit('Porthole_Glass',collection('Windows'),kind='glazing',material='glass')
 # Plate-lap strips and finite rounded rivet heads. Per 0.42m deliberately
 # sampled at game scale; 89mm pitch is carried in texture at distant LOD.
 seams=Mesh();rivets=Mesh()
 for side in (-1,1):
  for zz in (1.65,3.35,5.25,7.40,8.65,10.9):
   pts=[]
   for xx in np.arange(-79,81,.8):
    if hb(float(xx),zz)>.08 and keel_z(float(xx))+.05<zz<deck_z(float(xx))-.05:pts.append((float(xx),side*(hb(float(xx),zz)+.006),zz))
   if len(pts)>2:seams.tube(pts,.012,'Hull' if zz>6.5 else 'Oxide',4)
   for xx in np.arange(-77,79,.42):
    yy=hb(float(xx),zz)
    if yy>.12 and keel_z(float(xx))+.08<zz<deck_z(float(xx))-.08:
     rivets.lathe((float(xx),side*(yy+.014),zz),[(0,.010),(.006,.012),(.010,.006)],'Hull' if zz>6.5 else 'Oxide',6,(0,side,0))
  for k,xx in enumerate(np.arange(-72,76,4.9)):
   for lo,hi in ((7.5,8.55),(10.35,10.8),(3.45,5.1)):
    x=float(xx)+(.42 if k%2 else 0);y=hb(x,(lo+hi)/2)
    if y>.2 and keel_z(x)<lo:
     seams.rod((x,side*(hb(x,lo)+.012),lo),(x,side*(hb(x,hi)+.012),hi),.012,'Hull',4)
 seams.emit('Plate_Laps',collection('Hull'),kind='detail')
 if not GAME_QUALITY:rivets.emit('Shell_Rivets',collection('Hull'),kind='detail')  # normal map + close-range source retain the rivet pattern
 # Connected stern aperture: short heel shoe stays below the complete
 # screw sweep, then a rising fore-arm joins the actual keel at x=-73.5.
 # The former 11.2m flat shoe ended in open water beneath the rising keel.
 # Never hide that defect with a water plane or a renderer visibility rule.
 keel=Mesh();stations=list(np.arange(-73.5,72.,.9))+[72.]
 for a,b in zip(stations,stations[1:]):
  za=keel_z(float(a));zb=keel_z(float(b));keel.rod((float(a),0,za+.12),(float(b),0,zb+.12),.14,'Hull',4)
 keel.box((-78.45,0,.16),(2.70,.24,.22),'Hull',.025)
 keel.rod((-77.1,0,.16),(-73.5,0,keel_z(-73.5)+.12),.12,'Hull',8)
 keel.rod((-79.2,0,.27),(-79.2,0,8.7),.16,'Hull',10)
 # Fore aperture post carries the after stern-tube bearing. Leave an actual
 # opening around the rotating shaft/tube, rather than a rod through it.
 fx=-76.4;foot=.16+(fx+77.1)/3.6*(keel_z(-73.5)+.12-.16)
 keel.rod((fx,0,foot),(fx,0,2.58),.14,'Hull',10)
 keel.rod((fx,0,3.42),(fx,0,keel_z(fx)+.15),.14,'Hull',10)
 # Stem follows the forward rising profile up to the actual stem head.
 pts=[(float(x),0,keel_z(float(x))+.05) for x in np.linspace(72,83,25)]+[(83,0,13.05)]
 keel.tube(pts,.085,'Hull',8)
 keel.emit('Keel_Stem_SternFrame',collection('Structure'),kind='structure')
 print('NEW HULL',len(ob.data.vertices),'vertices,',len(SHELL_PORTS),'actual ports',flush=True)


def sweep_angle(m,x,points):
 # Rolled angle section: broad 160mm flange and 220mm web, 20mm metal.
 profile=[(-.08,0),(.08,0),(.08,.020),(-.06,.020),(-.06,.22),(-.08,.22)];vv=[];ff=[]
 for i,(y,z) in enumerate(points):
  a=Vector(points[max(0,i-1)]);b=Vector(points[min(len(points)-1,i+1)]);t=(b-a).normalized();n=Vector((-t.y,t.x))
  if n.x*y>0:n=-n
  for dx,dn in profile:vv.append((x+dx,y+n.x*(dn+.065),z+n.y*(dn+.065)))
 N=len(profile)
 for i in range(len(points)-1):
  for j in range(N):a=i*N+j;b=i*N+(j+1)%N;ff.append((a,b,b+N,a+N))
 ff.extend([tuple(range(N-1,-1,-1)),tuple((len(points)-1)*N+j for j in range(N))]);m.add(vv,ff,'Iron')

def inner_bottom_z(x0,x1,y,clearance=.055):
 # Use the actual finite loft at the member's own breadth, across its whole
 # length. The centreline or analytical bilge alone is insufficient.
 result=0.
 for x in np.linspace(x0,x1,9):
  x=float(x);hit=hull_tree().ray_cast(Vector((x,abs(y),-2.)),Vector((0,0,1)),20.)
  lo=float(hit[0].z)+clearance if hit[0] is not None else deck_z(x)+1.
  result=max(result,lo)
 return result


def build_frames():
 m=Mesh();beams=Mesh()
 for xx in np.arange(-76,77,.9144):
  x=float(xx);zk=inner_bottom_z(x-.09,x+.09,0.,clearance=0.)
  for side in (-1,1):
   pts=[];segments=[]
   for z in np.linspace(zk+.065,min(deck_z(x-.09),deck_z(x+.09))-.16,34):
    y=actual_min_breadth(x-.09,x+.09,float(z))
    if y>.025:pts.append((side*y,float(z)))
    else:
     if len(pts)>1:segments.append(pts)
     pts=[]
   if len(pts)>1:segments.append(pts)
   for pts in segments:
    if max(abs(p[0]) for p in pts)>.4:sweep_angle(m,x,pts)
  # Open floor-web assembly, fully INSIDE the actual local bottom profile.
  # Finite vertical web feet follow the inner bilge at their own y position.
  if -68<x<70:
   bottom=zk+.37;b=actual_min_breadth(x-.04,x+.04,bottom)-.08
   if b>.5:
    beams.box((x,0,bottom+.08),(.055,b*2,.16),'Iron')
    for yy in (-b*.55,0,b*.55):
     lo=inner_bottom_z(x-.04,x+.04,abs(yy)+.05);hi=bottom+.26
     if hi-lo>.03:beams.box((x,yy,(lo+hi)/2),(.07,.10,hi-lo),'Iron')
  for key,z in DECKS.items():
   if z>11.81 or z<zk+.45:continue
   width=min(actual_min_breadth(x-.085,x+.085,z-.35),actual_min_breadth(x-.085,x+.085,z-.06))-.06
   if width<.5:continue
   # Never send beams through open machinery / stair casings.
   if any(c['z0']<z<c['z1'] and c['rect'][0]-.12<x<c['rect'][1]+.12 for c in CASINGS):continue
   if z<8.7 and -28.5<x<36:continue
   if any(abs(s['z1']-z)<.08 and min(s['x0'],s['x1'])-.15<x<max(s['x0'],s['x1'])+.15 for s in STAIRS):continue
   beams.box((x,0,z-.20),(.045,width*2,.26),'Iron');beams.box((x,0,z-.33),(.15,width*2,.025),'Iron')
 m.emit('Rolled_Frames_ReverseAngles',collection('Structure'),kind='structure');beams.emit('Floors_And_DeckBeams',collection('Structure'),kind='structure')
 # Side-keelson lower edges are evaluated at their full flange breadth and
 # across their finite length, so no under-plating fins remain at fine ends.
 kl=Mesh()
 for y in (-3.2,0,3.2):
  for x in np.arange(-68,72,2.0):
   x=float(x);lo=inner_bottom_z(x,x+2,abs(y)+.15);top=max(1.16,lo+.30)
   if top>min(deck_z(x),deck_z(x+2))-.3:continue
   if min_hb(x,x+2,top)<abs(y)+.22:continue
   kl.box((x+1,y,(lo+top)/2),(2.0,.055,top-lo),'Iron');kl.box((x+1,y,top),(2.0,.28,.035),'Iron')
 kl.emit('Keelsons',collection('Structure'),kind='structure')


def deck_outline(deck,x):
 z=DECKS[deck]
 if z<=11.8:return max(0,hb(x,min(z,deck_z(x)-.01))-.12)
 if deck=='promenade':return max(0,beam_deck(x)-.38) if -72<x<63 else 0
 if deck=='boat':return max(0,beam_deck(x)-.52) if -62<x<50 else 0
 # The outboard bridge wings are separate fitted plates in topsides.py.
 # Do not overlap their top faces with a second full-width structural deck.
 if deck=='bridge':return min(4.775,max(0,beam_deck(x)-.20)) if 31.8<x<43 else 0
 return 0

def deck_holes(deck):
 z=DECKS[deck];holes=[]
 if deck=='lower':holes += [(-28.5,-9.65,-5.4,5.4),(-3.05,36.05,-7.0,7.0)]
 # Boilers extend to |y|=6.5m. Their continuous outboard service passages
 # must NOT lie under a 2.35m orlop plate only 0.62m above the tank top.
 if deck=='orlop':holes += [(-28.5,36.05,-7.9,7.9),(-70,-28.5,-1.5,1.5)]
 # The exterior galley flue has a real sleeve opening, not a solid deck
 # intersecting the pipe/lagging. Its fastened coamings are in interiors.py.
 if deck in ('promenade','boat'):holes.append((-39.63,-39.07,-5.08,-4.52))
 for c in CASINGS:
  if c['z0']<z+.03<c['z1']:holes.append(c['rect'])
 for s in STAIRS:
  if abs(s['z1']-z)<.06:holes.append((min(s['x0'],s['x1'])-.03,max(s['x0'],s['x1'])+.03,s['y']-s['width']/2-.04,s['y']+s['width']/2+.04))
 return holes

def build_decks():
 for dk,z in DECKS.items():
  m=Mesh();holes=deck_holes(dk);limits={'bridge':(31.81,42.99),'boat':(-61.99,49.99),'promenade':(-71.99,62.99)}.get(dk,(-81.5,81.8));x0,x1=limits
  xs=sorted(set([x0,x1]+[float(x) for x in np.arange(x0,x1,2.)]+[max(x0,min(x1,v)) for h in holes for v in h[:2]]));ys=sorted(set([-9.15,9.15]+[float(y) for y in np.arange(-9.15,9.15,1.3)]+[v for h in holes for v in h[2:]]))
  for a,b in zip(xs,xs[1:]):
   ba,bb=deck_outline(dk,a),deck_outline(dk,b)
   for c,d in zip(ys,ys[1:]):
    if any(h[0]<(a+b)/2<h[1] and h[2]<(c+d)/2<h[3] for h in holes):continue
    lo0=max(c,-ba);hi0=min(d,ba);lo1=max(c,-bb);hi1=min(d,bb)
    # Clip a full tapered strip to this transverse cell. Discarding a
    # cell whenever only ONE end narrowed away left triangular holes
    # under the stern weather finish. Keep those real triangular panels.
    poly=[(a,-ba),(b,-bb),(b,bb),(a,ba)]
    for bound,positive in ((c,True),(d,False)):
     clipped=[]
     for A,B in zip(poly,poly[1:]+poly[:1]):
      ia=A[1]>=bound if positive else A[1]<=bound;ib=B[1]>=bound if positive else B[1]<=bound
      if ia:clipped.append(A)
      if ia!=ib:
       t=(bound-A[1])/(B[1]-A[1]);clipped.append((A[0]+t*(B[0]-A[0]),bound))
     poly=clipped
     if not poly:break
    unique=[]
    for p in poly:
     if not unique or math.dist(p,unique[-1])>1e-8:unique.append(p)
    if len(unique)>1 and math.dist(unique[0],unique[-1])<1e-8:unique.pop()
    poly=unique;nn=len(poly)
    if nn<3 or abs(sum(A[0]*B[1]-A[1]*B[0] for A,B in zip(poly,poly[1:]+poly[:1])))<1e-7:continue
    vv=[(px,py,z+dz) for dz in (-.13,0) for px,py in poly]
    ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)]
    m.add(vv,ff,'Teak' if z>=8.8 else 'Iron')
    # Native rectangular proxy is safely inscribed in the curved strip.
    lo=max(lo0,lo1);hi=min(hi0,hi1)
    if hi-lo>.02:proxy(((a+b)/2,(lo+hi)/2,z-.09),(b-a,hi-lo,.18),tag='Deck_'+dk)
  m.emit('Deck_'+dk,collection('Decks'),kind='deck',deck=dk)
 # Real tank top / engine floor, accessible around the machines.
 tank=Mesh()
 for a,b in [(-72,-28),(-28,36)]:
  for x in np.arange(a,b,2):
   h=min_hb(float(x),float(x+2),1.6)-.15
   if h>.2:
    tank.box((float(x+1),0,1.52),(2,h*2,.16),'Iron');proxy((float(x+1),0,1.52),(2,h*2,.16),tag='TankTop')
 tank.emit('TankTop',collection('Decks'),kind='deck',deck='machinery')
 # Machinery/cargo bulkheads: never slice through cabin rows. Doorways at
 # actual deck access routes; header strips remain above the clear opening.
 bulk=Mesh()
 for x in (-74,-58,-30,-3.15,9.2,22.0,36.15,72):
  # Enclosing steel plate is tiled vertically so real door openings survive.
  stair_openings=[]
  for st in STAIRS:
   if min(st['x0'],st['x1'])-.30<x<max(st['x0'],st['x1'])+.30:
    zz=st['z0']+(st['z1']-st['z0'])*(x-st['x0'])/(st['x1']-st['x0']);stair_openings.append((st['y']-st['width']/2-.18,st['y']+st['width']/2+.18,zz-.25,zz+2.0))
  zs=[max(.3,keel_z(x)+.1),1.6,4.65,5.2,7.45,8.65]+[max(keel_z(x)+.08,min(8.65,v)) for op in stair_openings for v in op[2:]];zs=sorted(set(z for z in zs if z>=keel_z(x)+.08))
  for za,zb in zip(zs,zs[1:]):
   if zb-za<.03:continue
   bw=min(hb(x,za),hb(x,zb))-.13
   ys=sorted(set([-bw,bw,-4.45,-3.20,-1.45,1.45,3.20,4.45]+[v for op in stair_openings for v in op[:2]]));ys=[y for y in ys if -bw<=y<=bw]
   for a,b in zip(ys,ys[1:]):
    # two 1.25m side passage openings and centre machinery door
    opening=(za>=5.2-.01 and zb<=7.45+.01 and (abs((a+b)/2-3.825)<.5 or abs((a+b)/2+3.825)<.5)) or (za>=1.6-.01 and zb<=4.65+.01 and (abs((a+b)/2)<1.4 or abs(abs((a+b)/2)-3.825)<.625))
    if abs(x+3.15)<.03 and abs((a+b)/2)<1.5:opening=True
    if x==72 and za>=5.2-.01 and zb<=7.45+.01 and abs((a+b)/2)<1.4:opening=True
    if any(op[0]<(a+b)/2<op[1] and op[2]<(za+zb)/2<op[3] for op in stair_openings):opening=True
    if opening:continue
    c=(x,(a+b)/2,(za+zb)/2);s=(.045,b-a,zb-za);bulk.box(c,s,'Ivory');proxy(c,s,tag='Bulkhead')
 bulk.emit('Watertight_Bulkheads',collection('Structure'),kind='bulkhead')


def hull_collision_boundaries():
 for dk in ('orlop','lower','main'):
  z=DECKS[dk];xs=sorted(set([float(x) for x in np.arange(-79,80,3.0)]+[-2.85,-1.15]))
  for side in (-1,1):
   for a,b in zip(xs,xs[1:]):
    if dk=='main' and -2.86<(a+b)/2<-1.14:continue
    ya,yb=hb(a,z+1.1)-.10,hb(b,z+1.1)-.10
    if min(ya,yb)<.60:continue
    mid=((a+b)/2,side*(ya+yb)/2,z+1.2);dy=side*(yb-ya);length=math.hypot(b-a,dy)
    proxy(mid,(length,.12,2.4),math.atan2(dy,b-a),tag='HullBoundary_'+dk)


def build_stairs():
 for s in STAIRS:
  m=Mesh();x0,x1=s['x0'],s['x1'];z0,z1=s['z0'],s['z1'];y=s['y'];w=s['width'];n=math.ceil((z1-z0)/.18);rise=(z1-z0)/n;run=(x1-x0)/n;tile='Oak' if s['style']=='oak' else 'Iron'
  for i in range(n):
   xa=x0+i*run;xb=xa+run;zz=z0+(i+1)*rise
   m.box(((xa+xb)/2,y,zz-.035),(abs(run)+.015,w,.07),tile,.006)
   # House risers under the nosing and inside the side skirts. Their old
   # full-width ends overlapped the exposed tread end planes, producing
   # repeated black z-fighting slits in the actual grand-stair render.
   m.box((xa+(.010 if run>0 else -.010),y,zz-rise/2-.0275),(.025,w-.08,rise-.025),tile)
   m.box((xa-(.010 if run>0 else -.010),y,zz+.004),(.043,w-.12,.009),'Brass' if s['style']=='oak' else 'Steel')
  # Sloping structural stringers, no horizontal floating bars.
  for sy in (-1,1):
   yy=y+sy*(w/2-.04)
   if s['style']=='oak':
    # Closed stepped skirt meets the tread undersides and conceals neither
    # a route nor a riser gap. It replaces the coarse diagonal square rod.
    # Explicit conforming side caps. A single concave n-gon lets Blender
    # choose collinear diagonals through non-adjacent step corners; removing
    # their zero-area export triangles left 12 unpaired Grand_Main edges.
    # Every next trapezoid includes the preceding step height in its left
    # edge, so these real cap triangles have neither T-junctions nor fans
    # of collinear points. The whole skirt remains one closed extrusion.
    vv=[];ff=[];indices={}
    def sv(xx,dy,zz):
     key=(round(xx,8),round(yy+dy,8),round(zz,8))
     if key not in indices:indices[key]=len(vv);vv.append(key)
     return indices[key]
    for j in range(n):
     xa=x0+j*run;xb=x0+(j+1)*run;za=z0+(j+1)*rise-.065
     lowa=z0+j*rise-.30;lowb=z0+(j+1)*rise-.30;caps=[]
     for dy in (-.035,.035):
      A=sv(xa,dy,lowa);B=sv(xb,dy,lowb);C=sv(xb,dy,za);D=sv(xa,dy,za)
      if j:
       P=sv(xa,dy,z0+j*rise-.065);ff.extend([(A,B,P),(P,B,C),(P,C,D)])
      else:ff.extend([(A,B,C),(A,C,D)])
      caps.append((A,B,C,D))
     A,B,C,D=caps[0];E,F,G,H=caps[1]
     ff.extend([(A,E,F,B),(D,C,G,H)])  # lower slope and tread underside
     if j:
      P=sv(xa,-.035,z0+j*rise-.065);Q=sv(xa,.035,z0+j*rise-.065)
      ff.append((P,D,H,Q))  # exposed vertical riser of the stepped skirt
     else:ff.append((A,D,H,E))
     if j==n-1:ff.append((B,F,G,C))
    m.add(vv,ff,tile)
   else:m.rod((x0,yy,z0-.10),(x1,yy,z1-.10),.095,tile,4)
   m.tube([(x0-.20*(1 if run>0 else -1),yy,z0+.95),(x0,yy,z0+.95),(x1,yy,z1+.95),(x1+.15*(1 if run>0 else -1),yy,z1+.95)],.040,tile,10)
   for i in range(0,n+1,2):
    t=i/n;xx=x0+(x1-x0)*t;zz=z0+(z1-z0)*t
    m.lathe((xx,yy,zz),[(0,.023),(.12,.034),(.24,.023),(.36,.036),(.48,.026),(.66,.025),(.81,.036),(.91,.026)],tile,8)
   for xx,zz in ((x0,z0),(x1,z1)):
    m.lathe((xx,yy,zz),[(0,.075),(.12,.08),(.27,.06),(.54,.065),(.73,.05),(.96,.09),(1.06,.035)],tile,10)
  m.emit('Stair_'+s['id'],collection('Stairs'),kind='stair',deck=str(s['to']))
  slope=math.atan2(z1-z0,abs(x1-x0))
  for side in (-1,1):PROXIES.append(dict(kind='box',position=((x0+x1)/2,y+side*(w/2-.04),(z0+z1)/2+.55),size=(math.hypot(x1-x0,z1-z0),.07,.84),yaw=0,pitch=-slope if x1>x0 else slope,tag='StairGuard_'+s['id']))
  PROXIES.append(dict(kind='ramp',position=((x0+x1)/2,y,(z0+z1)/2-.04),size=(math.hypot(x1-x0,z1-z0),w-.07,.10),yaw=0,pitch=-slope if x1>x0 else slope,tag=s['id']))
 # Upper-landing guard rails stop at the stair arrival and leave ≥1.2m end
 # circulation. No rail is put across a traversable stair opening.
 for s in STAIRS:
  rr=Mesh();z=s['z1'];x0,x1=sorted((s['x0'],s['x1']));y=s['y'];w=s['width']
  for yy in (y-w/2-.045,y+w/2+.045):
   proxy(((x0+x1)/2,yy,z+.52),(x1-x0,.065,1.0),tag='LandingGuard_'+s['id'])
   rr.rod((x0,yy,z+.96),(x1,yy,z+.96),.035,'Oak' if s['style']=='oak' else 'White',8)
   for x in np.arange(x0,x1+.01,.5):
    rr.cylinder((float(x),yy,z+.01),.045,.04,'Oak' if s['style']=='oak' else 'White',10)
    rr.rod((float(x),yy,z+.02),(float(x),yy,z+.94),.021,'Oak' if s['style']=='oak' else 'White',7)
  rr.emit('LandingGuard_'+s['id'],collection('Stairs'),kind='rail',deck=str(s['to']))
