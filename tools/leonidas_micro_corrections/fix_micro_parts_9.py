"""One-off final door clearances/shared stations and visible shaft bores. Never rerun."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'blender/leonidas_ii'
staged={}
def load(n):return (ROOT/n).read_text()
def sub(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a))
 return s.replace(a,b)
def stage(n,s):compile(s,str(ROOT/n),'exec');staged[n]=s
s=load('visual_design.py')
s += '''\n\ndef washstand_stations(r):
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
'''
stage('visual_design.py',s)
s=load('interiors.py')
s=sub(s,'ceiling_beams,is_external_window','ceiling_beams,is_external_window,washstand_stations')
s=sub(s,"x,cy+.28,z);proxy((x,cy+.28,z+1.12)","x,cy+.38,z);proxy((x,cy+.38,z+1.12)")
s=sub(s,"    if n==1 and r['door_wall']=='y1':\n     place(m,washstand(),x0+.29,cy+.55,z,math.pi/2);panel_mirror(m,x0+.08,cy+.55,z+1.5,ang=math.pi/2)\n    else:\n     wx=[x0+.40,r['door_u']-r['door_width']/2-.70,r['door_u']+r['door_width']/2+.70,x1-.40][i] if r['id']=='P_Wash' else xx\n     place(m,washstand(),wx,y1-.35,z);panel_mirror(m,wx,y1-.08,z+1.5)", "    wx,wy,wa=washstand_stations(r)[i];place(m,washstand(),wx,wy,z,wa)\n    if wa:panel_mirror(m,x0+.08,wy,z+1.5,ang=wa)\n    else:panel_mirror(m,wx,y1-.08,z+1.5)")
stage('interiors.py',s)
s=load('working_detail.py')
s=sub(s,"  if k=='bath':stations=[(cx,y1-.30)]\n  elif k=='barber':stations=[(x0+1.10,y1-.40),(x1-1.10,y1-.40)]\n  else:\n   n=max(1,int((x1-x0)/1.3))\n   stations=[] if n==1 and r['door_wall']=='y1' else [(x0+(i+.5)*(x1-x0)/n,y1-.35) for i in range(n)]\n  for wx,wy in stations:\n   sx,sy=wx-.245,wy-.17", "  from visual_design import washstand_stations\n  for wx,wy,wa in washstand_stations(r):\n   sx=wx-.245*math.cos(wa)+.17*math.sin(wa);sy=wy-.245*math.sin(wa)-.17*math.cos(wa)")
s=sub(s,"m.box((sx,sy,z+WASHSTAND_TOP+.0416),(.065,.04,.032),'Ivory',.006)", "m.box((sx,sy,z+WASHSTAND_TOP+.0416),(.065,.04,.032),'Ivory',.006,wa)")
stage('working_detail.py',s)
s=load('public_rooms.py')
s=sub(s," else:  # small steerage mess, not a mahogany first-class table\n  put(utility_table(1.8,.65,.77),cx,cy)\n  for side in (-1,1):\n   put(plain_bench(1.9,'Oak',False),cx,cy+side*.68)\n   for dx in (-.6,0,.6):SEATS.append(dict(position=(cx+dx,cy+side*.68,z+.47),yaw=0 if side>0 else math.pi,size=(.4,.30,.10)));seats+=1\n  ceiling_fixture(m,r,cx,cy,'marine',True)", " else:  # small steerage mess, not a mahogany first-class table\n  tx=cx+(.20 if r['door_wall']=='x0' else -.20 if r['door_wall']=='x1' else 0)\n  put(utility_table(1.8,.65,.77),tx,cy)\n  for side in (-1,1):\n   put(plain_bench(1.9,'Oak',False),tx,cy+side*.68)\n   for dx in (-.6,0,.6):SEATS.append(dict(position=(tx+dx,cy+side*.68,z+.47),yaw=0 if side>0 else math.pi,size=(.4,.30,.10)));seats+=1\n  ceiling_fixture(m,r,tx,cy,'marine',True)")
stage('public_rooms.py',s)
s=load('meshkit.py')
s=sub(s,"def flange(m,c,r,axis=(0,0,1),t='Iron',count=8):\n size=min(.018,r*.10)\n m.cylinder(c,r,.06,t,16,axis)", "def flange(m,c,r,axis=(0,0,1),t='Iron',count=8,bore=None):\n size=min(.018,r*.10)\n if bore is None:m.cylinder(c,r,.06,t,16,axis)\n else:\n  assert 0<bore<r\n  m.lathe(c,[(-.030,r),(.030,r),(.030,bore),(-.030,bore)],t,16,axis,caps=False,closed=True)")
stage('meshkit.py',s)
s=load('machinery.py')
s=sub(s,"  still.box((x,0,2.48),(.68,.84,.80),'Engine',.08)\n  still.cylinder((x,0,SHAFT_Z),.40,.70,'Brass',20,(1,0,0));still.cylinder((x,0,SHAFT_Z+.04),.44,.36,'Engine',20,(1,0,0))", "  # A genuinely bored journal bearing: the former solid bronze/cast\n  # cylinders and tall chock occupied the rotating shaft's own volume.\n  still.box((x,0,2.37),(.68,.84,.50),'Engine',.04)\n  still.lathe((x,0,SHAFT_Z),[(-.35,.40),(.35,.40),(.35,.286),(-.35,.286)],'Brass',48,(1,0,0),caps=False,closed=True)\n  still.lathe((x,0,SHAFT_Z),[(-.18,.44),(.18,.44),(.18,.398),(-.18,.398)],'Engine',32,(1,0,0),caps=False,closed=True)")
s=sub(s,"  still.box((float(x)+.9,0,2.25),(.75,1.10,1.30),'Engine',.04);still.cylinder((float(x)+.9,0,SHAFT_Z),.38,.6,'Brass',20,(1,0,0))", "  still.box((float(x)+.9,0,2.12),(.75,1.10,1.04),'Engine',.04)\n  still.lathe((float(x)+.9,0,SHAFT_Z),[(-.30,.38),(.30,.38),(.30,.286),(-.30,.286)],'Brass',48,(1,0,0),caps=False,closed=True)\n  still.lathe((float(x)+.9,0,SHAFT_Z),[(-.15,.43),(.15,.43),(.15,.375),(-.15,.375)],'Engine',32,(1,0,0),caps=False,closed=True)")
s=sub(s," still.box((-27.8,0,2.25),(2.2,1.50,1.30),'Engine',.055)", " # Open thrust-collar bay: floor-founded sole, side cheeks and two bored\n # end carriers. Do not enclose all rotating collars in a solid cuboid.\n still.box((-27.8,0,1.80),(2.2,1.50,.40),'Engine',.040)\n for yy in (-.58,.58):still.box((-27.8,yy,2.55),(2.2,.20,1.10),'Engine',.025)\n for xx in (-28.78,-26.98):\n  still.box((xx,0,2.25),(.20,.90,.54),'Engine',.020)\n  still.lathe((xx,0,SHAFT_Z),[(-.07,.52),(.07,.52),(.07,.286),(-.07,.286)],'Brass',48,(1,0,0),caps=False,closed=True)")
s=sub(s,"flange(still,(-70.68,0,SHAFT_Z),.54,(1,0,0),count=14);flange(still,(-76.56,0,SHAFT_Z),.52,(1,0,0),count=14)", "flange(still,(-70.68,0,SHAFT_Z),.54,(1,0,0),count=14,bore=.305);flange(still,(-76.56,0,SHAFT_Z),.52,(1,0,0),count=14,bore=.305)")
s=sub(s,"(-75.5,side*.72,z+1.05),.023", "(-75.85,side*.72,z+1.05),.023")
s=sub(s,"handwheel(m,(-75.5,side*.72,z+1.05)","handwheel(m,(-75.85,side*.72,z+1.05)")
stage('machinery.py',s)
# Extend the actual saved-door screen to the steering equipment and helm,
# not only items carrying the furniture/navigation kind tags.
s=load('audit_door_sweeps.py')
s=sub(s,"in ('furniture','navigation')", "in ('furniture','navigation','steering','mover')")
s=s.replace('fixed in-room furniture/navigation','in-room furniture/navigation/steering/default-pose movers').replace('door-finite-sweep/1.1','door-finite-sweep/1.2')
stage('audit_door_sweeps.py',s)
for n,s in staged.items():(ROOT/n).write_text(s)
print('APPLIED staged correction 9:',', '.join(staged))
