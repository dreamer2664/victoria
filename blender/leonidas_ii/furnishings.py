"""New period furnishing geometry. Local +Y is the back of a chair/desk.
Profiles, open joinery, rolled arms, bowl interiors and hardware are actual
mesh geometry. Common templates are repeated, not substituted by texture boxes.
"""
import math
from functools import lru_cache
from meshkit import Mesh,handwheel,bolts

@lru_cache(None)
def chair(style='dining'):
 m=Mesh();wood='Oak' if style=='writing' else 'Mahogany';seat='LeatherGreen' if style=='writing' else 'Velvet'
 if style in ('dining','writing'):
  # Iron/brass revolving pedestal with four splayed feet.
  m.lathe((0,0,0),[(0,.12),(.04,.14),(.08,.09),(.14,.06),(.28,.055),(.33,.10),(.38,.095),(.41,.20)],'Iron',12)
  for a in (0,math.pi/2,math.pi,math.pi*1.5):
   m.tube([(0,0,.19),(.15*math.cos(a),.15*math.sin(a),.08),(.27*math.cos(a),.27*math.sin(a),.035)],.024,'Iron',6)
  m.lathe((0,0,.445),[(-.025,.225),(0,.25),(.045,.235),(.065,.19)],seat,16)
  for x in (-.20,.20):m.lathe((x,.18,.41),[(0,.025),(.14,.025),(.25,.018),(.43,.023),(.53,.028)],wood,8)
  m.cushion((0,.185,.76),(.39,.09,.31),seat)
  m.tube([(-.21,.18,.83),(-.17,.195,.95),(0,.20,1.0),(.17,.195,.95),(.21,.18,.83)],.023,wood,8)
  m.rod((-.20,.2,.64),(.20,.2,.64),.021,wood,8)
  if style=='writing':
   for x in (-.25,.25):m.tube([(x,-.15,.48),(x,-.17,.68),(x,.19,.73)],.023,wood,8)
 else:
  for x in (-.31,.31):
   for y in (-.29,.29):m.lathe((x,y,0),[(0,.035),(.045,.045),(.08,.028),(.20,.035)],wood,8)
  m.box((0,0,.24),(.76,.72,.16),wood,.035)
  m.cushion((0,-.015,.40),(.70,.68,.22),seat)
  m.cushion((0,.29,.70),(.70,.22,.68),seat)
  for x in (-.36,.36):
   m.cushion((x,0,.57),(.20,.75,.27),seat)
   m.rod((x,-.29,.25),(x,-.29,.6),.035,wood,8)
  for x in (-.20,0,.20):
   for z in (.6,.8):m.cylinder((x,.167,z),.013,.008,'Brass',6,(0,1,0))
 m.tags['RevolvingChair' if style in ('dining','writing') else 'UpholsteredArmchair']+=1
 return m

@lru_cache(None)
def sofa(length=2.1,material='Leather'):
 m=Mesh();l=length
 for x in (-l/2+.17,l/2-.17):
  for y in (-.25,.25):m.lathe((x,y,0),[(0,.035),(.05,.05),(.10,.029),(.22,.04)],'Mahogany',8)
 m.box((0,0,.23),(l,.74,.17),'Mahogany',.04)
 n=max(2,round(l/.64));w=(l-.25)/n
 for i in range(n):
  x=-l/2+.125+(i+.5)*w;m.cushion((x,-.05,.43),(w-.025,.68,.23),material);m.cushion((x,.29,.75),(w-.02,.24,.64),material)
  m.cylinder((x,.163,.74),.015,.012,'Brass',6,(0,1,0))
 for x in (-l/2+.06,l/2-.06):
  m.cushion((x,0,.61),(.22,.78,.26),material)
  m.lathe((x,-.31,.25),[(0,.04),(.08,.032),(.22,.035),(.34,.048)],'Mahogany',8)
 m.tags['RolledArmSettee']+=1;return m

@lru_cache(None)
def table(length=2.8,width=1.0,cloth=False):
 m=Mesh();l,w=length,width
 m.box((0,0,.745),(l,w,.075),'Mahogany',.025);m.box((0,0,.69),(l-.10,w-.09,.05),'Mahogany',.015)
 # Raised moulded apron and turned pedestal ends, not four square blocks.
 for y in (-w/2+.055,w/2-.055):m.box((0,y,.63),(l-.20,.065,.16),'Mahogany',.01)
 for x in (-l/2+.42,l/2-.42):
  m.lathe((x,0,.06),[(0,.14),(.04,.16),(.08,.09),(.20,.08),(.27,.13),(.32,.12),(.37,.055),(.52,.08),(.57,.14)],'Mahogany',12)
  m.box((x,0,.055),(.38,w*.85,.07),'Mahogany',.025)
 m.rod((-l/2+.42,0,.26),(l/2-.42,0,.26),.035,'Mahogany',8)
 if cloth:
  m.box((0,0,.791),(l+.025,w+.025,.012),'Linen',.003)
  for y in (-w/2-.012,w/2+.012):m.box((0,y,.72),(l+.024,.012,.14),'Linen',.004)
 m.tags['TurnedDiningTable']+=1;return m

@lru_cache(None)
def service_setting():
 m=Mesh();m.lathe((0,0,0),[(0,.09),(.012,.10),(.018,.11),(.026,.15),(.038,.16),(.045,.155),(.025,.11),(.023,.03)],'Porcelain',16)
 m.ring((0,0,.04),.145,.004,'Brass',16,4)
 m.lathe((.21,.14,.015),[(0,.045),(.008,.055),(.016,.055),(.021,.043),(.03,.04),(.10,.044),(.105,.041),(.035,.031)],'Porcelain',12)
 m.ring((.265,.14,.08),.026,.007,'Porcelain',10,4,(0,1,0))
 m.box((-.20,-.015,.025),(.018,.24,.012),'Steel',.005);m.box((.20,-.015,.025),(.018,.24,.012),'Steel',.005)
 for x in (-.207,-.199,-.191):m.rod((x,.10,.025),(x,.145,.025),.003,'Steel',4)
 m.box((0,-.22,.018),(.14,.10,.015),'Linen',.01)
 m.tags['PlaceSetting']+=1;return m

@lru_cache(None)
def bed(style='first'):
 m=Mesh();w=.78;l=1.96
 # Four lathe-turned brass posts, finials, curved head/foot top, spindles.
 for x in (-w/2,w/2):
  for y in (-l/2,l/2):
   h=1.15 if y>0 else .87
   m.lathe((x,y,0),[(0,.023),(.04,.038),(.07,.025),(.45,.025),(.48,.04),(.52,.026),(h-.06,.026),(h-.035,.045),(h,.018)],'Brass' if style=='first' else 'Iron',8)
 for y,h in [(-l/2,.81),(l/2,1.09)]:
  pts=[]
  for j in range(9):x=-w/2+w*j/8;pts.append((x,y,h+.10*(1-(2*x/w)**2)))
  m.tube(pts,.021,'Brass' if style=='first' else 'Iron',7)
  for x in (-.27,-.135,0,.135,.27):m.rod((x,y,.48),(x,y,h+.08),.012,'Brass' if style=='first' else 'Iron',6)
 for x in (-w/2,w/2):m.rod((x,-l/2,.42),(x,l/2,.42),.024,'Iron',6)
 m.cushion((0,0,.53),(w-.02,l-.04,.22),'Linen',tag='Mattress')
 m.cushion((0,-.18,.655),(w,l-.48,.055),'Mattress')
 m.cushion((0,.68,.70),(w-.11,.42,.15),'Linen',tag='Pillow')
 m.box((0,-.57,.695),(w-.02,.42,.012),'Velvet' if style=='first' else 'Canvas',.003)
 m.tags['SingleBerth']+=1;return m

@lru_cache(None)
def bunk():
 m=Mesh();w=.72;l=1.92
 for x in (-w/2,w/2):
  for y in (-l/2,l/2):m.cylinder((x,y,1.12),.023,2.24,'Iron',6)
 for z in (.45,1.46):
  m.box((0,0,z),(w,l,.075),'Oak',.018)
  m.cushion((0,0,z+.10),(w-.04,l-.04,.15),'Mattress')
  m.cushion((0,.69,z+.21),(w-.10,.40,.13),'Linen')
  m.box((0,-.54,z+.19),(w-.04,.63,.025),'Canvas',.006)
  for x in (-w/2,w/2):m.rod((x,-l/2,z+.26),(x,l/2,z+.26),.014,'Iron',5)
  for y in (-l/2,l/2):m.rod((-w/2,y,z+.30),(w/2,y,z+.30),.016,'Iron',6)
 for z in (.27,.56,.85,1.14):m.rod((-.23,-l/2-.025,z),(.23,-l/2-.025,z),.012,'Iron',5)
 m.tags['TwoBerthBunk']+=1;return m

@lru_cache(None)
def wardrobe(width=.7,height=2.05):
 m=Mesh();w=width;h=height
 m.box((0,0,h/2),(w,.53,h),'Oak',.018)
 # proud door stiles, inset panels and central hinges
 for x in (-w/2+.05,w/2-.05):m.box((x,-.285,h/2),(.07,.055,h-.12),'Oak',.01)
 for z in (.15,h*.50,h-.14):m.box((0,-.29,z),(w-.07,.06,.07),'Oak',.008)
 for z,hh in [(h*.275,h*.31),(h*.75,h*.32)]:m.box((0,-.28,z),(w-.17,.045,hh),'Mahogany',.012)
 m.box((0,0,h+.025),(w+.08,.59,.075),'Oak',.015)
 for z in (.30,h- .30):m.cylinder((-w/2+.03,-.32,z),.013,.07,'Brass',6)
 m.ring((w*.27,-.325,h*.49),.026,.007,'Brass',10,4,(1,0,0))
 m.tags['PanelledWardrobe']+=1;return m

@lru_cache(None)
def washstand():
 m=Mesh()
 for x in (-.25,.25):
  for y in (-.18,.18):m.lathe((x,y,0),[(0,.026),(.08,.030),(.31,.022),(.59,.028),(.77,.026)],'Oak',8)
 m.box((0,0,.28),(.55,.40,.035),'Oak',.01);m.box((0,0,.71),(.59,.45,.17),'Oak',.015);m.box((0,0,.815),(.64,.48,.055),'Marble',.015)
 m.box((0,-.244,.73),(.46,.025,.10),'Mahogany',.01);m.ring((0,-.27,.73),.025,.006,'Brass',10,4,(1,0,0))
 m.lathe((-.06,0,.85),[(0,.11),(.025,.14),(.095,.19),(.12,.195),(.13,.18),(.09,.16),(.025,.085)],'Porcelain',16)
 m.lathe((.215,.07,.85),[(0,.065),(.025,.077),(.13,.07),(.19,.045),(.25,.047),(.26,.04)],'Porcelain',12)
 m.ring((.29,.07,1.01),.065,.012,'Porcelain',12,5,(0,1,0))
 m.tube([(.22,.04,1.07),(.19,-.02,1.1),(.17,-.05,1.12)],.021,'Porcelain',7)
 m.tags['BowlJugWashstand']+=1;return m

@lru_cache(None)
def desk(width=1.25):
 m=Mesh();w=width
 for x in (-w/2+.09,w/2-.09):
  for y in (-.25,.25):m.lathe((x,y,0),[(0,.025),(.05,.035),(.15,.028),(.31,.037),(.40,.025),(.65,.035),(.72,.043)],'Oak',8)
 m.box((0,0,.77),(w,.66,.065),'Oak',.02)
 m.box((0,-.29,.65),(w-.16,.10,.15),'Oak',.012)
 for x in (-w*.25,w*.25):m.box((x,-.35,.65),(w*.36,.03,.12),'Mahogany',.01);m.ring((x,-.38,.65),.023,.006,'Brass',10,4,(1,0,0))
 m.box((0,-.02,.808),(w*.65,.41,.012),'LeatherGreen',.003)
 m.box((.04,-.03,.82),(.28,.32,.004),'Paper')
 m.lathe((w*.35,.15,.81),[(0,.035),(.045,.045),(.065,.028),(.085,.024)],'BookBlue',10)
 m.rod((w*.35,.15,.88),(w*.36,.13,1.08),.003,'Black',4)
 m.tags['WritingDesk']+=1;return m

@lru_cache(None)
def bookcase(width=1.5,style='Oak'):
 m=Mesh();w=width
 # Open carcass: back, stiles, cornice, real shelves; not a solid book box.
 m.box((0,.12,1.03),(w,.025,2.06),style)
 for x in (-w/2+.045,w/2-.045):m.box((x,0,1.03),(.09,.34,2.06),style,.012)
 m.box((0,0,2.10),(w+.12,.41,.11),style,.018);m.box((0,0,.07),(w+.06,.38,.14),style,.015)
 for row,z in enumerate((.18,.61,1.04,1.47,1.90)):
  m.box((0,0,z),(w-.10,.33,.04),style,.006)
  if row==4:continue
  num=max(10,int((w-.20)/.067));step=(w-.20)/num
  for j in range(num):
   h=.25+((j*7+row*3)%8)*.014;xx=-w/2+.10+(j+.5)*step;col=['BookRed','BookGreen','BookBlue','Walnut'][(j+row)%4]
   m.box((xx,-.015,z+.025+h/2),(step*.87,.23,h),'Paper')
   m.box((xx,-.14,z+.025+h/2),(step*.95,.027,h+.012),col,.003)
   for zz in (.06,h-.025):m.box((xx,-.157,z+.025+zz),(step*.85,.004,.008),'Brass')
 m.tags['OpenBookcase']+=1;return m

@lru_cache(None)
def wc():
 m=Mesh();m.lathe((0,0,0),[(0,.13),(.05,.14),(.09,.10),(.24,.09),(.31,.19),(.41,.23),(.45,.22),(.445,.18),(.36,.14),(.31,.04)],'Porcelain',16)
 m.lathe((0,0,.45),[(0,.225),(.035,.23),(.042,.19),(.018,.178),(0,.18)],'Mahogany',16)
 m.tube([(0,.12,.27),(0,.33,.27),(0,.36,.38),(0,.36,1.66)],.025,'Copper',8)
 m.box((0,.32,1.78),(.47,.24,.32),'Oak',.02)
 for z in (.42,1.55):m.ring((0,.36,z),.033,.008,'Brass',10,4)
 m.rod((.24,.26,1.65),(.24,.26,.91),.004,'Brass',4);m.lathe((.24,.26,.89),[(0,.025),(.08,.018)],'Ivory',8)
 m.tags['HighCisternWC']+=1;return m

@lru_cache(None)
def bathtub():
 m=Mesh();a=Mesh();a.lathe((0,0,0),[(.12,.31),(.20,.37),(.55,.45),(.64,.48),(.67,.48),(.67,.43),(.60,.41),(.22,.30),(.18,.18)],'Porcelain',24);m.append(a,scale=(1.9,.91,1))
 for x in (-.55,.55):
  for y in (-.24,.24):m.lathe((x,y,0),[(0,.045),(.04,.056),(.13,.033),(.19,.04)],'Iron',8)
 for y in (-.13,.13):
  m.tube([(.67,y,.16),(.67,y,.79),(.57,y,.79),(.57,y,.70)],.018,'Brass',8);handwheel(m,(.67,y,.83),.037,(0,0,1),'Brass')
 m.tags['ClawfootTub']+=1;return m

@lru_cache(None)
def piano():
 m=Mesh();outline=[(-.72,-.4),(.72,-.4),(.72,.05),(.61,.67),(.35,1.2),(-.1,1.30),(-.58,1.05),(-.72,.55)]
 vv=[(x,y,z) for z in (.69,1.0) for x,y in outline];n=len(outline);ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)];m.add(vv,ff,'Walnut')
 m.box((0,-.49,.78),(1.39,.25,.10),'Black',.01)
 for i in range(36):m.box((-.67+i*.038,-.51,.843),(.035,.25,.017),'Porcelain',.002)
 for i in range(25):
  if i%7 not in (2,6):m.box((-.66+i*.053,-.44,.873),(.026,.14,.04),'Black',.002)
 for x,y in [(-.57,-.25),(.57,-.25),(0,1.02)]:m.lathe((x,y,0),[(0,.04),(.08,.06),(.20,.035),(.42,.057),(.64,.039),(.70,.065)],'Walnut',10)
 m.box((0,.04,1.14),(.65,.045,.28),'Mahogany',.01);m.box((0,.015,1.17),(.48,.012,.23),'Paper')
 for x in (-.12,.12):m.tube([(x,.05,.1),(x,-.35,.1),(x,-.5,.06)],.012,'Brass',6)
 m.tags['Pianoforte']+=1;return m

@lru_cache(None)
def range_unit():
 m=Mesh();m.box((0,0,.14),(2.9,1.24,.20),'Iron',.025);m.box((0,.04,.65),(2.8,1.15,.85),'Firebrick',.025)
 m.box((0,0,1.12),(2.96,1.30,.09),'Iron',.025)
 for x in (-.88,0,.88):
  m.box((x,-.61,.70),(.71,.09,.55),'Iron',.04);m.box((x,-.668,.70),(.56,.035,.39),'Soot',.025);m.rod((x-.13,-.70,.81),(x+.13,-.70,.81),.018,'Brass',7)
  m.box((x,-.62,.30),(.66,.10,.13),'Iron',.015)
  m.lathe((x,0,1.17),[(0,.28),(.025,.28),(.03,.23)],'Iron',16)
  m.lathe((x,0,1.20),[(0,.18),(.04,.22),(.37,.24),(.40,.25),(.41,.23),(.09,.18),(.08,.01)],'Copper',16)
  for side in (-1,1):m.ring((x+side*.28,0,1.47),.065,.013,'Iron',10,4,(0,1,0))
 for x in (-1.22,1.22):m.cylinder((x,.43,1.48),.035,.65,'Iron',7)
 m.box((0,.44,1.78),(2.8,.68,.10),'Iron',.015)
 m.tags['CoalRangeThreeOvens']+=1;return m

@lru_cache(None)
def shelving(kind='pantry'):
 m=Mesh();w=1.4
 for x in (-.66,.66):
  for y in (-.2,.2):m.box((x,y,1.05),(.07,.07,2.1),'Oak',.007)
 for i,z in enumerate((.15,.65,1.15,1.65)):
  m.box((0,0,z),(w,.50,.045),'Oak',.007)
  for j in range(4):
   xx=-.48+j*.32
   if kind=='pantry':
    for k in range(4):m.lathe((xx,0,z+.03+k*.018),[(0,.08),(.012,.10),(.018,.095)],'Porcelain',10)
   else:
    m.box((xx,0,z+.17),(.27,.37,.28),'Canvas' if i%2 else 'Linen',.025)
    m.box((xx,-.195,z+.17),(.11,.008,.09),'Paper')
 m.tags['ProvisionShelving']+=1;return m
