"""One-off physical micro corrections, staged atomically. DO NOT RERUN once applied."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'blender/leonidas_ii'
staged={}
def load(n):return (ROOT/n).read_text()
def sub(s,a,b):
 assert s.count(a)==1,(a[:110],s.count(a))
 return s.replace(a,b)
def stage(n,s):compile(s,str(ROOT/n),'exec');staged[n]=s
# The caller supplies an OUTER face station. Calculate bolt centre from its
# actual finite height, rather than a 37mm stand-off that floated small heads.
s=load('meshkit.py')
s=sub(s," m.cylinder(c,r,.06,t,16,axis);bolts(m,tuple(Vector(c)+Vector(axis).normalized()*.037),r*.78,count,axis,min(.018,r*.10))", " size=min(.018,r*.10)\n m.cylinder(c,r,.06,t,16,axis)\n bolts(m,tuple(Vector(c)+Vector(axis).normalized()*(.030+size*.35-.0002)),r*.78,count,axis,size)")
stage('meshkit.py',s)
s=load('machinery.py')
s=sub(s,"bolts(m,(x-1.81,y,z),1.98", "bolts(m,(x-1.80715,y,z),1.98")
s=sub(s,"bolts(m,(x-1.95,y+yy,zf),.344", "bolts(m,(x-1.894,y+yy,zf),.344")
s=sub(s,"[(0,.29),(.07,.28),(.09,.23)],'Iron',18,(-1,0,0));bolts(m,(x-1.91,y,z+1.12)", "[(0,.29),(.07,.29),(.09,.29)],'Iron',18,(-1,0,0));bolts(m,(x-1.88505,y,z+1.12)")
s=sub(s,"yy-side*.18,2.48", "yy-side*.1448,2.48")
s=sub(s,"  for yy in (-.43,.43):bolts(still,(x,yy,2.93),.10,4,(0,0,1),.026)", "  for yy in (-.43,.43):\n   still.box((x,yy,2.91),(.68,.28,.12),'Engine',.018)\n   bolts(still,(x,yy,2.9789),.10,4,(0,0,1),.026)")
s=sub(s,"bolts(still,(x,yy,2.04),.14", "bolts(still,(x,yy,2.15855),.14")
s=sub(s,"bolts(still,(x,0,z1+.10)","bolts(still,(x,0,z1+.0975)")
s=sub(s,"bolts(still,(xx,side*2.40,2.08)","bolts(still,(xx,side*2.40,2.0761)")
s=sub(s,"still.box((x,-rr-.18,8.85)","still.box((x,-rr-.155,8.85)")
s=sub(s,"flange(still,(x,-rr-.38,zz)","flange(still,(x,-rr-.355,zz)")
s=sub(s,"still.rod((x,-rr-.38,zz)","still.rod((x,-rr-.355,zz)")
s=sub(s," for p in [(-8.8,-2.3,8.9),(-11.5,-1.2,9.25)]:handwheel(still,p,.25,(1,0,0),'Red')", " # Accessible, stem-carried main valves: no handwheel rim buried in\n # the HP chest or relied upon as the only pipe contact.\n for (px,py,pz),wy in (((-8.8,-2.3,8.9),-2.70),((-11.5,-1.15,9.25),-1.62)):\n  still.lathe((px,py,pz),[(0,.075),(-.17,.075),(-.25,.035)],'Brass',14,(0,1,0))\n  still.rod((px,py,pz),(px,wy,pz),.026,'Brass',10)\n  handwheel(still,(px,wy,pz),.25,(0,1,0),'Red')")
s=sub(s," still.box((-10.70,-3.3,2.48),(.19,.92,1.43),'Engine',.025)", " still.box((-10.70,-3.3,2.48),(.19,.92,1.43),'Engine',.025)\n still.box((-10.70,-3.3,1.63),(.34,1.10,.06),'Engine',.012)\n for yy in (-3.65,-2.95):still.rod((-10.70,yy,1.63),(-10.70,yy,1.80),.025,'Iron',10)")
s=sub(s," for xx in (-25.92,-23.68):flange", " # Two floor-founded curved saddles support the actual condenser shell;\n # steam/water pipe contact is not a substitute for a foundation.\n for xx in (-25.45,-24.15):\n  m.box((xx,-1.85,1.63),(.44,1.28,.06),'Engine',.012)\n  top=[(dy,2.75-math.sqrt(.65**2-dy**2)+.015) for dy in (-.56,-.42,-.28,-.14,0,.14,.28,.42,.56)]\n  profile=[(-.56,1.65),(.56,1.65)]+list(reversed(top));nn=len(profile)\n  vv=[(xx+dx,-1.85+dy,zz) for dx in (-.16,.16) for dy,zz in profile]\n  ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]+[(j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn)]\n  m.add(vv,ff,'Engine')\n  for sy in (-.57,.57):m.cylinder((xx,-1.85+sy,1.6661),.018,.0126,'Steel',6)\n for xx in (-25.92,-23.68):flange")
s=sub(s,"m.box((-5.88,2.586,2.30)","m.box((-5.88,2.5877,2.30)")
s=sub(s,"(xx,3.78,2.87),.023", "(xx,3.75,2.87),.023")
s=sub(s,"  # Copper turns wrap the two field pole cores, visibly distinct from shaft.", "  # A real common spindle connects commutator, rotor and flywheel.\n  m.rod((xx-1.04,-4.05,2.4),(xx+.98,-4.05,2.4),.075,'Steel',16)\n  # Copper turns wrap the two field pole cores, visibly distinct from shaft.")
s=sub(s,"  for dx in (-.62,.62):m.rod((xx+dx,-4.88,1.65),(xx+dx,-4.88,4.28),.028,'Iron',8)", "  for dx in (-.62,.62):\n   m.cylinder((xx+dx,-4.88,1.63),.055,.06,'Iron',12)\n   m.rod((xx+dx,-4.88,1.63),(xx+dx,-4.88,4.28),.028,'Iron',8)")
s=sub(s,"   for zz in (3.12,3.48):m.cylinder((xx+dx,-4.73,zz),.040,.08,'Porcelain',10,(0,1,0))", "   for zz in (3.12,3.48):\n    m.cylinder((xx+dx,-4.7425,zz),.040,.08,'Porcelain',10,(0,1,0))\n    m.rod((xx+dx,-4.725,zz),(xx+dx,-4.64,zz),.020,'Copper',8)\n   m.box((xx+dx,-4.635,3.48),(.060,.040,.075),'Copper',.006)")
s=sub(s,"m.cylinder((-9.15,-4.0,2.64),.04,.25,'Steel',8,(1,0,0))", "m.cylinder((-9.15,-4.0,2.64),.04,.25,'Steel',8,(1,0,0))\n for dx in (-.10,.10):m.box((-9.15+dx,-4.0,2.63),(.065,.35,.12),'Iron',.008)")
s=sub(s,"flange(still,(-70.65,0,SHAFT_Z)","flange(still,(-70.68,0,SHAFT_Z)")
s=sub(s,"sections=[(.48,.30)","sections=[(.43,.30)")
s=sub(s,"bolts(prop,(PROP_X+.52,0,SHAFT_Z)","bolts(prop,(PROP_X+.5082,0,SHAFT_Z)")
s=sub(s,"  for side in (-1,1):rudder.box((-80.55,side*.106,zz),(1.9,.04,.11),'Iron',.01)", "  if zz+.055<max(p[1] for p in outline):\n   # Each rib remains inside BOTH edges of the raked blade at its full\n   # finite height. No 8.1m ribs above the blade, no protruding upper ends.\n   sections=[]\n   for zedge in (zz-.055,zz+.055):\n    xs=[a[0]+(b[0]-a[0])*(zedge-a[1])/(b[1]-a[1]) for a,b in zip(outline,outline[1:]+outline[:1]) if min(a[1],b[1])<=zedge<=max(a[1],b[1]) and abs(b[1]-a[1])>1e-9]\n    sections.append((min(xs),max(xs)))\n   xa=max(v[0] for v in sections)+.025;xb=min(v[1] for v in sections)-.025\n   for side in (-1,1):rudder.box(((xa+xb)/2,side*.106,zz),(xb-xa,.04,.11),'Iron',.010)")
stage('machinery.py',s)
# Two earlier same-file parallel edits had overwritten these specific changes.
# Reapply serially and verify actual source through the next physical survey.
s=load('public_rooms.py')
s=sub(s,"    for zz in (.16,h-.20):m.ring((xx,yy,z+zz),.15,.008,'Brass',16,5)", "    # Collars seat at the real broad base/capital, not around a taper.\n    for zz,rad in ((.12,.16),(h-.18,.15)):m.ring((xx,yy,z+zz),rad,.008,'Brass',16,6)")
stage('public_rooms.py',s)
s=load('working_detail.py')
s=sub(s,"m.rod((x0+.14,cy-1.7,z+1.35),(x0+.14,cy-1.7,z+1.65)","m.rod((x0+.128,cy-1.7,z+1.35),(x0+.128,cy-1.7,z+1.65)")
stage('working_detail.py',s)
for n,s in staged.items():(ROOT/n).write_text(s)
print('APPLIED staged correction 6:',', '.join(staged))
