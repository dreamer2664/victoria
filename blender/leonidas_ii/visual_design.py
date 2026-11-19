"""Authored room identities and physical ceiling datums, not random dressing.

Five cabin *types* may legitimately repeat. Public rooms have separate plans,
joinery and textiles. Working rooms are not decorated as miniature saloons.
All values are metric; no room, bulkhead, stair or plant datum is moved here.
"""
import math
from shipdesign.leonidas_ii import STAIRS,CASINGS,ROOMS,rect,overlap

# The actual 25mm finish is centred at deck+35mm. Furniture, accessories
# and finish meshes share this bearing datum; no nominal 55mm spacer.
FLOOR_FINISH_TOP=.0475

def finished_floor(r):return r['z']+FLOOR_FINISH_TOP


def clipped_finish_cells(bounds,holes=(),inlays=()):
 """Partition a finite floor rectangle; never throw away a whole edge tile
 or fill a true stair/casing opening. Inlays replace, never overlap, finish.
 """
 a,b,c,d=bounds
 intersecting=lambda q:min(b,q[1])-max(a,q[0])>1e-9 and min(d,q[3])-max(c,q[2])>1e-9
 holes=[q for q in holes if intersecting(q)];inlays=[q for q in inlays if intersecting(q)]
 xs=sorted({a,b,*[max(a,min(b,x)) for q in holes+inlays for x in q[:2]]})
 ys=sorted({c,d,*[max(c,min(d,y)) for q in holes+inlays for y in q[2:]]})
 contains=lambda q,x,y:q[0]<x<q[1] and q[2]<y<q[3]
 for x0,x1 in zip(xs,xs[1:]):
  for y0,y1 in zip(ys,ys[1:]):
   if x1-x0<.0002 or y1-y0<.0002:continue
   x,y=(x0+x1)/2,(y0+y1)/2
   if not any(contains(q,x,y) for q in holes):yield (x0,x1,y0,y1),any(contains(q,x,y) for q in inlays)

CABIN_TYPES=(
 dict(identity='Walnut and indigo',wood='Walnut',panel='Ivory',wall='CabinBlue',floor='CarpetNavy',cloth='ClothBlue',curtain='ClothBlue'),
 dict(identity='Honey oak and sage',wood='Oak',panel='Oak',wall='CabinSage',floor='CarpetSage',cloth='ClothSage',curtain='ClothSage'),
 dict(identity='Mahogany and claret',wood='Mahogany',panel='Mahogany',wall='WritingWall',floor='CarpetWine',cloth='Velvet',curtain='Velvet'),
 dict(identity='Painted ivory and plum',wood='Ivory',panel='Ivory',wall='CabinBlue',floor='CarpetNavy',cloth='ClothPlum',curtain='ClothPlum'),
 dict(identity='Oak and ochre',wood='Oak',panel='Oak',wall='CabinSage',floor='CarpetSage',cloth='GoldCloth',curtain='GoldCloth'),
)
WORKING={'galley','bakery','pantry','store','cargo','mail','cold_store','hospital','bath','wc','third_wash','steering','dorm_third','dorm_crew','mess'}
SANITARY={'galley','bakery','pantry','cold_store','hospital','bath','wc','third_wash'}

def design(r):
 k=r['kind'];v=int(r.get('variant',sum(map(ord,r['id']))%5))
 d=dict(identity='Plain oak working joinery',wood='Oak',panel='Oak',wall='Ivory',floor='Teak',cloth='ClothBlue',curtain=None,mould='Oak',ceiling='Ivory',fixture='opal',working=k in WORKING,variant=v)
 if k=='cabin_first':d.update(CABIN_TYPES[v%5]);d['fixture']='cabin'
 elif k=='cabin_captain':d.update(identity='Captain: walnut, blue wool and navigation library',wood='Walnut',panel='Walnut',wall='CabinBlue',floor='CarpetNavy',cloth='ClothBlue',curtain='ClothBlue',fixture='cabin')
 elif k=='cabin_officer':d.update(identity='Officer: painted berth frames and fitted oak stowage',panel='Oak',wall='CabinSage',cloth='ClothBlue',fixture='cabin')
 elif k=='cabin_second':d.update(identity='Second-class berth cabin, restrained sage/blue type '+str(v%3+1),panel='SagePaint',wall='Ivory',cloth=['Canvas','ClothBlue','ClothSage'][v%3],fixture='marine')
 elif k=='dining':d.update(identity='Ivory dining saloon: articulated banquet groups and service cross aisle',wood='Mahogany',panel='Ivory',wall='MusicWall',floor='CarpetWine',cloth='Velvet',mould='Ivory',fixture='chandelier')
 elif k=='library':d.update(identity='Oak library: central shared reading table, low window books and end alcoves',wood='Oak',panel='Oak',wall='LibraryWall',floor='Parquet',cloth='LeatherGreen',fixture='reading',curtain='ClothSage')
 elif k=='writing':d.update(identity='Quiet correspondence room: ivory secretaires and plum window seating',wood='Walnut',panel='Ivory',wall='WritingWall',floor='Parquet',cloth='ClothPlum',mould='Ivory',fixture='chandelier',curtain='ClothPlum')
 elif k=='smoking':d.update(identity='Mahogany club: billiards, cards and fireside conversation',wood='Mahogany',panel='Mahogany',wall='SmokingWall',floor='Parquet',cloth='Leather',fixture='club',curtain='ClothSage')
 elif k=='music':d.update(identity='Cream and blue music room: open grand and piano-facing horseshoe',wood='Walnut',panel='Ivory',wall='MusicWall',floor='Parquet',cloth='ClothBlue',mould='Ivory',fixture='chandelier',curtain='ClothBlue')
 elif k=='lounge_second':d.update(identity='Second-class games and newspaper lounge: oak and blue wool',panel='Oak',wall='SagePaint',floor='Teak',cloth='ClothBlue',fixture='opal')
 elif k=='dining_second':d.update(identity='Second-class dining: crosswise oak tables, blue chairs, sideboard',panel='Oak',wall='SagePaint',floor='Teak',cloth='ClothBlue',fixture='opal')
 elif k=='stairhall':d.update(identity='Oak stair hall: inset panels, turned newels and landing lights',panel='Oak',wall='MusicWall',floor='Parquet',cloth='LeatherGreen',fixture='opal')
 elif k in ('wheelhouse','chart'):d.update(identity='Navigation: teak/oak framing, working chart surfaces',wood='Teak' if k=='wheelhouse' else 'Oak',panel='Teak' if k=='wheelhouse' else 'Oak',wall='Ivory',fixture='marine')
 elif k=='office':d.update(identity='Purser: green leather, walnut records and secure storage',wood='Walnut',panel='Walnut',wall='CabinSage',fixture='cabin')
 elif k=='bar':d.update(identity='Steward bar: mahogany cupboards and marble work surfaces',wood='Mahogany',panel='Mahogany',wall='Ivory',fixture='opal')
 elif k=='barber':d.update(identity='Barber: opaque mirror bays, central daylight and cleanable dado',panel='Enamel',wall='SagePaint',floor='Tile',cloth='Leather',fixture='opal')
 if k in WORKING:
  d.update(wood='Oak',panel='Enamel' if k in SANITARY else 'SagePaint',wall='White' if k in SANITARY else 'Ivory',mould='Iron' if k=='steering' else 'SagePaint',floor='Tile' if k in SANITARY else 'Iron' if k=='steering' else 'Teak',fixture='marine',curtain=None)
 if not d['working'] and k not in ('dining','music','writing'):d['mould']=d['wood']
 return d


def ceiling_holes(r):
 holes=[]
 for s in STAIRS:
  if abs(s['z1']-r['top'])<.25 or abs(s['z0']-r['z'])<.05:
   h=(min(s['x0'],s['x1'])-.10,max(s['x0'],s['x1'])+.10,s['y']-s['width']/2-.10,s['y']+s['width']/2+.10)
   if overlap(h,rect(r)):holes.append(h)
 for c in CASINGS:
  if c['z0']<r['top']<c['z1'] and overlap(c['rect'],rect(r)):holes.append(c['rect'])
 return holes


def ceiling_beams(r):
 holes=ceiling_holes(r);xs=[];x=r['x0']+.30
 while x<r['x1']-.15:
  if not any(h[0]-.10<x<h[1]+.10 for h in holes):xs.append(x)
  x+=1.60
 return xs


def ceiling_anchor(r,x,y):
 """Find a real ceiling face; never mount a canopy in a stair/skylight void.

A canopy close to a beam is centered on that beam, not left to appear to
float 170 mm below an adjacent panel. Returns the ACTUAL face elevation.
"""
 holes=ceiling_holes(r)
 def valid(a,b):
  return r['x0']+.19<a<r['x1']-.19 and r['y0']+.19<b<r['y1']-.19 and not any(h[0]-.17<a<h[1]+.17 and h[2]-.17<b<h[3]+.17 for h in holes)
 candidates=[(x,y)]+[(x+dx,y+dy) for dx,dy in ((0,.45),(0,-.45),(.55,0),(-.55,0),(0,1.),(0,-1.),(1.1,0),(-1.1,0),(0,1.6),(0,-1.6))]
 for a,b in candidates:
  if not valid(a,b):continue
  beams=ceiling_beams(r);near=min(beams,key=lambda q:abs(q-a)) if beams else None
  if near is not None and abs(near-a)<.21 and valid(near,b):return near,b,r['top']-.215,'beam_soffit'
  return a,b,r['top']-.0475,'ceiling_soffit'
 # Stair halls can consist mostly of open well. Use an actual perimeter
 # ceiling strip if one exists; callers may instead add a wall-mounted light.
 for a,b in ((r['x0']+.32,r['y0']+.32),(r['x1']-.32,r['y1']-.32),(r['x0']+.32,r['y1']-.32),(r['x1']-.32,r['y0']+.32)):
  if valid(a,b):return a,b,r['top']-.0475,'ceiling_soffit'
 raise ValueError((r['id'],'No supporting ceiling face for fixture',x,y))


def is_external_window(r,wall,u):
 if wall[0]!='y':return r['kind']=='wheelhouse' and wall=='x1'
 side=1 if wall=='y1' else -1;edge=r[wall]
 # An aperture into another cabin's back wall or an internal corridor is
 # not an exterior window. Visibility is resolved for EACH window station.
 for other in ROOMS:
  if other['id']==r['id'] or other['deck']!=r['deck']:continue
  if not other['x0']-.04<u<other['x1']+.04:continue
  near=other['y0'] if side>0 else other['y1']
  if side*(near-edge)>.06:return False
 if abs(edge)<.75:return False
 return True


def washstand_stations(r):
 """Actual shared basin stations for geometry AND small toiletries."""
 x0,x1,y0,y1=rect(r);cx=(x0+x1)/2;cy=(y0+y1)/2;k=r['kind']
 if k=='bath':return [(cx,y1-.30,0.)]
 if k=='barber':return [(x0+1.10,y1-.40,0.),(x1-1.10,y1-.40,0.)]
 n=max(1,int((x1-x0)/1.3))
 if n==1 and r['door_wall']=='y1':return [(x0+.29,cy+.55,math.pi/2)]
 if r['id']=='P_Wash':
  assert n==4
  xs=[x0+.40,r['door_u']-r['door_width']/2-.70,r['door_u']+r['door_width']/2+.70,x1-.40]
 else:xs=[x0+(i+.5)*(x1-x0)/n for i in range(n)]
 return [(x,y1-.35,0.) for x in xs]
