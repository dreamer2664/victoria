"""Small explicit-mesh construction kit, semantic source / spatial export.
No mesh operators per chair leg, no inherited furniture or merged old hull.
Every emitted mesh has an atlas UV, outward normals and material assignment.
"""
import math, json, os
from pathlib import Path
from collections import Counter
import bpy, bmesh
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[2]
MATDIR=ROOT/'reference'/'leonidas_ii'/'materials'
ATLAS=json.loads((MATDIR/'atlas.json').read_text())
SIGNINDEX=json.loads((MATDIR/'signs.json').read_text())
GAME_QUALITY=os.getenv('LII_GAME_DETAIL')=='1'
MATERIALS={};OBJECT_RECORDS=[];PROXIES=[];MOVERS=[];LIGHTS=[];SEATS=[];FIXTURES=[]

def collection(name,parent=None):
 c=bpy.data.collections.get(name)
 if not c:
  c=bpy.data.collections.new(name);(parent or bpy.context.scene.collection).children.link(c)
 return c

def materials():
 def image(name,noncolor=False):
  im=bpy.data.images.load(str(MATDIR/f'Aurelian_{name}.png'),check_existing=True)
  if noncolor:im.colorspace_settings.name='Non-Color'
  im.pack();return im
 mat=bpy.data.materials.new('Aurelian_OriginalPBR_Atlas');mat.use_nodes=True
 n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF')
 for channel,socket,noncolor in [('basecolor','Base Color',False),('roughness','Roughness',True),('metallic','Metallic',True)]:
  t=n.new('ShaderNodeTexImage');t.image=image(channel,noncolor);t.interpolation='Linear';l.new(t.outputs['Color'],bs.inputs[socket])
 t=n.new('ShaderNodeTexImage');t.image=image('normal',True);nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.4;l.new(t.outputs['Color'],nm.inputs['Color']);l.new(nm.outputs['Normal'],bs.inputs['Normal'])
 t=n.new('ShaderNodeTexImage');t.image=image('emission');l.new(t.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1.4
 MATERIALS['atlas']=mat
 glass=bpy.data.materials.new('Aurelian_WindowGlass');glass.use_nodes=True;bs=glass.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.24,.39,.38,1);bs.inputs['Roughness'].default_value=.12;bs.inputs['Transmission Weight'].default_value=.50;bs.inputs['IOR'].default_value=1.46;MATERIALS['glass']=glass
 bulb=bpy.data.materials.new('Aurelian_Incandescent');bulb.use_nodes=True;bs=bulb.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(1,.80,.46,1);bs.inputs['Emission Color'].default_value=(1,.63,.26,1);bs.inputs['Emission Strength'].default_value=2.2;MATERIALS['bulb']=bulb
 sign=bpy.data.materials.new('Aurelian_CompartmentPlaques');sign.use_nodes=True;bs=sign.node_tree.nodes.get('Principled BSDF');t=sign.node_tree.nodes.new('ShaderNodeTexImage');t.image=image('signs');sign.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.42;MATERIALS['sign']=sign
 return MATERIALS

class Mesh:
 def __init__(self):self.v=[];self.f=[];self.tiles=[];self.smooth=[];self.tags=Counter();self.groups=[]
 def add(self,v,f,tile='Ivory',smooth=False,tag=None):
  off=len(self.v);self.v.extend(tuple(map(float,p)) for p in v);self.f.extend(tuple(off+i for i in q) for q in f);self.tiles.extend([tile]*len(f));self.smooth.extend([smooth]*len(f))
  self.groups.append(len(self.f))
  if tag:self.tags[tag]+=1
  return self
 def append(self,other,loc=(0,0,0),ang=0,scale=(1,1,1),tag=None):
  ca,sa=math.cos(ang),math.sin(ang);sx,sy,sz=scale;x,y,z=loc;vv=[]
  for a,b,c in other.v:a*=sx;b*=sy;vv.append((x+a*ca-b*sa,y+a*sa+b*ca,z+c*sz))
  off=len(self.v);faceoff=len(self.f);self.groups.extend(faceoff+g for g in (other.groups or [len(other.f)]));self.v.extend(vv);self.f.extend(tuple(off+i for i in f) for f in other.f);self.tiles.extend(other.tiles);self.smooth.extend(other.smooth);self.tags.update(other.tags)
  if tag:self.tags[tag]+=1
  return self
 def box(self,c,size,t='Ivory',b=0,ang=0,tag=None):
  hx,hy,hz=(max(.0001,a/2) for a in size)
  b=min(b,hx*.65,hy*.65,hz*.65)
  if GAME_QUALITY and b<.022:b=0
  # Sub-centimetre bevels are texture/normal-map detail at this scale.
  # Keep real bevel geometry on furniture silhouettes, not every panel bead.
  if b<.009:
   vv=[(sx*hx,sy*hy,sz*hz) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]];ff=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
  else:
   b=min(b,hx*.65,hy*.65,hz*.65);vv=[];ii={};ff=[];hs=(hx,hy,hz)
   for sx in (-1,1):
    for sy in (-1,1):
     for sz in (-1,1):
      ss=(sx,sy,sz)
      for axis in range(3):
       p=tuple(ss[j]*(hs[j]-(0 if j==axis else b)) for j in range(3));ii[(sx,sy,sz,axis)]=len(vv);vv.append(p)
   for axis in range(3):
    other=[j for j in range(3) if j!=axis]
    for s in (-1,1):
     face=[]
     for a,bb in [(-1,-1),(1,-1),(1,1),(-1,1)]:
      ss=[0,0,0];ss[axis]=s;ss[other[0]]=a;ss[other[1]]=bb;face.append(ii[tuple(ss)+(axis,)])
     ff.append(tuple(face))
   for axis in range(3):
    other=[j for j in range(3) if j!=axis]
    for a in (-1,1):
     for bb in (-1,1):
      keys=[]
      for s,fa in [(-1,other[0]),(1,other[0]),(1,other[1]),(-1,other[1])]:
       ss=[0,0,0];ss[axis]=s;ss[other[0]]=a;ss[other[1]]=bb;keys.append(ii[tuple(ss)+(fa,)])
      ff.append(tuple(keys))
   for sx in (-1,1):
    for sy in (-1,1):
     for sz in (-1,1):ff.append(tuple(ii[(sx,sy,sz,a)] for a in range(3)))
  ca,sa=math.cos(ang),math.sin(ang);x,y,z=c;vv=[(x+a*ca-bb*sa,y+a*sa+bb*ca,z+cc) for a,bb,cc in vv]
  return self.add(vv,ff,t,False,tag)
 def lathe(self,c,profile,t='Brass',n=12,axis=(0,0,1),tag=None,caps=True,closed=False):
  n=max(6,round(n*.60)) if GAME_QUALITY else n
  axis=Vector(axis).normalized();q=Vector((0,0,1)).rotation_difference(axis);cc=Vector(c);vv=[];ff=[]
  for h,r in profile:
   r=max(r,.0002)
   for j in range(n):a=j*math.tau/n;vv.append(tuple(cc+q@Vector((r*math.cos(a),r*math.sin(a),h))))
  for k in range(len(profile)-1+(1 if closed else 0)):
   kn=(k+1)%len(profile)
   for j in range(n):a=k*n+j;b=k*n+(j+1)%n;ff.append((a,b,kn*n+(j+1)%n,kn*n+j))
  if caps and not closed:ff.extend([tuple(range(n-1,-1,-1)),tuple((len(profile)-1)*n+j for j in range(n))])
  return self.add(vv,ff,t,True,tag)
 def cylinder(self,c,r,h,t='Brass',n=12,axis=(0,0,1),r2=None,tag=None):return self.lathe(c,[(-h/2,r),(h/2,r if r2 is None else r2)],t,n,axis,tag)
 def rod(self,a,b,r,t='Brass',n=8,r2=None,tag=None):
  a,b=Vector(a),Vector(b);d=b-a
  if d.length<1e-5:return self
  return self.cylinder(tuple((a+b)/2),r,d.length,t,n,tuple(d.normalized()),r2,tag)
 def tube(self,points,r,t='Copper',n=8,tag=None):
  # Continuous swept elbow centreline. Closed ends, shared ring vertices.
  n=max(6,round(n*.65)) if GAME_QUALITY else n
  pts=[Vector(p) for p in points];vv=[];ff=[]
  for i,p in enumerate(pts):
   tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=tangent.cross(Vector((0,0,1)))
   if u.length<.01:u=tangent.cross(Vector((0,1,0)))
   u.normalize();v=tangent.cross(u).normalized()
   for j in range(n):a=j*math.tau/n;vv.append(tuple(p+r*(math.cos(a)*u+math.sin(a)*v)))
  for i in range(len(pts)-1):
   for j in range(n):a=i*n+j;b=i*n+(j+1)%n;ff.append((a,b,b+n,a+n))
  ff+=[tuple(range(n-1,-1,-1)),tuple((len(pts)-1)*n+j for j in range(n))]
  return self.add(vv,ff,t,True,tag)
 def ring(self,c,r,minor=.014,t='Brass',n=20,m=5,axis=(0,0,1),tag=None):
  if GAME_QUALITY:n=max(8,round(n*.60));m=3
  q=Vector((0,0,1)).rotation_difference(Vector(axis).normalized());cc=Vector(c);vv=[];ff=[]
  for i in range(n):
   a=i*math.tau/n
   for j in range(m):b=j*math.tau/m;rr=r+minor*math.cos(b);vv.append(tuple(cc+q@Vector((rr*math.cos(a),rr*math.sin(a),minor*math.sin(b)))))
  for i in range(n):
   for j in range(m):ff.append((i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m))
  return self.add(vv,ff,t,True,tag)
 def cushion(self,c,size,t='Velvet',tag=None):
  # Rounded upholstered squircle, separate crown, welt seam, no sharp box.
  x,y,z=c;lx,ly,lz=size;vv=[];ff=[];N=10 if GAME_QUALITY else 16
  for zz,fac in [(-.5,.78),(-.30,.98),(.22,1),(.5,.83)]:
   for j in range(N):a=j*math.tau/N;ca,sa=math.cos(a),math.sin(a);vv.append((x+lx/2*fac*math.copysign(abs(ca)**.38,ca),y+ly/2*fac*math.copysign(abs(sa)**.38,sa),z+lz*zz))
  for k in range(3):
   for j in range(N):a=k*N+j;b=k*N+(j+1)%N;ff.append((a,b,b+N,a+N))
  ff += [tuple(range(N-1,-1,-1)),tuple(3*N+j for j in range(N))]
  return self.add(vv,ff,t,True,tag)
 def emit(self,name,col,kind='furniture',deck='',room='',origin=None,mover=None,material='atlas',maxtris=18500):
  if not self.f:return []
  # Never split a chair leg / closed primitive in the middle of its faces.
  # Groups retain primitive ends through template appends and cabin mirrors.
  chunks=[];start=0;budget=0;previous=0
  ends=self.groups if self.groups and self.groups[-1]==len(self.f) else [len(self.f)]
  for end in ends:
   t=sum(len(f)-2 for f in self.f[previous:end])
   if budget+t>maxtris and previous>start:chunks.append((start,previous));start=previous;budget=0
   budget+=t;previous=end
  chunks.append((start,len(self.f)));objects=[]
  for j,(a,b) in enumerate(chunks):
   vv=[];ff=[];remap={}
   for face in self.f[a:b]:
    out=[]
    for k in face:
     if k not in remap:remap[k]=len(vv);vv.append(self.v[k])
     out.append(remap[k])
    ff.append(tuple(out))
   if origin:vv=[tuple(Vector(v)-Vector(origin)) for v in vv]
   nm=name+(f'_{j+1:02}' if len(chunks)>1 else '')
   me=bpy.data.meshes.new(nm);me.from_pydata(vv,[],ff);me.update()
   bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
   uv=me.uv_layers.new(name='UV0')
   for poly,ti,sm in zip(me.polygons,self.tiles[a:b],self.smooth[a:b]):
    poly.use_smooth=sm
    if material=='sign':
     idx=SIGNINDEX[ti]['cell'];cx,cy=idx%8,idx//8
     coords=[((cx*256+4)/2048,1-(cy*64+60)/2048),((cx*256+252)/2048,1-(cy*64+60)/2048),((cx*256+252)/2048,1-(cy*64+4)/2048),((cx*256+4)/2048,1-(cy*64+4)/2048)]
    else:
     tile=ATLAS.get(ti,ATLAS['Ivory']);cx,cy=tile['column'],tile['row'];n=poly.normal;axis=max(range(3),key=lambda k:abs(n[k]));ax=[k for k in range(3) if k!=axis];ps=[me.vertices[k].co for k in poly.vertices];lo=[min(p[k] for p in ps) for k in ax];hi=[max(p[k] for p in ps) for k in ax]
     if hi[0]-lo[0]<hi[1]-lo[1]:ax=ax[::-1];lo=lo[::-1];hi=hi[::-1]
     coords=[]
     for p in ps:
      u=(p[ax[0]]-lo[0])/max(hi[0]-lo[0],1e-8);v=(p[ax[1]]-lo[1])/max(hi[1]-lo[1],1e-8);coords.append(((cx+(4+248*u)/256)/8,1-(cy+(4+248*v)/256)/8))
    for li,co in zip(poly.loop_indices,coords):uv.data[li].uv=co
   ob=bpy.data.objects.new(nm,me);col.objects.link(ob);ob.location=origin or (0,0,0);me.materials.append(MATERIALS[material]);ob['LII_kind']=kind;ob['LII_deck']=deck;ob['LII_room']=room;ob['LII_tags']=json.dumps(self.tags);ob['LII_export']=True
   if mover:ob['LII_mover']=mover
   me.calc_loop_triangles();OBJECT_RECORDS.append(dict(name=nm,kind=kind,deck=deck,room=room,triangles=len(me.loop_triangles),origin=list(ob.location),mover=mover,components=dict(self.tags)))
   objects.append(ob)
  return objects

def proxy(c,size,ang=0,tag='',kind='box'):
 if min(size)>.001:PROXIES.append(dict(position=[round(float(x),5) for x in c],size=[round(float(x),5) for x in size],yaw=round(ang,6),tag=tag,kind=kind))

def handwheel(m,c,r=.14,axis=(0,1,0),t='Red'):
 m.ring(c,r,.012,t,16,5,axis);a=Vector(axis).normalized();u=a.cross(Vector((0,0,1)))
 if u.length<.01:u=a.cross(Vector((0,1,0)))
 u.normalize();v=a.cross(u);p=Vector(c)
 for j in range(4):ang=j*math.tau/4;m.rod(c,tuple(p+r*(math.cos(ang)*u+math.sin(ang)*v)),.008,t,5)
 m.cylinder(c,.026,.055,'Brass',8,axis)

def bolts(m,c,r,count=8,axis=(0,0,1),size=.018,t='Steel'):
 a=Vector(axis).normalized();q=Vector((0,0,1)).rotation_difference(a);p=Vector(c)
 for j in range(count):ang=j*math.tau/count;co=p+q@Vector((r*math.cos(ang),r*math.sin(ang),0));m.cylinder(tuple(co),size,size*.7,t,6,axis)

def flange(m,c,r,axis=(0,0,1),t='Iron',count=8):
 m.cylinder(c,r,.06,t,16,axis);bolts(m,tuple(Vector(c)+Vector(axis).normalized()*.037),r*.78,count,axis,min(.018,r*.10))

def guarded_lamp(m,x,y,z):
 # Compact caged incandescent for working flats, fixed UNDER a supporting
 # plate/bracket. Unlike saloon pendants it does not hang into the walk lane.
 m.cylinder((x,y,z-.018),.075,.036,'Iron',10)
 m.cylinder((x,y,z-.09),.035,.13,'Brass',10)
 m.lathe((x,y,z-.13),[(0,.035),(-.05,.058),(-.13,.060),(-.18,.035)],'Bulb',12)
 for zz in (z-.13,z-.32):m.ring((x,y,zz),.080,.008,'Iron',12,5)
 for a in (0,math.pi/2,math.pi,3*math.pi/2):
  m.rod((x+.08*math.cos(a),y+.08*math.sin(a),z-.13),(x+.08*math.cos(a),y+.08*math.sin(a),z-.32),.006,'Iron',5)
 LIGHTS.append(dict(position=(x,y,z-.22),range_m=4.2,brightness=1.1))
 m.tags['GuardedMarineIncandescent']+=1


def lamp(m,x,y,z,kind='pendant'):
 if kind=='pendant':
  m.lathe((x,y,z),[(0,.08),(-.03,.09),(-.06,.035),(-.26,.025),(-.28,.055),(-.32,.09),(-.38,.15)],'Brass',12)
  m.lathe((x,y,z-.38),[(0,.15),(-.035,.19),(-.11,.12),(-.20,.075)],'Linen',16)
  m.cushion((x,y,z-.54),(.14,.14,.16),'Bulb')
 else:
  m.lathe((x,y,z),[(0,.14),(.035,.15),(.07,.07),(.27,.035),(.30,.10)],'Brass',12)
  m.lathe((x,y,z+.3),[(0,.20),(.09,.14),(.16,.07)],'GoldCloth',16)
 LIGHTS.append(dict(position=(x,y,z-.45 if kind=='pendant' else z+.3),range_m=4.2,brightness=.8))
