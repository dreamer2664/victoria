"""Room-derived structure and furnishing. All physical compartments receive
new meshes and an inventory. Counts refer to built objects, not nominal berths.
"""
import math,json
from collections import Counter
import numpy as np
from mathutils import Vector
from meshkit import *
from furnishings import *
from service_fittings import chart_table,mail_cubby,drinks_rack,ice_chest,cargo_crate,staved_barrel,medicine_cabinet,barber_chair,iron_safe,medical_trolley,provision_rack,folded_deckchair
from structure import deck_holes
from visual_design import finished_floor,design,ceiling_holes,ceiling_beams,is_external_window,washstand_stations,clipped_finish_cells
from period_detail import ceiling_fixture,cabin_accessories,recolour,utility_table,plain_bench,framed_panel,wall_clock,tea_tray,book_stack
import public_rooms
from shipdesign.leonidas_ii import ROOMS,DECKS,DECK_TOPS,STAIRS,CASINGS,hb,rect,overlap
ROOM_REPORT=[];DOORS=[];CURRENT_ROOM=None

def door(m,r,wall,u,w,h=2.10,external=False):
 z=finished_floor(r);d=design(r);horizontal=wall[0]=='y';x=u if horizontal else r[wall];y=r[wall] if horizontal else u
 # Hinge at negative local X end; local door lies along X, +Y normal.
 ang=0 if horizontal else math.pi/2;hx=x-w/2 if horizontal else x;hy=y if horizontal else y-w/2
 # The pivot/knuckles must sit OUTSIDE the 150mm-deep door casing.
 # A 35mm offset left the moving knuckle embedded in the own wall/jamb.
 swing=92 if wall in ('y0','x1') else -92;hinge_offset=math.copysign(.100,swing)
 pivot=(hx-math.sin(ang)*hinge_offset,hy+math.cos(ang)*hinge_offset,z)
 leaf=Mesh();leaf.box((w/2,0,h/2),(w-.045,.055,h-.035),d['wood'],.008)
 for zz,hh in [(.52,.70),(1.45,.82)]:
  leaf.box((w/2,-.034,zz),(w-.19,.028,hh),d['panel'],.012)
  leaf.box((w/2,.034,zz),(w-.19,.028,hh),d['panel'],.012)
 for zz in (.20,1.70):
  # The real pivot is on the opening-side face, not through the middle
  # of the timber thickness. A bored middle knuckle and attached leaf
  # plate rotate around two stationary end knuckles/pin.
  leaf.lathe((0,hinge_offset,zz),[(-.025,.018),(.025,.018),(.025,.0095),(-.025,.0095)],'Brass',12,caps=False,closed=True)
  # Cranked strap reaches the original timber leaf AND the outboard
  # hinge barrel; moving the pivot alone would leave this plate floating.
  leaf.box((.0475,hinge_offset*.55,zz),(.070,.100,.040),'Brass',.002)
  hinge=Mesh()
  for dz in (-.0475,.0475):
   hinge.lathe((0,hinge_offset,zz+dz),[(-.0175,.018),(.0175,.018),(.0175,.0095),(-.0175,.0095)],'Brass',12,caps=False,closed=True)
   hinge.box((-.035,hinge_offset*.55,zz+dz),(.05,.100,.035),'Brass',.002)
  hinge.cylinder((0,hinge_offset,zz),.0075,.15,'Steel',10)
  hinge.cylinder((0,hinge_offset,zz+.0728),.012,.016,'Steel',10)
  m.append(hinge,(hx,hy,z),ang)
 for side in (-1,1):
  leaf.cylinder((w-.12,side*.058,1.02),.027,.05,'Brass',10,(0,1,0));leaf.rod((w-.12,side*.08,1.02),(w-.23,side*.08,1.02),.012,'Brass',7)
 world=Mesh();world.append(leaf,(hx,hy,z),ang)
 name='Door_'+r['id'];world.emit(name,collection('Doors'),kind='door',deck=r['deck'],room=r['id'],origin=pivot,mover='door')
 DOORS.append(dict(id=r['id'],name=name,hinge=pivot,yaw=ang,width=w,height=h,angle_deg=swing,watertight=False))
 # Doorframe carried by static walls, not by animated leaf.
 for du in (-w/2-.045,w/2+.045):
  c=(x+du,y,z+h/2) if horizontal else (x,y+du,z+h/2);s=(.07,.15,h+.05) if horizontal else (.15,.07,h+.05);m.box(c,s,d['wood'],.007)
 c=(x,y,z+h+.025);s=(w+.16,.15,.08) if horizontal else (.15,w+.16,.08);m.box(c,s,d['wood'],.007)
 return (x,y,z)

def wall_mesh(m,r,wall,windows=True):
 scheme=design(r);horizontal=wall[0]=='y';u0,u1=(r['x0'],r['x1']) if horizontal else (r['y0'],r['y1']);fixed=r[wall];z0=r['z']+.025;z1=r['top'];holes=[]
 if r['id']=='M_Entrance' and wall=='y1':holes.append((r['door_u']-.8,r['door_u']+.8,z0,z0+2.10,'opening'))
 # End-to-end third-class circulation avoids 0.3-0.4m inaccessible gaps.
 if r['kind'].startswith('dorm') or r['kind'] in ('third_wash','cold_store'):
  if wall in ('x0','x1') and wall!=r['door_wall']:
   mid=(r['y0']+r['y1'])/2;holes.append((mid-.65,mid+.65,z0,z0+2.15,'opening'))
 # Door height is based on its ACTUAL finished floor, not wall-bottom
 # z0: their 22.5mm datum difference put the header through every leaf.
 if wall==r['door_wall']:holes.append((r['door_u']-r['door_width']/2,r['door_u']+r['door_width']/2,z0,finished_floor(r)+2.10,'door'))
 # Second exits in large rooms make a real fore-and-aft passenger route.
 if r['kind'] in ('dining','library','music','smoking','writing','dining_second','lounge_second','stairhall') and wall in ('x0','x1'):
  for yy in (-min(3.35,(r['y1']-r['y0'])/2- .75),min(3.35,(r['y1']-r['y0'])/2-.75)):
   if not any(a-.4<yy<b+.4 for a,b,*_ in holes):holes.append((yy-.65,yy+.65,z0,z0+2.16,'opening'))
 above=r['z']>=11.75;kind=r['kind']
 haswin=above and horizontal and kind not in ('store','mail','bath','wc') and (not kind.startswith('cabin') or wall!=r['door_wall'])
 if kind=='wheelhouse':haswin=wall!='x0'
 if haswin and windows:
  step=1.65 if kind in ('wheelhouse','library','dining') else 1.8
  for u in np.arange(u0+.9,u1-.5,step):
   ww=.95 if kind!='wheelhouse' else 1.22
   if not is_external_window(r,wall,float(u)):continue
   if kind=='barber' and abs(float(u)-(r['x0']+r['x1'])/2)>.65:continue
   if any(not(u+ww/2<a-.18 or u-ww/2>b+.18) for a,b,*_ in holes):continue
   holes.append((float(u-ww/2),float(u+ww/2),z0+1.13,min(z0+2.10,z1-.25),'window'))
 us=sorted(set([u0,u1]+[v for a,b,_,_,_ in holes for v in (a,b)]));zs=sorted(set([z0,z1]+[v for _,_,a,b,_ in holes for v in (a,b)]))
 for a,b in zip(us,us[1:]):
  for c,d in zip(zs,zs[1:]):
   if any(h0-1e-7<(a+b)/2<h1+1e-7 and h2-1e-7<(c+d)/2<h3+1e-7 for h0,h1,h2,h3,_ in holes):continue
   pos=((a+b)/2,fixed,(c+d)/2) if horizontal else (fixed,(a+b)/2,(c+d)/2);size=(b-a,.085,d-c) if horizontal else (.085,b-a,d-c)
   m.box(pos,size,scheme['wall'])
 # Native walls keep door openings, but include glazing as solid collision.
 solidholes=[h for h in holes if h[4]!='window']
 pu=sorted(set([u0,u1]+[v for a,b,_,_,_ in solidholes for v in (a,b)]));pz=sorted(set([z0,z1]+[v for _,_,a,b,_ in solidholes for v in (a,b)]))
 for a,b in zip(pu,pu[1:]):
  for c,d in zip(pz,pz[1:]):
   if any(h0<(a+b)/2<h1 and h2<(c+d)/2<h3 for h0,h1,h2,h3,_ in solidholes):continue
   pos=((a+b)/2,fixed,(c+d)/2) if horizontal else (fixed,(a+b)/2,(c+d)/2);size=(b-a,.085,d-c) if horizontal else (.085,b-a,d-c);proxy(pos,size,tag=r['id']+'_wall')
 # Fields of individually moulded wood joinery; actual skirting/dado/cornice.
 inset=(.065 if wall in ('y0','x0') else -.065);wood=scheme['wood']
 def bar(uc,zc,length,height,depth=.028,tile=wood):
  pos=(uc,fixed+inset,zc) if horizontal else (fixed+inset,uc,zc);size=(length,depth,height) if horizontal else (depth,length,height);m.box(pos,size,tile,.004)
 for zz,ht,dep in [(z0+.09,.14,.035),(z0+1.0,.065,.048),(z1-.17,.10,.065),(z1-.07,.075,.09)]:
  for a,b in zip(us,us[1:]):
   if any(h0-1e-5<(a+b)/2<h1+1e-5 and h2<zz<h3 for h0,h1,h2,h3,_ in holes):continue
   bar((a+b)/2,zz,b-a,ht,dep,scheme['mould'])
 for a,b in zip(us,us[1:]):
  n=max(1,round((b-a)/({'music':1.25,'writing':1.1,'smoking':.75,'library':1.0}.get(kind,.9))));step=(b-a)/n
  for j in range(n):
   aa=a+j*step+.07;bb=a+(j+1)*step-.07
   for lo,hi in [(z0+.20,z0+.90),(z0+1.13,z1-.29)]:
    if bb-aa<.14 or hi-lo<.18:continue
    if any(min(bb,h1)>max(aa,h0) and min(hi,h3)>max(lo,h2) for h0,h1,h2,h3,_ in holes):continue
    lower=lo<z0+1.0;panel=scheme['panel'] if lower else scheme['wall']
    bar((aa+bb)/2,(lo+hi)/2,bb-aa,hi-lo,.020,panel)
    if not scheme['working']:
     mould=scheme['mould'];accent='Brass' if kind in ('dining','music','writing') else mould
     for uu in (aa,bb):bar(uu,(lo+hi)/2,.028,hi-lo+.028,.040,mould)
     # Butt the rails BETWEEN the stiles. Coplanar overlapping front
     # faces formerly produced black square corner/self-shadow artefacts.
     for zz in (lo,hi):bar((aa+bb)/2,zz,bb-aa-.028,.028,.040,mould)
     if lower and kind in ('dining','music','writing'):
      for zz in (lo+.045,hi-.045):bar((aa+bb)/2,zz,bb-aa-.08,.008,.044,accent)
    elif lower and kind in ('steering','cargo','store'):
     bar(aa,(lo+hi)/2,.022,hi-lo,.034,scheme['mould'])
 # Open secondary exits are dressed openings, not untrimmed holes. The
 # jambs sit OUTSIDE the clear opening; no threshold narrows a tested route.
 for a,b,c,top,typ in holes:
  if typ!='opening':continue
  for edge in (a-.031,b+.031):bar(edge,(z0+top)/2,.062,top-z0+.045,.19,wood)
  bar((a+b)/2,top+.034,b-a+.19,.068,.19,wood)
  if not scheme['working']:
   bar((a+b)/2,top+.086,b-a+.25,.026,.21,scheme['mould'])
  m.tags['CasedSecondaryOpening']+=1
 glass=Mesh()
 for a,b,c,top,typ in holes:
  if typ!='window':continue
  mid=(a+b)/2;frame=design(r)['wood'];inside=1 if inset>0 else -1
  # Full-depth jambs/reveals intersect the wall; the former thin bars gave
  # the appearance of isolated floating glazing at several corner seams.
  for uu in (a,b):bar(uu,(c+top)/2,.070,top-c+.10,.19,frame)
  for zz in (c,top):bar(mid,zz,b-a-.070,.070,.19,frame)
  bar(mid,(c+top)/2,.034,top-c-.070,.19,frame)
  bar(mid,c-.025,b-a+.18,.060,.29,frame)  # substantial sill, not a loose line
  bar(mid,top+.075,b-a+.16,.042,.20,frame)
  for aa,bb in ((a+.025,mid-.020),(mid+.020,b-.025)):
   pos=((aa+bb)/2,fixed,(c+top)/2) if horizontal else (fixed,(aa+bb)/2,(c+top)/2)
   sz=(bb-aa,.014,top-c-.04) if horizontal else (.014,bb-aa,top-c-.04);glass.box(pos,sz,'Ivory')
  # The sash catch is fastened to the meeting rail, not suspended in glass.
  if horizontal:
   m.box((mid,fixed+inside*.173,c+.18),(.10,.027,.035),'Brass',.004)
   for xx in (mid-.038,mid+.038):m.cylinder((xx,fixed+inside*.190,c+.18),.006,.009,'Brass',7,(0,1,0))
  curtain=design(r)['curtain']
  if curtain and horizontal:
   yy=fixed+inside*.235;zz=top+.13
   for xx in (a-.11,b+.11):
    m.rod((xx,fixed+inside*.035,zz),(xx,yy,zz),.013,'Brass',8)
    m.cylinder((xx,fixed+inside*.045,zz),.029,.020,'Brass',12,(0,1,0))
   m.rod((a-.16,yy,zz),(b+.16,yy,zz),.014,'Brass',10)
   for end in (a-.16,b+.16):m.cylinder((end,yy,zz),.029,.04,'Brass',12,(1,0,0))
   for edge in (a-.035,b-.105):
    # Closed thin folded fabric, sewn head and foot, with supporting rings.
    for j in range(4):
     xx=edge+j*.036;fy=yy+inside*(.012 if j%2 else .038)
     m.box((xx,fy,(c-.13+zz-.035)/2),(.041,.025,zz-.035-(c-.13)),curtain,.006)
     m.box((xx,(fy+yy)/2,zz-.025),(.030,abs(fy-yy)+.026,.026),curtain,.003)
     m.ring((xx,yy,zz-.008),.021,.004,'Brass',10,4,(1,0,0))
   m.tags['WallFastenedWindowCurtains']+=1
 if glass.f:glass.emit('Glazing_'+r['id']+'_'+wall,collection('Windows'),kind='glazing',deck=r['deck'],room=r['id'],material='glass')


def surfaces(r):
 col=collection(r['id'],collection('Rooms_'+r['deck']));m=Mesh();fl=Mesh();ce=Mesh();z=r['z'];x0,x1,y0,y1=rect(r);kind=r['kind'];scheme=design(r)
 for wall in ('x0','x1','y0','y1'):wall_mesh(m,r,wall)
 door(m,r,r['door_wall'],r['door_u'],r['door_width'])
 # A real deck-founded underlay carries the finish: the former 25mm
 # panels began 22.5mm above the deck with no bearer at all. Clip BOTH
 # layers to exact stair/casing edges, never cap an actual opening.
 tile=scheme['floor'];floor_holes=deck_holes(r['deck']);inlays=[]
 for (a,b,c,d),_ in clipped_finish_cells((x0+.05,x1-.05,y0+.05,y1-.05),floor_holes):
  fl.box(((a+b)/2,(c+d)/2,z+.01125),(b-a,d-c,.0229),'Tile' if tile=='Tile' else 'Oak')
 # Border is a FLUSH material inlay. The old proud 6.5mm strip actually
 # intersected the feet of every convertible first-class settee.
 if tile.startswith('Carpet') or tile=='Rubber':
  inlays += [(x0+.15,x1-.15,y-.0325,y+.0325) for y in (y0+.18,y1-.18)]
  inlays += [(x-.0325,x+.0325,y0+.15,y1-.15) for x in (x0+.18,x1-.18)]
 pitch=.80 if tile.startswith('Carpet') or tile=='Parquet' else .40 if tile=='Tile' else .17
 for row,y in enumerate(np.arange(y0+.05,y1-.05,pitch)):
  step=.8 if tile=='Parquet' or tile.startswith('Carpet') else .4 if tile=='Tile' else 1.6
  xx=x0+.05
  while xx<x1-.05:
   dx=min(step if xx>x0+.051 or row%2==0 else step*.50,x1-.05-xx);dy=min(pitch,y1-.05-y)
   if dx>.012 and dy>.012:
    t=tile
    if tile=='Tile' and kind in ('bath','wc','hospital','barber'):t='Enamel' if (row+round((xx-x0)/step))%2 else 'Tile'
    bounds=(float(xx+.001),float(xx+dx-.001),float(y+.001),float(y+dy-.001))
    for (a,b,c,d),gold in clipped_finish_cells(bounds,floor_holes,inlays):
     fl.box(((a+b)/2,(c+d)/2,z+.035),(b-a,d-c,.025),'GoldCloth' if gold else t)
   xx+=dx
 # Ceiling holes follow actual stair wells/casings. Structural deck remains.
 holes=ceiling_holes(r)
 xs=sorted(set([x0+.04,x1-.04]+[max(x0+.04,min(x1-.04,v)) for h in holes for v in h[:2]]));ys=sorted(set([y0+.04,y1-.04]+[max(y0+.04,min(y1-.04,v)) for h in holes for v in h[2:]]))
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(ys,ys[1:]):
   if b-a<.01 or d-c<.01 or any(h[0]<(a+b)/2<h[1] and h[2]<(c+d)/2<h[3] for h in holes):continue
   ce.box(((a+b)/2,(c+d)/2,r['top']-.025),(b-a,d-c,.045),scheme['ceiling'])
 # Cased transverse deckheads / coffers, interrupted at the same well.
 for x in ceiling_beams(r):
  beam='Mahogany' if kind=='smoking' else 'Oak' if kind=='library' else 'Ivory' if kind in ('dining','music','writing') else scheme['mould']
  ce.box((float(x),(y0+y1)/2,r['top']-.13),(.095,y1-y0-.13,.17),beam,.012)
  if kind in ('dining','music','writing'):
   for xx in (x-.055,x+.055):ce.box((xx,(y0+y1)/2,r['top']-.18),(.012,y1-y0-.17,.020),'Brass',.003)
 # A dimensional sign rather than unsupported type.
 signs=Mesh();wall=r['door_wall'];u=r['door_u'];zz=z+2.27
 if wall[0]=='y':
  yy=r[wall]+(-.05 if wall=='y0' else .05);signs.box((u,yy,zz),(.52,.012,.13),r['id'])
 else:
  xx=r[wall]+(-.05 if wall=='x0' else .05);signs.box((xx,u,zz),(.012,.52,.13),r['id'])
 signs.emit('Plaque_'+r['id'],col,kind='sign',deck=r['deck'],room=r['id'],material='sign')
 m.emit('Joinery_'+r['id'],col,kind='wall',deck=r['deck'],room=r['id']);fl.emit('Finish_'+r['id'],col,kind='finish',deck=r['deck'],room=r['id']);ce.emit('Ceiling_'+r['id'],col,kind='ceiling',deck=r['deck'],room=r['id'])
 return col


def place(m,template,x,y,z,ang=0):
 m.append(template,(x,y,z),ang)
 # Independent fixture bounds for arrangement diagnostics and native proxies.
 if template.v:
  ca,sa=math.cos(ang),math.sin(ang);vv=[(x+a*ca-b*sa,y+a*sa+b*ca,z+c) for a,b,c in template.v];lo=[min(p[k] for p in vv) for k in range(3)];hi=[max(p[k] for p in vv) for k in range(3)];label=next((t for t in ('TwoBerthBunk','SingleBerth') if template.tags.get(t)),next(iter(template.tags),'Furnishing'))
  fixture=dict(room=CURRENT_ROOM,label=label,bounds=[lo,hi],position=(x,y,z),yaw=ang)
  if label=='ClawfootTub':
   # The two below-floor plumbing tails are not the four cast feet. Read
   # the ACTUAL iron-claw primitives for this scoped bearing datum; keep
   # every service tail/collar in the delivered geometry and envelope.
   claws=[];previous=0
   for end in template.groups:
    ids={i for f in template.f[previous:end] for i in f};zz=[template.v[i][2] for i in ids]
    if set(template.tiles[previous:end])=={'Iron'} and abs(min(zz))<1e-7:claws.append(min(zz))
    previous=end
   assert len(claws)==4,('Tub must have four actual cast foot soles',claws)
   fixture.update(floor_bearing_z=z+min(claws),floor_bearing_basis='Four actual Iron claw primitives; below-floor plumbing tails are not feet',floor_bearing_primitive_count=len(claws))
  FIXTURES.append(fixture)
  if any(template.tags.get(t) for t in ('TurnedDiningTable','WritingDesk','PanelledWardrobe','BowlJugWashstand','OpenBookcase','RolledArmSettee','HighCisternWC','ClawfootTub','CoalRangeThreeOvens','CoalBreadOven','ProvisionShelving','Pianoforte','ChartTableWithDrawers','MailSortingCubby','StewardDrinksCabinet','InsulatedIceChest','SlattedCargoCrate','HoopedCargoBarrel','ApothecaryCabinet','PurserIronSafe','MedicalInstrumentTrolley','FoodProvisionRack','FoldedDeckChair','RoundPedestalTable','UtilityWorkbench','LowWindowBookcase','BilliardTable','FittedSlatBench')):
   local_lo=[min(p[k] for p in template.v) for k in range(3)];local_hi=[max(p[k] for p in template.v) for k in range(3)];cc=[(local_lo[k]+local_hi[k])/2 for k in range(3)];ww=[local_hi[k]-local_lo[k] for k in range(3)];proxy((x+cc[0]*ca-cc[1]*sa,y+cc[0]*sa+cc[1]*ca,z+cc[2]),ww,ang,tag=(CURRENT_ROOM or '')+'_fixture')
 if template.tags.get('RevolvingChair') or template.tags.get('UpholsteredArmchair') or template.tags.get('FourLegSideChair'):
  SEATS.append(dict(position=(x,y,z+.43),yaw=ang,size=(.42,.40,.10)))

def panel_mirror(m,x,y,z,w=.45,h=.65,ang=0):
 a=Mesh();a.box((0,0,0),(w+.10,.04,h+.10),'Oak',.012);a.box((0,-.025,0),(w,.014,h),'Steel',.003);m.append(a,(x,y,z),ang)

def fit_cabin(m,r):
 z=finished_floor(r);x0,x1,y0,y1=rect(r);cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];w=x1-x0;d=y1-y0;scheme=design(r)
 pstart,lstart,sstart,fstart,mstart=len(PROXIES),len(LIGHTS),len(SEATS),len(FIXTURES),len(FIXTURE_MOUNTS)
 # Beds along Y, two clear parallel berth lines. Door opens into the centre.
 if kind in ('cabin_second','cabin_officer'):
  positions=[x0+.44,x1-.44] if w>2.5 and r.get('berths',2)>2 else [x0+.44]
  for x in positions:place(m,recolour(bunk(scheme['variant']%3),{'Canvas':scheme['cloth']}),x,cy+.38,z);proxy((x,cy+.38,z+1.12),(.78,2.04,2.24),tag=r['id']+'_bunk')
  actual=2*len(positions)
 else:
  place(m,bed('first',scheme['cloth']),x0+.49,cy,z);proxy((x0+.49,cy,z+.48),(.82,1.97,.95),tag=r['id']+'_bed')
  actual=1
  if r.get('berths',1)>1:
   # Convertible upholstered berth, separate mattress/bolster geometry.
   a=Mesh();a.append(recolour(sofa(1.82,scheme['cloth']),{'Mahogany':scheme['wood']}),(0,0,0),-math.pi/2);place(m,a,x1-.48,cy+.34,z)
   proxy((x1-.48,cy+.34,z+.44),(.78,1.92,.88),tag=r['id']+'_settee');actual+=1
 place(m,recolour(washstand(),{'Oak':scheme['wood'],'Mahogany':scheme['panel']}),cx,y1-.29,z);panel_mirror(m,cx,y1-.075,z+1.43,.42,.62)
 # Compact wardrobe by the door, clear of the central opening and berth.
 # Short boat-deck first cabins need the cabinet 120mm nearer the entry
 # bulkhead; the generic .48 station overlaps their convertible settee.
 wardrobe_y=y0+(.36 if kind=='cabin_first' and d<2.8 else .48)
 # The full cranked-leaf swing clips the wider crown by ~24mm in the
 # 97 long first-class cabins. Preserve the cabinet and berths, but use a
 # genuinely narrower 540mm carcass / 620mm crown, not an overlap waiver.
 wardrobe_width=.54 if kind=='cabin_first' and d>=2.8 else .62
 place(m,recolour(wardrobe(wardrobe_width,1.98),{'Oak':scheme['wood'],'Mahogany':scheme['panel']}),x1-.39,wardrobe_y,z,math.pi)
 # Bell push and reading lamp at the head. Actual switch plate/cable.
 m.box((x0+.08,cy+.68,z+1.35),(.035,.09,.13),'Brass',.008);m.cylinder((x0+.053,cy+.68,z+1.35),.019,.025,'Black',8,(1,0,0))
 if kind=='cabin_captain':
  place(m,desk(1.4),x0+2.15,y0+.60,z,math.pi);place(m,chair('writing'),x0+2.15,y0+1.48,z);place(m,bookcase(1.3),x1-.28,cy,z,-math.pi/2);place(m,sofa(1.8,'Leather'),x1-1.0,cy,z,-math.pi/2)
 cabin_accessories(m,r)
 ceiling_fixture(m,r,cx,cy)
 if r['door_wall']=='y1':
  m.v=[(x,2*cy-y,zz) for x,y,zz in m.v]
  m.f=[tuple(reversed(f)) for f in m.f]  # mirror has determinant -1
  for p in PROXIES[pstart:]:p['position'][1]=2*cy-p['position'][1];p['yaw']=-p['yaw']
  for p in LIGHTS[lstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2])
  for f in FIXTURES[fstart:]:
   f['bounds']=[(f['bounds'][0][0],2*cy-f['bounds'][1][1],f['bounds'][0][2]),(f['bounds'][1][0],2*cy-f['bounds'][0][1],f['bounds'][1][2])];f['position']=(f['position'][0],2*cy-f['position'][1],f['position'][2]);f['yaw']=-f['yaw']
  for p in FIXTURE_MOUNTS[mstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2])
  for p in SEATS[sstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2]);p['yaw']=-p['yaw']
 return {'actual_berths':actual,'visual_identity':scheme['identity'],'cabin_type':scheme['variant']%5,'inventory':'Class-specific bedstead/two-tier berths; coordinated upholstered convertible berth where scheduled, dressed bedding, fitted shelf/books, wall-fastened reading sconce, below-berth case, wardrobe, bowl/jug washstand, towel rail, framed picture, bell push and physically ceiling-mounted opal/caged fixture.'}


def clear_side_door_row(r,centres,half_length,gap=.03):
 # Preserve the ACTUAL number of existing units. Pack complete finite
 # extents on the two sides of the full door approach, never by checking
 # only the furniture centre or deleting a colliding berth.
 assert r['door_wall'][0]=='y'
 n=len(centres);u=r['door_u'];half_door=r['door_width']/2
 left=(r['x0']+.07,u-half_door-.25);right=(u+half_door+.25,r['x1']-.07)
 def fit(interval,count):
  lo,hi=interval
  if not count:return []
  if hi-lo<count*2*half_length+(count-1)*gap-1e-7:return None
  return [(lo+hi)/2] if count==1 else [float(x) for x in np.linspace(lo+half_length,hi-half_length,count)]
 choices=[]
 for nl in range(n+1):
  a=fit(left,nl);b=fit(right,n-nl)
  if a is not None and b is not None:choices.append((abs(nl-sum(x<u for x in centres)),a+b))
 assert choices,(r['id'],'Cannot preserve all units with full door clearance',n,half_length)
 result=min(choices,key=lambda q:q[0])[1]
 assert len(result)==n
 return result


def fit_dorm(m,r):
 x0,x1,y0,y1=rect(r);z=finished_floor(r);length=x1-x0;width=y1-y0;actual=0
 # Transverse bunks along a central aisle: 1.92 m bed, 0.80 m longitudinal
 # pitch; occasional cross-aisle. Wider rooms add back-to-back outer rows.
 ys=[]
 if width>=5.25:
  cy=(y0+y1)/2;ys=[cy-(2.15 if width>=8 else 1.68),cy+(2.15 if width>=8 else 1.68)]
  for i,x in enumerate(np.arange(x0+.65,x1-.45,.88)):
   if i%9==8:continue
   if width>=8 and abs(x-(x0+3.6))<1.85:continue  # furnished mess alcove, bypass round table
   # Entry cross aisle is at room centre for Y-side doors.
   if r['door_wall'][0]=='y' and abs(x-r['door_u'])<.85:continue
   for yy in ys:
    place(m,bunk((i+(1 if yy>cy else 0))%3),float(x),yy,z,0);proxy((float(x),yy,z+1.1),(.76,1.96,2.2),0,tag=r['id']+'_bunk');actual+=2
 else:
  # Narrow crew wing: longitudinal bunks against each outer wall, a real
  # continuous aisle; small third-class wings have only one berth row.
  cy=(y0+y1)/2
  ys=[y0+.50,y1-.50] if width>3.0 else [y1-.48 if y0>0 else y0+.48]
  centres=[float(x) for x in np.arange(x0+1.15,x1-.9,2.12) if not (r['door_wall'][0]=='y' and abs(x-r['door_u'])<1.1)]
  if r['door_wall'][0]=='y':centres=clear_side_door_row(r,centres,.983)
  for i,x in enumerate(centres):
   for yy in ys:
    side=-1 if yy>cy else 1
    place(m,bunk((i+(1 if yy>cy else 0))%3,ladder_side=side),float(x),yy,z,math.pi/2);proxy((float(x),yy,z+1.12),(.86,1.97,2.24),math.pi/2,tag=r['id']+'_bunk');actual+=2
 # Enamel drinking-water tank / wash shelf at end, baggage racks overhead.
 m.lathe((x1-.45,y0+.38,z),[(0,.22),(.03,.25),(.72,.25),(.78,.22)],'Iron',12)
 m.tube([(x1-.45,y0+.38,z+.28),(x1-.17,y0+.38,z+.28),(x1-.17,y0+.38,z+.21)],.018,'Brass',7)
 if width>=8:
  for xx in [x0+3.6] if x1-x0>7.2 else []:
   place(m,utility_table(2.25,.68,.7825),float(xx),cy,z)
   for side in (-1,1):
    yy=cy+side*.72;m.box((float(xx),yy,z+.45),(2.2,.28,.055),'Oak',.012)
    for dx in (-.82,.82):
     for dy in (-.11,.11):m.cylinder((float(xx)+dx,yy+dy,z+.010),.035,.020,'Iron',8)
     m.rod((float(xx)+dx,yy-.11,z+.02),(float(xx)+dx,yy,z+.43),.032,'Iron',7);m.rod((float(xx)+dx,yy+.11,z+.02),(float(xx)+dx,yy,z+.43),.032,'Iron',7)
   m.tags['SteerageMessTable']+=1
 mess_seats=0
 if r['kind']=='dorm_crew' and 3.0<width<5.25 and r['door_wall'][0]=='y':
  # The existing berth-free entrance bay doubles as a small mess alcove.
  # Keep its table/bench against the OPPOSITE wall so the entrance and
  # longitudinal middle aisle remain free; no berths are deleted or invented.
  # Berth centres are pitched from the aft bulkhead, not the doorway.
  # Centre in their existing gap using exact placement datums and nominal
  # 2m berth length, NOT angular-tessellation-dependent mesh bounds. Actual
  # mesh-pair overlap is independently gated for both master and GAME.
  cc=[f['position'][0] for f in FIXTURES if f['room']==r['id'] and f['label']=='TwoBerthBunk'];u=r['door_u'];a=max(x for x in cc if x<u);b=min(x for x in cc if x>u);assert b-a-2.0>1.5,(r['id'],'mess bay too short')
  xx=(a+b)/2;sign=1 if r['door_wall']=='y1' else -1;edge=y0 if sign>0 else y1;yy=edge+sign*.85;bench_y=edge+sign*.30
  place(m,utility_table(1.20,.50,.7825),xx,yy,z)
  m.box((xx,bench_y,z+.45),(1.15,.27,.055),'Oak',.012)
  for dx in (-.43,.43):
   for dy in (-.09,.09):
    m.cylinder((xx+dx,bench_y+dy,z+.010),.028,.020,'Iron',8)
    m.rod((xx+dx,bench_y+dy,z+.02),(xx+dx,bench_y,z+.43),.025,'Iron',7)
  for dx in (-.30,.30):SEATS.append(dict(position=(xx+dx,bench_y,z+.43),yaw=math.pi if sign>0 else 0,size=(.38,.27,.10)))
  m.tags['CrewMessAlcove']+=1;mess_seats=2
 for x in np.arange(x0+1,x1-.5,4):ceiling_fixture(m,r,float(x),(y0+y1)/2,'marine')
 return {'actual_berths':actual,'actual_mess_seats':mess_seats,'inventory':'Individually framed two-tier berths with mattress, pillow, blanket, retaining rails and ladders; continuous central aisle/cross aisles and drinking-water tank.'+(' Two-seat table/bench mess alcove in the berth-free entrance bay.' if mess_seats else '')}


def fit_public(m,r):
 return public_rooms.fit(m,r,place)


def fit_service(m,r):
 x0,x1,y0,y1=rect(r);z=finished_floor(r);cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];actual=0
 if kind in ('galley','bakery'):
  # Furnace/oven doors face the working aisle (+Y), not the close outer
  # bulkhead. The former unrotated range put its firing front 0.3m off-wall.
  from working_detail import bake_oven
  place(m,range_unit() if kind=='galley' else bake_oven(),x0+2.0,y0+1.0,z,math.pi)
  # Hood duct joins a dedicated corner flue (not random pipe decoration).
  m.box((x0+2.0,y0+1.0,z+2.05),(3.35,1.55,.22),'Iron',.03)
  for xx in np.arange(x0+2,x1-1.2,3.0):
   if r['door_wall'][0]=='y' and abs(xx-r['door_u'])<2:continue
   place(m,utility_table(2.2,.75,.90),float(xx),y1-.6,z)
   m.box((float(xx),y1-.6,z+.9173),(.58,.34,.035),'Oak',.006)
   m.lathe((float(xx)+.5,y1-.60,z+.8998),[(0,.14),(.12,.20),(.18,.22),(.19,.20),(.06,.08)],'Copper',14)
  # Galley and bakery join an exterior lagged common flue at deckhead
  # level. Never run one diagonal chimney through the writing room above.
  m.tube([(x0+2,y0+1,z+2.15),(-39.35,y0+1,z+2.25),(-39.35,-4.8,z+2.25)],.16,'Lagging',12)
  if kind=='galley':
   flue=Mesh();flue.tube([(-39.35,-4.8,z+2.25),(-39.35,-4.8,20.60)],.20,'Lagging',12)
   for zz in (14.4,17.2):
    # Finite sleeves bridge the intentional structural opening and seat
    # against the lagging, not 5mm away from it. No deck caps the flue.
    for dx in (-.30,.30):flue.box((-39.35+dx,-4.8,zz+.025),(.12,.72,.06),'Iron',.009)
    for dy in (-.30,.30):flue.box((-39.35,-4.8+dy,zz+.025),(.72,.12,.06),'Iron',.009)
    flue.ring((-39.35,-4.8,zz+.045),.24,.050,'Iron',16,6)
   flue.lathe((-39.35,-4.8,20.60),[(0,.23),(.05,.29),(.16,.31),(.24,.04)],'Iron',16)
   flue.emit('Galley_Exterior_CommonFlue',collection('DeckEquipment'),kind='superstructure',deck='promenade',room=r['id'])
   proxy((-39.35,-4.8,17.42),(.45,.45,6.35),tag='GalleyFlue')
 elif kind in ('pantry','store','cargo','mail','cold_store','bar'):
  rows=[(y0+.34,math.pi),(y1-.34,0)]
  if y1-y0<2.6:rows=[rows[1] if r['door_wall']=='y0' else rows[0]]
  if kind=='cargo':
   # Walkable central hold: individually slatted/strapped crates and hooped
   # barrels, NOT solid cubes intersecting a second set of linen racks.
   for i,xx in enumerate(np.arange(x0+1,x1-.8,1.3)):
    for side in (-1,1):
     yy=y0+.75 if side<0 else y1-.75
     place(m,staved_barrel() if i%3==1 else cargo_crate(),float(xx),yy,z+(0 if i%3==1 else .0125),0 if side<0 else math.pi)
   # Open chain bin, finite bars and interlinked stored chain at fore end.
   xx=x1-.50;m.box((xx,cy,z+.06),(.82,.98,.12),'Iron',.015)
   for yy in (cy-.47,cy+.47):
    for dx in (-.37,0,.37):m.rod((xx+dx,yy,z+.10),(xx+dx,yy,z+.85),.025,'Iron',8)
    m.rod((xx-.39,yy,z+.85),(xx+.39,yy,z+.85),.030,'Iron',8)
   # Four short, interlinked lengths lie on the bin base. Alternating
   # +/-45-degree link planes have equal finite ground clearance; 153.8mm
   # pitch seats neighbouring inner cheeks without floating an empty row
   # as the old i//8 height rule did. No rigid-body chain simulation claimed.
   for i in range(14):
    first=len(m.v);a=math.pi/4*(1 if i%2 else -1)
    m.ring((xx-.2307+(i%4)*.1538,cy-.285+(i//4)*.19,z+.23),.095,.018,'Iron',14,6,(0,math.sin(a),math.cos(a)))
    m.rest(first,z+.12)
   m.tags['StoredInterlinkedShortChainLengths']+=1
   proxy((xx,cy,z+.46),(.88,1.04,.92),tag=r['id']+'_chainbin')
  elif r['id']=='P_Coats':
   for i in range(4):place(m,folded_deckchair(),x0+.75+i*.70,y1-.26,z)
   place(m,shelving('linen'),x1-1.0,y1-.34,z)
   # Peg rail and hooks above the otherwise clear cloak-storage wall.
   for a,b in ((x0+.7,r['door_u']-r['door_width']/2-.13),(r['door_u']+r['door_width']/2+.13,x0+5.5)):
    if b>a:m.box(((a+b)/2,y0+.09,z+1.80),(b-a,.06,.08),'Oak',.008)
   for xx in np.arange(x0+1.1,x0+5.2,.55):
    if abs(xx-r['door_u'])<r['door_width']/2+.18:continue
    m.tube([(float(xx),y0+.12,z+1.80),(float(xx),y0+.25,z+1.75),(float(xx),y0+.29,z+1.82)],.012,'Brass',8)
  else:
   for yy,ang in rows:
    stocks=[float(x) for x in np.arange(x0+1,x1-.6,1.7)]
    if kind=='store' and y1-y0<2.0 and r['door_wall'][0]=='y':stocks=clear_side_door_row(r,stocks,.70,.05)
    for stock_i,xx in enumerate(stocks):
     if r['door_wall'][0]=='y' and abs(xx-r['door_u'])<1.40 and abs(yy-r[r['door_wall']])<.8:continue
     template=(mail_cubby(stock_i%3) if kind=='mail' else drinks_rack(stock_i%3) if kind=='bar' else ice_chest() if kind=='cold_store' and yy>cy else provision_rack() if kind=='cold_store' else shelving('pantry' if kind=='pantry' else 'linen',stock_i%3))
     place(m,template,float(xx),yy,z,ang)
  if kind=='pantry' and y1-y0>=3.0:
   for xx in np.arange(x0+1.3,x1-.9,2.4):
    if abs(xx-r['door_u'])<1.15:continue
    place(m,utility_table(1.4,.65,.90,'Marble'),float(xx),cy,z)
  if kind=='mail' and y1-y0>=2.4:
   place(m,desk(1.2,True),x0+1.0,cy,z,math.pi/2)
   # Tied letter bundles on the sorting surface, not a writing pad alone.
   for i in range(3):
    m.box((x0+1.0,cy-.30+i*.25,z+DESK_PAD_TOP+.0373),(.28,.20,.075),'Paper',.004)
    m.rod((x0+.85,cy-.30+i*.25,z+.89),(x0+1.15,cy-.30+i*.25,z+.89),.005,'Rope',5)
 elif kind in ('bath','wc','third_wash'):
  if kind=='bath':
   place(m,bathtub(),cx,cy-.2,z,math.pi/2);place(m,washstand(),cx,y1-.3,z);panel_mirror(m,cx,y1-.08,z+1.5)
  else:
   n=max(1,int((x1-x0)/1.3))
   for i in range(n):
    xx=x0+(i+.5)*(x1-x0)/n;place(m,wc(),xx,y0+.75,z,math.pi)
    wx,wy,wa=washstand_stations(r)[i];place(m,washstand(),wx,wy,z,wa)
    if wa:panel_mirror(m,x0+.08,wy,z+1.5,ang=wa)
    else:panel_mirror(m,wx,y1-.08,z+1.5)
    if i<n-1:
     xx=x0+(i+1)*(x1-x0)/n;m.box((xx,y0+1.05,z+1.0),(.055,1.65,2.0),'Ivory');proxy((xx,y0+1.05,z+1.0),(.055,1.65,2.0),tag=r['id']+'_cubicle')
 elif kind=='barber':
  for xx in (x0+1.10,x1-1.10):
   xx=float(xx);place(m,barber_chair(),xx,cy,z,math.pi);place(m,washstand(),xx,y1-.4,z);panel_mirror(m,xx,y1-.08,z+1.50,.75,.80)
   # Brush, razor and leather strop at each basin station.
   m.lathe((xx+.255,y1-.22,z+WASHSTAND_TOP-.0002),[(0,.022),(.06,.026),(.08,.020),(.13,.030),(.15,.033)],'Walnut',12)
   m.cylinder((xx+.255,y1-.22,z+1.015),.034,.055,'Linen',12)
   m.box((xx-.10,y1-.61,z+WASHSTAND_TOP+.0073),(.18,.025,.015),'Steel',.003)
   m.tube([(xx+.22,y1-.60,z+.74),(xx+.22,y1-.655,z+.74),(xx+.22,y1-.655,z+.69)],.008,'Brass',8)
   m.box((xx+.22,y1-.66,z+.46),(.055,.012,.48),'Leather',.005)
 elif kind=='hospital':
  for xx in (x0+1.75,x1-1.1):place(m,bed('hospital','ClothBlue'),xx,cy,z);actual+=1
  place(m,washstand(),cx,y1-.35,z);place(m,wardrobe(.8,1.9),x1-.5,y0+.40,z,math.pi);place(m,utility_table(1.3,.65,.86,'Marble'),cx,cy,z);place(m,chair('writing'),cx,cy-.85,z)
  place(m,medicine_cabinet(),x0+1.1,y0+.28,z,math.pi)
  place(m,medical_trolley(),cx+1.10,y1-.65,z)
 elif kind in ('office','chart','wheelhouse'):
  for xx in ([x0+1.3,x0+3.7] if kind=='wheelhouse' else np.arange(x0+1.1,x1-.8,2.6)):
   # An office desk must not sit immediately inside its own doorway.
   if r['door_wall']=='y1' and abs(float(xx)-r['door_u'])<1.25:continue
   place(m,desk(1.6,True),float(xx),y1-.65,z);place(m,chair('writing'),float(xx),y1-1.45,z,math.pi)
   m.box((float(xx),y1-.65,z+DESK_PAD_TOP+.0038),(1.15,.44,.008),'Chart' if kind!='office' else 'Paper')
  place(m,bookcase(1.0 if kind=='office' else 1.4),x0+.3,y0+.70 if kind=='office' else y0+1.1 if r['door_wall']=='x0' else cy,z,math.pi/2)
  if kind=='office':place(m,iron_safe(),x1-.45,y0+.50,z,-math.pi/2)
  if kind=='chart':
   place(m,chart_table(),cx+.20,cy,z)
   # Open, subdivided signal-flag/rolled-chart rack along the end bulkhead.
   yy0=y0+.42;yy1=y1-.42;step=(yy1-yy0)/10
   m.box((x1-.075,cy,z+1.24),(.035,yy1-yy0,1.90),'Oak')
   for i in range(11):m.box((x1-.28,yy0+i*step,z+1.24),(.43,.035,1.90),'Oak',.004)
   for zz in (.30,.76,1.22,1.68,2.17):
    m.box((x1-.28,cy,z+zz),(.45,yy1-yy0,.035),'Oak',.005)
    if zz<2:
     for i in range(10):
      if (i+round(zz*10))%11 in (0,1):continue
      first=len(m.v);yy=yy0+(i+.5)*step;m.cylinder((x1-.30,yy,z+zz+.13),.09,.30,['Canvas','BookRed','BookBlue','GoldCloth'][i%4],12,(1,0,0))
      m.ring((x1-.38,yy,z+zz+.13),.095,.008,'Rope',12,5,(1,0,0))
      m.rest(first,z+zz+.0175)
   proxy((x1-.28,cy,z+1.24),(.47,yy1-yy0,1.94),tag=r['id']+'_signalrack')
 elif kind=='stairhall':
  # The narrow upper hall's former corner bases barely caught a parquet
  # edge in MASTER and hung over the stair-margin void in GAME. Four
  # perimeter piers now bear fully on the actual side strips, clear of the
  # primary door and both cased secondary escape openings.
  stations=[(xx,yy) for xx in (x0+.27,x1-.27) for yy in (-1.1,1.1)] if y1-y0<=8 else [(xx,yy) for xx in (x0+.6,x1-.6) for yy in (y0+.35,y1-.35)]
  for xx,yy in stations:
   # A capital meets the real beam soffit or panel, not an arbitrary point
   # 72.5mm below the ceiling (nor through the full beam depth).
   top=r['top']-.0475
   if any(abs(bx-xx)<.2175 for bx in ceiling_beams(r)):top=r['top']-.215
   h=top-z+.0002
   m.lathe((xx,yy,z),[(0,.16),(.10,.17),(.17,.12),(h-.18,.10),(h-.06,.17),(h,.17)],'Oak',12)
  if y1-y0>8:
   for yy in (y0+.65,y1-.65):place(m,sofa(2.0,'LeatherGreen'),x0+1.45,yy,z,math.pi if yy<cy else 0)
 # Purposeful light allocation, not random light spam.
 for xx in np.arange(x0+min(1.,(x1-x0)/2),x1-.3,4):ceiling_fixture(m,r,float(xx),cy)
 from working_detail import finish_service
 finish_service(m,r,place)
 return {'actual_berths':actual,'inventory':{'galley':'Three-oven coal range, firebrick base, burners, hollow copper pots and handles, hood/connected flue, work tables, cutting boards.','bakery':'Dedicated twin-mouth brick-lined bread oven, kneading workbench with scored loaves, flour bin/scoop, peel retained to the bulkhead, tool rail and connected hood/flue.','bath':'Clawfoot ceramic tub and connected brass taps.','wc':'High-cistern ceramic WCs, bowl interiors, seats, flush chain and pipes; partitioned cubicles; bowl/jug washstands and mirrors.','wheelhouse':'Chart desks, writing seats and publications; helm, binnacle, telegraphs and navigation fixtures are separate functional meshes.','chart':'Central standing chart table with paired drawer pedestals, chart rollers, parallel rules and dividers; writing desks/seats, publications, open signal-flag and rolled-chart rack. No wireless.','office':'Door-clear writing desks/chairs, publications, ledgers and hinged-wheel iron safe.','mail':'Open letter-sorting cubbies with individually tied paper/parcels and a bundle-covered sorting table.','cargo':'Hollow slatted wooden crates with battens, iron straps, nail heads, rope handles and labels; hooped staved barrels and open stored-chain bin.','bar':'Steward service cabinets with paneled cupboards, marble counters, individual stoppered bottles and pewter measuring/drinking vessels.','cold_store':'Latched insulated ice chest with drain/catch pan, and separate racks of provision sacks and sealed ceramic jars; no powered refrigeration asserted.','hospital':'Two bedsteads, washstand, examination/writing table and chair, apothecary bottle/bandage cabinet, wheeled instrument trolley and cleanable tiled floor.','barber':'Pedestal reclining barber chairs with headrests, footboards and adjuster wheels; individual bowl/jug basins and mirrors, brushes, razors and leather strops.','stairhall':'Turned columns, upholstered waiting seats where space permits; actual cut-through stairs and handrails in separate stair module.'}.get(kind,'Fitted purpose-specific shelving/storage, office/chart/wash/medical equipment and incandescent lighting.')}


def build():
 global CURRENT_ROOM
 for r in ROOMS:
  CURRENT_ROOM=r['id']
  if r['kind'] in ('machinery','steering'):continue
  col=surfaces(r);m=Mesh()
  if r['kind'].startswith('cabin'):inv=fit_cabin(m,r)
  elif r['kind'].startswith('dorm'):inv=fit_dorm(m,r)
  elif r['kind'] in ('dining','dining_second','library','music','smoking','writing','lounge_second','mess'):inv=fit_public(m,r)
  else:inv=fit_service(m,r)
  obs=m.emit('Furniture_'+r['id'],col,deck=r['deck'],room=r['id'])
  ROOM_REPORT.append(dict(id=r['id'],name=r['name'],deck=r['deck'],kind=r['kind'],bounds=rect(r),z=r['z'],top=r['top'],floor_area_m2=round((r['x1']-r['x0'])*(r['y1']-r['y0']),2),design_scheme=design(r),source_objects=[o.name for o in obs],components=dict(m.tags),triangles=sum(len(o.data.loop_triangles) for o in obs),nominal_berths=r.get('berths',0),**inv))
  print('FURNISHED',r['id'],sum(len(o.data.loop_triangles) for o in obs),flush=True)
 return ROOM_REPORT
