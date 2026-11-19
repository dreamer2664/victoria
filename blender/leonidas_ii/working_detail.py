"""Functional working-room detail, deliberately not saloon clutter."""
import math
from functools import lru_cache
from meshkit import Mesh,bolts
from furnishings import WASHSTAND_TOP,DESK_PAD_TOP
from period_detail import framed_panel,wall_clock,book_stack,utility_table,recolour
from visual_design import design,finished_floor


@lru_cache(None)
def bake_oven():
 m=Mesh();m.box((0,0,.10),(2.90,1.30,.20),'Iron',.020)
 m.box((0,.03,.87),(2.80,1.15,1.38),'Firebrick',.025)
 # Two independently latched bread-oven mouths, refractory lintels and hearth.
 for x in (-.68,.68):
  m.box((x,-.58,.87),(1.05,.055,.66),'Soot',.025)
  m.box((x,-.62,.87),(.82,.045,.48),'Iron',.025)
  m.box((x,-.61,.52),(1.12,.25,.10),'Marble',.018)
  for xx in (x-.49,x+.49):m.box((xx,-.615,.84),(.10,.12,.64),'Firebrick',.010)
  m.box((x,-.615,1.23),(1.08,.14,.14),'Firebrick',.012)
  for dx in (-.14,.14):m.rod((x+dx,-.627,.91),(x+dx,-.68,.91),.012,'Brass',8)
  m.rod((x-.14,-.68,.91),(x+.14,-.68,.91),.018,'Brass',8)
  for dz in (-.14,.14):
   m.box((x-.41,-.648,.87+dz),(.080,.055,.12),'Iron',.006)
   m.cylinder((x-.41,-.66,.87+dz),.018,.10,'Steel',8)
 m.box((0,0,1.61),(2.98,1.29,.10),'Iron',.020)
 m.cylinder((.95,.25,1.76),.15,.28,'Iron',14)
 m.tags['CoalBreadOven']+=1;return m


def finish_service(m,r,place):
 x0,x1,y0,y1=(r[q] for q in ('x0','x1','y0','y1'));cx=(x0+x1)/2;cy=(y0+y1)/2;z=finished_floor(r);k=r['kind'];d=design(r)
 if k in ('galley','bakery'):
  # Tool rail on the opaque end bulkhead, physically braced to it.
  xx=x1-.14
  for yy in (cy-.55,cy+.55):m.rod((x1-.025,yy,z+1.55),(xx-.08,yy,z+1.55),.013,'Iron',8)
  m.rod((xx-.08,cy-.6,z+1.55),(xx-.08,cy+.6,z+1.55),.013,'Iron',8)
  for j in range(3):
   yy=cy-.40+j*.4;m.tube([(xx-.08,yy,z+1.55),(xx-.14,yy,z+1.48),(xx-.14,yy,z+1.125)],.009,'Iron',8)
   m.lathe((xx-.14,yy,z+1.13),[(0,.045),(-.025,.065),(-.06,.045)],'Copper' if j%2 else 'Iron',12)
  # A finite grating meets the finished floor; no unsupported drain decal.
  m.box((cx,cy,z-.0047),(.50,.38,.010),'Grating',.003)
  if k=='bakery':
   xx=x0+2.0;yy=y1-.60
   for i,dx in enumerate((-.70,0,.70)):
    surface=.935 if i==1 else .90
    m.cushion((xx+dx,yy,z+surface+.0698),(.40,.22,.14),'Bread')
    for q in range(3):m.rod((xx+dx-.12+q*.10,yy-.06,z+surface+.139),(xx+dx-.09+q*.10,yy+.06,z+surface+.139),.004,'Ivory',5)
   # Flour bin with wooden cover and scoop, beside the kneading bench.
   bx=x0+.50;by=y1-1.05
   m.box((bx,by,z+.365),(.70,.65,.73),'Oak',.018)
   m.box((bx,by,z+.7525),(.74,.69,.045),'Oak',.012)
   m.lathe((bx,by,z+.7748),[(0,.065),(.035,.10),(.10,.10),(.115,.08)],'Steel',14)
   m.rod((bx,by,z+.84),(bx+.22,by,z+.84),.012,'Oak',8)
   # Long peel: blade bears on floor, shaft retained by wall cleat.
   m.box((x0+.14,cy,z+.22),(.055,.34,.44),'Oak',.014)
   m.rod((x0+.14,cy,z+.43),(x0+.14,cy,z+1.89),.020,'Oak',8)
   m.box((x0+.095,cy,z+1.56),(.19,.15,.055),'Iron',.005)
  else:
   # Portable copper washing basin on the forward workbench, supplied by a
   # bulkhead-fastened tap, rather than another inkpot/writing desktop.
   xx=x1-2.0;yy=y1-.60
   m.lathe((xx,yy,z+.9348),[(0,.15),(.045,.21),(.16,.26),(.19,.27),(.20,.25),(.15,.225),(.035,.13)],'Copper',24)
   m.tube([(xx,y1-.035,z+1.12),(xx,y1-.30,z+1.12),(xx,yy,z+1.27),(xx,yy,z+1.18)],.018,'Brass',10)
   m.cylinder((xx,y1-.035,z+1.12),.045,.055,'Brass',12,(0,1,0))
 elif k=='pantry':
  xx=x0+1.30;yy=cy
  m.box((xx,yy,z+.909),(.65,.40,.018),'Steel',.009)
  for i in range(5):m.lathe((xx-.12,yy,z+.9178+i*.0178),[(0,.10),(.012,.13),(.018,.12)],'Porcelain',16)
  m.box((xx+.22,yy,z+.9478),(.20,.29,.06),'Linen',.012)
  m.lathe((xx+.23,yy+.09,z+.9776),[(0,.025),(.09,.035),(.13,.022)],'Porcelain',12)
 elif k in ('bath','wc','third_wash','barber'):
  # Use the SAME washstand stations and rotations as fit_service. The
  # former general x0+1.1/y1-.29 rule left soap between multiple basins.
  from visual_design import washstand_stations
  for wx,wy,wa in washstand_stations(r):
   sx=wx-.245*math.cos(wa)+.17*math.sin(wa);sy=wy-.245*math.sin(wa)-.17*math.cos(wa)
   m.lathe((sx,sy,z+WASHSTAND_TOP-.0002),[(0,.035),(.01,.055),(.022,.060),(.026,.05)],'Porcelain',14)
   m.box((sx,sy,z+WASHSTAND_TOP+.0416),(.065,.04,.032),'Ivory',.006,wa)
  if x1-x0>2:
   tx=x1-.40
   for xx0 in (tx-.20,tx+.20):m.rod((xx0,y1-.035,z+1.02),(xx0,y1-.19,z+1.02),.012,'Brass',8)
   m.rod((tx-.22,y1-.19,z+1.02),(tx+.22,y1-.19,z+1.02),.011,'Brass',8)
   m.box((tx,y1-.205,z+.85),(.28,.028,.34),'Linen',.006)
  if k=='bath':
   # Floor grate and a robe hook mounted into the end wall.
   m.box((cx,y0+.75,z-.0047),(.23,.23,.010),'Grating',.003)
   m.box((x1-.065,cy,z+1.65),(.095,.08,.10),'Oak',.006)
   m.tube([(x1-.08,cy,z+1.65),(x1-.22,cy,z+1.62),(x1-.24,cy,z+1.69)],.012,'Brass',8)
 elif k=='hospital':
  # Floor-supported privacy rail at the head end, not a floating curtain.
  for xx in (x0+1.15,x0+2.37):
   m.cylinder((xx,cy+1.35,z+.025),.065,.05,'Iron',12)
   m.rod((xx,cy+1.35,z+.05),(xx,cy+1.35,z+2.06),.016,'Iron',8)
  m.rod((x0+1.15,cy+1.35,z+2.06),(x0+2.37,cy+1.35,z+2.06),.018,'Iron',8)
  for i in range(7):
   xx=x0+1.21+i*.085;m.box((xx,cy+1.35+(i%2)*.025,z+1.29),(.09,.025,1.42),'Linen',.005)
   m.box((xx,cy+1.35+(i%2)*.0125,z+2.012),(.033,.052,.045),'Linen',.004)
   m.ring((xx,cy+1.35,z+2.04),.025,.004,'Steel',12,4,(1,0,0))
  # Mounted clinical notice and simple thermometer rather than gilded art.
  framed_panel(m,x1-.09,cy,z+1.70,.55,.56,'Notice',-math.pi/2,'Ivory')
  m.box((x0+.09,cy-1.7,z+1.50),(.07,.10,.42),'Ivory',.008)
  m.rod((x0+.128,cy-1.7,z+1.35),(x0+.128,cy-1.7,z+1.65),.005,'Red',6)
 elif k=='office':
  framed_panel(m,x1-.10,cy,z+1.71,1.0,.55,'Notice',-math.pi/2,'Walnut')
  wall_clock(m,x0+.10,cy,z+1.80,math.pi/2)
  m.append(book_stack(2),(x0+1.1,y1-.65,z+DESK_PAD_TOP+.0076))
 elif k=='mail':
  framed_panel(m,x1-.10,cy,z+1.70,1.0,.45,'Notice',-math.pi/2,'Oak')
 elif k=='cold_store':
  # Insulated room thermometer, wall-fixed brine/drain support, no claim
  # of powered refrigeration or made-up extra connected process networks.
  m.box((x0+.09,cy+1.1,z+1.50),(.07,.15,.44),'Oak',.009)
  m.box((x0+.132,cy+1.1,z+1.50),(.015,.095,.36),'Porcelain',.003)
  m.rod((x0+.143,cy+1.1,z+1.36),(x0+.143,cy+1.1,z+1.61),.005,'Red',6)
  m.box((cx,cy,z-.0047),(.30,.30,.010),'Grating',.003)
 elif k in ('wheelhouse','chart'):
  framed_panel(m,x0+.11,cy-1.2,z+1.75,.65,.40,'Notice',math.pi/2,'Teak')
  # Binoculars rest on the already modelled chart/writing surface.
  xx=x0+1.1;yy=y1-.65
  first=len(m.v)
  for dx in (-.043,.043):
   m.cylinder((xx+dx,yy,z+.855),.025,.15,'Black',12,(0,1,0))
   m.ring((xx+dx,yy-.078,z+.855),.026,.006,'Brass',12,5,(0,1,0))
  m.rod((xx-.043,yy,z+.855),(xx+.043,yy,z+.855),.008,'Brass',7)
  m.rest(first,z+DESK_PAD_TOP+.0078)
 elif k=='bar':
  # Cell-level variation is in drinks_rack; a mounted work notice avoids
  # adding an impossible freestanding counter in the 2.05m-wide store.
  framed_panel(m,x1-.09,cy,z+1.65,.65,.40,'Notice',-math.pi/2,'Mahogany')
 m.tags['PurposeSpecificWorkingDetail']+=1
