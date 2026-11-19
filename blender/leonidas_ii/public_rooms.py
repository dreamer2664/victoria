"""Seven separately composed public-room plans (1889 fictional Aurelian).
No shared chair/table grid. Door approaches, service cross aisles, glazing
and period room function drive the plans; counts are actual placed seats.
"""
import math
from meshkit import Mesh,SEATS,LIGHTS
from furnishings import chair,sofa,table,desk,wardrobe,service_setting,bookcase,TABLE_WOOD_TOP,TABLE_CLOTH_TOP,DESK_PAD_TOP
from period_detail import *
from visual_design import design,finished_floor


def fit(m,r,place):
 x0,x1,y0,y1=(r[k] for k in ('x0','x1','y0','y1'));cx=(x0+x1)/2;cy=(y0+y1)/2;z=finished_floor(r);k=r['kind'];d=design(r);seats=0
 def put(t,x,y,a=0):place(m,t,x,y,z,a)
 def seat(x,y,a=0,style='plain',cloth=None):
  nonlocal seats
  q=plain_chair(cloth or d['cloth'],d['wood']) if style=='plain' else recolour(chair('armchair'),{'Velvet':cloth or d['cloth'],'Mahogany':d['wood']}) if style=='club' else recolour(chair('writing' if style=='writing' else 'dining'),{'Velvet':cloth or d['cloth'],'LeatherGreen':cloth or d['cloth'],'Oak':d['wood'],'Mahogany':d['wood']})
  put(q,x,y,a);seats+=1
 def settee(x,y,a=0,length=2.1,cloth=None):
  nonlocal seats
  put(recolour(sofa(length,cloth or d['cloth']),{'Mahogany':d['wood']}),x,y,a);seats+=3 if length>=1.9 else 2
 def low_books(x,y,a=0,variant=0):put(low_bookcase(1.5,variant,d['wood']),x,y,a)
 def reading_lamp(x,y,top):
  m.lathe((x,y,top),[(0,.075),(.018,.09),(.045,.04),(.24,.023),(.27,.06)],'Brass',12)
  m.lathe((x,y,top+.27),[(0,.11),(.045,.115),(.13,.055)],'Porcelain',16)
  LIGHTS.append(dict(position=(x,y,top+.33),range_m=2.1,brightness=.25));m.tags['TableFixedOpalReadingLamp']+=1
 if k=='dining':
  # Sixteen separate banquet groups, not four almost continuous slabs.
  # A real 1.7m transverse service aisle separates the two room halves.
  xs=[x0+2.90,x0+6.60,x1-7.00,x1-2.60];ys=[cy-4.65,cy-1.55,cy+1.55,cy+4.65]
  for row,yy in enumerate(ys):
   for i,xx in enumerate(xs):
    put(table(2.70,1.02,True),xx,yy)
    for dx in (-.86,0,.86):
     for side in (-1,1):
      seat(xx+dx,yy+side*.84,0 if side>0 else math.pi,style='dining')
      place(m,service_setting(),xx+dx,yy+side*.30,z+TABLE_CLOTH_TOP-.0002,0 if side>0 else math.pi)
    # One purposeful centrepiece per table, not the same desktop in every room.
    if (row+i)%2:
     m.lathe((xx,yy,z+TABLE_CLOTH_TOP-.0002),[(0,.055),(.025,.08),(.055,.04),(.22,.06),(.26,.04)],'Porcelain',16)
     for dx in (-.055,.015,.060):
      m.tube([(xx,yy,z+1.02),(xx+dx,yy+.015,z+1.23)],.003,'BookGreen',5)
      m.cushion((xx+dx,yy+.015,z+1.23),(.055,.055,.040),'GoldCloth')
    else:
     m.cylinder((xx,yy,z+TABLE_CLOTH_TOP+.0173),.12,.035,'Steel',20)
     for dx in (-.045,.045):m.lathe((xx+dx,yy,z+TABLE_CLOTH_TOP+.0346),[(0,.025),(.07,.025),(.085,.031)],'Porcelain',10)
    ceiling_fixture(m,r,xx,yy,over_table=True)
  # Wall-side columns do not intersect chair backs or windows.
  for xx in (x0+1.4,cx-2.2,cx+2.2,x1-1.4):
   for yy in (y0+.33,y1-.33):
    h=r['top']-z-.05
    m.lathe((xx,yy,z),[(0,.15),(.12,.16),(.22,.10),(h-.25,.10),(h-.18,.15),(h+.006,.16)],'Ivory',16)
    # Collars seat at the real broad base/capital, not around a taper.
    for zz,rad in ((.12,.16),(h-.18,.15)):m.ring((xx,yy,z+zz),rad,.008,'Brass',16,6)
  # Low service credenza along the opaque middle of the forward end wall.
  put(recolour(wardrobe(1.9,.91),{'Oak':'Mahogany'}),x1-.33,cy,-math.pi/2)
  framed_panel(m,x1-.09,cy,z+1.64,1.70,.66,'Seascape',-math.pi/2,'Ivory')
  inventory='96 actual swivel dining seats at 16 separate six-place tables; transverse service cross aisle, individual linen/tableware, alternating salt cruets/flower vases, low service credenza, ivory columns and ceiling-fastened three-branch electroliers.'
 elif k=='dining_second':
  # Eight CROSSWISE tables create a central fore/aft aisle. This is not the
  # first-class plan with a cheaper wall colour or the same red swivel chairs.
  for xx in (x0+2.6,x0+6.1,x0+9.6,x0+13.1):
   for side in (-1,1):
    yy=cy+side*2.13;put(recolour(table(2.25,.86,False),{'Mahogany':'Oak'}),xx,yy,math.pi/2)
    m.box((xx,yy,z+TABLE_WOOD_TOP+.0045),(.58,1.95,.009),'Linen',.002)
    for dy in (-.70,0,.70):
     for sx in (-1,1):
      seat(xx+sx*.79,yy+dy,-math.pi/2 if sx>0 else math.pi/2)
      q=recolour(service_setting(.009),{'Brass':'Porcelain'});place(m,q,xx+sx*.25,yy+dy,z+TABLE_WOOD_TOP+.0088,-math.pi/2 if sx>0 else math.pi/2)
    ceiling_fixture(m,r,xx,yy,'opal',True)
  put(wardrobe(1.5,.93),x0+.33,cy,math.pi/2);tea_tray(m,x0+.33,cy,z+.9923)
  framed_panel(m,x0+.09,cy,z+1.68,1.30,.62,'Seascape',math.pi/2)
  inventory='48 actual oak/blue four-legged dining seats at eight crosswise six-place tables, central fore/aft aisle, linen runners rather than first-class full cloths, plain opal fixtures and a low end-wall service sideboard.'
 elif k=='library':
  # Tall bookcases never cover exterior windows. Low sills house low books.
  for side in (-1,1):
   yy=y0+.25 if side<0 else y1-.25
   for j in range(8):low_books(x0+1.35+j*2.18,yy,math.pi if side<0 else 0,j)
  # Single shared double-sided reading table with a supported centre leg.
  t=recolour(table(6.0,1.40),{'Mahogany':'Oak'});t.lathe((0,0,0),[(0,.16),(.08,.18),(.16,.095),(.54,.09),(.675,.16)],'Oak',16)
  put(t,cx,cy)
  for dx in (-2.35,-.80,.80,2.35):
   for side in (-1,1):
    seat(cx+dx,cy+side*1.05,0 if side>0 else math.pi,'writing')
    m.append(book_stack((int((dx+3)*10)+side)%3),(cx+dx,cy+side*.40,z+TABLE_WOOD_TOP-.0002))
  for dx in (-1.5,1.5):reading_lamp(cx+dx,cy,z+TABLE_WOOD_TOP-.0002);ceiling_fixture(m,r,cx+dx,cy,'reading',True)
  # End alcoves and a true window reading bench: quiet peripheral seating.
  settee(x0+1.10,cy,math.pi/2,1.9)
  settee(x1-1.10,cy,-math.pi/2,1.9)
  for xx in (x0+3.20,x1-3.20):
   put(round_table(.47,'Oak'),xx,cy);m.append(book_stack(1),(xx,cy,z+.7698))
  settee(cx,y1-1.10,0,2.3);settee(cx,y0+1.10,math.pi,2.3)
  framed_panel(m,x0+.10,cy,z+1.86,1.30,.56,'Seascape',math.pi/2)
  wall_clock(m,x1-.11,cy,z+1.85,-math.pi/2)
  rug(m,cx,cy,z,8.6,4.5,'CarpetSage')
  inventory='Central double-sided eight-seat reading table, opal table lamps with fixed feet, end reading alcoves, window settees, low bookcases below real sills, book stacks, framed marine picture and clock; no library/writing-room desk grid.'
 elif k=='writing':
  # Perimeter individual secretaires, not library shelves marching round
  # the walls. Keep the aftermost 1.8m and forward door approaches clear.
  for j,xx in enumerate((x0+2.4,x0+5.5,x0+8.6,x0+11.5)):
   put(recolour(desk(1.35),{'Oak':'Ivory','Mahogany':'Walnut','LeatherGreen':'ClothPlum'}),xx,y1-.48)
   seat(xx,y1-1.32,math.pi,'writing','ClothPlum')
   reading_lamp(xx-.40,y1-.50,z+DESK_PAD_TOP-.0002)
  # A central correspondence table accepts letters and newspapers in common.
  xx=cx+.35;yy=cy-.30;put(recolour(table(2.7,1.10),{'Mahogany':'Walnut'}),xx,yy)
  for dx in (-.78,.78):
   for side in (-1,1):seat(xx+dx,yy+side*.92,0 if side>0 else math.pi,'writing','ClothPlum');paper_and_ink(m,xx+dx,yy+side*.25,z+TABLE_WOOD_TOP-.0002,int(dx>0))
  settee(x0+3.2,y0+.70,math.pi,2.4,'ClothPlum')
  put(round_table(.43,'Walnut'),x0+3.2,y0+1.85);m.append(book_stack(2),(x0+3.2,y0+1.85,z+.7698))
  # Correspondence cabinet is on an opaque END wall, not over a window.
  put(bookcase(1.35,'Ivory'),x0+.24,cy,math.pi/2)
  framed_panel(m,x1-.10,cy+.2,z+1.65,1.35,.62,'Seascape',-math.pi/2,'Ivory')
  for xx0,yy0 in ((cx,cy-.3),(x0+3.2,y0+2.6),(x1-3.0,y1-2.2)):ceiling_fixture(m,r,xx0,yy0,'chandelier',yy0==cy-.3)
  rug(m,cx+.35,cy-.3,z,5.0,3.8,'CarpetNavy')
  inventory='Four individual ivory window secretaires with fixed opal desk lamps, central four-seat correspondence table, plum upholstered window settee, low tea/book table, end-wall reference cabinet and marine picture.'
 elif k=='smoking':
  # A compact club billiard area and separate cards/conversation zones.
  put(billiard_table(),x0+4.0,cy-2.1)
  ceiling_fixture(m,r,x0+4.0,cy-2.1,'club',True)
  xx=x1-3.1;yy=y0+2.5;put(round_table(.57,'Mahogany'),xx,yy);game_board(m,xx,yy,z+.7698,'domino')
  for dx,dy,a in ((0,.98,0),(0,-.98,math.pi),(-.98,0,math.pi/2),(.98,0,-math.pi/2)):seat(xx+dx,yy+dy,a,'club','LeatherGreen')
  ceiling_fixture(m,r,xx,yy,'club',True)
  # Two facing upholstered sofas form ONE conversation bay, not a grid.
  xx=cx+.25;yy=cy+3.3
  settee(xx,y1-.75,0,2.5,'Leather')
  seat(xx-1.80,yy-.45,math.pi/2,'club','Leather');seat(xx+1.80,yy-.45,-math.pi/2,'club','Leather')
  put(round_table(.54,'Mahogany'),xx,yy-.25);tea_tray(m,xx,yy-.25,z+.7698)
  ceiling_fixture(m,r,xx,yy-.3,'club',True)
  # Actual shallow mantel on the opaque end bay between escape openings.
  m.box((x0+.18,cy+.55,z+.65),(.25,1.55,1.30),'Marble',.020)
  m.box((x0+.32,cy+.55,z+.60),(.04,.93,.83),'Black',.008)
  m.box((x0+.24,cy+.55,z+1.34),(.52,1.80,.10),'Mahogany',.020)
  for dy in (-.35,-.18,0,.18,.35):m.rod((x0+.35,cy+.55+dy,z+.22),(x0+.35,cy+.55+dy,z+.94),.008,'Brass',6)
  # A finite grate frame and two short hearth feet carry the five bars;
  # they are not suspended just in front of the black fireback surface.
  for zz in (.22,.94):m.rod((x0+.35,cy+.10,z+zz),(x0+.35,cy+1.00,z+zz),.012,'Brass',8)
  for yy0 in (cy+.10,cy+1.00):
   m.rod((x0+.35,yy0,z+.22),(x0+.35,yy0,z+.94),.010,'Brass',8)
   m.rod((x0+.29,yy0,z+.22),(x0+.35,yy0,z+.22),.014,'Brass',8)
  framed_panel(m,x0+.10,cy+.55,z+1.96,1.35,.56,'Seascape',math.pi/2,'Mahogany')
  # Cue rack is wall-fastened, with separate butt and head retention strips.
  for zz in (.24,1.60):m.box((x0+.12,cy-1.35,z+zz),(.16,.70,.07),'Mahogany',.008)
  for j in range(5):m.rod((x0+.20,cy-1.62+j*.13,z+.26),(x0+.20,cy-1.62+j*.13,z+1.73),.012,'Oak',7,r2=.006)
  rug(m,cx+.25,cy+3.25,z,6.1,3.1,'CarpetSage')
  inventory='Pocketless three-ball carom billiard table with cloth-seated balls/cue, bulkhead cue rack, separate four-seat domino table, single leather conversation bay and marble/mahogany mantel. Club joinery and low branch lamps; not the music-room furniture grid.'
 elif k=='music':
  # Preserve the documented piano datum close to the after end; add a
  # genuine rim/harp/raised lid/85-note keyboard, not a block with 36 keys.
  px=x0+2.5;put(grand_piano(),px,cy,math.pi/2);put(piano_stool(),px+1.16,cy,math.pi/2);seats+=1
  # A horseshoe leaves a clear view and standing performance space.
  settee(cx+1.0,y1-.82,0,2.65,'ClothBlue');settee(cx+1.0,y0+.82,math.pi,2.65,'ClothBlue')
  for yy in (cy-2.0,cy+2.0):seat(x1-1.65,yy,-math.pi/2,'club','ClothBlue')
  for xx,yy in ((cx+.4,cy+2.9),(cx+.4,cy-2.9)):
   put(round_table(.43,'Walnut'),xx,yy)
  tea_tray(m,cx+.4,cy+2.9,z+.7698);m.append(book_stack(0),(cx+.4,cy-2.9,z+.7698))
  # A separate little two-chair window bay, not another music-room grid.
  seat(x0+2.3,y1-1.7,math.pi/2,'plain','ClothBlue');seat(x0+2.3,y0+1.7,math.pi/2,'plain','ClothBlue')
  for xx,yy in ((px,cy),(cx+1.7,cy),(cx+.7,cy+3.6),(cx+.7,cy-3.6)):ceiling_fixture(m,r,xx,yy,'chandelier',xx==px)
  framed_panel(m,x0+.10,cy,z+1.82,1.40,.59,'Seascape',math.pi/2,'Ivory')
  rug(m,cx+.8,cy,z,5.4,4.4,'CarpetNavy')
  inventory='Open-lid 85-note grand with separate harp/strings/keyboard/pedals and adjustable stool; blue horseshoe seating facing the instrument, two small tea/music tables, peripheral chairs and ivory/blue room joinery.'
 elif k=='lounge_second':
  for j,yy in enumerate((cy-2.05,cy+2.05)):
   xx=x0+3.0;put(round_table(.54,'Oak'),xx,yy);game_board(m,xx,yy,z+.7698,'chess' if j else 'domino')
   for dx,dy,a in ((-.88,0,math.pi/2),(.88,0,-math.pi/2),(0,.88,0),(0,-.88,math.pi)):seat(xx+dx,yy+dy,a)
   ceiling_fixture(m,r,xx,yy,'opal',True)
  settee(x1-3.15,y1-.73,0,2.4,'ClothBlue')
  put(round_table(.44,'Oak'),x1-3.15,y1-1.92);m.append(book_stack(1),(x1-3.15,y1-1.92,z+.7698))
  # Newspaper/book bay away from the centre exit and from glazing.
  low_books(x1-2.80,y0+.25,math.pi,2);low_books(x1-5.0,y0+.25,math.pi,1)
  seat(x1-3.10,cy-1.1,math.pi,'plain','ClothBlue');seat(x1-5.00,cy-1.1,math.pi,'plain','ClothBlue')
  ceiling_fixture(m,r,x1-3.3,cy+.2,'opal')
  framed_panel(m,x0+.10,cy,z+1.64,1.20,.60,'Notice',math.pi/2)
  wall_clock(m,x1-.10,cy+1.5,z+1.88,-math.pi/2)
  inventory='Two small oak game tables with actual chessmen/dominoes, blue four-legged chairs, one window settee/tea table and a low newspaper/book bay. Uncarpeted timber floor and plain opal fittings, distinct from the smoking club.'
 else:  # small steerage mess, not a mahogany first-class table
  tx=cx+(.20 if r['door_wall']=='x0' else -.20 if r['door_wall']=='x1' else 0)
  put(utility_table(1.8,.65,.77),tx,cy)
  for side in (-1,1):
   put(plain_bench(1.9,'Oak',False),tx,cy+side*.68)
   for dx in (-.6,0,.6):SEATS.append(dict(position=(tx+dx,cy+side*.68,z+.47),yaw=0 if side>0 else math.pi,size=(.4,.30,.10)));seats+=1
  ceiling_fixture(m,r,tx,cy,'marine',True)
  inventory='Plain trestle mess table with two slat benches, six actual seating positions and a supported caged working light.'
 return dict(actual_seats=seats,inventory=inventory,visual_identity=d['identity'],layout_revision='Detail refinement 1: purpose-specific physical layout')
