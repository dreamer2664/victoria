"""Deck machinery, hollow funnels, standing/running rigging, bridge
instruments and load-rated host mounts. No substitute launch is generated.
"""
import math
import numpy as np
from mathutils import Vector
from meshkit import *
from shipdesign.leonidas_ii import *

def railing(m,points,z,height=1.03,post=.025,t='White',spacing=1.1,gate=False):
 for a,b in zip(points,points[1:]):
  A=Vector((a[0],a[1],z));B=Vector((b[0],b[1],z));L=(B-A).length
  if L<.02:continue
  proxy(tuple((A+B)/2+Vector((0,0,.55))),(L,.075,1.0),math.atan2(B.y-A.y,B.x-A.x),tag='WeatherGuard')
  for ht,rad,tile in ((height,.032,'Teak'),(.53,.013,t),(.25,.011,t)):
   m.rod(tuple(A+Vector((0,0,ht))),tuple(B+Vector((0,0,ht))),rad,tile,8)
  for f in np.linspace(0,1,max(2,math.ceil(L/spacing)+1)):
   p=A+(B-A)*float(f);m.rod(tuple(p),tuple(p+Vector((0,0,height))),post,t,8)
   m.cylinder(tuple(p+Vector((0,0,.025))),post*2,.05,t,8)


def funnels_and_casings():
 m=Mesh();inner=Mesh();rig=Mesh()
 for x in FUNNELS:
  # Oval, tapered, 5 degree aft rake, outer and inner shells with real rim.
  z0,z1=17.2,30.6;r=1.70;N=48;vv=[];ff=[];ti=[]
  levels=[(z0,1.02),(19.,1.0),(28.5,.95),(30.6,.95)]
  for z,f in levels:
   xx=x-(z-z0)*math.tan(math.radians(5))
   for j in range(N):a=j*math.tau/N;vv.append((xx+r*1.15*f*math.cos(a),r*f*math.sin(a),z))
  for k in range(len(levels)-1):
   for j in range(N):a=k*N+j;b=k*N+(j+1)%N;ff.append((a,b,b+N,a+N));ti.append('Soot' if k==2 else 'Funnel')
  nn=len(vv)
  for z,f in [(z0,1.02),(z1,.95)]:
   xx=x-(z-z0)*math.tan(math.radians(5))
   for j in range(N):a=j*math.tau/N;vv.append((xx+(r*1.15*f-.075)*math.cos(a),(r*f-.075)*math.sin(a),z))
  for j in range(N):
   j1=(j+1)%N;ff.append((nn+j,nn+N+j,nn+N+j1,nn+j1));ti.append('Soot');ff.append((3*N+j,3*N+j1,nn+N+j1,nn+N+j));ti.append('Soot');ff.append((j,nn+j,nn+j1,j1));ti.append('Funnel')
  off=len(m.v);m.v.extend(vv);m.f.extend(tuple(off+i for i in f) for f in ff);m.tiles.extend(ti);m.smooth.extend([True]*len(ff))
  # Uptake lining stops at open funnel throat; the rising lower collector
  # joins the same centreline. An interior black disc is not used as a lid.
  inner.lathe((x,0,0),[(7.85,.44),(9.0,.65),(16.95,1.37),(17.25,1.45),(17.25,1.43),(16.95,1.35),(9.0,.63),(7.85,.42)],'Soot',32,caps=False,closed=True)
  # Base coaming, stiffening rings, ladder, steam escape pipe and whistle.
  for yy in (-2.075,2.075):m.box((x,yy,17.3),(4.35,.14,.30),'White',.025)
  for xx in (x-2.175,x+2.175):m.box((xx,0,17.3),(.14,4.15,.30),'White',.025)
  for z in (18.,22.,26.5,28.5):
   xx=x-(z-z0)*math.tan(math.radians(5));ring=Mesh();ring.ring((0,0,0),r*(.99 if z<28 else .95),.035,'Iron',48,5);m.append(ring,(xx,0,z),scale=(1.15,1,1))
  pts=[]
  for z in (17.7,21.,25.,29.):pts.append((x-(z-z0)*math.tan(math.radians(5))+2.06,0,z))
  for side in (-1,1):m.tube([(a,side*.25,c) for a,b,c in pts],.021,'Iron',7)
  for z in np.arange(18,29,.34):
   xx=x-(float(z)-z0)*math.tan(math.radians(5))+2.06;m.rod((xx,-.25,float(z)),(xx,.25,float(z)),.014,'Iron',6)
  m.tube([(x-2.0,.7,17.45),(x-2.0,.7,28.4),(x-2.15,.7,28.65)],.065,'Steel',10)
  m.lathe((x-2.0,.7,27.4),[(0,.14),(.45,.14),(.5,.20),(.64,.18)],'Brass',16)
  for side in (-1,1):
   for dx in (-3.6,3.6):
    top=(x- .65+dx*.20,side*1.60,25.1);bottom=(x+dx,side*4.4,17.35);rig.rod(top,bottom,.014,'Iron',5)
    p=tuple(Vector(bottom)*.88+Vector(top)*.12);rig.cylinder(p,.035,.35,'Iron',8,tuple(Vector(top)-Vector(bottom)))
 # Casings are real walls. Engine access uses open fore/aft ends below main
 # deck, rather than placing a wall across the rising maintenance staircase.
 for c in CASINGS:
  x0,x1,y0,y1=c['rect'];za,zb=c['z0'],c['z1']
  if c['id'].startswith('Uptake'):za=8.55;zb=17.15
  if c['id']=='EngineCasing':za=8.65;zb=11.73
  for yy in (y0,y1):
   m.box(((x0+x1)/2,yy,(za+zb)/2),(x1-x0,.08,zb-za),'White')
   proxy(((x0+x1)/2,yy,(za+zb)/2),(x1-x0,.08,zb-za),tag=c['id'])
  for xx in (x0,x1):
   if c['id']=='EngineVent':
    if zb>9.2:m.box((xx,0,(9.2+zb)/2),(.08,y1-y0,zb-9.2),'White')
   else:
    m.box((xx,0,(za+zb)/2),(.08,y1-y0,zb-za),'White');proxy((xx,0,(za+zb)/2),(.08,y1-y0,zb-za),tag=c['id'])
 m.emit('Funnels_And_CasingWalls',collection('Funnels'),kind='superstructure');inner.emit('Connected_Uptake_Liners',collection('Funnels'),kind='uptake');rig.emit('Funnel_Stays_And_Turnbuckles',collection('Rigging'),kind='rigging')


def rails_supports():
 m=Mesh();support=Mesh()
 for dk,x0,x1,z in [('saloon',-81,81,11.8),('promenade',-69,61,14.4),('boat',-60,48.5,17.2)]:
  for side in (-1,1):
   pts=[]
   for x in np.linspace(x0,x1,85):
    w=beam_deck(float(x))-(.12 if dk=='saloon' else .46 if dk=='promenade' else .60)
    if w>.4:pts.append((float(x),side*w))
   railing(m,pts,z)
  if dk in ('promenade','boat'):
   for x in np.arange(-59,49,3.7):
    w=beam_deck(float(x))-.55
    if w<3:continue
    for side in (-1,1):
     yy=side*w;za=z-2.8;support.cylinder((float(x),yy,(za+z)/2),.052,z-za,'White',10)
     support.tube([(float(x)-.45,yy,za+2.3),(float(x),yy,z-.06),(float(x)+.45,yy,za+2.3)],.035,'White',7)
     support.ring((float(x),yy,z-.09),.10,.025,'White',12,5)
 m.emit('WeatherDeck_Rails',collection('DeckEquipment'),kind='rail');support.emit('Promenade_Pillars_Knees',collection('Structure'),kind='structure')
 # Continuous lower-deck engine access cross landing, safely above the lower
 # flight, supplying a 1.2m return route to the next staircase.
 land=Mesh();land.box((-9.10,0,5.20),(.70,4.7,.12),'Iron');proxy((-9.10,0,5.17),(.70,4.7,.18),tag='EngineAccessReturnLanding')
 land.box((-2.10,0,5.20),(1.2,4.2,.12),'Iron');proxy((-2.10,0,5.17),(1.2,4.2,.18),tag='EngineAccessForeLanding')
 for yy in (-1.50,1.50):
  land.box((-5.8,yy,5.20),(7.2,1.1,.12),'Iron');proxy((-5.8,yy,5.17),(7.2,1.1,.18),tag='EngineAccessReturnWalk')
 land.emit('Engine_Access_Landing',collection('Stairs'),kind='platform',deck='lower')


def masts_and_rig():
 m=Mesh();standing=Mesh();running=Mesh()
 # Pole/derrick rig is a defensible 1889 liner choice, not a barque imposed
 # by the earlier QA aesthetic opinion. No phantom square sails are added.
 for name,x,z0,height,r in [('Fore',67.2,11.8,23.5,.28),('Main',8.5,17.2,23.5,.30),('Mizzen',-46.4,17.2,19.0,.24)]:
  rake=.045;top=(x-height*rake,0,z0+height)
  m.rod((x,0,z0),top,r,'Oak',16,r2=r*.42,tag='PoleMast')
  for ht in (.25,1.2,5.0,11.0):m.ring((x-ht*rake,0,z0+ht),r*(1-.55*ht/height)+.025,.035,'Iron',18,5)
  # Crowsnest platform and full guard rail, with actual ladder rungs.
  nestz=z0+height*.62;nestx=x-(nestz-z0)*rake;m.cylinder((nestx,0,nestz),.68,.09,'Oak',24);m.ring((nestx,0,nestz+.85),.66,.025,'Iron',24,5)
  for a in np.linspace(0,math.tau,12,endpoint=False):m.rod((nestx+.65*math.cos(float(a)),.65*math.sin(float(a)),nestz),(nestx+.65*math.cos(float(a)),.65*math.sin(float(a)),nestz+.85),.018,'Iron',5)
  for z in np.arange(z0+.5,nestz,.37):
   xx=x-(float(z)-z0)*rake;m.rod((xx-r-.08,-.20,float(z)),(xx-r-.08,.20,float(z)),.014,'Iron',6)
  # Shrouds land on same deck edge, stay leads stop clear of public doors.
  for side in (-1,1):
   for dx in (-4.2,0,4.2):
    bx=x+dx;yy=side*max(2.0,beam_deck(bx)-.7);bottom=(bx,yy,z0+.08)
    standing.rod((x-height*.72*rake,0,z0+height*.72),bottom,.014,'Iron',5)
    p=tuple(Vector(bottom)*.88+Vector(top)*.12);standing.cylinder(p,.026,.34,'Iron',8,tuple(Vector(top)-Vector(bottom)))
  for dx in (-10,10):
   bx=max(-79,min(79,x+dx));standing.rod(top,(bx,0,z0+.2),.017,'Iron',6)
  # Cargo boom + topping lift where the main/fore hatch is located.
  if name!='Mizzen':
   end=(x+8.5,-2.2,z0+4.5);m.rod((x,0,z0+1.1),end,.12,'Oak',12,r2=.07);running.rod((x-.5,0,z0+12),end,.012,'Rope',6)
   running.rod(end,(end[0],end[1],z0+1.7),.014,'Rope',6)
   running.ring((end[0],end[1],z0+1.5),.16,.024,'Iron',16,5,(1,0,0))
  # Flag halyard / belaying pins properly end at a fitted pinrail.
  for yy in (-.36,.36):running.rod(top,(x+.25,yy,z0+1.1),.007,'Rope',5)
  m.box((x+.2,0,z0+1.1),(.20,1.2,.09),'Oak',.015)
  for yy in np.arange(-.48,.5,.16):m.lathe((x+.2,float(yy),z0+1.1),[(-.12,.012),(.06,.02),(.14,.014)],'Oak',7)
 m.emit('Masts_Derricks_Crowsnests',collection('Masts'),kind='mast');standing.emit('Shrouds_Stays_Deadeyes',collection('Rigging'),kind='rigging');running.emit('Running_Rig_Halyards',collection('Rigging'),kind='rigging')


def deck_machinery():
 m=Mesh();chains=Mesh()
 # Bower windlass, gypsy chainwheels, common shaft, geared steam drive.
 x,z=75.5,11.9
 m.box((x,0,z+.18),(2.6,3.5,.33),'Iron',.04)
 m.cylinder((x,0,z+.92),.13,3.7,'Steel',16,(0,1,0))
 for y in (-1.22,1.22):
  m.lathe((x,y,z+.92),[(-.32,.34),(-.20,.40),(-.12,.29),(.12,.29),(.20,.4),(.32,.34)],'Iron',24,(0,1,0))
  m.box((x,y,z+.52),(.50,.55,.70),'Engine',.04)
 for y in (-.64,.64):
  m.cylinder((x,y,z+.92),.48,.13,'Iron',28,(0,1,0));m.ring((x,y,z+.92),.40,.055,'Steel',28,5,(0,1,0))
 for dx in (-.6,.6):m.cylinder((x+dx,0,z+.55),.19,.72,'Engine',16,(1,0,0))
 for side in (-1,1):
  # Actual alternating chain-link loops from gypsy toward hawse then anchor.
  y=side*1.25
  for j in range(18):
   xx=x+j*.19;zz=z+.95-.060*j;chains.ring((xx,y,zz),.105,.025,'Iron',10,5,(0,1,0) if j%2 else (0,0,1))
  hx=79.0;hy=side*max(.5,hb(hx,10.65));m.ring((hx,hy,10.65),.28,.09,'Iron',20,6,(0,1,0))
  ax,ay,az=79.05,hy+side*.16,9.6
  m.rod((ax,ay,az-1.05),(ax,ay,az+1.0),.085,'Iron',10)
  for sy in (-1,1):
   m.tube([(ax,ay,az-1.0),(ax+sy*.48,ay,az-1.20),(ax+sy*.80,ay,az-.73)],.085,'Iron',8)
   m.box((ax+sy*.77,ay,az-.67),(.35,.13,.48),'Iron',.025,ang=sy*.5)
  m.ring((ax,ay,az+1.08),.15,.04,'Iron',14,6,(0,1,0))
 # After capstan and paired bitts / fairleads at actual deck-edge positions.
 for xx in (-70,64):
  zz=11.85;m.lathe((xx,0,zz),[(0,.58),(.09,.60),(.18,.33),(.65,.35),(.81,.52),(.94,.50)],'Iron',24)
  for a in np.linspace(0,math.tau,8,endpoint=False):m.rod((xx+.32*math.cos(float(a)),.32*math.sin(float(a)),zz+.9),(xx+.70*math.cos(float(a)),.70*math.sin(float(a)),zz+.9),.034,'Oak',7)
 for xx in (-68,-34,34,68):
  for side in (-1,1):
   yy=side*(beam_deck(xx)-.55);zz=11.84;m.box((xx,yy,zz+.08),(1.25,.62,.15),'Iron',.025)
   for dx in (-.35,.35):
    m.lathe((xx+dx,yy,zz+.14),[(0,.14),(.55,.14),(.61,.20),(.68,.20)],'Iron',14)
 # Hatch coamings with individual timber hatch boards and battens. Holds
 # have actual walls/floors below, not bottomless black rectangles.
 for xx,l,w in [(61.0,4.8,3.5),(-66.3,3.8,2.8)]:
  for yy in (-w/2,w/2):m.box((xx,yy,12.02),(l,.11,.43),'White',.015)
  for xa in (xx-l/2,xx+l/2):m.box((xa,0,12.02),(.11,w,.43),'White',.015)
  for xa in np.arange(xx-l/2+.12,xx+l/2,.24):m.box((float(xa),0,12.27),(.235,w-.12,.075),'Oak',.008)
  for yy in (-w*.28,w*.28):m.box((xx,yy,12.34),(l,.065,.055),'Iron',.01)
 # Hollow ventilator cowls, curves finish in an open annular mouth.
 for xx,yy,z0 in [(-29,-5.4,17.25),(-29,5.4,17.25),(-6.8,-3.3,17.25),(-6.8,3.3,17.25),(24,-5.8,17.25),(24,5.8,17.25),(54,-3.2,11.85),(54,3.2,11.85)]:
  m.lathe((xx,yy,z0),[(0,.38),(.12,.41),(.18,.27),(1.35,.27),(1.35,.235),(.18,.235),(.12,.375),(0,.345)],'White',20,caps=False,closed=True)
  # Quarter-bend has an open swept shell; rings visible at the throat.
  N=16;K=10;vv=[];ff=[]
  for outer in (True,False):
   for k in range(K):
    a=k/(K-1)*math.pi/2;centre=Vector((xx+.40*(1-math.cos(a)),yy,z0+1.35+.40*math.sin(a)));axis=Vector((math.sin(a),0,math.cos(a)));u=Vector((0,1,0));v=axis.cross(u)
    rr=(.27+.17*(k/(K-1))**2)-(0 if outer else .035)
    for j in range(N):b=j*math.tau/N;vv.append(tuple(centre+rr*(math.cos(b)*u+math.sin(b)*v)))
  for sh in (0,K*N):
   for k in range(K-1):
    for j in range(N):a=sh+k*N+j;b=sh+k*N+(j+1)%N;ff.append((a,b,b+N,a+N))
  for j in range(N):
   a=(K-1)*N+j;b=(K-1)*N+(j+1)%N;ff.append((a,b,b+K*N,a+K*N));ff.append((j,K*N+j,K*N+(j+1)%N,(j+1)%N))
  m.add(vv,ff,'White',True)
  m.ring((xx+.4,yy,z0+1.75),.44,.027,'Red',24,5,(1,0,0))
 m.emit('Windlass_Capstans_Bitts_Hatches_Vents',collection('DeckEquipment'),kind='equipment');chains.emit('Bower_Anchor_Chains',collection('DeckEquipment'),kind='chain')


def davits():
 m=Mesh()
 for b in BOAT_MOUNTS:
  x,y,z=b['position'];side=1 if y>0 else -1;footy=y+side*1.65
  for sling in (b['fore_sling'],b['aft_sling']):
   xx=x+sling;m.cylinder((xx,footy,17.28),.24,.16,'Iron',16);bolts(m,(xx,footy,17.38),.18,8,(0,0,1),.022)
   m.tube([(xx,footy,17.35),(xx,footy,19.9),(xx,footy-side*.25,20.5),(xx,y,20.7)],.085,'White',12,tag='RatedGooseneckDavit')
   m.cylinder((xx,y,20.57),.18,.13,'Brass',16,(1,0,0));m.ring((xx,y,20.57),.18,.027,'Iron',16,5,(1,0,0))
   # Two-part falls down to the hook. Slings are host locators, not fictional
   # lifting eyes placed on a substitute boat model.
   for dy in (-.06,.06):m.rod((xx,y+dy,20.52),(xx,y+dy,19.35),.014,'Rope',6)
   m.cylinder((xx,y,19.32),.14,.12,'Brass',14,(1,0,0));m.ring((xx,y,19.10),.11,.022,'Iron',14,5,(1,0,0))
   m.box((xx,footy-side*.12,18.1),(.42,.08,.23),'Brass',.018)
   m.rod((xx-.25,footy,17.7),(xx+.25,footy,17.7),.035,'Iron',8)
  # Two actual saddle/cradle supports meet the latest boat contact stations.
  for localx,localz in b['cradles']:
   xx=x+localx;top=z+localz;h=max(.07,top-17.2)
   m.box((xx,y,17.2+h/2),(.22,1.5,h),'Oak',.02)
   m.box((xx,y,top+.018),(.24,1.54,.035),'Canvas',.008)
 m.emit('Davits_And_Contract_Cradles',collection('BoatMounts'),kind='mount')
 # Invisible authoritative attachment empties survive as manifest points.
 for b in BOAT_MOUNTS:
  ob=bpy.data.objects.new('Mount_'+b['id'],None);collection('BoatMounts').objects.link(ob);ob.location=b['position'];ob.empty_display_type='ARROWS';ob.empty_display_size=.65;ob['craft_id']=b['craft'];ob['required_swl_kg']=b['required_swl_kg']


def bridge():
 m=Mesh();wheel=Mesh();z=20.055
 # Wheel shaft longitudinal. Hub, eight turned handles/spokes, bronze rim.
 origin=(38.5,0,z+1.03)
 wheel.ring(origin,.56,.035,'Teak',40,7,(1,0,0));wheel.ring(origin,.50,.016,'Brass',36,5,(1,0,0));wheel.cylinder(origin,.12,.22,'Brass',16,(1,0,0))
 for a in np.linspace(0,math.tau,8,endpoint=False):
  ca,sa=math.cos(float(a)),math.sin(float(a));wheel.rod(origin,(38.5,.66*sa,z+1.03+.66*ca),.023,'Teak',8);wheel.cylinder((38.5,.69*sa,z+1.03+.69*ca),.035,.13,'Teak',10,(0,sa,ca))
 wheel.emit('HelmWheel',collection('Navigation'),kind='mover',deck='bridge',room='N_Wheelhouse',origin=origin,mover='helm');MOVERS.append(dict(name='HelmWheel',type='helm',origin=origin))
 for xx in (38.38,38.68):m.lathe((xx,0,z),[(0,.24),(.09,.25),(.15,.14),(.76,.10),(.86,.17),(1.03,.15)],'Teak',12)
 m.rod((38.1,0,z+1.03),(38.95,0,z+1.03),.065,'Brass',12)
 # Brass binnacle forward of helm, shaded hood / internal compass card.
 m.lathe((39.6,0,z),[(0,.30),(.10,.31),(.16,.20),(.80,.19),(.93,.31),(1.07,.32)],'Teak',20)
 m.lathe((39.6,0,z+1.0),[(0,.34),(.24,.35),(.35,.28),(.42,.10)],'Brass',24)
 m.cylinder((39.24,0,z+1.22),.19,.015,'Paper',24,(1,0,0));m.ring((39.22,0,z+1.22),.20,.025,'Brass',24,6,(1,0,0))
 for a in np.linspace(0,math.tau,16,endpoint=False):m.rod((39.205,.14*math.cos(float(a)),z+1.22+.14*math.sin(float(a))),(39.205,.18*math.cos(float(a)),z+1.22+.18*math.sin(float(a))),.003,'Black',4)
 # Separate port and starboard telegraph heads, dials and ordered handles.
 for yy in (-2.1,-2.8):
  m.lathe((38.2,yy,z),[(0,.22),(.06,.23),(.12,.10),(.88,.09),(.95,.15)],'Brass',16)
  m.cylinder((38.2,yy,z+1.19),.27,.20,'Brass',24,(1,0,0));m.cylinder((38.085,yy,z+1.19),.235,.014,'Paper',24,(1,0,0));m.ring((38.07,yy,z+1.19),.24,.018,'Brass',24,5,(1,0,0))
  for i in range(9):a=math.radians(-110+i*27.5);m.rod((38.06,yy+.18*math.sin(a),z+1.19+.18*math.cos(a)),(38.06,yy+.22*math.sin(a),z+1.19+.22*math.cos(a)),.004,'Black',4)
  m.rod((38.2,yy,z+1.19),(38.2,yy,z+1.60),.022,'Brass',8);m.cylinder((38.2,yy,z+1.62),.045,.16,'Teak',10,(0,1,0))
 # Speaking tubes, voice mouthpiece, engine bell, ship's clock.
 for yy in (2.8,3.1):m.tube([(36.2,yy,z),(36.2,yy,z+1.28),(36.1,yy,z+1.42),(35.95,yy,z+1.42)],.026,'Copper',10);m.lathe((35.95,yy,z+1.42),[(0,.04),(.09,.085)],'Brass',16,(-1,0,0))
 m.lathe((39.1,3.7,z+1.6),[(0,.15),(.12,.13),(.22,.06)],'Brass',16)
 m.cylinder((40.85,0,z+2.06),.17,.045,'Brass',20,(1,0,0));m.cylinder((40.82,0,z+2.06),.15,.015,'Paper',20,(1,0,0));m.rod((40.805,0,z+2.06),(40.805,0,z+2.17),.005,'Black',4);m.rod((40.805,0,z+2.06),(40.805,.095,z+2.06),.004,'Black',4)
 # Wing nav lights correspond to the actual bridge, not the old x=12.5.
 for side in (-1,1):
  yy=side*7.0;m.box((38.5,yy,20.50),(.45,.36,.76),'Black',.025);m.lathe((38.5,yy,20.39),[(0,.13),(.27,.13)],'Red' if side>0 else 'Green',16)
 m.emit('Binnacle_Telegraphs_VoiceTubes_Navlights',collection('Navigation'),kind='navigation',deck='bridge',room='N_Wheelhouse')
 # Bridge wing platforms are above the real officer cabins; no full-width
 # front dodger blocks the wheelhouse's forward window.
 wings=Mesh()
 for side in (-1,1):
  y=side*5.9
  # Bridge access opening must cut BOTH structural bridge and wing plate.
  ys=sorted([side*4.775,side*5.40,side*6.80,side*7.025]);xs=[31.81,32.97,38.53,43.0]
  for a,b in zip(xs,xs[1:]):
   for c,d in zip(ys,ys[1:]):
    if side>0 and 32.97<(a+b)/2<38.53 and 5.4<(c+d)/2<6.8:continue
    wings.box(((a+b)/2,(c+d)/2,19.94),(b-a,d-c,.12),'Teak');proxy(((a+b)/2,(c+d)/2,19.94),(b-a,d-c,.12),tag='BridgeWing')
  railing(wings,[(31.81,side*7.1),(43,side*7.1)],20)
 railing(wings,[(43,-7.1),(43,7.1)],20)
 # A full 1.19m after lobby at the wheelhouse door, and guards that join
 # rather than run through the forward funnel casing (|y|<=2.2m).
 for a,b in [(-7.1,-2.25),(2.25,7.1)]:railing(wings,[(31.81,a),(31.81,b)],20)
 wings.emit('Navigating_Bridge_Wings',collection('Navigation'),kind='deck',deck='bridge')


def boarding_and_skylight():
 m=Mesh()
 # Stowed gangway is a real hinged assembly at the shell opening; server
 # switches between boarding and fully shipped positions with an interlock.
 for side in (-1,1):
  y=side*9.10;z=8.85;name='Gangway_Port' if side>0 else 'Gangway_Starboard';a=Mesh()
  a.box((-2.0,y+side*2.5,z),(1.5,5.0,.13),'Teak',.015)
  for yy in np.arange(y+side*.2,y+side*4.9,side*.24):a.box((-2,float(yy),z+.085),(1.42,.035,.035),'Oak',.005)
  for xx in (-2.73,-1.27):
   a.rod((xx,y,z+1.02),(xx,y+side*5,z+1.02),.030,'White',8)
   for dy in np.linspace(0,5,8):a.rod((xx,y+side*float(dy),z),(xx,y+side*float(dy),z+1.02),.022,'White',6)
  origin=(-2,y,z);a.emit(name,collection('Boarding'),kind='mover',origin=origin,mover='gangway');MOVERS.append(dict(name=name,type='gangway',origin=origin,side=side))
 # Gabled stained-glass stair skylight, not a Titanic dome. Genuine holes
 # below the ridge leave an observable continuous stairwell.
 glass=Mesh();z=19.85;x0,x1=-5.8,1.8;w=3.1
 for side in (-1,1):
  normal=Vector((0,side*.75/w,1)).normalized()*.009;face=[Vector(p) for p in [(x0,0,z+.75),(x1,0,z+.75),(x1,side*w,z),(x0,side*w,z)]]
  vv=[tuple(p+normal*s) for s in (-1,1) for p in face];glass.add(vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Ivory')
  for x in np.linspace(x0,x1,9):m.rod((float(x),0,z+.75),(float(x),side*w,z),.037,'Teak',8)
  m.rod((x0,side*w,z),(x1,side*w,z),.055,'Teak',10)
  for y in np.linspace(0,w,6):m.rod((x0,side*float(y),z+.75*(1-y/w)),(x1,side*float(y),z+.75*(1-y/w)),.016,'Brass',6)
 m.rod((x0,0,z+.75),(x1,0,z+.75),.055,'Teak',10)
 m.emit('Grand_Stair_Skylight_Joinery',collection('Stairs'),kind='skylight',deck='boat');glass.emit('Grand_Stair_Skylight_Glass',collection('Windows'),kind='glazing',material='glass')


def build():funnels_and_casings();rails_supports();masts_and_rig();deck_machinery();davits();bridge();boarding_and_skylight()
