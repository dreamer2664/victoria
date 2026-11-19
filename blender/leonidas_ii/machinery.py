"""Connected single-screw plant; static engineering relationships and exact
slider-crank movers. All values are fictional reconstruction design choices.
"""
import math,json
import numpy as np
from mathutils import Vector
from meshkit import *
from shipdesign.leonidas_ii import *
CONNECTIONS=[]

def pipe(m,id,points,r=.09,t='Copper',flanges=True):
 m.tube(points,r,t,12,tag=id)
 if flanges:
  for idx,jdx in [(0,1),(-1,-2)]:
   p=Vector(points[idx]);d=(p-Vector(points[jdx])).normalized();flange(m,tuple(p),r*1.48,tuple(d),t='Iron')
 medium=('steam' if 'Steam' in id or 'Receiver' in id else 'exhaust_steam' if 'Exhaust' in id else 'condensate' if 'Condensate' in id else 'feedwater' if 'Feed' in id or 'Hotwell_Suction' in id else 'seawater' if 'Sea' in id else 'flue_gas' if 'Flue' in id or 'Uptake' in id else 'unclassified')
 CONNECTIONS.append(dict(id=id,points=points,radius=r,start=points[0],end=points[-1],medium=medium))

def gauge(m,c,r=.13,axis=(1,0,0),reading=.60):
 m.lathe(c,[(-.055,r*.86),(-.04,r),(.025,r),(.04,r*.88)],'Brass',16,axis)
 q=Vector((0,0,1)).rotation_difference(Vector(axis));p=Vector(c);face=p+q@Vector((0,0,.044));m.cylinder(tuple(face),r*.85,.008,'Paper',20,axis)
 for i in range(11):
  a=math.radians(-125+i*25);a0=face+q@Vector((math.sin(a)*r*.68,math.cos(a)*r*.68,.004));b0=face+q@Vector((math.sin(a)*r*.80,math.cos(a)*r*.80,.004));m.rod(tuple(a0),tuple(b0),.003,'Black',4)
 a=math.radians(-125+250*reading);m.rod(tuple(face+q@Vector((0,0,.006))),tuple(face+q@Vector((math.sin(a)*r*.62,math.cos(a)*r*.62,.006))),.004,'Red',5)


def boilers():
 for row,x in enumerate(BOILER_XS):
  m=Mesh();pipes=Mesh();z=4.02
  for j,y in enumerate(BOILER_YS):
   id=f'B{row+1}{j+1}'
   proxy((x,y,z),(3.55,4.20,4.20),tag=id+'_Boiler')
   m.lathe((x,y,z),[(-1.75,1.94),(-1.67,2.10),(1.67,2.10),(1.75,1.94)],'Lagging',36,(1,0,0),tag='SingleEndedScotchBoiler')
   for dx in (-1.62,-.80,.80,1.62):m.ring((x+dx,y,z),2.105,.035,'Iron',36,5,(1,0,0))
   # Riveted circular front plate, longitudinal tie-rod ends and stays.
   m.cylinder((x-1.77,y,z),2.04,.06,'Iron',36,(1,0,0));bolts(m,(x-1.80715,y,z),1.98,36,(-1,0,0),.021)
   for yy in (-1.25,-.42,.42,1.25):
    # Four 0.60m firing mouths at 0.83m centres. The old 0.94m
    # flanges overlapped each other; 0.75m OD rings now leave 80mm
    # between neighbours and fit wholly inside the 4.08m front plate.
    zf=2.97;cf=(x-1.82,y+yy,zf)
    m.lathe(cf,[(-.04,.336),(0,.375),(.07,.368)],'Iron',16,(-1,0,0));m.cylinder((x-1.91,y+yy,zf),.308,.035,'Soot',16,(1,0,0));bolts(m,(x-1.894,y+yy,zf),.344,10,(-1,0,0),.012)
    # Hinged dished furnace door with latch; ashpan below it.
    m.lathe((x-1.90,y+yy,zf),[(0,.288),(.05,.272),(.09,.208)],'Iron',16,(-1,0,0),tag='FurnaceDoor_600mm');m.box((x-1.90,y+yy,zf-.55),(.22,.65,.25),'Soot',.025)
    m.rod((x-1.98,y+yy,zf),(x-2.06,y+yy,zf),.018,'Steel',8)
    m.rod((x-2.06,y+yy-.16,zf),(x-2.06,y+yy+.16,zf),.014,'Steel',7)
    for dz in (-.16,.16):
     m.box((x-1.93,y+yy-.28,zf+dz),(.12,.10,.10),'Iron',.010)
     m.cylinder((x-1.96,y+yy-.28,zf+dz),.023,.09,'Steel',8,(0,0,1))
   # One manhole over furnace bank; twin water gauge columns and pressure dial.
   m.lathe((x-1.79,y,z+1.12),[(0,.29),(.07,.29),(.09,.29)],'Iron',18,(-1,0,0));bolts(m,(x-1.88505,y,z+1.12),.25,10,(-1,0,0),.015)
   m.rod((x-1.79,y-.58,z+1.16),(x-1.96,y-.58,z+1.16),.022,'Copper',9)
   gauge(m,(x-2.00,y-.58,z+1.16),.15,(-1,0,0),.64)
   m.rod((x-1.79,y+.65,5.85),(x-2.28,y+.65,5.85),.015,'Iron',7)
   guarded_lamp(m,x-2.28,y+.65,5.85)
   for gy in (-.95,.95):
    m.cylinder((x-1.98,y+gy,z+.58),.025,.65,'Brass',8)
    for zz in (z+.27,z+.89):m.tube([(x-1.79,y+gy,zz),(x-2.00,y+gy,zz)],.022,'Copper',7);handwheel(m,(x-2.02,y+gy,zz),.065,(-1,0,0),'Brass')
   for dx in (-1.05,1.05):
    for sy in (-1,1):m.box((x+dx,y+sy*1.05,1.79),(.42,.65,.38),'Engine',.025);m.rod((x+dx,y+sy*1.05,1.9),(x+dx,y+sy*1.45,2.40),.13,'Engine',4)
   # Domed steam stop, safety valves, feedwater check-valve and blowdown.
   m.lathe((x,y,z+2.10),[(0,.20),(.20,.22),(.39,.18),(.46,.12)],'Iron',16)
   pipe(pipes,id+'_SteamStop',[(x,y,6.55),(x,y,6.90),(x,y- .40,7.05)],.105,'Lagging')
   handwheel(m,(x,y-.40,7.10),.15,(0,0,1),'Red')
   for dy in (-.34,.34):
    m.lathe((x+.55,y+dy,z+2.05),[(0,.07),(.22,.07),(.25,.11),(.40,.065)],'Brass',10)
   pipe(pipes,id+'_Feed',[(x-1.78,y-1.5,3.2),(x-2.25,y-1.5,3.2),(x-2.25,y-1.5,2.4)],.045,'Copper')
   # Smokebox hood/branch: intentionally attached to furnace-front top.
   m.box((x-1.50,y,5.55),(.70,3.55,.65),'Soot',.07)
   pipe(pipes,id+'_Flue',[(x-1.35,y,5.90),(x-1.35,y,6.75),(x-.2,y,8.00),(x,0,8.00)],.29,'Iron')
  # Across-row dry-steam and feed mains, with a human-readable single flow.
  pipe(pipes,f'Row{row+1}_SteamHeader',[(x,-4.8,7.05),(x,4.8,7.05)],.14,'Lagging')
  pipe(pipes,f'Row{row+1}_FeedHeader',[(x-2.25,-6.65,2.4),(x-2.25,7.0,2.4)],.065,'Copper')
  target=4.5 if row<2 else 30.0
  pipe(pipes,f'Row{row+1}_CollectorUptake',[(x,0,8.00),(target,0,8.00),(target,0,8.1)],.44,'Soot')
  m.emit(f'Scotch_Row_{row+1}',collection('Boilers'),kind='boiler',deck='machinery',room=['E_Boilers_A','E_Boilers_M','E_Boilers_F'][row]);pipes.emit(f'Boiler_Pipework_{row+1}',collection('PlantPipes'),kind='pipe',deck='machinery')
 # Fire tools and coal trimmer bunkers, correctly outside furnace front.
 coal=Mesh()
 for x in BOILER_XS:
  for side in (-1,1):
   yy=side*7.45;coal.box((x,yy,3.0),(7.3,.22,2.8),'Iron');proxy((x,yy,3.0),(7.3,.22,2.8),tag='CoalBunkerWall');coal.box((x,yy-side*.1448,2.48),(1.0,.07,.85),'Soot',.025)
   # The visible lumps now bear on a finite coal bulk down to the tank
   # top, following the ACTUAL bilge breadth. Former lumps hung over void.
   from structure import actual_min_breadth
   levels=(1.60,2.40,3.20,4.30);vv=[]
   for zz in levels:
    outer=actual_min_breadth(x-3.6,x+3.6,zz)-.13
    assert outer>7.56,(x,zz,outer)
    vv.extend([(xa,side*yy,zz) for xa,yy in ((x-3.6,7.55),(x+3.6,7.55),(x+3.6,outer),(x-3.6,outer))])
   ff=[(3,2,1,0),tuple(range(12,16))]
   for k in range(3):
    for j in range(4):ff.append((k*4+j,k*4+(j+1)%4,(k+1)*4+(j+1)%4,(k+1)*4+j))
   coal.add(vv,ff,'Coal')
   for j in range(6):coal.cushion((x-2+j*.75,yy+side*.35,4.45),(.9,.6,.32),'Coal')
  for j in range(3):
   xx=x-3.4+j*.38;coal.rod((xx,-3.3,1.65),(xx,-3.3,2.9),.015,'Oak',7);coal.box((xx,-3.3,1.74),(.20,.08,.28),'Iron',.02)
 coal.emit('CoalBunkers_FireTools',collection('Boilers'),kind='equipment',deck='machinery')


def engine():
 still=Mesh();crank=Mesh();pipes=Mesh();platform=Mesh();xlo,xhi=-26.8,-9.6
 proxy((-18.2,0,6.05),(17.2,5.9,8.5),tag='GuardedEngineCore')
 # Cast bedplate with bearing housings and longitudinal feet.
 for yy in (-2.55,2.55):still.box(((xlo+xhi)/2,yy,1.81),(xhi-xlo,.46,.42),'Engine',.05)
 for x in (-26,-23.4,-18.7,-13.8,-9.9):
  still.box((x,0,2.0),(.78,5.6,.30),'Engine',.035)
  # A genuinely bored journal bearing: the former solid bronze/cast
  # cylinders and tall chock occupied the rotating shaft's own volume.
  still.box((x,0,2.37),(.68,.84,.50),'Engine',.04)
  still.lathe((x,0,SHAFT_Z),[(-.35,.40),(.35,.40),(.35,.286),(-.35,.286)],'Brass',48,(1,0,0),caps=False,closed=True)
  still.lathe((x,0,SHAFT_Z),[(-.18,.44),(.18,.44),(.18,.398),(-.18,.398)],'Engine',32,(1,0,0),caps=False,closed=True)
  for yy in (-.43,.43):
   still.box((x,yy,2.91),(.68,.28,.12),'Engine',.018)
   bolts(still,(x,yy,2.9789),.10,4,(0,0,1),.026)
  for yy in (-2.5,2.5):bolts(still,(x,yy,2.15855),.14,4,(0,0,1),.025)
 # Main journals rotate together but do not run a solid central cylinder
 # through the offset crankpin. Gaps at each crank throw are explicit.
 spans=[(-27,-21.45),(-20.55,-16.45),(-15.55,-11.95),(-11.05,-9.3)]
 for a,b in spans:crank.cylinder(((a+b)/2,0,SHAFT_Z),.28,b-a,'Steel',20,(1,0,0))
 for i,(x,bore) in enumerate(zip(ENGINE_XS,ENGINE_BORES)):
  phase=i*math.tau/3;dy=CRANK_R*math.sin(phase);dz=CRANK_R*math.cos(phase);pin=(x,dy,SHAFT_Z+dz);crossz=SHAFT_Z+dz+math.sqrt(CONROD_L**2-dy**2)
  # Two thick shaped crank webs, offset crankpin and balance lobes.
  axis=Vector((math.sin(phase),math.cos(phase)));perp=Vector((math.cos(phase),-math.sin(phase)))
  outline=[-.25*axis-.32*perp,-.25*axis+.32*perp,CRANK_R*axis+.24*perp,(CRANK_R+.20)*axis,CRANK_R*axis-.24*perp]
  for xx in (x-.35,x+.35):
   vv=[(xx+d,p.x,SHAFT_Z+p.y) for d in (-.10,.10) for p in outline];n=len(outline);ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)];crank.add(vv,ff,'Iron')
  crank.cylinder(pin,.17,.90,'Steel',20,(1,0,0))
  # Cylinder jacket, heavily flanged heads, covers, studs, indicator cocks.
  rr=bore/2+.17;z0,z1=7.73,10.13
  still.lathe((x,0,0),[(z0,rr+.07),(z0+.12,rr+.07),(z0+.18,rr),(z1-.15,rr),(z1-.11,rr+.08),(z1,rr+.08)],'Engine',32,tag='TripleExpansionCylinder')
  still.cylinder((x,0,z1+.045),rr+.10,.09,'Iron',32);bolts(still,(x,0,z1+.0975),rr+.035,20,(0,0,1),.022)
  still.cylinder((x,0,z0-.08),.20,.16,'Brass',16)
  # A-frame columns / guides support the cylinder, not floating stacks.
  spread=max(1.05,rr+.25)
  for side in (-1,1):
   yy=side*spread
   still.rod((x-1.05,side*2.40,1.97),(x-.60,yy,7.70),.11,'Engine',8)
   still.rod((x+1.05,side*2.40,1.97),(x+.60,yy,7.70),.11,'Engine',8)
   for xx in (x-1.05,x+1.05):
    still.box((xx,side*2.40,2.02),(.45,.50,.10),'Engine',.020);bolts(still,(xx,side*2.40,2.0761),.14,4,(0,0,1),.018)
   for xx in (x-.61,x+.61):still.cylinder((xx,yy,7.65),.19,.12,'Engine',12)
   still.rod((x-.65,yy,7.52),(x+.65,yy,7.52),.09,'Engine',6)
  # Two transverse cylinder-support girders leave the piston/gland bay open.
  # The former side-only top ties never actually reached the jacket base.
  for xx in (x-.65,x+.65):
   spans=[(-spread-.175,.40),(.76,spread+.175)] if xx>x else [(-spread-.175,spread+.175)]
   for a,b in spans:still.box((xx,(a+b)/2,7.68),(.35,b-a,.18),'Engine',.025)
  # Crosshead guide bars and separate working slipper/crosshead/piston rod.
  for yy in (-.475,.475):
   still.box((x,yy,6.05),(.30,.095,2.35),'Steel',.015)
   for dx in (-.65,.65):still.rod((x,yy,7.20),(x+dx,math.copysign(spread,yy),7.65),.055,'Engine',8)
  piston=Mesh();piston.box((x,0,crossz),(.39,.84,.25),'Brass',.025);piston.cylinder((x,0,crossz),.15,.57,'Steel',14,(1,0,0));piston.cylinder((x,0,crossz+PISTON_ROD_L/2),.086,PISTON_ROD_L,'Steel',14)
  nm=['HP','IP','LP'][i];origin=(x,0,crossz);obs=piston.emit('Piston_'+nm,collection('EngineMoving'),kind='mover',room='E_Engine',origin=origin,mover='piston')
  MOVERS.append(dict(name='Piston_'+nm,type='piston',phase=phase,origin=origin,x=x,r=CRANK_R,l=CONROD_L,cross_z0=crossz))
  rod=Mesh();top=(x,0,crossz);u=(Vector(top)-Vector(pin)).normalized()
  # Bearing centres/kinematics remain exact. The shank stops at the real
  # eyes instead of going straight through the rotating crank/wrist pins.
  rod.rod(tuple(Vector(pin)+u*.235),tuple(Vector(top)-u*.195),.105,'Steel',12,r2=.08)
  rod.ring(pin,.245,.070,'Brass',20,6,(1,0,0));rod.ring(top,.195,.040,'Brass',20,6,(1,0,0))
  rod.lathe(pin,[(-.17,.205),(.17,.205),(.17,.171),(-.17,.171)],'Brass',20,(1,0,0),caps=False,closed=True)
  rod.lathe(top,[(-.15,.176),(.15,.176),(.15,.151),(-.15,.151)],'Brass',20,(1,0,0),caps=False,closed=True)
  # Split big-end cap carries its four studs clear of the actual bore.
  rod.box((x,dy,SHAFT_Z+dz-.255),(.34,.56,.11),'Iron',.009)
  for dx in (-.13,.13):
   for sy in (-.22,.22):
    rod.rod((x+dx,dy+sy,SHAFT_Z+dz-.32),(x+dx,dy+sy,SHAFT_Z+dz-.18),.013,'Steel',8)
    rod.cylinder((x+dx,dy+sy,SHAFT_Z+dz-.32),.023,.025,'Steel',6)
  mid=tuple((Vector(pin)+Vector(top))/2);rod.emit('Conrod_'+nm,collection('EngineMoving'),kind='mover',room='E_Engine',origin=mid,mover='conrod');MOVERS.append(dict(name='Conrod_'+nm,type='conrod',phase=phase,x=x,r=CRANK_R,l=CONROD_L,pin0=pin,cross0=top,origin=mid))
  # Stephenson-type eccentric / double link at one side of each crank.
  ex=x+.65;ey=.18*math.sin(phase+.7);ez=SHAFT_Z+.18*math.cos(phase+.7)
  crank.cylinder((ex,ey,ez),.25,.10,'Brass',16,(1,0,0))
  vl=2.75;vy=.58;vc=ez+math.sqrt(vl*vl-(vy-ey)**2);vpin=(ex,ey,ez);vcross=(ex,vy,vc)
  link=Mesh();link.rod(vpin,vcross,.035,'Steel',8);link.ring(vcross,.12,.028,'Iron',14,5,(1,0,0));link.ring(vpin,.28,.025,'Iron',16,5,(1,0,0))
  vmid=tuple((Vector(vpin)+Vector(vcross))/2);link.emit('ValveLink_'+nm,collection('EngineMoving'),kind='mover',room='E_Engine',origin=vmid,mover='conrod');MOVERS.append(dict(name='ValveLink_'+nm,type='conrod',phase=phase+.7,x=ex,r=.18,l=vl,shaft_z=SHAFT_Z,slider_y=vy,pin0=vpin,cross0=vcross,origin=vmid))
  spindle=Mesh();spindle.box((ex,vy,vc),(.09,.16,.18),'Brass',.015);spindle.rod(vcross,(ex,vy,vc+2.9),.026,'Steel',8)
  spindle.emit('ValveSpindle_'+nm,collection('EngineMoving'),kind='mover',room='E_Engine',origin=vcross,mover='piston');MOVERS.append(dict(name='ValveSpindle_'+nm,type='piston',phase=phase+.7,x=ex,r=.18,l=vl,shaft_z=SHAFT_Z,slider_y=vy,cross_z0=vc,origin=vcross))
  for dx in (-.075,.075):still.box((ex+dx,vy,6.1),(.040,.25,1.0),'Engine',.010)
  # The backplate overlaps the actual guide side faces, including their
  # finite bevel; tangency at y=.705 left both guide bars detached.
  still.box((ex,.815,6.1),(.22,.25,.12),'Engine',.010)
  t=(6.1-1.97)/(7.70-1.97)
  still.rod((ex,.90,6.1),(x+1.05-.45*t,2.40+(spread-2.40)*t,6.1),.040,'Engine',8)
  # Steam chest fitted to the jacket; valves and drain copper tails.
  still.box((x,-rr-.155,8.85),(.62,.34,1.76),'Engine',.04)
  for zz in (8.1,9.7):
   flange(still,(x,-rr-.355,zz),.16,(0,-1,0));still.rod((x,-rr-.355,zz),(x,-rr-.50,zz),.023,'Brass',10);handwheel(still,(x,-rr-.50,zz),.14,(0,1,0),'Red')
  pipe(pipes,nm+'_CondensateDrain',[(x,.35,7.65),(x,.75,7.45),(x,.75,2.7),(x,-2.8,2.7)],.035,'Copper')
 # Working side platforms, holes around rods, proper grated-looking rails.
 for yy in (-4.05,4.05):
  lad_y=yy-math.copysign(.40,yy)
  for za in (4.60,6.80):
   lo,hi=(-26.60,-21.0) if za<5 else (-21.0,-16.10)
   for a,b in [(-26.75,lo),(hi,-9.65)]:
    if b-a>.03:platform.box(((a+b)/2,yy,za),(b-a,1.80,.10),'Iron');proxy(((a+b)/2,yy,za),(b-a,1.80,.10),tag='EnginePlatform')
   # 0.84m outer bypass beside, not through, the ladder well.
   oy=math.copysign(4.53,yy);platform.box(((lo+hi)/2,oy,za),(hi-lo,.84,.10),'Iron');proxy(((lo+hi)/2,oy,za),(hi-lo,.84,.10),tag='EnginePlatform')
   for side in (-1,1):
    y=yy+side*.89;proxy((-18.2,y,za+.52),(17.1,.06,1.0),tag='EnginePlatformGuard');platform.rod((-26.6,y,za+.98),(-9.9,y,za+.98),.028,'Brass',8)
    for xx in np.arange(-26.4,-9.8,1.3):platform.rod((float(xx),y,za),(float(xx),y,za+.98),.021,'Iron',6)
   # Bracketed flat edges are carried by actual floor-founded stanchions.
   # In ladder wells the bracket stops at the narrow OUTER bypass, never
   # across the ladder's head/body envelope.
   for xx in (-25,-18,-11):
    iy=4.18 if lo<xx<hi else 3.24
    platform.rod((xx,math.copysign(4.87,yy),za-.75),(xx,math.copysign(iy,yy),za-.05),.045,'Iron',8)
  for xx in (-25,-18,-11):
   oy=math.copysign(4.87,yy)
   platform.box((xx,oy,1.65),(.28,.18,.10),'Iron',.015)
   platform.rod((xx,oy,1.65),(xx,oy,6.75),.060,'Iron',10)
   proxy((xx,oy,4.20),(.12,.12,5.10),tag='EnginePlatformColumn')
  # Sloping ladders between platforms, clear of the crankshaft.
  for za,zb,xa,xb in [(1.6,4.6,-26.5,-21.1),(4.6,6.8,-20.9,-16.2)]:
   PROXIES.append(dict(kind='ramp',position=((xa+xb)/2,lad_y,(za+zb)/2-.05),size=(math.hypot(xb-xa,zb-za),.76,.10),yaw=0,pitch=-math.atan2(zb-za,xb-xa),tag='EngineLadder'))
   for y in (lad_y-.38,lad_y+.38):platform.rod((xa,y,za),(xb,y,zb),.045,'Iron',6)
   for t in np.linspace(0,1,16):platform.rod((xa+(xb-xa)*t,lad_y-.38,za+(zb-za)*t),(xa+(xb-xa)*t,lad_y+.38,za+(zb-za)*t),.020,'Iron',6)
  # Working fixtures: short caged incandescent lights, not decorative
  # pendants at avatar waist height. Lower lamps mount under the next flat;
  # the upper pair use a supported bracket with >2m clear working height.
  for xx in (-25,-18,-11):
   for zz in (4.55,6.75):
    platform.rod((xx,math.copysign(4.53,yy),zz),(xx,yy,zz),.014,'Iron',7)
    guarded_lamp(platform,xx,yy,zz)
   platform.rod((xx,yy+math.copysign(.87,yy),6.85),(xx,yy+math.copysign(.87,yy),9.25),.016,'Iron',7)
   platform.rod((xx,yy+math.copysign(.87,yy),9.25),(xx,yy,9.25),.016,'Iron',7)
   guarded_lamp(platform,xx,yy,9.25)
 # Steam distribution + serial receivers. Identified endpoints make it
 # possible to audit the plant without guessing what a cylinder represents.
 pipe(pipes,'MainSteam',[(28,4.0,7.05),(3,4.0,7.05),(-8.8,4.,7.05),(-8.8,-2.30,7.05),(-8.8,-2.30,9.25),(-11.5,-.87,9.25)],.16,'Lagging')
 pipe(pipes,'HP_to_IP_Receiver',[(-11.5,.91,8.45),(-11.5,1.45,8.45),(-16,1.45,8.45),(-16,1.30,9.30)],.17,'Lagging')
 pipe(pipes,'IP_to_LP_Receiver',[(-16,1.31,8.30),(-16,2.25,8.30),(-21,2.25,8.30),(-21,1.93,9.2)],.24,'Lagging')
 pipe(pipes,'LP_Exhaust_to_Condenser',[(-21,-1.94,8.35),(-21,-2.70,8.35),(-24.8,-2.70,8.35),(-24.8,-2.70,4.05),(-24.8,-1.85,4.05),(-24.8,-1.85,3.20)],.29,'Iron')
 pipe(pipes,'Condensate_EngineDrainHeader',[(-21,-2.8,2.7),(-10.,-2.8,2.7),(-10.,-2.8,2.05),(-6.,-2.8,2.05),(-6.,3.1,2.05)],.045,'Copper')
 # Accessible, stem-carried main valves: no handwheel rim buried in
 # the HP chest or relied upon as the only pipe contact.
 for (px,py,pz),wy in (((-8.8,-2.3,8.9),-2.70),((-11.5,-1.15,9.25),-1.62)):
  still.lathe((px,py,pz),[(0,.075),(-.17,.075),(-.25,.035)],'Brass',14,(0,1,0))
  still.rod((px,py,pz),(px,wy,pz),.026,'Brass',10)
  handwheel(still,(px,wy,pz),.25,(0,1,0),'Red')
 gauge(still,(-10.6,-3.10,3.10),.17,(1,0,0));gauge(still,(-10.6,-3.50,3.10),.13,(1,0,0),.25)
 still.box((-10.70,-3.3,2.48),(.19,.92,1.43),'Engine',.025)
 still.box((-10.70,-3.3,1.63),(.34,1.10,.06),'Engine',.012)
 for yy in (-3.65,-2.95):still.rod((-10.70,yy,1.63),(-10.70,yy,1.80),.025,'Iron',10)
 still.emit('Engine_Bed_Standards_Cylinders',collection('Engine'),kind='engine',deck='machinery',room='E_Engine')
 platform.emit('Engine_Working_Levels',collection('Engine'),kind='platform',deck='machinery',room='E_Engine')
 crank.emit('Crankshaft_3Throws',collection('EngineMoving'),kind='mover',origin=(-18,0,SHAFT_Z),mover='shaft');MOVERS.append(dict(name='Crankshaft_3Throws',type='shaft',origin=(-18,0,SHAFT_Z)))
 pipes.emit('Engine_Steam_Receivers',collection('PlantPipes'),kind='pipe',room='E_Engine')


def auxiliaries():
 m=Mesh();p=Mesh()
 # Surface condenser horizontally alongside the LP crank, with water boxes
 # and an identifiable exhaust entry at x=-24.8,y=-1.85,z=3.2. It sits
 # INSIDE the protected core, not in the adjacent maintenance stair flight.
 m.cylinder((-24.8,-1.85,2.75),.65,2.15,'Copper',24,(1,0,0),tag='SurfaceCondenser')
 # Two floor-founded curved saddles support the actual condenser shell;
 # steam/water pipe contact is not a substitute for a foundation.
 for xx in (-25.45,-24.15):
  m.box((xx,-1.85,1.63),(.44,1.28,.06),'Engine',.012)
  top=[(dy,2.75-math.sqrt(.65**2-dy**2)+.015) for dy in (-.56,-.42,-.28,-.14,0,.14,.28,.42,.56)]
  profile=[(-.56,1.65),(.56,1.65)]+list(reversed(top));nn=len(profile)
  vv=[(xx+dx,-1.85+dy,zz) for dx in (-.16,.16) for dy,zz in profile]
  ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)]
  m.add(vv,ff,'Engine')
  for sy in (-.57,.57):m.cylinder((xx,-1.85+sy,1.6661),.018,.0126,'Steel',6)
 for xx in (-25.92,-23.68):flange(m,(xx,-1.85,2.75),.74,(1,0,0),'Iron',16)
 proxy((-24.8,-1.85,2.75),(2.35,1.50,1.45),tag='Condenser')
 pipe(p,'Sea_Intake_to_CirculatingPump',[(-6.0,hb(-6,2.0),2.0),(-6,4.8,2.0),(-6,4.8,2.55),(-6,4.48,2.55)],.18,'Iron')
 pipe(p,'Sea_Pump_to_Condenser',[(-6.36,4.2,2.60),(-7.6,4.2,2.60),(-7.6,4.2,2.1),(-25.9,4.2,2.1),(-25.9,-1.85,2.75)],.16,'Iron')
 pipe(p,'Sea_Condenser_to_Overboard',[(-23.65,-1.85,2.75),(-23.65,-4.6,2.75),(-9,-4.6,2.75),(-6,-hb(-6,2.8),2.8)],.16,'Iron')
 pipe(p,'Condensate_to_Hotwell',[(-24.8,-1.85,2.1),(-24.8,-3.7,1.95),(-6.,-3.7,1.95),(-6.,3.1,1.95)],.07,'Copper')
 # Riveted hotwell: lid seam, bolted inspection manhole, level tube and
 # low suction outlet make this a tank assembly, not a bare labeled box.
 m.box((-6.,3.1,2.11),(1.5,1.0,1.02),'Iron',.035);proxy((-6.,3.1,2.12),(1.60,1.10,1.12),tag='Hotwell')
 m.box((-6.,3.1,2.6473),(1.58,1.08,.055),'Iron',.018)
 m.cylinder((-6.,3.1,2.695),.27,.045,'Iron',20);bolts(m,(-6.,3.1,2.7215),.23,10,(0,0,1),.012)
 for xx in (-6.61,-5.39):
  for yy in (2.68,3.52):m.cylinder((xx,yy,2.6871),.016,.025,'Steel',8)
 for zz in (1.88,2.46):
  m.rod((-6.43,2.60,zz),(-6.43,2.48,zz),.018,'Copper',7);handwheel(m,(-6.43,2.453,zz),.055,(0,-1,0),'Brass')
 m.cylinder((-6.43,2.48,2.17),.022,.58,'Steel',9)
 m.box((-5.88,2.5877,2.30),(.42,.025,.20),'Brass',.008)
 pipe(p,'Hotwell_SuctionHeader',[(-6.,3.60,1.95),(-6.,3.77,1.95),(-7.5,3.77,1.95)],.065,'Copper')
 pipe(p,'Hotwell_SuctionHeader_Forward',[(-6.,3.77,1.95),(-4.8,3.77,1.95)],.065,'Copper')
 # Distinct circulating pump at the named sea-main endpoint, not an empty
 # space labelled 'pump'. Volute, flanges, drive cylinder and base align.
 m.box((-6.,4.2,1.775),(1.35,.95,.35),'Engine',.025)
 m.cylinder((-6.,4.2,2.55),.40,.50,'Iron',20,(0,1,0),tag='CirculatingPump')
 # Cast volute foot lands on the common base; the steam driver's thin
 # support rods and water mains must not be its only load path.
 m.box((-6.,4.2,2.05),(.44,.46,.24),'Engine',.018)
 flange(m,(-6.,3.92,2.55),.28,(0,1,0));flange(m,(-6.,4.48,2.55),.28,(0,1,0))
 # Vertical steam driver acts through a short crank/flywheel on the pump
 # spindle. Its cylinder is not an unrelated offset stack beside the volute.
 m.cylinder((-6.,3.77,3.53),.18,.70,'Engine',18)
 for zz in (3.16,3.90):flange(m,(-6.,3.77,zz),.21,(0,0,1),count=8)
 m.cylinder((-6.,3.86,2.55),.08,.30,'Steel',14,(0,1,0))
 m.ring((-6.,3.77,2.55),.32,.03,'Iron',24,6,(0,1,0))
 for a in np.linspace(0,math.tau,6,endpoint=False):m.rod((-6.,3.77,2.55),(-6.+.30*math.cos(float(a)),3.77,2.55+.30*math.sin(float(a))),.020,'Engine',8)
 m.rod((-6.,3.77,2.55),(-5.92,3.77,2.72),.045,'Iron',8)
 m.rod((-5.92,3.77,2.72),(-6.,3.77,3.04),.024,'Steel',9);m.rod((-6.,3.77,3.04),(-6.,3.77,3.45),.022,'Steel',9)
 for dx in (-.29,.29):
  m.rod((-6.+dx,4.08,1.95),(-6.+dx,4.08,3.18),.030,'Engine',8)
  m.rod((-6.+dx,4.08,3.18),(-6.+dx*.5,3.77,3.18),.030,'Engine',8)
 proxy((-5.95,4.10,2.80),(1.50,1.20,2.40),tag='CirculatingPump')
 pipe(p,'Auxiliary_Steam_ReducingMain',[(-8.8,-2.30,8.9),(-8.8,-2.65,8.9),(-8.8,-2.65,4.15)],.055,'Lagging')
 pipe(p,'FeedAndCirculating_SteamHeader',[(-8.8,-2.65,4.15),(-8.8,4.15,4.15),(-4.8,4.15,4.15)],.045,'Lagging')
 for px in (-7.5,-4.8):pipe(p,'FeedPump_Steam_'+str(px),[(px,4.15,4.15),(px,4.15,2.95)],.035,'Lagging')
 pipe(p,'CirculatingPump_Steam',[(-6.,4.15,4.15),(-6.,3.77,4.15),(-6.,3.77,3.70)],.035,'Lagging')
 pipe(p,'CirculatingPump_Exhaust',[(-6.,3.95,3.53),(-6.7,3.95,3.53),(-6.7,3.95,2.30),(-6.,3.10,2.30)],.035,'Copper')
 pipe(p,'Steering_Steam_Branch',[(-8.8,-2.65,4.15),(-10.6,-2.65,4.15),(-10.6,1.15,4.5)],.045,'Lagging')
 for xx in (-7.5,-4.8):
  proxy((xx,4.15,2.38),(.68,.90,1.56),tag='FeedPump')
  m.box((xx,4.15,1.685),(.65,.75,.17),'Engine',.025)
  # Separate lower water barrel and upper steam cylinder, with a real
  # open crosshead/rod bay between them. Static auxiliary pose is explicit.
  m.lathe((xx,4.15,0),[(1.77,.23),(1.81,.26),(1.86,.19),(2.08,.19),(2.13,.26),(2.18,.26)],'Engine',18,tag='ReciprocatingFeedPump')
  m.lathe((xx,4.15,0),[(2.69,.27),(2.74,.27),(2.78,.23),(3.03,.23),(3.08,.27),(3.13,.27)],'Engine',18)
  for zz,direction in ((2.18435,1),(2.68565,-1),(3.13435,1)):
   bolts(m,(xx,4.15,zz),.22,8,(0,0,direction),.013)
  for dx in (-.25,.25):m.rod((xx+dx,4.15,2.12),(xx+dx,4.15,2.74),.027,'Steel',8)
  m.cylinder((xx,4.15,2.45),.045,.66,'Steel',12);m.box((xx,4.15,2.43),(.45,.16,.12),'Brass',.012)
  m.box((xx,4.40,2.91),(.22,.13,.31),'Engine',.015)
  m.rod((xx,4.15,2.87),(xx,3.75,2.87),.023,'Copper',8);handwheel(m,(xx,3.75,2.87),.14,(0,1,0),'Red')
  pipe(p,'FeedPump_Suction_'+str(xx),[(xx,3.77,1.95),(xx,3.98,1.95)],.05,'Copper')
  pipe(p,'FeedPump_Discharge_'+str(xx),[(xx,4.33,2.02),(xx,4.55,2.02)],.045,'Copper')
  m.lathe((xx,4.52,2.02),[(-.055,.055),(0,.085),(.08,.065)],'Brass',12,(0,1,0),tag='FeedCheckValve')
  pipe(p,'FeedPump_Exhaust_'+str(xx),[(xx,4.39,2.91),(xx,4.62,2.91),(xx,4.62,2.30)],.03,'Copper')
 pipe(p,'FeedPump_ExhaustHeader',[(-7.5,4.62,2.30),(-4.8,4.62,2.30)],.04,'Copper')
 pipe(p,'FeedPump_ExhaustReturn',[(-6.,4.62,2.30),(-6.,3.10,2.30)],.04,'Copper')
 pipe(p,'FeedPump_to_BoilerMain',[(-7.5,4.55,2.02),(-3.5,4.55,2.02),(-3.5,7.0,2.4),(25.75,7.0,2.4)],.075,'Copper')
 # Two direct steam-driven early electrical dynamos, not modern sealed
 # alternators. Segmented commutators/brushes, field coils and open driver
 # linkage remain modeled even in GAME; no electricity/animation is claimed.
 for xx in (-7.8,-4.9):
  proxy((xx,-4.05,2.80),(2.20,1.20,2.45),tag='Dynamo')
  proxy((xx,-4.84,3.03),(1.46,.42,2.8),tag='Switchboard')
  m.box((xx,-4.05,1.775),(2.10,1.0,.35),'Engine',.025)
  for dx in (-.85,.85):
   for sy in (-.35,.35):bolts(m,(xx+dx,-4.05+sy,1.9547),.06,4,(0,0,1),.014)
  m.cylinder((xx,-4.05,2.4),.35,1.16,'Iron',24,(1,0,0),tag='ElectricDynamo')
  for dx in (-.52,.52):
   m.ring((xx+dx,-4.05,2.4),.365,.035,'Engine',24,6,(1,0,0))
   m.box((xx+dx,-4.05,2.10),(.19,.52,.30),'Engine',.025)
  # A real common spindle connects commutator, rotor and flywheel.
  m.rod((xx-1.04,-4.05,2.4),(xx+.98,-4.05,2.4),.075,'Steel',16)
  # Copper turns wrap the two field pole cores, visibly distinct from shaft.
  for side in (-1,1):
   yy=-4.05+side*.34;m.box((xx,yy,2.40),(.47,.20,.66),'Engine',.035)
   for zz in np.linspace(2.16,2.64,8):
    pts=[(xx+.27*math.cos(float(a)),yy+.135*math.sin(float(a)),float(zz)) for a in np.linspace(0,math.tau,17)]
    m.tube(pts,.012,'Copper',6,tag='DynamoFieldWinding')
  # Insulating drum, individual axial copper segments, two carbon brushes.
  m.cylinder((xx-.82,-4.05,2.4),.18,.40,'Black',24,(1,0,0))
  for a in np.linspace(0,math.tau,24,endpoint=False):
   yy=-4.05+.184*math.cos(float(a));zz=2.4+.184*math.sin(float(a));m.rod((xx-1.01,yy,zz),(xx-.63,yy,zz),.013,'Copper',5)
  for side in (-1,1):
   yy=-4.05+side*.205;m.box((xx-.82,yy,2.4),(.13,.07,.11),'Black',.010)
   m.rod((xx-.82,yy,2.4),(xx-.82,yy+side*.10,2.4),.025,'Brass',8)
   m.tube([(xx-.82,yy+side*.10,2.4),(xx-.82,yy+side*.10,2.85),(xx-.65,-4.69,2.85),(xx-.65,-4.69,3.16)],.013,'Black',7,tag='DynamoInsulatedLead')
  m.lathe((xx+.82,-4.05,0),[(3.28,.18),(3.36,.21),(3.91,.21),(3.99,.18)],'Engine',18,tag='DynamoSteamDriver')
  for zz,direction in ((3.276,-1),(3.994,1)):
   bolts(m,(xx+.82,-4.05,zz),.16,8,(0,0,direction),.012)
  for sy in (-1,1):m.rod((xx+.82,-4.05+sy*.25,1.95),(xx+.82,-4.05+sy*.18,3.30),.035,'Engine',8)
  pipe(p,'Dynamo_Steam_'+str(xx),[(-8.8,-2.65,4.15),(xx+.82,-2.65,4.15),(xx+.82,-4.05,4.15),(xx+.82,-4.05,3.75)],.035,'Lagging')
  pipe(p,'Dynamo_Exhaust_'+str(xx),[(xx+.82,-4.25,3.50),(xx+.82,-4.4,2.12),(-24.8,-4.4,2.12),(-24.8,-1.85,2.12)],.045,'Copper')
  # Spoked flywheel and offset crank pin connect visibly to the crosshead.
  m.ring((xx+.70,-4.05,2.4),.40,.030,'Iron',28,6,(1,0,0))
  for a in np.linspace(0,math.tau,6,endpoint=False):m.rod((xx+.70,-4.05,2.4),(xx+.70,-4.05+.38*math.cos(float(a)),2.4+.38*math.sin(float(a))),.027,'Engine',8)
  m.cylinder((xx+.82,-4.05,2.4),.16,.25,'Steel',18,(1,0,0))
  m.rod((xx+.92,-4.05,2.4),(xx+.92,-3.95,2.56),.065,'Iron',10)
  m.cylinder((xx+.92,-3.95,2.56),.055,.12,'Brass',12,(1,0,0))
  m.rod((xx+.92,-3.95,2.56),(xx+.92,-4.05,3.08),.028,'Steel',10)
  m.box((xx+.92,-4.05,3.08),(.13,.28,.13),'Brass',.012);m.rod((xx+.92,-4.05,3.08),(xx+.92,-4.05,3.62),.024,'Steel',10)
  # Slate instruments and knife switches face INBOARD into working aisle,
  # elevated above the machines. Braced floor posts support the board.
  m.box((xx,-4.84,3.58),(1.42,.13,1.45),'Black',.020)
  for dx in (-.62,.62):
   m.cylinder((xx+dx,-4.88,1.63),.055,.06,'Iron',12)
   m.rod((xx+dx,-4.88,1.63),(xx+dx,-4.88,4.28),.028,'Iron',8)
  for dx in (-.35,.35):gauge(m,(xx+dx,-4.745,3.96),.13,(0,1,0),.5)
  for dx in (-.42,0,.42):
   for zz in (3.12,3.48):
    m.cylinder((xx+dx,-4.7425,zz),.040,.08,'Porcelain',10,(0,1,0))
    m.rod((xx+dx,-4.725,zz),(xx+dx,-4.64,zz),.020,'Copper',8)
   m.box((xx+dx,-4.635,3.48),(.060,.040,.075),'Copper',.006)
   m.rod((xx+dx,-4.64,3.12),(xx+dx,-4.47,3.45),.016,'Copper',7);m.cylinder((xx+dx,-4.46,3.46),.027,.13,'Black',10,(1,0,0))
 # Workshop vice, bench and tool hooks, mounted clear of walkways.
 from period_detail import utility_table
 m.append(utility_table(1.6,.42,.81,'Iron'),(-9.15,-4.1,1.60),math.pi/2);m.box((-9.15,-4.0,2.50),(.24,.35,.18),'Iron',.02);m.cylinder((-9.15,-4.0,2.64),.04,.25,'Steel',8,(1,0,0))
 for dx in (-.10,.10):m.box((-9.15+dx,-4.0,2.63),(.065,.35,.12),'Iron',.008)
 proxy((-9.15,-4.1,2.15),(.42,1.65,1.1),tag='DynamoWorkbench')
 for xx in (-8,-5):
  for yy in (-4.0,4.0):
   m.rod((xx,yy,5.0),(xx,yy,5.13),.014,'Iron',7);guarded_lamp(m,xx,yy,5.0)
 m.emit('Condenser_Pumps_Dynamos_Workshop',collection('Auxiliaries'),kind='auxiliary',deck='machinery');p.emit('Feed_Sea_Condensate_Mains',collection('PlantPipes'),kind='pipe',deck='machinery')


def stern():
 shaft=Mesh();still=Mesh();prop=Mesh();rudder=Mesh()
 # A real steel shaft-alley enclosure, clear of the lower crew wing rooms.
 # The orlop deck has a full-width opening here; it must not cross the aisle.
 alley_case=Mesh()
 for yy in (-1.5,1.5):
  alley_case.box((-49.1,yy,3.15),(41.8,.045,3.10),'Ivory');proxy((-49.1,yy,3.15),(41.8,.045,3.10),tag='AlleyWall')
 alley_case.box((-49.1,0,4.70),(41.8,3.045,.045),'Iron');proxy((-49.1,0,4.70),(41.8,3.045,.045),tag='AlleyRoof')
 # Aft seal wall with a shaft-sized aperture, not a sheet through the shaft.
 for yy in (-1.,1.):alley_case.box((-70,yy,3.15),(.045,1.,3.10),'Iron')
 for zz,hh in [(2.05,.90),(4.05,1.30)]:alley_case.box((-70,0,zz),(.045,1.,hh),'Iron')
 alley_case.emit('Watertight_ShaftAlley_Enclosure',collection('ShaftAlley'),kind='wall',deck='machinery',room='E_Alley')
 proxy((-50,0,3.0),(44,1.20,1.08),tag='GuardedShaft')
 a,b=-78.08,-26.9;shaft.cylinder(((a+b)/2,0,SHAFT_Z),.28,b-a,'Steel',24,(1,0,0))
 # The aftmost coupling belongs in the accessible alley, never inside
 # the narrow bored stern tube. The tube itself carries its aft journal.
 for x in np.arange(-67,-28,5.0):
  shaft.cylinder((float(x),0,SHAFT_Z),.41,.14,'Iron',20,(1,0,0));bolts(shaft,(float(x)-.075,0,SHAFT_Z),.345,10,(-1,0,0),.023)
  still.box((float(x)+.9,0,2.12),(.75,1.10,1.04),'Engine',.04)
  still.lathe((float(x)+.9,0,SHAFT_Z),[(-.30,.38),(.30,.38),(.30,.286),(-.30,.286)],'Brass',48,(1,0,0),caps=False,closed=True)
  still.lathe((float(x)+.9,0,SHAFT_Z),[(-.15,.43),(.15,.43),(.15,.375),(-.15,.375)],'Engine',32,(1,0,0),caps=False,closed=True)
 # Ten rotating thrust collars fit BETWEEN the actual end carriers.
 # Separate bored stationary shoes transmit their thrust to the cheeks;
 # neither a solid carrier through a collar nor unsupported rings in air.
 thrust_xs=[-28.56+i*.16 for i in range(10)]
 for x in thrust_xs:shaft.cylinder((x,0,SHAFT_Z),.43,.08,'Steel',20,(1,0,0))
 # Open thrust-collar bay: floor-founded sole, side cheeks and two bored
 # end carriers. Do not enclose all rotating collars in a solid cuboid.
 still.box((-27.8,0,1.80),(2.2,1.50,.40),'Engine',.040)
 for yy in (-.58,.58):still.box((-27.8,yy,2.55),(2.2,.20,1.10),'Engine',.025)
 for xx in (-28.78,-26.98):
  still.box((xx,0,2.25),(.20,.90,.54),'Engine',.020)
  still.lathe((xx,0,SHAFT_Z),[(-.07,.52),(.07,.52),(.07,.286),(-.07,.286)],'Brass',48,(1,0,0),caps=False,closed=True)
 for x in thrust_xs[:-1]:
  still.lathe((x+.08,0,SHAFT_Z),[(-.03,.52),(.03,.52),(.03,.29),(-.03,.29)],'Brass',48,(1,0,0),caps=False,closed=True)
 tubev=[];tubef=[]
 for xx,rr in [(-76.55,.44),(-70.7,.44),(-70.7,.305),(-76.55,.305)]:
  for j in range(24):a=j*math.tau/24;tubev.append((xx,rr*math.cos(a),SHAFT_Z+rr*math.sin(a)))
 for k in range(4):
  for j in range(24):tubef.append((k*24+j,k*24+(j+1)%24,((k+1)%4)*24+(j+1)%24,((k+1)%4)*24+j))
 still.add(tubev,tubef,'Iron',True);flange(still,(-70.68,0,SHAFT_Z),.54,(1,0,0),count=14,bore=.305);flange(still,(-76.56,0,SHAFT_Z),.52,(1,0,0),count=14,bore=.305)
 # Thick, twisted blade sections. Pitch is reflected by local helix angle.
 for k in range(4):
  base=k*math.tau/4;vv=[];ff=[];sections=[(.43,.30),(.78,.66),(1.25,1.02),(1.85,1.12),(2.35,.78),(2.65,.12)]
  for r,chord in sections:
   beta=math.atan(PROP_PITCH/(math.tau*r));sweep=.32*(r/PROP_R)**2;theta=base+sweep
   for j in range(12):
    u=math.cos(j*math.tau/12)*.5;th=.055*math.sin(j*math.tau/12)*(1-r/3.4)
    axial=u*chord*math.sin(beta)+th*math.cos(beta);tangent=u*chord*math.cos(beta)-th*math.sin(beta)
    vv.append((PROP_X+axial,r*math.sin(theta)+tangent*math.cos(theta),SHAFT_Z+r*math.cos(theta)-tangent*math.sin(theta)))
  for i in range(len(sections)-1):
   for j in range(12):a=i*12+j;b=i*12+(j+1)%12;ff.append((a,b,b+12,a+12))
  ff.extend([tuple(range(11,-1,-1)),tuple((len(sections)-1)*12+j for j in range(12))]);prop.add(vv,ff,'Brass',True,tag='PitchedPropellerBlade')
 prop.lathe((PROP_X,0,SHAFT_Z),[(-.58,.15),(-.45,.33),(-.25,.46),(.3,.46),(.5,.34)],'Brass',32,(1,0,0));bolts(prop,(PROP_X+.5082,0,SHAFT_Z),.29,12,(1,0,0),.024)
 shaft.emit('Tailshaft_And_Couplings',collection('EngineMoving'),kind='mover',origin=(-50,0,SHAFT_Z),mover='shaft');MOVERS.append(dict(name='Tailshaft_And_Couplings',type='shaft',origin=(-50,0,SHAFT_Z)))
 prop.emit('Propeller_4Blade',collection('EngineMoving'),kind='mover',origin=(PROP_X,0,SHAFT_Z),mover='shaft');MOVERS.append(dict(name='Propeller_4Blade',type='shaft',origin=(PROP_X,0,SHAFT_Z)))
 # Raked steel plate rudder, real thickness, separate pivot/stock.
 outline=[(-79.56,.60),(-82.1,.70),(-82.4,2.7),(-81.95,5.75),(-79.56,6.20)]
 vv=[(x,y,z) for y in (-.09,.09) for x,z in outline];n=len(outline);ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)];rudder.add(vv,ff,'Hull')
 rudder.cylinder((RUDDER_X,0,6.675),.12,12.25,'Iron',16)
 for zz in (1.1,2.7,4.3,5.9,8.1):
  if zz+.055<max(p[1] for p in outline):
   # Each rib remains inside BOTH edges of the raked blade at its full
   # finite height. No 8.1m ribs above the blade, no protruding upper ends.
   sections=[]
   for zedge in (zz-.055,zz+.055):
    xs=[a[0]+(b[0]-a[0])*(zedge-a[1])/(b[1]-a[1]) for a,b in zip(outline,outline[1:]+outline[:1]) if min(a[1],b[1])<=zedge<=max(a[1],b[1]) and abs(b[1]-a[1])>1e-9]
    sections.append((min(xs),max(xs)))
   xa=max(v[0] for v in sections)+.025;xb=min(v[1] for v in sections)-.025
   for side in (-1,1):rudder.box(((xa+xb)/2,side*.106,zz),(xb-xa,.04,.11),'Iron',.010)
  still.ring((RUDDER_X,0,zz),.17,.045,'Brass',16,6);still.rod((-79.20,0,zz),(RUDDER_X,0,zz),.10,'Iron',8)
 rudder.emit('Rudder_Stock_Blade',collection('Steering'),kind='mover',origin=(RUDDER_X,0,3.4),mover='rudder');MOVERS.append(dict(name='Rudder_Stock_Blade',type='rudder',origin=(RUDDER_X,0,3.4)))
 # Heel bearing ties the stock foot to the connected stern shoe.
 still.box((RUDDER_X,0,.29),(.60,.48,.06),'Iron',.015)
 still.cylinder((RUDDER_X,0,.43),.22,.32,'Brass',18)
 still.emit('Shaft_Bearings_SternTube_Pintles',collection('ShaftAlley'),kind='shaft_support',deck='machinery',room='E_Alley')
 # Enclosed steam steering house at saloon height. No claim that this is
 # Teutonic's literal arrangement; Aurelian's counter demands this level.
 from interiors import surfaces,ROOM_REPORT
 r=next(r for r in ROOMS if r['id']=='S_Steering');surfaces(r);m=Mesh();q=Mesh();z=r['z']+.06
 # Sector quadrant extends forward from stock (not through the aft wall).
 pts=[]
 for a in np.linspace(-1.15,1.15,28):pts.append((RUDDER_X+.93*math.cos(float(a)),.93*math.sin(float(a)),12.50))
 q.tube(pts,.075,'Iron',8)
 for a in (-1.0,-.5,0,.5,1.0):q.rod((RUDDER_X,0,12.5),(RUDDER_X+.93*math.cos(a),.93*math.sin(a),12.5),.055,'Iron',7)
 for side in (-1,1):
  from visual_design import finished_floor
  low=finished_floor(r)-.0002;top=z+.575
  m.box((-76.5,side*.72,(low+top)/2),(1.35,.60,top-low),'Engine',.03);m.cylinder((-76.5,side*.72,z+.74),.22,.77,'Engine',16,(1,0,0));m.rod((-76.80,side*.72,z+.74),(-78.8,side*.72,12.50),.055,'Steel',10)
  m.rod((-76.2,side*.72,z+.88),(-76.2,side*.72,z+1.05),.050,'Brass',12)
  m.rod((-76.2,side*.72,z+1.05),(-75.85,side*.72,z+1.05),.023,'Brass',10)
  handwheel(m,(-75.85,side*.72,z+1.05),.19,(1,0,0),'Brass')
 m.rod((-78.5,-1.1,12.50),(-78.5,1.1,12.50),.12,'Steel',14)
 pipe(m,'Steering_SteamSupply',[(-74.7,.9,12.6),(-76.5,.9,12.6),(-76.5,-.9,12.6)],.045,'Lagging')
 # Forged bored boss fastens quadrant and emergency tiller to the stock.
 # The wooden root seats in the forward wall, not through the stock bore;
 # stock/boss axes and both rudder mover pivots remain unchanged.
 q.lathe((RUDDER_X,0,12.5),[(-.12,.19),(.40,.19),(.40,.124),(-.12,.124)],'Iron',20,caps=False,closed=True)
 q.rod((RUDDER_X+.14,0,12.8),(-77.1,0,12.8),.065,'Oak',10)
 q.emit('Steering_Quadrant_Tiller',collection('Steering'),kind='mover',deck='saloon',room='S_Steering',origin=(RUDDER_X,0,12.5),mover='rudder')
 MOVERS.append(dict(name='Steering_Quadrant_Tiller',type='rudder',origin=(RUDDER_X,0,12.5)))
 pipe(m,'Steering_Exhaust_Return',[(-76.5,-.95,12.15),(-74.5,-1.15,12.15),(-74.5,-1.15,4.2),(-6,-1.15,4.2),(-6,3.1,2.3)],.04,'Copper')
 from period_detail import ceiling_fixture
 ceiling_fixture(m,r,-77.1,0,'marine');obs=m.emit('Steam_Steering_And_HandTiller',collection('Steering'),kind='steering',deck='saloon',room='S_Steering')
 ROOM_REPORT.append(dict(id='S_Steering',name=r['name'],deck='saloon',kind='steering',bounds=rect(r),z=r['z'],top=r['top'],floor_area_m2=round((r['x1']-r['x0'])*(r['y1']-r['y0']),2),triangles=sum(len(o.data.loop_triangles) for o in obs),inventory='Steam steering engines, connected worm shaft/quadrant, rudder stock/pintles and emergency hand tiller.',components=dict(m.tags)))
 # Shaft alley lamps/guard rails and the final steam service run aft.
 alley=Mesh()
 for side in (-1,1):
  alley.rod((-69.2,side*.57,3.52),(-28.8,side*.57,3.52),.022,'Iron',8)
  for x in np.arange(-68,-28,2.5):
   alley.cylinder((float(x),side*.57,1.615),.040,.030,'Iron',10)
   alley.rod((float(x),side*.57,1.615),(float(x),side*.57,3.52),.020,'Iron',7)
 for x in np.arange(-68,-29,5):
  guarded_lamp(alley,float(x),1.07,4.6775)
 pipe(alley,'Steering_SteamMain',[(-10.6,1.15,4.5),(-70.5,1.15,4.5),(-74.7,.9,4.5),(-74.7,.9,12.6)],.045,'Lagging')
 alley.emit('ShaftAlley_Lamps_ServiceSteam',collection('ShaftAlley'),kind='equipment',deck='machinery',room='E_Alley')


def build():
 boilers();engine();auxiliaries();stern()
 from plant_detail import build as detail_build
 detail_build()
