"""Weather-deck architecture and supported equipment, not a texture-only pass.
No lifeboat is invented and no contracted socket/cradle datum is changed.
"""
import math
import numpy as np
from meshkit import *
from shipdesign.leonidas_ii import ROOMS,DECKS,BOAT_MOUNTS,beam_deck
from structure import deck_outline,deck_holes
from period_detail import plain_bench


def crown_roof(name,bounds,z,rise=.14,deck='boat'):
 x0,x1,y0,y1=bounds;w=y1-y0;m=Mesh();profile=[]
 for j in range(17):
  t=-1+2*j/16;profile.append(((y0+y1)/2+t*w/2,z+.035+rise*(1-t*t)))
 profile.extend([(y1,z),(y0,z)]);n=len(profile)
 vv=[(x,y,zz) for x in (x0,x1) for y,zz in profile]
 ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
 m.add(vv,ff,'DeckCanvas',True,tag='CrownedWeatherRoof')
 # Shallow fascia, fine eaves/gutter and corner knees join the actual walls.
 for yy in (y0+.025,y1-.025):
  m.box(((x0+x1)/2,yy,z-.025),(x1-x0,.095,.15),'White',.012)
  m.rod((x0,yy,z+.035),(x1,yy,z+.035),.030,'White',10)
  m.box(((x0+x1)/2,yy,z-.085),(x1-x0,.115,.030),'Teak',.006)
 for xx in (x0+.025,x1-.025):m.box((xx,(y0+y1)/2,z-.025),(.095,w-.05,.15),'White',.012)
 m.emit(name,collection('WeatherArchitecture'),kind='superstructure',deck=deck)


def weather_planks():
 # A finite 150mm plank surface on weather/exposed passage areas only.
 # Existing collision decks remain authoritative; the 9mm finish does not
 # seal a stair/casing opening or silently plank over an occupied room.
 for dk in ('saloon','promenade','boat','bridge'):
  m=Mesh();z=DECKS[dk];holes=deck_holes(dk);spaces=[r for r in ROOMS if r['deck']==dk]
  start,end={'saloon':(-81.4,81.6),'promenade':(-71.8,62.8),'boat':(-61.8,49.8),'bridge':(31.85,42.95)}[dk]
  for row,yy in enumerate(np.arange(-8.9,8.91,.15)):
   # Intervals are clipped by EVERY exact room/well boundary, not just by a
   # midpoint classification, so a plank cannot bridge a 1.3m stair opening.
   cuts=sorted(set([start,end]+[float(x) for x in np.arange(start+(row%3)*1.05,end,3.15)]+[max(start,min(end,v)) for h in holes for v in h[:2]]+[max(start,min(end,v)) for r in spaces for v in (r['x0']-.055,r['x1']+.055)]))
   for a,b in zip(cuts,cuts[1:]):
    if b-a<.025:continue
    # Inscribe the entire board in the curved deck at all three stations.
    width=min(deck_outline(dk,float(q)) for q in (a,(a+b)/2,b))-.035
    if abs(yy)+.074>width:continue
    if any(h[0]<(a+b)/2<h[1] and h[2]-.08<yy<h[3]+.08 for h in holes):continue
    if any(r['x0']-.055<(a+b)/2<r['x1']+.055 and r['y0']-.08<yy<r['y1']+.08 for r in spaces):continue
    m.box(((a+b)/2,float(yy),z+.004),(b-a-.002,.148,.010),'WeatheredTeak')
  m.tags['ActualWeatherPlanking']+=1
  m.emit('Weather_Planks_'+dk,collection('WeatherArchitecture'),kind='deck',deck=dk)


def fascia():
 for dk,xa,xb in (('saloon',-81.0,81.0),('promenade',-71.5,62.5),('boat',-61.5,49.5)):
  m=Mesh();z=DECKS[dk]
  for side in (-1,1):
   pts=[]
   for xx in np.linspace(xa,xb,165):
    w=deck_outline(dk,float(xx))
    if w>.35:pts.append((float(xx),side*w,z-.085))
   for a,b in zip(pts,pts[1:]):
    # Vertical flat edge band follows the deck edge instead of a thin tube.
    dx,dy=b[0]-a[0],b[1]-a[1];m.box(((a[0]+b[0])/2,(a[1]+b[1])/2,z-.085),(math.hypot(dx,dy)+.008,.055,.18),'White',.009,math.atan2(dy,dx))
   if pts:m.tube([(a,b,z-.177) for a,b,_ in pts],.016,'Teak',8)
  m.emit('Sheer_Fascia_'+dk,collection('WeatherArchitecture'),kind='superstructure',deck=dk)


def deck_furnishings():
 # Promenade benches are outboard of the public-room windows and do NOT
 # occupy the fixed boat/stair landing footprints above them.
 m=Mesh()
 for xx in (-43.,-31.,-16.,14.,24.,44.):
  for side in (-1,1):
   yy=side*(min(deck_outline('promenade',xx),deck_outline('promenade',xx+1.15),deck_outline('promenade',xx-1.15))-.62)
   if abs(yy)<6.5:continue
   m.append(plain_bench(2.05,'Teak',True),(xx,yy,14.409),0 if side>0 else math.pi)
   proxy((xx,yy,14.88),(2.12,.58,.92),tag='PromenadeBench')
 # Lifebuoys rest in actual rail brackets, with perimeter grab ropes.
 for xx in (-56.,-37.,-12.,18.,43.):
  for side in (-1,1):
   yy=side*(beam_deck(xx)-.60);zz=17.2
   for dx in (-.17,.17):
    m.tube([(xx+dx,yy,zz+1.03),(xx+dx,yy-side*.12,zz+1.00),(xx+dx,yy-side*.12,zz+.43)],.012,'Iron',8)
   c=(xx,yy-side*.09,zz+.67);m.ring(c,.25,.075,'Ivory',28,8,(0,1,0));m.ring((xx,yy-side*.17,zz+.67),.35,.010,'Rope',28,5,(0,1,0))
   for a in (0,math.pi/2,math.pi,3*math.pi/2):
    x=xx+.25*math.cos(a);z=zz+.67+.25*math.sin(a)
    m.cylinder((x,yy-side*.09,z),.082,.095,'Red',10,(0,1,0))
    # Four finite rope bridles join the outer grab loop to the buoy bands.
    # The former offset torus was a disconnected decorative ring.
    m.rod((xx+.31*math.cos(a),yy-side*.09,zz+.67+.31*math.sin(a)),(xx+.35*math.cos(a),yy-side*.17,zz+.67+.35*math.sin(a)),.009,'Rope',8)
    m.tags['LifebuoyGrabRopeBridle']+=1
   m.tags['RailBracketLifebuoy']+=1
 # A floor-supported fire-bucket rack by the aft uptake. It is NOT a
 # free-floating accessory or an invented extension of the steam system.
 xx,yy,zz=7.25,-2.8,17.2088
 for dx in (-.75,.75):
  m.box((xx+dx,yy,zz+.025),(.22,.25,.05),'Iron',.009)
  m.rod((xx+dx,yy,zz+.05),(xx+dx,yy,zz+1.05),.023,'Iron',8)
 m.rod((xx-.78,yy,zz+1.04),(xx+.78,yy,zz+1.04),.022,'Iron',8)
 for dx in (-.48,0,.48):
  m.lathe((xx+dx,yy,zz+.39),[(0,.045),(.30,.13),(.33,.14),(.34,.125),(.05,.025)],'Red',16)
  m.tube([(xx+dx,yy-.13,zz+.72),(xx+dx,yy-.14,zz+.86),(xx+dx,yy,zz+.99),(xx+dx,yy+.14,zz+.86),(xx+dx,yy+.13,zz+.72)],.010,'Iron',8)
  m.ring((xx+dx,yy,zz+1.015),.026,.007,'Iron',12,5,(1,0,0))
 # Support the navigation-light housings down to the actual wing plate.
 for side in (-1,1):
  yy=side*7.0
  m.box((38.5,yy,20.055),(.35,.28,.13),'Black',.012)
  for dx in (-.12,.12):bolts(m,(38.5+dx,yy,20.125),.035,4,(0,0,1),.008)
 m.emit('Promenade_Seats_Lifesaving_And_FireRack',collection('DeckEquipment'),kind='equipment')


def build():
 # Continuous roofs unite repetitive cabin pods and give the deckhouses
 # crowned, eaved silhouettes. Main decks and window datums are untouched.
 crown_roof('After_DeckCabin_Continuous_CrownedRoof',(-54.35,-25.30,-3.65,3.65),19.88,.13)
 crown_roof('Officers_Continuous_CrownedRoof',(10.85,19.15,-4.55,4.55),19.88,.13)
 crown_roof('Chart_Room_CrownedRoof',(19.85,26.75,-4.55,4.55),19.88,.14)
 crown_roof('Wheelhouse_CrownedRoof',(32.80,41.20,-4.92,4.92),22.50,.15,deck='bridge')
 crown_roof('Hospital_WeatherRoof',(49.65,56.15,-3.75,3.75),17.08,.13,deck='promenade')
 weather_planks();fascia();deck_furnishings()
