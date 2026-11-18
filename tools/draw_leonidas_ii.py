"""Editable SVG arrangement/datum/flow sheets from the new metric contract.
These are analytical project drawings, NOT traced historical shipyard plans.
Actual mesh evidence remains in renders/leonidas_ii/ and its camera register.
"""
from pathlib import Path
import sys,math,json,html
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS,DECKS,STAIRS,CASINGS,hb,beam_deck,deck_z,keel_z,BOAT_MOUNTS
OUT=ROOT/'drawings'/'leonidas_ii';OUT.mkdir(parents=True,exist_ok=True)
DATA=json.loads((ROOT/'exports'/'leonidas_ii'/'build_data.json').read_text())['counts']
def esc(s):return html.escape(str(s))
class Sheet:
 def __init__(self,w,h,title):
  self.w,self.h=w,h;self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><title>{esc(title)}</title><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M0,8 L8,0" stroke="#9b7d4c" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="#f4f0e7"/>']
 def text(self,x,y,text,size=18,color='#223841',anchor='start',weight='normal'):
  self.p.append(f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{esc(text)}</text>')
 def rect(self,x,y,w,h,fill='none',stroke='#33464b',sw=1,rx=0):self.p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def path(self,points,color='#33464b',sw=1,fill='none',arrow=False,close=False,dash=None):
  d='M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in points)+(' Z' if close else '');self.p.append(f'<path d="{d}" stroke="{color}" stroke-width="{sw}" fill="{fill}"'+(' marker-end="url(#arrow)"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def save(self,name):
  (OUT/name).write_text('\n'.join(self.p)+f'<metadata>Generated from interfaces/leonidas_ii_ship.json by tools/draw_leonidas_ii.py. Fictional 1889 Aurelian design; not a museum or certified naval drawing.</metadata></svg>')

COLORS={'cabin_first':'#d9c08a','cabin_second':'#c6d4c3','cabin_officer':'#adc5cd','cabin_captain':'#adc5cd','dorm_crew':'#b9ced2','dorm_third':'#d3d9b0','machinery':'#c5c6c5','stairhall':'#eee4cd','steering':'#bbb9bc'}
def ga():
 s=Sheet(4400,4920,'SS Aurelian — LEONIDAS-II analytical general arrangement')
 s.text(100,82,'SS AURELIAN · 1889',46,weight='bold');s.text(100,126,'LEONIDAS-II / 7 DECKS / 203 PHYSICAL SPACES / METRES, +X BOW TO RIGHT, PORT AT TOP',24)
 s.text(100,165,'Project-derived arrangement. Not a traced museum plan; see DESIGN_AND_SOURCES.md. Actual mesh cutaways and per-room images are separate evidence.',20)
 scale=25.;cx=2200
 for i,(dk,z) in enumerate(DECKS.items()):
  y=485+i*630;s.text(120,y-250,f'{dk.upper()}  /  z = {z:.2f} m above baseline',27,weight='bold')
  def pt(x,yy):return cx+x*scale,y-yy*scale
  def width(x):
   if dk=='bridge':return 7.025 if 31.81<x<43 else 0
   if dk=='boat':return max(0,beam_deck(x)-.52) if -62<x<50 else 0
   if dk=='promenade':return max(0,beam_deck(x)-.38) if -72<x<63 else 0
   return hb(x,min(z,deck_z(x)-.01))
  xx=[-82.99+j*165.98/500 for j in range(501)];outline=[pt(x,width(x)) for x in xx]+[pt(x,-width(x)) for x in reversed(xx)]
  s.path(outline,'#34464c',2,'#ebe4d5',close=True);s.path([pt(-83,0),pt(83,0)],'#8c9a9b',1,dash='10 8')
  for r in ROOMS:
   if r['deck']!=dk:continue
   x0,x1,y0,y1=r['x0'],r['x1'],r['y0'],r['y1'];kind=r['kind'];x,yy=pt(x0,y1);w,h=(x1-x0)*scale,(y1-y0)*scale
   s.rect(x,yy,w,h,COLORS.get(kind,'#d9cab4'),'#5a665f',.9)
   s.text(x+w/2,yy+h/2+4,r['id'],min(13 if w<100 else 17,(w-4)/max(1,len(r['id'])*.62)),anchor='middle',weight='bold')
   if w>130 and h>62:
    label=r['name'];limit=min(37,int((w-10)/6.8));label=label if len(label)<limit else label[:max(1,limit-1)]+'…';s.text(x+w/2,yy+h/2+27,label,13,anchor='middle')
   if kind=='machinery':continue
   wall=r['door_wall'];u=r['door_u'];dw=r['door_width'];xy=(u,r[wall]) if wall.startswith('y') else (r[wall],u)
   if wall.startswith('y'):a,b=pt(xy[0]-dw/2,xy[1]),pt(xy[0]+dw/2,xy[1]);leaf=pt(xy[0]-dw/2,xy[1]+(dw if wall=='y0' else -dw))
   else:a,b=pt(xy[0],xy[1]-dw/2),pt(xy[0],xy[1]+dw/2);leaf=pt(xy[0]+(dw if wall=='x0' else -dw),xy[1]-dw/2)
   s.path([a,b],'#f4f0e7',3.5);s.path([a,leaf],'#ad5541',1.2)
  for c in CASINGS:
   if c['z0']<z<c['z1']:
    a,b,c0,d=c['rect'];x,yy=pt(a,d);s.rect(x,yy,(b-a)*scale,(d-c0)*scale,'url(#hatch)','#806c4e',1.6)
  for st in STAIRS:
   if abs(st['z0']-z)>.05 and abs(st['z1']-z)>.05:continue
   a,b=min(st['x0'],st['x1']),max(st['x0'],st['x1']);x,yy=pt(a,st['y']+st['width']/2)
   s.rect(x,yy,(b-a)*scale,st['width']*scale,'#eed5c7','#a04f3a',1)
   s.path([pt(st['x0'],st['y']),pt(st['x1'],st['y'])],'#a04f3a',1.5,arrow=True)
  for x in range(-80,81,10):s.path([pt(x,-9.6),pt(x,-9.9)],'#667777');s.text(*pt(x,-10.7),str(x),13,anchor='middle')
  s.text(120,y+295,'BOW →  |  Primary doorway / leaf shown; secondary public-room openings are detailed in the model. Stair arrows point UP.',16)
 s.text(100,4740,'LEGEND',24,weight='bold')
 x=100
 for label,col in [('First class','#d9c08a'),('Second class','#c6d4c3'),('Third class','#d3d9b0'),('Crew/officers','#b9ced2'),('Public/service','#d9cab4'),('Machinery below orlop','#c5c6c5')]:
  s.rect(x,4770,24,24,col);s.text(x+35,4790,label,20);x+=650
 s.text(100,4860,f"Built berths: {DATA['actual_first_berths']+DATA['actual_second_berths']+DATA['actual_third_berths']} passengers ({DATA['actual_first_berths']} / {DATA['actual_second_berths']} / {DATA['actual_third_berths']}) + {DATA['actual_crew_berths']} crew. Planning targets 900 / 196 are NOT achieved. Not a stability, safety or capacity certificate.",20)
 s.save('General_Arrangement.svg')

def datums():
 s=Sheet(1800,1450,'Aurelian principal dimensions and coordinate handoff')
 s.text(65,65,'AURELIAN · DIMENSIONS & DATUMS',34,weight='bold');s.text(65,103,'Fictional single-screw express liner / new project geometry basis / not a certified naval drawing',19)
 sc=9.;xc=900;yb=560
 def pt(x,z):return xc+x*sc,yb-z*sc
 xx=[-82.99+j*165.98/300 for j in range(301)];s.path([pt(x,keel_z(x)) for x in xx]+[pt(x,deck_z(x)) for x in reversed(xx)],'#263d47',2,'#d0d4ce',close=True)
 for z,txt in [(0,'BASELINE'),(6.5,'LOAD WATERLINE'),(8.8,'MAIN'),(11.8,'SALOON'),(14.4,'PROMENADE'),(17.2,'BOAT'),(20,'BRIDGE')]:
  s.path([pt(-84,z),pt(85,z)],'#3e8995' if z==6.5 else '#929b96',1,dash='9 7');s.text(30,pt(-84,z)[1]-4,txt,14)
 for st in ((-60,50,17.2),(33,41,22.5)):
  a,b,z=st;s.rect(*pt(a,z),(b-a)*sc,(z-11.8)*sc,'#f1eee3','#777f7b',1)
 for x in (4.5,30):s.rect(*pt(x-1.8,30.6),3.6*sc,13.4*sc,'#c8a254','#5b5949',1)
 s.path([pt(-83,-4),pt(83,-4)],'#294650',1.4,arrow=True);s.text(900,yb+70,'166.00 m LOA  /  158.00 m LBP',24,anchor='middle',weight='bold')
 s.text(65,655,'Analytical hull/level envelope; deck massing simplified. Refer to the actual model renders for the complete silhouette.',17)
 s.text(65,690,'PRINCIPAL ENVELOPE',23,weight='bold')
 for j,line in enumerate(['LOA 166.00 m · moulded beam 18.40 m · design draught 6.50 m','At 0.28 m/stud: 592.857 × 65.714 × 23.214 studs','Authoring (x,y,z) = (+X bow,+Y port,+Z baseline)','GLB metric point = (−y, z−6.5, −x); Roblox studs = metric / 0.28','Final pivot: amidships at load waterline. Scale ONCE using calibration.']):s.text(65,735+j*35,line,23)
 s.text(65,970,'BOAT MOUNTS — UNILATERAL COMPATIBILITY HANDOFF',23,weight='bold')
 for j,b in enumerate(BOAT_MOUNTS):
  s.text(65,1018+j*43,f"{b['id']}  /  {b['craft']}  /  source centre {b['position']} m  /  required SWL {b['required_swl_kg']:,} kg",21)
 s.text(65,1170,'PORT INTERFACE',23,weight='bold')
 s.text(65,1210,'Ship boarding at +2.3 m WL / host gangway surface approx. +2.4 m; quay assumption +4.0 m.',22)
 s.text(65,1248,'5 m hinged gangways target the rise; transformed world fit and operation against the real quay are UNVERIFIED.',21)
 s.text(65,1310,'No other agent assets changed. Only three host sockets are modeled; not the inherited eleven-boat inventory.',21,'#9a4834')
 s.text(65,1372,'Source: interfaces/leonidas_ii_ship.json; exact source-space craft contacts and sling stations are in its boat_mounts records.',18)
 s.save('Dimensions_And_Datums.svg')

def flow():
 s=Sheet(1800,1270,'Aurelian simplified machinery flow schematic')
 s.text(65,65,'AURELIAN · CONNECTED PLANT',36,weight='bold');s.text(65,105,'Flow schematic of the named modeled routes. NOT physical pipe routing, thermodynamic proof or pressure-vessel certification.',21)
 steam='#ad5a3c';water='#367d94';feed='#518169';exhaust='#6d6684'
 def box(x,y,w,h,title,sub,fill='#e5e0d4'):
  s.rect(x,y,w,h,fill,'#43565b',1.5,8);s.text(x+w/2,y+32,title,min(21,(w-24)/max(1,len(title)*.62)),anchor='middle',weight='bold');s.text(x+w/2,y+62,sub,min(17,(w-24)/max(1,len(sub)*.55)),anchor='middle')
 for i,(xx,label) in enumerate([(3.0,'AFTER'),(15.5,'MIDDLE'),(28.0,'FORWARD')]):
  y=190+i*160;box(65,y,350,110,label+' BOILER ROW',f'3 × single-ended Scotch · source x={xx} m')
  s.text(240,y+91,'Ø 4.2 m · barrel 3.35 m · 11 bar target',16,anchor='middle')
  s.path([(415,y+45),(485,y+45),(485,205)],steam,4,arrow=False)
 s.path([(485,205),(620,205)],steam,5,arrow=True);s.text(492,185,'MainSteam',18,steam)
 for x,title,sub in [(620,'HP','bore 1.40 m'),(955,'IP','bore 2.25 m'),(1290,'LP','bore 3.50 m')]:box(x,160,255,115,title,sub,'#d9d9cb')
 s.path([(875,218),(955,218)],steam,4,arrow=True);s.text(912,147,'HP→IP receiver',16,steam,anchor='middle')
 s.path([(1210,218),(1290,218)],steam,4,arrow=True);s.text(1248,147,'IP→LP receiver',16,steam,anchor='middle')
 box(665,345,830,90,'COMMON THREE-THROW CRANKSHAFT','1.8 m stroke · 0.9 m crank · 3.0 m rods · signed 72 rpm nominal','#e1d5bd')
 for x in (747,1082,1417):s.path([(x,275),(x,345)],'#54656a',3,arrow=True)
 box(970,550,340,100,'SURFACE CONDENSER','source centre (−24.8, −1.85, 2.75) m','#d6e1df')
 s.path([(1545,218),(1620,218),(1620,505),(1140,505),(1140,550)],exhaust,5,arrow=True);s.text(1280,489,'LP_Exhaust_to_Condenser',18,exhaust)
 box(1410,760,310,90,'CIRCULATING PUMP','seawater / dedicated steam driver','#d2e1e4')
 s.text(1560,925,'SEA INTAKE',23,water,anchor='middle',weight='bold');s.path([(1560,900),(1560,850)],water,5,arrow=True)
 s.path([(1410,800),(1370,800),(1370,600),(1310,600)],water,5,arrow=True)
 s.path([(970,600),(900,600),(900,965),(1175,965)],water,5,arrow=True);s.text(1190,972,'OVERBOARD',23,water,weight='bold')
 box(565,760,300,90,'HOTWELL','condenser condensate return','#d8e4d5');s.path([(1080,650),(1080,700),(715,700),(715,760)],feed,4,arrow=True)
 box(65,760,355,90,'RECIPROCATING FEED PUMPS','Row1/2/3 feed headers → 9 boilers','#d8e4d5');s.path([(565,805),(420,805)],feed,4,arrow=True)
 s.path([(65,805),(35,805),(35,235),(65,235)],feed,4,arrow=True)
 box(555,1010,510,90,'AUXILIARY REDUCING STEAM MAIN','feed/circulation · dynamos · steam steering','#e5d8c8')
 s.path([(485,310),(520,310),(520,1054),(555,1054)],steam,3,arrow=True)
 s.text(65,1160,'Mechanical output: aligned tailshaft / bearings / stern tube → pitched four-blade Ø 5.30 m screw; rudder and quadrant are separate movers.',21)
 s.text(65,1210,'Actual polyline endpoints and media: exports/leonidas_ii/build_data.json → pipe_network. Internal machinery details and performance remain simplified.',19)
 s.save('Machinery_Flow.svg')
if __name__=='__main__':
 ga();datums();flow()
 if '--pdf' in sys.argv:
  import cairosvg
  for file in OUT.glob('*.svg'):cairosvg.svg2pdf(url=str(file),write_to=str(file.with_suffix('.pdf')))
 print('Wrote editable analytical sheets, not historical tracings.')
