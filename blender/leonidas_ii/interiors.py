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
from shipdesign.leonidas_ii import ROOMS,DECKS,DECK_TOPS,STAIRS,CASINGS,hb,rect,overlap
ROOM_REPORT=[];DOORS=[];CURRENT_ROOM=None

def door(m,r,wall,u,w,h=2.10,external=False):
 z=r['z']+.055;horizontal=wall[0]=='y';x=u if horizontal else r[wall];y=r[wall] if horizontal else u
 # Hinge at negative local X end; local door lies along X, +Y normal.
 ang=0 if horizontal else math.pi/2;hx=x-w/2 if horizontal else x;hy=y if horizontal else y-w/2
 leaf=Mesh();leaf.box((w/2,0,h/2),(w-.045,.055,h-.035),'Oak',.008)
 for zz,hh in [(.52,.70),(1.45,.82)]:
  leaf.box((w/2,-.034,zz),(w-.19,.028,hh),'Mahogany' if r['style']=='mahogany' else 'Oak',.012)
  leaf.box((w/2,.034,zz),(w-.19,.028,hh),'Oak',.012)
 for zz in (.20,1.70):
  leaf.cylinder((.015,0,zz),.018,.13,'Brass',8)
 for side in (-1,1):
  leaf.cylinder((w-.12,side*.058,1.02),.027,.05,'Brass',10,(0,1,0));leaf.rod((w-.12,side*.08,1.02),(w-.23,side*.08,1.02),.012,'Brass',7)
 world=Mesh();world.append(leaf,(hx,hy,z),ang)
 name='Door_'+r['id'];world.emit(name,collection('Doors'),kind='door',deck=r['deck'],room=r['id'],origin=(hx,hy,z),mover='door')
 DOORS.append(dict(id=r['id'],name=name,hinge=(hx,hy,z),yaw=ang,width=w,height=h,angle_deg=92 if wall in ('y0','x1') else -92,watertight=False))
 # Doorframe carried by static walls, not by animated leaf.
 for du in (-w/2-.045,w/2+.045):
  c=(x+du,y,z+h/2) if horizontal else (x,y+du,z+h/2);s=(.07,.15,h+.05) if horizontal else (.15,.07,h+.05);m.box(c,s,'Oak',.007)
 c=(x,y,z+h+.025);s=(w+.16,.15,.08) if horizontal else (.15,w+.16,.08);m.box(c,s,'Oak',.007)
 return (x,y,z)

def wall_mesh(m,r,wall,windows=True):
 horizontal=wall[0]=='y';u0,u1=(r['x0'],r['x1']) if horizontal else (r['y0'],r['y1']);fixed=r[wall];z0=r['z']+.025;z1=r['top'];holes=[]
 if r['id']=='M_Entrance' and wall=='y1':holes.append((r['door_u']-.8,r['door_u']+.8,z0,z0+2.10,'opening'))
 # End-to-end third-class circulation avoids 0.3-0.4m inaccessible gaps.
 if r['kind'].startswith('dorm') or r['kind'] in ('third_wash','cold_store'):
  if wall in ('x0','x1') and wall!=r['door_wall']:
   mid=(r['y0']+r['y1'])/2;holes.append((mid-.65,mid+.65,z0,z0+2.15,'opening'))
 if wall==r['door_wall']:holes.append((r['door_u']-r['door_width']/2,r['door_u']+r['door_width']/2,z0,z0+2.10,'door'))
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
   if any(not(u+ww/2<a-.18 or u-ww/2>b+.18) for a,b,*_ in holes):continue
   holes.append((float(u-ww/2),float(u+ww/2),z0+1.13,min(z0+2.10,z1-.25),'window'))
 us=sorted(set([u0,u1]+[v for a,b,_,_,_ in holes for v in (a,b)]));zs=sorted(set([z0,z1]+[v for _,_,a,b,_ in holes for v in (a,b)]))
 for a,b in zip(us,us[1:]):
  for c,d in zip(zs,zs[1:]):
   if any(h0-1e-7<(a+b)/2<h1+1e-7 and h2-1e-7<(c+d)/2<h3+1e-7 for h0,h1,h2,h3,_ in holes):continue
   pos=((a+b)/2,fixed,(c+d)/2) if horizontal else (fixed,(a+b)/2,(c+d)/2);size=(b-a,.085,d-c) if horizontal else (.085,b-a,d-c)
   m.box(pos,size,'White' if above else 'Ivory')
 # Native walls keep door openings, but include glazing as solid collision.
 solidholes=[h for h in holes if h[4]!='window']
 pu=sorted(set([u0,u1]+[v for a,b,_,_,_ in solidholes for v in (a,b)]));pz=sorted(set([z0,z1]+[v for _,_,a,b,_ in solidholes for v in (a,b)]))
 for a,b in zip(pu,pu[1:]):
  for c,d in zip(pz,pz[1:]):
   if any(h0<(a+b)/2<h1 and h2<(c+d)/2<h3 for h0,h1,h2,h3,_ in solidholes):continue
   pos=((a+b)/2,fixed,(c+d)/2) if horizontal else (fixed,(a+b)/2,(c+d)/2);size=(b-a,.085,d-c) if horizontal else (.085,b-a,d-c);proxy(pos,size,tag=r['id']+'_wall')
 # Fields of individually moulded wood joinery; actual skirting/dado/cornice.
 inset=(.065 if wall in ('y0','x0') else -.065);wood={'ivory':'Ivory','mahogany':'Mahogany','teak':'Teak'}.get(r['style'],'Oak')
 def bar(uc,zc,length,height,depth=.028,tile=wood):
  pos=(uc,fixed+inset,zc) if horizontal else (fixed+inset,uc,zc);size=(length,depth,height) if horizontal else (depth,length,height);m.box(pos,size,tile,.004)
 for zz,ht,dep in [(z0+.09,.14,.035),(z0+.91,.065,.048),(z1-.17,.10,.065),(z1-.07,.075,.09)]:
  for a,b in zip(us,us[1:]):
   if any(h0-1e-5<(a+b)/2<h1+1e-5 and h2<zz<h3 for h0,h1,h2,h3,_ in holes):continue
   bar((a+b)/2,zz,b-a,ht,dep)
 for a,b in zip(us,us[1:]):
  n=max(1,round((b-a)/.9));step=(b-a)/n
  for j in range(n):
   aa=a+j*step+.07;bb=a+(j+1)*step-.07
   for lo,hi in [(z0+.20,z0+.81),(z0+1.05,z1-.29)]:
    if bb-aa<.14 or hi-lo<.18:continue
    if any(min(bb,h1)>max(aa,h0) and min(hi,h3)>max(lo,h2) for h0,h1,h2,h3,_ in holes):continue
    bar((aa+bb)/2,(lo+hi)/2,bb-aa,hi-lo,.018,wood)
    for uu in (aa,bb):bar(uu,(lo+hi)/2,.026,hi-lo,.042,'Brass' if r['style']=='ivory' else wood)
    for zz in (lo,hi):bar((aa+bb)/2,zz,bb-aa,.026,.042,'Brass' if r['style']=='ivory' else wood)
 glass=Mesh()
 for a,b,c,d,typ in holes:
  if typ=='window':
   mid=(a+b)/2
   for uu in (a-.025,b+.025):bar(uu,(c+d)/2,.065,d-c+.12,.12,'Teak')
   for zz in (c-.025,d+.025):bar(mid,zz,b-a+.12,.065,.12,'Teak')
   bar(mid,(c+d)/2,.035,d-c,.13,'Teak')
   for aa,bb in ((a,mid-.018),(mid+.018,b)):
    p=((aa+bb)/2,fixed,(c+d)/2) if horizontal else (fixed,(aa+bb)/2,(c+d)/2);sz=(bb-aa,.012,d-c) if horizontal else (.012,bb-aa,d-c);glass.box(p,sz,'Ivory')
 if glass.f:glass.emit('Glazing_'+r['id']+'_'+wall,collection('Windows'),kind='glazing',deck=r['deck'],room=r['id'],material='glass')


def surfaces(r):
 col=collection(r['id'],collection('Rooms_'+r['deck']));m=Mesh();fl=Mesh();ce=Mesh();z=r['z'];x0,x1,y0,y1=rect(r);kind=r['kind']
 for wall in ('x0','x1','y0','y1'):wall_mesh(m,r,wall)
 door(m,r,r['door_wall'],r['door_u'],r['door_width'])
 # Timber margin around carpet/tile. Wood grain along individual planks.
 tile='Rubber' if kind=='smoking' else 'Tile' if r['style']=='tile' or kind in ('galley','pantry','bakery','third_wash','cold_store','hospital') else 'Carpet' if r['style'] in ('ivory','mahogany') or kind.startswith('cabin_first') else 'Teak'
 for x in np.arange(x0+.05,x1-.05,1.6):
  for y in np.arange(y0+.05,y1-.05,.32 if tile=='Teak' else .80):
   dx=min(1.6,x1-.05-x);dy=min(.32 if tile=='Teak' else .8,y1-.05-y)
   if any(overlap((float(x),float(x+dx),float(y),float(y+dy)),h,.001) for h in deck_holes(r['deck'])):continue
   if dx>.01 and dy>.01:fl.box((float(x+dx/2),float(y+dy/2),z+.035),(dx-.004,dy-.003,.025),tile)
 # Carpet/rubber border inlaid in the floor, not a floating mat.
 if tile in ('Carpet','Rubber'):
  for y in (y0+.18,y1-.18):fl.box(((x0+x1)/2,y,z+.050),(x1-x0-.30,.065,.008),'GoldCloth')
  for x in (x0+.18,x1-.18):fl.box((x,(y0+y1)/2,z+.050),(.065,y1-y0-.30,.008),'GoldCloth')
 # Ceiling holes follow actual stair wells/casings. Structural deck remains.
 holes=[]
 for s in STAIRS:
  if abs(s['z1']-r['top'])<.25 or abs(s['z0']-r['z'])<.05:
   rr=(min(s['x0'],s['x1'])-.1,max(s['x0'],s['x1'])+.1,s['y']-s['width']/2-.1,s['y']+s['width']/2+.1)
   if overlap(rr,rect(r)):holes.append(rr)
 for c in CASINGS:
  if c['z0']<r['top']<c['z1'] and overlap(c['rect'],rect(r)):holes.append(c['rect'])
 xs=sorted(set([x0+.04,x1-.04]+[max(x0+.04,min(x1-.04,v)) for h in holes for v in h[:2]]));ys=sorted(set([y0+.04,y1-.04]+[max(y0+.04,min(y1-.04,v)) for h in holes for v in h[2:]]))
 for a,b in zip(xs,xs[1:]):
  for c,d in zip(ys,ys[1:]):
   if b-a<.01 or d-c<.01 or any(h[0]<(a+b)/2<h[1] and h[2]<(c+d)/2<h[3] for h in holes):continue
   ce.box(((a+b)/2,(c+d)/2,r['top']-.025),(b-a,d-c,.045),'Ivory')
 # Cased transverse deckheads / coffers, interrupted at the same well.
 for x in np.arange(x0+.30,x1-.15,1.60):
  if any(h[0]-.10<x<h[1]+.10 for h in holes):continue
  ce.box((float(x),(y0+y1)/2,r['top']-.13),(.095,y1-y0-.13,.17),'Ivory' if r['style']=='ivory' else 'Oak',.012)
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
  ca,sa=math.cos(ang),math.sin(ang);vv=[(x+a*ca-b*sa,y+a*sa+b*ca,z+c) for a,b,c in template.v];lo=[min(p[k] for p in vv) for k in range(3)];hi=[max(p[k] for p in vv) for k in range(3)];label=next(iter(template.tags),'Furnishing')
  FIXTURES.append(dict(room=CURRENT_ROOM,label=label,bounds=[lo,hi],position=(x,y,z),yaw=ang))
  if any(template.tags.get(t) for t in ('TurnedDiningTable','WritingDesk','PanelledWardrobe','BowlJugWashstand','OpenBookcase','RolledArmSettee','HighCisternWC','ClawfootTub','CoalRangeThreeOvens','ProvisionShelving','Pianoforte','ChartTableWithDrawers','MailSortingCubby','StewardDrinksCabinet','InsulatedIceChest','SlattedCargoCrate','HoopedCargoBarrel','ApothecaryCabinet','PurserIronSafe','MedicalInstrumentTrolley','FoodProvisionRack','FoldedDeckChair')):
   local_lo=[min(p[k] for p in template.v) for k in range(3)];local_hi=[max(p[k] for p in template.v) for k in range(3)];cc=[(local_lo[k]+local_hi[k])/2 for k in range(3)];ww=[local_hi[k]-local_lo[k] for k in range(3)];proxy((x+cc[0]*ca-cc[1]*sa,y+cc[0]*sa+cc[1]*ca,z+cc[2]),ww,ang,tag=(CURRENT_ROOM or '')+'_fixture')
 if template.tags.get('RevolvingChair') or template.tags.get('UpholsteredArmchair'):
  SEATS.append(dict(position=(x,y,z+.43),yaw=ang,size=(.42,.40,.10)))

def panel_mirror(m,x,y,z,w=.45,h=.65,ang=0):
 a=Mesh();a.box((0,0,0),(w+.10,.04,h+.10),'Oak',.012);a.box((0,-.025,0),(w,.014,h),'Steel',.003);m.append(a,(x,y,z),ang)

def fit_cabin(m,r):
 z=r['z']+.055;x0,x1,y0,y1=rect(r);cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];w=x1-x0;d=y1-y0
 pstart,lstart,sstart,fstart=len(PROXIES),len(LIGHTS),len(SEATS),len(FIXTURES)
 # Beds along Y, two clear parallel berth lines. Door opens into the centre.
 if kind in ('cabin_second','cabin_officer'):
  positions=[x0+.50,x1-.50] if w>2.5 and r.get('berths',2)>2 else [x0+.55]
  for x in positions:place(m,bunk(),x,cy+.28,z);proxy((x,cy+.28,z+1.0),(.76,1.96,2),tag=r['id']+'_bunk')
  actual=2*len(positions)
 else:
  place(m,bed(),x0+.54,cy,z);proxy((x0+.54,cy,z+.48),(.82,1.97,.95),tag=r['id']+'_bed')
  actual=1
  if r.get('berths',1)>1:
   # Convertible upholstered berth, separate mattress/bolster geometry.
   a=Mesh();a.append(sofa(1.82,'GoldCloth'),(0,0,0),-math.pi/2);place(m,a,x1-.48,cy+.34,z)
   proxy((x1-.48,cy+.34,z+.44),(.78,1.92,.88),tag=r['id']+'_settee');actual+=1
 place(m,washstand(),cx,y1-.29,z);panel_mirror(m,cx,y1-.075,z+1.43,.42,.62)
 # Compact wardrobe by the door, clear of the central opening and berth.
 place(m,wardrobe(.62,1.98),x1-.39,y0+.34,z,math.pi)
 # Bell push and reading lamp at the head. Actual switch plate/cable.
 m.box((x0+.08,cy+.68,z+1.35),(.035,.09,.13),'Brass',.008);m.cylinder((x0+.053,cy+.68,z+1.35),.019,.025,'Black',8,(1,0,0))
 if kind=='cabin_captain':
  place(m,desk(1.4),x0+2.15,y0+.60,z,math.pi);place(m,chair('writing'),x0+2.15,y0+1.48,z);place(m,bookcase(1.3),x1-.28,cy,z,-math.pi/2);place(m,sofa(1.8,'Leather'),x1-1.0,cy,z,-math.pi/2)
 lamp(m,cx,cy,r['top']-.18)
 if r['door_wall']=='y1':
  m.v=[(x,2*cy-y,zz) for x,y,zz in m.v]
  m.f=[tuple(reversed(f)) for f in m.f]  # mirror has determinant -1
  for p in PROXIES[pstart:]:p['position'][1]=2*cy-p['position'][1];p['yaw']=-p['yaw']
  for p in LIGHTS[lstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2])
  for f in FIXTURES[fstart:]:
   f['bounds']=[(f['bounds'][0][0],2*cy-f['bounds'][1][1],f['bounds'][0][2]),(f['bounds'][1][0],2*cy-f['bounds'][0][1],f['bounds'][1][2])];f['position']=(f['position'][0],2*cy-f['position'][1],f['position'][2]);f['yaw']=-f['yaw']
  for p in SEATS[sstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2]);p['yaw']=-p['yaw']
 return {'actual_berths':actual,'inventory':'Iron/brass bedstead or two-tier berths; upholstered convertible berth where scheduled; panelled wardrobe, bowl/jug washstand, mirror, bell push and incandescent pendant.'}


def fit_dorm(m,r):
 x0,x1,y0,y1=rect(r);z=r['z']+.055;length=x1-x0;width=y1-y0;actual=0
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
    place(m,bunk(),float(x),yy,z,0);proxy((float(x),yy,z+1.1),(.76,1.96,2.2),0,tag=r['id']+'_bunk');actual+=2
 else:
  # Narrow crew wing: longitudinal bunks against each outer wall, a real
  # continuous aisle; small third-class wings have only one berth row.
  cy=(y0+y1)/2
  ys=[y0+.50,y1-.50] if width>3.0 else [y1-.48 if y0>0 else y0+.48]
  for i,x in enumerate(np.arange(x0+1.15,x1-.9,2.12)):
   if abs(x-r['door_u'])<1.1 and r['door_wall'][0]=='y':continue
   for yy in ys:
    place(m,bunk(),float(x),yy,z,math.pi/2);proxy((float(x),yy,z+1.1),(.76,1.96,2.2),math.pi/2,tag=r['id']+'_bunk');actual+=2
 # Enamel drinking-water tank / wash shelf at end, baggage racks overhead.
 m.lathe((x1-.45,y0+.38,z),[(0,.22),(.03,.25),(.72,.25),(.78,.22)],'Iron',12)
 m.tube([(x1-.45,y0+.38,z+.28),(x1-.17,y0+.38,z+.28),(x1-.17,y0+.38,z+.21)],.018,'Brass',7)
 if width>=8:
  for xx in [x0+3.6] if x1-x0>7.2 else []:
   place(m,table(2.25,.68),float(xx),cy,z)
   for side in (-1,1):
    yy=cy+side*.72;m.box((float(xx),yy,z+.45),(2.2,.28,.055),'Oak',.012)
    for dx in (-.82,.82):
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
  place(m,table(1.20,.50),xx,yy,z)
  m.box((xx,bench_y,z+.45),(1.15,.27,.055),'Oak',.012)
  for dx in (-.43,.43):
   for dy in (-.09,.09):m.rod((xx+dx,bench_y+dy,z+.02),(xx+dx,bench_y,z+.43),.025,'Iron',7)
  for dx in (-.30,.30):SEATS.append(dict(position=(xx+dx,bench_y,z+.43),yaw=math.pi if sign>0 else 0,size=(.38,.27,.10)))
  m.tags['CrewMessAlcove']+=1;mess_seats=2
 for x in np.arange(x0+1,x1-.5,4):lamp(m,float(x),(y0+y1)/2,r['top']-.12)
 return {'actual_berths':actual,'actual_mess_seats':mess_seats,'inventory':'Individually framed two-tier berths with mattress, pillow, blanket, retaining rails and ladders; continuous central aisle/cross aisles and drinking-water tank.'+(' Two-seat table/bench mess alcove in the berth-free entrance bay.' if mess_seats else '')}


def fit_public(m,r):
 x0,x1,y0,y1=rect(r);z=r['z']+.055;cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];actual_seats=0
 if kind in ('dining','dining_second','mess'):
  width=y1-y0;rows=[cy-4.65,cy-1.55,cy+1.55,cy+4.65] if width>11 else [cy-2.1,cy+2.1] if width>6 else [cy]
  usable=x1-x0-3.0;n=max(1,int(usable/3.15));step=usable/n
  for yy in rows:
   for i in range(n):
    xx=x0+1.5+(i+.5)*step;place(m,table(round(step-.10,3),.94,True),xx,yy,z)
    for dx in ((-step*.31,0,step*.31) if step>=2 else (-.32,.32)):
     for side in (-1,1):
      place(m,chair(),xx+dx,yy+side*.83,z,0 if side>0 else math.pi);place(m,service_setting(),xx+dx,yy+side*.28,z+.806,0 if side>0 else math.pi);actual_seats+=1
    lamp(m,xx,yy,r['top']-.10)
  # Buffet with framed doors/drawers and mirror at end, cased columns.
  place(m,wardrobe(1.4,1.0),x1-.50,y0+1.0,z,math.pi/2)
  for x in np.arange(x0+2.2,x1-1,4.2):
   for yy in (y0+.65,y1-.65):
    m.lathe((float(x),yy,z),[(0,.17),(.12,.18),(.20,.12),(r['top']-z-.26,.11),(r['top']-z-.16,.17),(r['top']-z-.10,.19)],'Ivory',12)
 elif kind in ('library','writing'):
  # Open bookcases with hundreds of separately coloured spine/page meshes.
  for side in (-1,1):
   yy=y0+.24 if side<0 else y1-.24
   for xx in np.arange(x0+1.3,x1-1,1.85):place(m,bookcase(1.50),float(xx),yy,z,0 if side>0 else math.pi)
  # Individual writing tables facing the light, not an enormous empty slab.
  xs=np.linspace(x0+2.0,x1-2.0,5 if x1-x0>16 else 4)
  for xx in xs:
   for side in (-1,1):
    yy=cy+side*1.85;place(m,desk(1.30),float(xx),yy,z,0 if side>0 else math.pi);place(m,chair('writing'),float(xx),yy-side*.86,z,math.pi if side>0 else 0);actual_seats+=1;lamp(m,float(xx),yy,r['top']-.12)
  for xx in (x0+1.15,x1-1.15):
   place(m,sofa(1.9,'LeatherGreen'),xx,cy,z,math.pi/2 if xx<x0+2 else -math.pi/2);actual_seats+=3
 elif kind in ('smoking','lounge_second','music'):
  for side in (-1,1):
   yy=y0+.7 if side<0 else y1-.7
   for xx in np.arange(x0+2,x1-1.5,3.5):
    place(m,sofa(2.25,'Leather' if kind=='smoking' else 'GoldCloth'),float(xx),yy,z,math.pi if side<0 else 0);actual_seats+=3
  for xx in np.arange(x0+2.4,x1-2.0,3.8):
   for side in (-1,1):
    yy=cy+side*1.8;place(m,table(1.15,.72),float(xx),yy,z);place(m,chair('armchair'),float(xx)-1.0,yy,z,-math.pi/2);place(m,chair('armchair'),float(xx)+1.0,yy,z,math.pi/2);actual_seats+=2
    lamp(m,float(xx),yy,r['top']-.12)
  if kind=='music':place(m,piano(),x0+2.1,cy,z,math.pi/2);place(m,chair(),x0+3.2,cy,z,math.pi/2)
  else:
   # Period mantels with a dark grille/recess, and a framed maritime chart.
   m.box((x0+.17,cy,z+.68),(.24,1.70,1.35),'Marble',.025);m.box((x0+.30,cy,z+.61),(.035,1.0,.86),'Black',.01);m.box((x0+.20,cy,z+1.38),(.52,1.92,.10),'Mahogany',.025)
   for yy in np.arange(cy-.44,cy+.49,.11):m.rod((x0+.33,float(yy),z+.25),(x0+.33,float(yy),z+.94),.009,'Brass',5)
   m.box((x0+.09,cy,z+1.98),(.04,1.8,.80),'Oak',.012);m.box((x0+.115,cy,z+1.98),(.015,1.64,.65),'Chart')
 return {'actual_seats':actual_seats,'inventory':'Period upholstered seating, turned/revolving chairs, fitted tables/desks, meaningful tableware or writing implements; open bookcases / pianoforte / fireplace as appropriate.'}


def fit_service(m,r):
 x0,x1,y0,y1=rect(r);z=r['z']+.055;cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];actual=0
 if kind in ('galley','bakery'):
  # Furnace/oven doors face the working aisle (+Y), not the close outer
  # bulkhead. The former unrotated range put its firing front 0.3m off-wall.
  place(m,range_unit(),x0+2.0,y0+1.0,z,math.pi)
  # Hood duct joins a dedicated corner flue (not random pipe decoration).
  m.box((x0+2.0,y0+1.0,z+2.05),(3.35,1.55,.22),'Iron',.03)
  for xx in np.arange(x0+2,x1-1.2,3.0):
   if xx<r['door_u'] and abs(xx-r['door_u'])<2:continue
   place(m,table(2.2,.75),float(xx),y1-.6,z)
   m.box((float(xx),y1-.6,z+.80),(.58,.34,.035),'Oak',.006)
   m.lathe((float(xx)+.5,y1-.60,z+.81),[(0,.14),(.12,.20),(.18,.22),(.19,.20),(.06,.08)],'Copper',14)
  # Galley and bakery join an exterior lagged common flue at deckhead
  # level. Never run one diagonal chimney through the writing room above.
  m.tube([(x0+2,y0+1,z+2.15),(-39.35,y0+1,z+2.25),(-39.35,-4.8,z+2.25)],.16,'Lagging',12)
  if kind=='galley':
   flue=Mesh();flue.tube([(-39.35,-4.8,z+2.25),(-39.35,-4.8,20.60)],.20,'Lagging',12)
   for zz in (14.4,17.2):flue.ring((-39.35,-4.8,zz),.24,.035,'Iron',16,6)
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
     place(m,staved_barrel() if i%3==1 else cargo_crate(),float(xx),yy,z+.015,0 if side<0 else math.pi)
   # Open chain bin, finite bars and interlinked stored chain at fore end.
   xx=x1-.50;m.box((xx,cy,z+.08),(.82,.98,.12),'Iron',.015)
   for yy in (cy-.47,cy+.47):
    for dx in (-.37,0,.37):m.rod((xx+dx,yy,z+.10),(xx+dx,yy,z+.85),.025,'Iron',8)
    m.rod((xx-.39,yy,z+.85),(xx+.39,yy,z+.85),.030,'Iron',8)
   for i in range(14):m.ring((xx-.27+(i%4)*.17,cy-.27+((i//4)%3)*.22,z+.17+(i//8)*.12),.095,.018,'Iron',14,6,(0,1,0) if i%2 else (0,0,1))
   proxy((xx,cy,z+.46),(.88,1.04,.92),tag=r['id']+'_chainbin')
  elif r['id']=='P_Coats':
   for i in range(4):place(m,folded_deckchair(),x0+.75+i*.70,y1-.26,z)
   place(m,shelving('linen'),x1-1.0,y1-.34,z)
   # Peg rail and hooks above the otherwise clear cloak-storage wall.
   m.box((x0+3.1,y0+.09,z+1.80),(4.8,.06,.08),'Oak',.008)
   for xx in np.arange(x0+1.1,x0+5.2,.55):m.tube([(float(xx),y0+.12,z+1.80),(float(xx),y0+.25,z+1.75),(float(xx),y0+.29,z+1.82)],.012,'Brass',8)
  else:
   for yy,ang in rows:
    for xx in np.arange(x0+1,x1-.6,1.7):
     if r['door_wall'][0]=='y' and abs(xx-r['door_u'])<1.40 and abs(yy-r[r['door_wall']])<.8:continue
     template=(mail_cubby() if kind=='mail' else drinks_rack() if kind=='bar' else ice_chest() if kind=='cold_store' and yy>cy else provision_rack() if kind=='cold_store' else shelving('pantry' if kind=='pantry' else 'linen'))
     place(m,template,float(xx),yy,z,ang)
  if kind=='pantry' and y1-y0>=3.0:
   for xx in np.arange(x0+1.3,x1-.9,2.4):
    if abs(xx-r['door_u'])<1.15:continue
    place(m,desk(1.4),float(xx),cy,z)
  if kind=='mail' and y1-y0>=2.4:
   place(m,desk(1.2),x0+1.0,cy,z,math.pi/2)
   # Tied letter bundles on the sorting surface, not a writing pad alone.
   for i in range(3):
    m.box((x0+1.0,cy-.30+i*.25,z+.85),(.28,.20,.075),'Paper',.004)
    m.rod((x0+.85,cy-.30+i*.25,z+.89),(x0+1.15,cy-.30+i*.25,z+.89),.005,'Rope',5)
 elif kind in ('bath','wc','third_wash'):
  if kind=='bath':
   place(m,bathtub(),cx,cy-.2,z,math.pi/2);place(m,washstand(),cx,y1-.3,z);panel_mirror(m,cx,y1-.08,z+1.5)
  else:
   n=max(1,int((x1-x0)/1.3))
   for i in range(n):
    xx=x0+(i+.5)*(x1-x0)/n;place(m,wc(),xx,y0+.75,z,math.pi)
    if n==1 and r['door_wall']=='y1':
     place(m,washstand(),x0+.29,cy+.55,z,math.pi/2);panel_mirror(m,x0+.08,cy+.55,z+1.5,ang=math.pi/2)
    else:place(m,washstand(),xx,y1-.35,z);panel_mirror(m,xx,y1-.08,z+1.5)
    if i<n-1:
     xx=x0+(i+1)*(x1-x0)/n;m.box((xx,y0+1.05,z+1.0),(.055,1.65,2.0),'Ivory');proxy((xx,y0+1.05,z+1.0),(.055,1.65,2.0),tag=r['id']+'_cubicle')
 elif kind=='barber':
  for xx in np.arange(x0+1,x1-.5,1.55):
   xx=float(xx);place(m,barber_chair(),xx,cy,z,math.pi);place(m,washstand(),xx,y1-.4,z);panel_mirror(m,xx,y1-.08,z+1.50,.75,.80)
   # Brush, razor and leather strop at each basin station.
   m.lathe((xx-.20,y1-.40,z+.85),[(0,.022),(.06,.026),(.08,.020),(.13,.030),(.15,.033)],'Walnut',12)
   m.cylinder((xx-.20,y1-.40,z+1.015),.034,.055,'Linen',12)
   m.box((xx-.20,y1-.64,z+.86),(.18,.025,.015),'Steel',.003)
   m.box((xx+.22,y1-.66,z+.46),(.055,.012,.48),'Leather',.005)
 elif kind=='hospital':
  for xx in (x0+1.1,x1-1.1):place(m,bed(),xx,cy,z);actual+=1
  place(m,washstand(),cx,y1-.35,z);place(m,wardrobe(.8,1.9),x1-.5,y0+.40,z,math.pi);place(m,desk(1.3),cx,cy,z);place(m,chair(),cx,cy-.85,z)
  place(m,medicine_cabinet(),x0+1.1,y0+.28,z,math.pi)
  place(m,medical_trolley(),cx+1.10,y1-.65,z)
 elif kind in ('office','chart','wheelhouse'):
  for xx in np.arange(x0+1.1,x1-.8,2.6):
   # An office desk must not sit immediately inside its own doorway.
   if r['door_wall']=='y1' and abs(float(xx)-r['door_u'])<1.25:continue
   place(m,desk(1.6),float(xx),y1-.65,z);place(m,chair('writing'),float(xx),y1-1.45,z,math.pi)
   m.box((float(xx),y1-.65,z+.82),(1.15,.44,.008),'Chart' if kind!='office' else 'Paper')
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
      yy=yy0+(i+.5)*step;m.cylinder((x1-.30,yy,z+zz+.13),.09,.30,['Canvas','BookRed','BookBlue','GoldCloth'][i%4],12,(1,0,0))
      m.ring((x1-.38,yy,z+zz+.13),.095,.008,'Rope',12,5,(1,0,0))
   proxy((x1-.28,cy,z+1.24),(.47,yy1-yy0,1.94),tag=r['id']+'_signalrack')
 elif kind=='stairhall':
  for xx in (x0+.6,x1-.6):
   for yy in (y0+.35,y1-.35):
    m.lathe((xx,yy,z),[(0,.16),(.10,.17),(.17,.12),(r['top']-z-.3,.10),(r['top']-z-.18,.17),(r['top']-z-.12,.17)],'Oak',12)
  if y1-y0>8:
   for yy in (y0+.65,y1-.65):place(m,sofa(2.0,'LeatherGreen'),x0+1.45,yy,z,math.pi if yy<cy else 0)
 # Purposeful light allocation, not random light spam.
 for xx in np.arange(x0+min(1.,(x1-x0)/2),x1-.3,4):lamp(m,float(xx),cy,r['top']-.12)
 return {'actual_berths':actual,'inventory':{'galley':'Three-oven coal range, firebrick base, burners, hollow copper pots and handles, hood/connected flue, work tables, cutting boards.','bakery':'Range/ovens, work benches and baking vessels.','bath':'Clawfoot ceramic tub and connected brass taps.','wc':'High-cistern ceramic WCs, bowl interiors, seats, flush chain and pipes; partitioned cubicles; bowl/jug washstands and mirrors.','wheelhouse':'Chart desks, writing seats and publications; helm, binnacle, telegraphs and navigation fixtures are separate functional meshes.','chart':'Central standing chart table with paired drawer pedestals, chart rollers, parallel rules and dividers; writing desks/seats, publications, open signal-flag and rolled-chart rack. No wireless.','office':'Door-clear writing desks/chairs, publications, ledgers and hinged-wheel iron safe.','mail':'Open letter-sorting cubbies with individually tied paper/parcels and a bundle-covered sorting table.','cargo':'Hollow slatted wooden crates with battens, iron straps, nail heads, rope handles and labels; hooped staved barrels and open stored-chain bin.','bar':'Steward service cabinets with paneled cupboards, marble counters, individual stoppered bottles and pewter measuring/drinking vessels.','cold_store':'Latched insulated ice chest with drain/catch pan, and separate racks of provision sacks and sealed ceramic jars; no powered refrigeration asserted.','hospital':'Two bedsteads, washstand, examination/writing table and chair, apothecary bottle/bandage cabinet, wheeled instrument trolley and cleanable tiled floor.','barber':'Pedestal reclining barber chairs with headrests, footboards and adjuster wheels; individual bowl/jug basins and mirrors, brushes, razors and leather strops.','stairhall':'Turned columns, upholstered waiting seats where space permits; actual cut-through stairs and handrails in separate stair module.'}.get(kind,'Fitted purpose-specific shelving/storage, office/chart/wash/medical equipment and incandescent lighting.')}


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
  ROOM_REPORT.append(dict(id=r['id'],name=r['name'],deck=r['deck'],kind=r['kind'],bounds=rect(r),z=r['z'],top=r['top'],floor_area_m2=round((r['x1']-r['x0'])*(r['y1']-r['y0']),2),source_objects=[o.name for o in obs],components=dict(m.tags),triangles=sum(len(o.data.loop_triangles) for o in obs),nominal_berths=r.get('berths',0),**inv))
  print('FURNISHED',r['id'],sum(len(o.data.loop_triangles) for o in obs),flush=True)
 return ROOM_REPORT
