"""Purpose-specific period working-room fittings, authored for LEONIDAS-II.
Closed stores can have closed doors; recognizable hardware, joinery and actual
contents replace the former generic linen/plate racks in unrelated rooms.
No branded objects, borrowed textures, modern electronics or uploaded assets.
"""
import math
from functools import lru_cache
from meshkit import Mesh,bolts,handwheel,drop_pull


def bottle(m,x,y,z,t='BookGreen',h=.31):
 m.lathe((x,y,z),[(0,.043),(.025,.050),(h*.63,.050),(h*.75,.024),(h*.94,.021),(h,.024)],t,12)
 m.cylinder((x,y,z+h+.012),.023,.024,'Oak',10)
 m.box((x,y-.050,z+h*.40),(.060,.008,h*.23),'Paper',.003)


@lru_cache(None)
def chart_table():
 m=Mesh();m.tags['ChartTableWithDrawers']+=1
 # Paired drawer pedestals, open central knee bay, framed fronts/hardware.
 for x in (-.94,.94):
  m.box((x,0,.07),(.72,1.39,.14),'Oak',.018)
  for xx in (x-.32,x+.32):m.box((xx,0,.52),(.055,1.30,.88),'Oak',.008)
  m.box((x,.64,.52),(.64,.035,.88),'Oak')
  for z in (.23,.43,.63,.83):
   m.box((x,-.66,z),(.61,.065,.175),'Oak',.012)
   m.box((x,-.701,z),(.51,.025,.115),'Mahogany',.008)
   for dx in (-.16,.16):m.ring((x+dx,-.725,z),.025,.006,'Brass',12,5,(1,0,0))
 m.box((0,0,1.00),(2.80,1.60,.085),'Oak',.022)
 m.box((0,0,1.047),(2.40,1.28,.009),'Chart')
 # Rollers at the chart edges and genuine parallel rules / dividers.
 for x in (-1.21,1.21):
  m.cylinder((x,0,1.09),.045,1.18,'Paper',14,(0,1,0))
  for y in (-.61,.61):m.cylinder((x,y,1.09),.056,.035,'Brass',12,(0,1,0))
 for y in (-.10,.015):m.box((-.18,y,1.0603),(.90,.035,.018),'Walnut',.004)
 for x in (-.42,.07):m.rod((x,-.10,1.0703),(x+.05,.015,1.0703),.009,'Brass',7)
 first=len(m.v)
 m.ring((.60,.20,1.073),.025,.006,'Brass',12,5)
 for x in (.48,.73):m.rod((.60,.20,1.073),(x,-.06,1.073),.006,'Brass',7)
 m.rest(first,1.0515)
 return m


@lru_cache(None)
def mail_cubby(variant=0):
 m=Mesh();m.tags['MailSortingCubby']+=1
 m.box((0,.20,1.08),(1.40,.035,2.16),'Oak')
 for x in (-.69,-.23,.23,.69):m.box((x,0,1.08),(.035,.43,2.16),'Oak',.004)
 for z in (.08,.49,.90,1.31,1.72,2.13):m.box((0,0,z),(1.42,.46,.035),'Oak',.005)
 for row,shelf in enumerate((.08,.49,.90,1.31,1.72)):
  for col,x in enumerate((-.46,0,.46)):
   if (row*3+col+variant)%11==0:continue
   count=1+(row+col+variant)%4;base=shelf+.0173
   for k in range(count):m.box((x,-.025,base+.0225+k*.0448),(.33,.28,.045),'Paper' if (row+col+k)%2 else 'Canvas',.005)
   top=base+.045+(count-1)*.0448
   # Closed ties wrap the actual parcel stack rather than hovering above
   # a count-dependent notional height, and every envelope bears below.
   m.tube([(x-.164,-.025,base+.002),(x-.164,-.025,top),(x+.164,-.025,top),(x+.164,-.025,base+.002),(x-.164,-.025,base+.002)],.005,'Rope',6)
   m.tube([(x,-.163,base+.002),(x,-.163,top),(x,.113,top),(x,.113,base+.002),(x,-.163,base+.002)],.005,'Rope',6)
   m.box((x,-.237,shelf),(.14,.020,.025),'Brass',.003)
 return m


@lru_cache(None)
def drinks_rack(variant=0):
 m=Mesh();m.tags['StewardDrinksCabinet']+=1
 # Lower counter/cupboard, paneled doors and a shallow open bottle display.
 m.box((0,0,.43),(1.42,.54,.86),'Mahogany',.015)
 m.box((0,-.015,.8925),(1.49,.65,.065),'Marble',.015)
 for x in (-.35,.35):
  m.box((x,-.287,.45),(.62,.035,.68),'Oak',.008)
  m.box((x,-.309,.45),(.49,.020,.53),'Mahogany',.010)
  drop_pull(m,(x+.18,-.341,.49),.024)
 m.box((0,.20,1.50),(1.42,.035,1.17),'Mahogany')
 for x in (-.69,.69):m.box((x,.015,1.50),(.045,.42,1.17),'Mahogany',.005)
 for z in (.96,1.49,2.05):
  m.box((0,0,z),(1.43,.45,.035),'Mahogany',.006)
  if z<2:
   for i in range(6):
    if (i+variant+round(z*10))%7==0:continue
    bottle(m,-.54+i*.215,.025,z+.0173,['BookGreen','BookRed','BookBlue'][(i+variant)%3],.26+((i+variant)%3)*.025)
 # Pewter measuring cups / footed drinking vessels on the working counter.
 for x in ((-.48,-.20,.08) if variant%2 else (-.48,-.20,.08,.36)):
  m.lathe((x,-.28,.9248),[(0,.045),(.02,.045),(.025,.012),(.09,.012),(.11,.035),(.17,.052),(.18,.048),(.12,.026)],'Steel',14)
 return m


@lru_cache(None)
def ice_chest():
 m=Mesh();m.tags['InsulatedIceChest']+=1
 # Wood/cork insulated double chest with latched doors, not a claimed
 # powered refrigeration plant. Internal shelves remain behind closed doors.
 for x in (-.69,.69):m.box((x,0,1.02),(.07,.63,2.04),'Oak',.012)
 m.box((0,.29,1.02),(1.33,.06,2.04),'Oak')
 for z in (.06,1.03,2.03):m.box((0,0,z),(1.43,.66,.07),'Oak',.012)
 for x in (-.34,.34):
  for z in (.54,1.54):
   m.box((x,-.345,z),(.62,.09,.89),'Oak',.015)
   m.box((x,-.400,z),(.47,.035,.70),'Ivory',.018)
   for zz in (z-.29,z+.29):
    hx=x+(-.29 if x<0 else .29)
    m.box((hx,-.365,zz),(.14,.12,.055),'Iron',.008)
    m.cylinder((hx,-.419,zz),.016,.075,'Brass',10)
   m.rod((x+.19,-.43,z-.08),(x+.19,-.43,z+.08),.018,'Brass',8)
 m.tube([(.53,-.15,.19),(.53,-.45,.19),(.53,-.45,.06)],.018,'Copper',9)
 m.lathe((.53,-.45,0),[(0,.095),(.012,.11),(.045,.12),(.050,.11),(.02,.085)],'Iron',16)
 return m


@lru_cache(None)
def cargo_crate():
 m=Mesh();m.tags['SlattedCargoCrate']+=1
 # Hollow board construction, lid seams, external battens/straps, finite
 # nail heads and rope handles; no textured solid cuboid masquerading as cargo.
 for z in (.025,.875):
  for j in range(5):m.box((-.384+j*.192,0,z),(.184,.92,.05),'Oak',.003)
 for y in (-.445,.445):
  for j in range(4):m.box((0,y,.135+j*.21),(.96,.04,.198),'Oak',.003)
 for x in (-.46,.46):
  for j in range(4):m.box((x,0,.135+j*.21),(.04,.86,.198),'Walnut',.003)
 for x in (-.40,.40):
  for y in (-.474,.474):m.box((x,y,.45),(.08,.030,.90),'Walnut',.004)
 for x in (-.31,.31):
  for y in (-.498,.498):m.box((x,y,.45),(.035,.015,.90),'Iron',.003)
  for z in (-.005,.905):m.box((x,0,z),(.035,1.01,.015),'Iron',.002)
 for side in (-1,1):
  y=side*.505
  for xx in (-.13,.13):m.cylinder((xx,side*.485,.59),.018,.070,'Iron',10,(0,1,0))
  m.tube([(-.13,y,.59),(-.12,y+side*.035,.48),(.12,y+side*.035,.48),(.13,y,.59)],.012,'Rope',7)
  for x in (-.40,.40):
   for z in (.12,.76):m.cylinder((x,side*.494,z),.010,.015,'Iron',7,(0,1,0))
 m.box((.05,-.470,.61),(.26,.012,.17),'Paper',.003)
 return m


@lru_cache(None)
def staved_barrel():
 m=Mesh();m.tags['HoopedCargoBarrel']+=1
 profile=[(0,.27),(.05,.30),(.25,.35),(.50,.37),(.75,.35),(.88,.30),(.90,.28)]
 m.lathe((0,0,0),profile,'Oak',20)
 for z,r in ((.08,.310),(.27,.357),(.70,.360),(.85,.314)):m.ring((0,0,z),r,.018,'Iron',24,6)
 for a in [i*math.tau/20 for i in range(20)]:
  m.tube([(r*math.cos(a),r*math.sin(a),z) for z,r in profile[1:-1]],.0035,'Walnut',4)
 m.cylinder((0,0,.907),.266,.018,'Walnut',20)
 m.cylinder((.10,0,.920),.031,.020,'Oak',10)
 return m


@lru_cache(None)
def medicine_cabinet():
 m=Mesh();m.tags['ApothecaryCabinet']+=1
 m.box((0,.15,.92),(1.12,.035,1.84),'Oak')
 for x in (-.54,.54):m.box((x,0,.92),(.06,.36,1.84),'Oak',.006)
 for z in (.08,.57,.98,1.39,1.81):m.box((0,0,z),(1.15,.39,.035),'Oak',.005)
 for x in (-.27,.27):
  m.box((x,-.19,.31),(.49,.035,.40),'Ivory',.007)
  drop_pull(m,(x,-.233,.33),.023)
 for row,shelf in enumerate((.57,.98,1.39)):
  z=shelf+.0173
  for i in range(5):
   x=-.41+i*.205
   if row==1 and i<2:
    first=len(m.v);m.cylinder((x,-.015,z+.065),.065,.17,'Linen',14,(0,1,0));m.rest(first,shelf+.0175)
   else:bottle(m,x,.025,z,'BookBlue' if i%2 else 'BookRed',.27)
 return m


@lru_cache(None)
def barber_chair():
 m=Mesh();m.tags['BarberRecliningChair']+=1;m.tags['UpholsteredArmchair']+=1
 m.lathe((0,0,0),[(0,.30),(.045,.34),(.075,.21),(.12,.11),(.28,.10),(.32,.22)],'Iron',20)
 m.box((0,0,.34),(.68,.66,.12),'Mahogany',.025)
 m.cushion((0,-.02,.445),(.65,.63,.16),'Leather')
 m.cushion((0,.26,.78),(.65,.17,.65),'Leather')
 for x in (-.34,.34):
  m.cushion((x,0,.61),(.14,.66,.17),'Leather');m.rod((x,-.25,.35),(x,-.25,.60),.025,'Iron',8)
 for x in (-.13,.13):m.rod((x,.28,.99),(x,.28,1.20),.016,'Brass',8)
 m.cushion((0,.25,1.20),(.38,.16,.17),'Leather')
 for x in (-.24,.24):m.tube([(x,-.20,.34),(x,-.58,.19),(x,-.72,.19)],.026,'Iron',8)
 m.box((0,-.65,.20),(.54,.24,.045),'Iron',.012)
 for x in (-.18,-.06,.06,.18):m.rod((x,-.75,.225),(x,-.55,.225),.008,'Brass',6)
 handwheel(m,(.40,.10,.59),.065,(1,0,0),'Brass')
 return m


@lru_cache(None)
def iron_safe():
 m=Mesh();m.tags['PurserIronSafe']+=1
 m.box((0,0,.58),(.73,.65,1.16),'Iron',.028)
 m.box((0,-.35,.59),(.63,.055,.99),'Engine',.020)
 m.box((0,-.385,.59),(.49,.025,.82),'Iron',.018)
 for z in (.24,.94):m.cylinder((-.30,-.385,z),.035,.15,'Steel',10)
 m.cylinder((.06,-.414,.61),.026,.060,'Steel',12,(0,1,0))
 handwheel(m,(.06,-.43,.61),.13,(0,-1,0),'Brass')
 m.cylinder((-.15,-.425,.75),.045,.060,'Brass',14,(0,1,0))
 for x in (-.23,.23):
  for z in (.19,.99):m.cylinder((x,-.405,z),.015,.016,'Brass',8,(0,1,0))
 return m


@lru_cache(None)
def medical_trolley():
 m=Mesh();m.tags['MedicalInstrumentTrolley']+=1
 for x in (-.31,.31):
  for y in (-.20,.20):
   m.rod((x,y,.10),(x,y,.80),.019,'Iron',8)
   m.cylinder((x,y,.057),.047,.026,'Iron',16,(1,0,0));m.ring((x,y,.057),.045,.012,'Iron',16,8,(1,0,0))
 for z in (.27,.80):m.box((0,0,z),(.72,.49,.035),'Steel',.008)
 for y in (-.23,.23):
  for x in (-.35,.35):m.rod((x,y,.80),(x,y,.86),.012,'Brass',8)
  m.rod((-.35,y,.86),(.35,y,.86),.012,'Brass',8)
 m.lathe((-.15,0,.8173),[(0,.065),(.015,.085),(.05,.10),(.055,.092),(.025,.055)],'Porcelain',16)
 for x in (.04,.12,.20):
  first=len(m.v);m.rod((x,-.12,.83),(x,.10,.83),.006,'Steel',7);m.rest(first,.8175)
 return m


@lru_cache(None)
def provision_rack():
 m=Mesh();m.tags['FoodProvisionRack']+=1
 for x in (-.66,.66):
  for y in (-.20,.20):m.box((x,y,1.05),(.06,.06,2.10),'Oak',.006)
 for row,z in enumerate((.10,.65,1.20,1.75)):
  m.box((0,0,z),(1.40,.50,.04),'Oak',.005)
  for i,x in enumerate((-.45,0,.45)):
   if (row+i)%2:
    m.lathe((x,0,z+.0198),[(0,.12),(.04,.15),(.29,.15),(.35,.11),(.38,.09)],'Porcelain',14)
    m.cylinder((x,0,z+.4171),.105,.035,'Oak',14)
   else:
    m.lathe((x,0,z+.0198),[(0,.10),(.05,.145),(.22,.15),(.33,.09),(.37,.04),(.40,.055)],'Canvas',14)
    m.ring((x,0,z+.3848),.048,.008,'Rope',12,5)
 return m


@lru_cache(None)
def folded_deckchair():
 m=Mesh();m.tags['FoldedDeckChair']+=1
 for x in (-.26,.26):
  for yy in (-.06,.12):m.cylinder((x,yy,.010),.025,.020,'Teak',8)
  m.rod((x,-.06,.02),(x,.15,1.34),.022,'Teak',8)
  m.rod((x,.12,.02),(x,-.08,.88),.022,'Teak',8)
  m.cylinder((x,0,.58),.027,.060,'Brass',10,(1,0,0))
 for z,y in ((.14,-.04),(.41,.0),(1.22,.13)):
  m.rod((-.26,y,z),(.26,y,z),.022,'Teak',8)
 # A taut folded canvas sling, finite thickness, follows the frame slope.
 vv=[(x,y+d,z) for d in (-.006,.006) for x,y,z in [(-.225,-.005,.42),(.225,-.005,.42),(.225,.129,1.24),(-.225,.129,1.24)]]
 m.add(vv,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'Canvas')
 return m
