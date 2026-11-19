"""Small, supported period fittings and non-interchangeable furniture families.
All geometry is authored here; ornament is subordinate to the room's purpose.
"""
import math
from functools import lru_cache
from meshkit import Mesh,LIGHTS,FIXTURE_MOUNTS,guarded_lamp,bolts,handwheel
from visual_design import design,ceiling_anchor,finished_floor


def recolour(template,mapping):
 m=Mesh();m.append(template);m.tiles=[mapping.get(t,t) for t in m.tiles];return m


def ceiling_fixture(m,r,x,y,style=None,over_table=False):
 """Place a fixture THROUGH a backplate in contact with a real soffit.
 The old supplied top-.18/top-.12 was below the ceiling, leaving a gap.
 """
 x,y,face,support=ceiling_anchor(r,x,y);style=style or design(r)['fixture']
 tile='Iron' if style=='marine' else 'Brass'
 m.cylinder((x,y,face-.008),.105,.024,tile,12)  # top embeds 4mm
 body_start=len(m.v);light_start=len(LIGHTS)
 if style=='marine':
  guarded_lamp(m,x,y,face-.016);drop=.344
 elif style in ('cabin','opal'):
  m.lathe((x,y,face-.018),[(0,.085),(-.035,.09),(-.075,.035),(-.105,.10)],'Brass',16)
  m.lathe((x,y,face-.12),[(0,.095),(-.025,.13),(-.12,.135),(-.19,.065)],'Porcelain',20)
  m.ring((x,y,face-.15),.132,.006,'Brass',16,5)
  m.cushion((x,y,face-.282),(.085,.085,.07),'Bulb');drop=.317
 else:
  # Low, three-branch electrolier. No dangling fixture in a standing lane.
  drop=min(.44 if over_table else .39,face-r['z']-(1.91 if over_table else 2.03))
  drop=max(.21,drop);scale=drop/.40
  m.lathe((x,y,face-.018),[(0,.085),(-.035,.09),(-.065,.032),(-.15*scale,.027),(-.22*scale,.070)],'Brass',16)
  for a in (0,math.tau/3,2*math.tau/3):
   radius=.30 if style in ('chandelier','club') else .23;cx=x+radius*math.cos(a);cy=y+radius*math.sin(a)
   m.tube([(x,y,face-.19*scale),(cx,cy,face-.23*scale),(cx,cy,face-.27*scale)],.012,'Brass',8)
   m.lathe((cx,cy,face-.25*scale),[(0,.045),(-.018,.085),(-.07*scale,.105),(-.14*scale,.065)],'ClothSage' if style=='club' else 'Porcelain',16)
   m.cushion((cx,cy,face-.36*scale),(.075,.075,.06),'Bulb')
  m.lathe((x,y,face-.23*scale),[(0,.045),(-.10*scale,.035),(-.14*scale,.012)],'Brass',12)
  m.tags['ThreeBranchElectrolier']+=1
 # In the few low beam bays a compact fixture is required, not a lower
 # head clearance. Keep the backplate fixed; shorten only the actual body.
 if not over_table and face-drop<r['z']+2.035:
  factor=max(.55,(face-r['z']-2.035)/drop)
  m.v[body_start:]=[(a,b,face+(c-face)*factor) for a,b,c in m.v[body_start:]]
  for light in LIGHTS[light_start:]:
   a,b,c=light['position'];light['position']=(a,b,face+(c-face)*factor)
  drop*=factor
 LIGHTS.append(dict(position=(x,y,face-drop+.035),range_m=4.8,brightness=1.0 if style not in ('marine','cabin') else .7)) if style!='marine' else None
 FIXTURE_MOUNTS.append(dict(room=r['id'],type='ceiling',style=style,position=(x,y,face),support=support,backplate_top=face+.004,bottom=face-drop,over_table=over_table))
 m.tags['SupportedCeilingFixture']+=1
 return x,y,face


def reading_sconce(m,r,x,y,z,ang=0):
 """Local wall is at Y=0, room side -Y. Substantial rear block intersects wall."""
 q=Mesh();q.box((0,.012,0),(.095,.105,.18),'Oak',.012);q.box((0,-.047,0),(.075,.025,.14),'Brass',.01)
 q.tube([(0,-.06,-.035),(0,-.18,-.035),(0,-.21,.075)],.012,'Brass',8)
 q.lathe((0,-.21,.065),[(0,.035),(-.045,.085),(-.10,.09)],'Porcelain',16)
 q.cushion((0,-.21,-.035),(.07,.07,.07),'Bulb');m.append(q,(x,y,z),ang)
 ca,sa=math.cos(ang),math.sin(ang);LIGHTS.append(dict(position=(x+.21*sa,y-.21*ca,z-.06),range_m=2.2,brightness=.32));m.tags['BulkheadReadingSconce']+=1


@lru_cache(None)
def round_table(radius=.54,wood='Walnut',height=.75):
 m=Mesh();m.lathe((0,0,height-.055),[(0,radius-.025),(.025,radius),(.06,radius),(.075,radius-.025)],wood,32)
 m.lathe((0,0,.08),[(0,.14),(.06,.19),(.12,.11),(.25,.075),(.32,.13),(.40,.085),(height-.12,.10)],wood,16)
 for a in (0,math.tau/3,2*math.tau/3):
  m.tube([(0,0,.22),(.22*math.cos(a),.22*math.sin(a),.09),(.40*math.cos(a),.40*math.sin(a),.045)],.035,wood,8)
  m.cylinder((.40*math.cos(a),.40*math.sin(a),.012),.040,.024,wood,10)
 m.tags['RoundPedestalTable']+=1;return m


@lru_cache(None)
def plain_chair(cloth='ClothBlue',wood='Oak',arms=False):
 """Splayed four-legged second-class/cane-frame chair, not a red swivel copy."""
 m=Mesh()
 for x in (-.21,.21):
  for y in (-.20,.20):
   m.cylinder((x*1.15,y*1.15,.013),.027,.026,wood,8)
   m.rod((x*1.15,y*1.15,.02),(x,y,.44),.024,wood,8)
 for y in (-.20,.20):m.rod((-.21,y,.25),(.21,y,.25),.017,wood,8)
 m.box((0,0,.43),(.49,.47,.065),wood,.018);m.cushion((0,-.01,.48),(.44,.43,.075),cloth)
 for x in (-.21,.21):m.rod((x,.2,.44),(x,.24,.98),.026,wood,8)
 for z in (.69,.91):m.box((0,.23,z),(.43,.045,.075),wood,.012)
 m.cushion((0,.215,.80),(.35,.055,.18),cloth)
 if arms:
  for x in (-.27,.27):m.tube([(x,-.18,.45),(x,-.19,.68),(x,.20,.72)],.024,wood,8)
 m.tags['FourLegSideChair']+=1;return m


@lru_cache(None)
def utility_table(length=1.8,width=.70,height=.86,top='Oak'):
 m=Mesh();l,w=length,width
 m.box((0,0,height-.035),(l,w,.07),top,.012)
 for x in (-l/2+.14,l/2-.14):
  for y in (-w/2+.10,w/2-.10):m.box((x,y,height/2-.03),(.065,.065,height-.06),'Oak',.008)
  m.box((x,0,.20),(.07,w-.10,.055),'Oak',.008)
 for y in (-w/2+.08,w/2-.08):m.box((0,y,height-.13),(l-.16,.045,.16),'Oak',.008)
 m.box((0,0,.18),(l-.25,w-.18,.035),'Oak',.008)
 m.tags['UtilityWorkbench']+=1;return m


@lru_cache(None)
def plain_bench(length=1.8,wood='Oak',back=True):
 m=Mesh();l=length
 for x in (-l/2+.16,l/2-.16):
  for y in (-.19,.19):
   # Flat soles sit on the common finished surface, not a nominal spacer.
   m.cylinder((x,y,.015),.044,.030,'Iron',12)
   m.rod((x,y,.015),(x,y*.85,.43),.027,'Iron',8)
  # Each of the three independent slats bears on an actual cross bearer.
  m.box((x,0,.427),(.080,.47,.045),'Iron',.006)
  if back:m.tube([(x,.16,.40),(x,.23,.83),(x,.27,.95)],.024,'Iron',8)
 for y in (-.16,0,.16):m.box((0,y,.46),(l,.145,.055),wood,.010)
 if back:
  for z in (.66,.83):m.box((0,.23,z),(l,.045,.13),wood,.010)
 m.tags['FittedSlatBench']+=1;return m


@lru_cache(None)
def low_bookcase(width=1.5,variant=0,wood='Oak'):
 m=Mesh();w=width
 # Two proper shelves of normal-sized books below the 1.155m sill; not a
 # vertically squashed tall bookcase or a hidden window behind a cabinet.
 m.box((0,.16,.51),(w,.025,1.02),wood)
 for x in (-w/2+.035,w/2-.035):m.box((x,0,.51),(.07,.37,1.02),wood,.010)
 for zz in (.08,.53,1.01):m.box((0,0,zz),(w+.035,.40,.055),wood,.010)
 for row,zz in enumerate((.11,.56)):
  for j in range(16):
   if (j+variant*3+row)%17 in (0,1):continue
   xx=-w/2+.13+j*(w-.26)/16;h=.26+((j*3+row+variant)%5)*.018;col=['BookGreen','BookBlue','BookRed','Walnut'][(j+row+variant)%4]
   m.box((xx,-.005,zz+h/2),(.058,.24,h),'Paper',.002);m.box((xx,-.132,zz+h/2),(.063,.022,h+.010),col,.002)
   for dz in (.05,h-.025):m.box((xx,-.145,zz+dz),(.052,.003,.006),'Brass')
 m.tags['LowWindowBookcase']+=1;return m


@lru_cache(None)
def book_stack(variant=0):
 m=Mesh();h=.003
 for i in range(2+variant%2):
  th=.035+(i%2)*.009;q=Mesh();q.box((0,0,h+th/2),(.23,.30,th),'Paper',.003)
  for z in (h,h+th):q.box((0,0,z),(.25,.32,.006),['BookBlue','BookRed','BookGreen'][(i+variant)%3],.002)
  m.append(q,(0,0,0),(.07 if i%2 else -.035));h+=th+.0058
 m.tags['ReadingBooks']+=1;return m


def paper_and_ink(m,x,y,z,variant=0):
 m.box((x,y,z+.0028),(.23,.31,.006),'Paper',.002)
 for i in range(5):m.box((x-.015,y-.09+i*.036,z+.006),(.14,.0015,.0008),'Walnut')
 m.lathe((x+.25,y+.10,z),[(0,.032),(.045,.038),(.065,.023)],'BookBlue',12)
 m.rod((x+.25,y+.10,z+.065),(x+.29,y+.08,z+.24),.003,'Walnut',5)
 if variant%2:m.box((x-.17,y+.12,z+.008),(.14,.09,.009),'Paper',.003)


def framed_panel(m,x,y,z,w=1.0,h=.65,tile='Seascape',ang=0,wood='Walnut'):
 q=Mesh();q.box((0,0,0),(w+.10,.055,h+.10),wood,.014);q.box((0,-.032,0),(w,.012,h),tile)
 # Brass backs enter the real wooden face by 0.2mm; the former
 # -38mm centres left the complete four-strip surround 1.5mm in air.
 for xx in (-w/2-.022,w/2+.022):q.box((xx,-.0363,0),(.025,.018,h+.069),'Brass',.003)
 # Butt joints, never duplicated coplanar brass faces at the four corners.
 for zz in (-h/2-.022,h/2+.022):q.box((0,-.0363,zz),(w+.019,.018,.025),'Brass',.003)
 m.append(q,(x,y,z),ang);m.tags['MountedFramedPanel']+=1


def wall_clock(m,x,y,z,ang=0):
 q=Mesh();q.cylinder((0,0,0),.205,.075,'Walnut',24,(0,1,0));q.cylinder((0,-.042,0),.176,.012,'Dial',32,(0,1,0));q.ring((0,-.05,0),.18,.015,'Brass',28,6,(0,1,0));m.append(q,(x,y,z),ang);m.tags['BulkheadClock']+=1


def tea_tray(m,x,y,z,variant=0):
 m.box((x,y,z+.014),(.54,.35,.028),'Steel',.012)
 m.lathe((x-.10,y,z+.0278),[(0,.065),(.04,.10),(.15,.09),(.21,.035),(.23,.03)],'Porcelain',16)
 m.lathe((x-.10,y,z+.2478),[(0,.043),(.015,.055),(.035,.012)],'Porcelain',16)
 m.tube([(x-.18,y,z+.14),(x-.25,y,z+.20),(x-.27,y,z+.23)],.016,'Porcelain',8)
 m.ring((x+.02,y,z+.16),.055,.009,'Porcelain',14,5,(0,1,0))
 for yy in (y-.10,y+.10):
  m.lathe((x+.16,yy,z+.0278),[(0,.047),(.012,.057),(.022,.051),(.027,.035),(.11,.043),(.115,.039),(.04,.030)],'Porcelain',14)
  m.ring((x+.213,yy,z+.1008),.022,.006,'Porcelain',12,5,(0,1,0))
 m.tags['TeaServiceTray']+=1


@lru_cache(None)
def billiard_table():
 # A three-ball carom table is period-appropriate and has NO pockets.
 # The old six black discs were raised solids, not real pocket openings.
 m=Mesh();l,w=3.0,1.62
 for x in (-1.12,1.12):
  for y in (-.55,.55):m.lathe((x,y,0),[(0,.08),(.09,.10),(.20,.075),(.31,.11),(.42,.095),(.68,.105)],'Mahogany',12)
 m.box((0,0,.72),(l,w,.22),'Mahogany',.035);m.box((0,0,.846),(l-.25,w-.25,.035),'BilliardBaize',.01)
 # One closed, mitred annular rail. Four full-length bevelled boxes had
 # overlapping coplanar top faces at all four corners: valid components
 # individually, but dark false-pocket/z-fighting artifacts in real pixels.
 # Every corner and bevel now shares vertices; the carom bed has no pockets.
 outer=(l/2+.01,w/2+.01);inner=(l/2-.15,w/2-.15);bevel=.015
 rings=[(*outer,.825),(*outer,.910),(outer[0]-bevel,outer[1]-bevel,.925),
        (inner[0]+bevel,inner[1]+bevel,.925),(*inner,.910),(*inner,.825)]
 vv=[(sx*xx,sy*yy,zz) for xx,yy,zz in rings for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
 ff=[(4*k+j,4*k+(j+1)%4,4*((k+1)%len(rings))+(j+1)%4,4*((k+1)%len(rings))+j) for k in range(len(rings)) for j in range(4)]
 m.add(vv,ff,'Walnut',tag='SingleMitredCaromRail')
 for x,y,t in ((-.65,.15,'Porcelain'),(.37,-.21,'Red'),(.63,.33,'Ivory')):
  m.lathe((x,y,.8633),[(0,.004),(.01,.023),(.027,.028),(.05,.015),(.055,.002)],t,16)
 v=len(m.v);m.rod((-.95,-.35,.90),(.75,.22,.90),.009,'Oak',8);m.rest(v,.8635)
 m.tags['BilliardTable']+=1;m.tags['PocketlessThreeBallCaromTable']+=1;return m


def game_board(m,x,y,z,game='chess'):
 m.box((x,y,z+.014),(.47,.47,.028),'Walnut',.010)
 for i in range(8):
  for j in range(8):m.box((x-.196+i*.056,y-.196+j*.056,z+.031),(.055,.055,.007),'Ivory' if (i+j)%2 else 'Walnut')
 if game=='chess':
  for side in (-1,1):
   for i in range(8):
    xx=x-.196+i*.056;yy=y+side*.14
    m.lathe((xx,yy,z+.0343),[(0,.017),(.008,.018),(.017,.012),(.038,.009),(.045,.014),(.056,.008)],'Porcelain' if side>0 else 'Black',8)
 else:
  for j in range(4):
   m.box((x-.11+j*.075,y,z+.0443),(.055,.10,.02),'Porcelain',.004)
   for q in range(j+1):m.cylinder((x-.11+j*.075,y-.026+q*.015,z+.0553),.003,.003,'Black',6)
 m.tags['ChessBoard' if game=='chess' else 'DominoBoard']+=1


@lru_cache(None)
def grand_piano():
 """85-note grand; every carrier, string group, pedal and caster is finite."""
 m=Mesh();outline=[(-.88,-.55),(.88,-.55),(.89,.10),(.86,.52),(.70,1.05),(.45,1.44),(.12,1.64),(-.21,1.67),(-.54,1.48),(-.77,1.10),(-.88,.58)]
 n=len(outline);vv=[(x,y,z) for z in (.73,.97) for x,y in outline]
 vv += [(x*.94,y*.95,z) for z in (.73,.97) for x,y in outline];ff=[]
 for i in range(n):
  j=(i+1)%n;ff.extend([(i,j,j+n,i+n),(2*n+i,3*n+i,3*n+j,2*n+j),(n+i,n+j,3*n+j,3*n+i),(i,2*n+i,2*n+j,j)])
 m.add(vv,ff,'Walnut')
 # Full outline soundboard reaches the tail leg. Former short box ended
 # 440mm before that leg, and left the harp hovering above the soundboard.
 ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 m.add([(x,y,z) for z in (.71,.755) for x,y in outline],ff,'Walnut')
 m.box((0,.38,.777),(1.48,1.52,.050),'Brass',.014)
 for yy in (-.26,1.04):m.box((0,yy,.819),(1.48,.055,.036),'Walnut',.006)
 for i in range(32):m.rod((-.69+i*.042,-.26,.83),(-.53+i*.029,1.04,.83),.0018,'Copper',6)
 # Lid terminates behind the music rack. It no longer slices through the
 # sheet music. Its prop starts on the actual harp, not in empty air.
 lidoutline=[(x,max(-.25,y)) for x,y in outline]
 lid=Mesh();lid.add([(x,y,z) for z in (0,.026) for x,y in lidoutline],ff,'Walnut')
 lid.v=[(x,y,1.00+z+.30*(x+.88)/1.76) for x,y,z in lid.v];m.append(lid)
 m.rod((.64,.65,.800),(.64,.65,1.269),.016,'Walnut',8)
 # Both hinge barrels lie on the straight left rim. The former rear
 # barrel at y=.78 missed the curved rim and was suspended beside it.
 for y in (-.17,.40):m.cylinder((-.875,y,.987),.018,.16,'Brass',12,(0,1,0))
 m.box((0,-.41,.93),(1.69,.28,.050),'Walnut',.008)
 m.box((0,-.65,.77),(1.75,.33,.11),'Walnut',.018)
 white=1.65/50
 for i in range(50):m.box((-.825+(i+.5)*white,-.665,.837),(white-.0015,.30,.019),'Porcelain',.002)
 for i in range(49):
  if i%7 not in (2,6):m.box((-.825+(i+1)*white,-.59,.862),(.019,.16,.038),'Black',.002)
 for x,y in ((-.72,-.37),(.72,-.37),(-.10,1.35)):
  m.lathe((x,y,.045),[(0,.045),(.06,.065),(.14,.037),(.39,.060),(.62,.042),(.71,.075)],'Walnut',12)
  m.cylinder((x,y,.040),.033,.036,'Brass',16,(1,0,0))
  m.ring((x,y,.040),.032,.008,'Iron',16,8,(1,0,0))
 m.box((0,-.40,1.08),(.66,.038,.27),'Walnut',.008)
 m.box((0,-.422,1.09),(.53,.012,.23),'Paper')
 # A suspended lyre, rather than three unsupported bent rods.
 for x in (-.20,.20):m.rod((x,.13,.15),(x,.13,.735),.025,'Walnut',10)
 m.box((0,.13,.155),(.46,.12,.07),'Walnut',.008)
 for x in (-.13,0,.13):m.tube([(x,.13,.14),(x,-.34,.13),(x,-.49,.08)],.013,'Brass',8)
 m.tags['Pianoforte']+=1;m.tags['ConnectedSoundboardHarpLidAndPedalLyre']+=1;return m


@lru_cache(None)
def piano_stool():
 # A genuine three-foot stool: the turned hub is ABOVE the floor, carried
 # by three splayed legs with flattened wooden foot ends. The former hub
 # sat on the floor while all three decorative tips stopped ~18mm above it.
 m=Mesh();m.lathe((0,0,0),[(.11,.065),(.14,.09),(.19,.064),(.39,.055),(.43,.15)],'Walnut',12)
 for a in (0,math.tau/3,2*math.tau/3):
  x,y=.24*math.cos(a),.24*math.sin(a)
  m.tube([(0,0,.20),(.15*math.cos(a),.15*math.sin(a),.08),(x,y,.04)],.024,'Walnut',8)
  m.lathe((x,y,0),[(0,.036),(.010,.040),(.034,.029),(.050,.018)],'Walnut',12)
 m.cushion((0,0,.47),(.43,.37,.10),'ClothBlue');m.tags['ThreeFootPianoStool']+=1;m.tags['RevolvingChair']+=1;return m


def rug(m,x,y,z,length,width,cloth='CarpetNavy'):
 # A fitted textile INLAY in the 25mm floor finish, not a hovering mat
 # or an 8mm slab driven up through already floor-seated furniture feet.
 m.box((x,y,z-.0035),(length,width,.008),cloth,.002)
 for yy in (y-width/2+.07,y+width/2-.07):m.box((x,yy,z+.00055),(length-.165,.025,.0007),'GoldCloth')
 for xx in (x-length/2+.07,x+length/2-.07):m.box((xx,y,z+.00055),(.025,width-.10,.0007),'GoldCloth')


def cabin_accessories(m,r):
 d=design(r);x0,x1,y0,y1=(r[k] for k in ('x0','x1','y0','y1'));cx=(x0+x1)/2;cy=(y0+y1)/2;z=finished_floor(r)
 # A bulkhead-fastened reading shelf above the berth, clear of access strip.
 m.box((x0+.135,cy+.60,z+1.02),(.23,.49,.035),d['wood'],.008)
 for yy in (cy+.41,cy+.79):m.rod((x0+.05,yy,z+.86),(x0+.23,yy,z+1.0),.010,'Brass',6)
 m.append(book_stack(d['variant']%3),(x0+.14,cy+.60,z+1.0373),math.pi/2,scale=(.65,.60,.65))
 reading_sconce(m,r,x0+.09,cy+.60,z+1.51,math.pi/2)
 # Folded towel on a rod whose end brackets enter the washstand wall.
 yy=y1-.13
 for xx in (cx-.24,cx+.24):m.rod((xx,y1-.04,z+1.01),(xx,yy,z+1.01),.011,'Brass',7)
 m.rod((cx-.25,yy,z+1.01),(cx+.25,yy,z+1.01),.010,'Brass',8)
 m.box((cx,yy-.015,z+.88),(.31,.03,.26),'Linen',.006)
 # Only single-berth cabins receive this floor-seated case. Two-tier
 # bunks already have their own supported stowage; do not intersect it.
 if r['kind'] not in ('cabin_second','cabin_officer'):
  m.box((x0+.54,cy-.37,z+.12),(.58,.65,.24),'Leather',.018)
  for yy0 in (cy-.57,cy-.20):m.box((x0+.54,yy0,z+.245),(.56,.026,.012),'Brass',.003)
 # Different, still purposeful wall dressing for the five actual types.
 if d['variant'] in (0,2,4):framed_panel(m,x0+.10,cy-.50,z+1.67,.48,.34,'Seascape',math.pi/2,d['wood'])
 else:framed_panel(m,x0+.10,cy-.50,z+1.67,.38,.41,'Notice',math.pi/2,d['wood'])
 m.tags['FittedCabinAccessories']+=1
