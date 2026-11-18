"""Recorded first-render / route-review corrections, not a production build.
Idempotence is not claimed; this one-off file is retained for audit provenance.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def change(path,old,new):
 p=ROOT/path;s=p.read_text();assert old in s,(path,old[:100]);p.write_text(s.replace(old,new))
change('shipdesign/leonidas_ii.py',"r.setdefault('door_u',(x0+x1)/2)","r.setdefault('door_u',(x0+x1)/2+(.15 if kind.startswith('cabin') else 0))")
change('shipdesign/leonidas_ii.py',"door_u=float(x+1.28)","door_u=float(x+1.43)")
change('shipdesign/leonidas_ii.py',"(-54.6,-31,1.6,5.1)","(-52.0,-31,1.6,5.1)")
change('shipdesign/leonidas_ii.py',"(-54.6,-31,-5.1,-1.6)","(-52.0,-31,-5.1,-1.6)")
change('shipdesign/leonidas_ii.py',"'orlop','lower',38.0,43.7,5.5,1.2","'orlop','lower',37.0,42.8,6.15,1.0")
change('shipdesign/leonidas_ii.py',"'lower','main',-58.8,-52.4,4.7,1.25","'lower','main',-54.5,-47.8,4.8,1.1")
change('shipdesign/leonidas_ii.py',"'orlop','lower',-58.8,-53.3,5.6,1.2","'orlop','lower',-58.0,-52.4,4.3,1.0")
change('shipdesign/leonidas_ii.py',"'main','saloon',-58.8,-53.6,5.2,1.25","'main','saloon',-54.5,-49.1,4.8,1.1")
change('shipdesign/leonidas_ii.py',"'saloon','promenade',-58.8,-53.6,5.2,1.25","'saloon','promenade',-54.5,-49.1,4.8,1.1")
# Camera clear of the real wardrobe; source walls/furniture are not removed.
change('blender/leonidas_ii/render.py',"pos=(x1-.20,y0+.25,z+1.50);target=(x0+.50,y1-.35,z+1.08);lens=19","pos=((x0+x1)/2+.15,y0+.16 if r['door_wall']=='y0' else y1-.16,z+1.50);target=(x0+.55,y1-.35 if r['door_wall']=='y0' else y0+.35,z+1.05);lens=19")
change('blender/leonidas_ii/render.py',"(139,110,64)","(195,155,88)")
change('blender/leonidas_ii/render.py',"(-139,-104,51)","(-195,-146,72)")
change('blender/leonidas_ii/render.py',"(85,-115,139)","(119,-161,195)")
change('blender/leonidas_ii/render.py',"(133,-105,57)","(186,-147,79)")
# Canonical compact cabin, reflected as a whole for a door at the other end.
change('blender/leonidas_ii/interiors.py',"a.append(sofa(1.62,'GoldCloth'),(0,0,0),math.pi/2)","a.append(sofa(1.62,'GoldCloth'),(0,0,0),-math.pi/2)")
change('blender/leonidas_ii/interiors.py',"z=r['z']+.055;x0,x1,y0,y1=rect(r);cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];w=x1-x0;d=y1-y0","z=r['z']+.055;x0,x1,y0,y1=rect(r);cx=(x0+x1)/2;cy=(y0+y1)/2;kind=r['kind'];w=x1-x0;d=y1-y0\n pstart,lstart,sstart=len(PROXIES),len(LIGHTS),len(SEATS)")
change('blender/leonidas_ii/interiors.py',"lamp(m,cx,cy,r['top']-.18)\n return", "lamp(m,cx,cy,r['top']-.18)\n if r['door_wall']=='y1':\n  m.v=[(x,2*cy-y,zz) for x,y,zz in m.v]\n  for p in PROXIES[pstart:]:p['position'][1]=2*cy-p['position'][1];p['yaw']=-p['yaw']\n  for p in LIGHTS[lstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2])\n  for p in SEATS[sstart:]:p['position']=(p['position'][0],2*cy-p['position'][1],p['position'][2]);p['yaw']=-p['yaw']\n return")
# Wide steerage halls receive dining tables + benches, with usable outer aisles.
change('blender/leonidas_ii/interiors.py',"cy=(y0+y1)/2;ys=[cy-1.68,cy+1.68]\n  if width>10.4:ys+=[y0+1.10,y1-1.10]","cy=(y0+y1)/2;ys=[cy-(2.15 if width>=8 else 1.68),cy+(2.15 if width>=8 else 1.68)]")
change('blender/leonidas_ii/interiors.py',"# Enamel drinking-water tank / wash shelf", "# Enamel drinking-water tank / wash shelf") if False else None
change('blender/leonidas_ii/interiors.py',"m.lathe((x1-.45,(y0+y1)/2,z)","m.lathe((x1-.45,y0+.38,z)")
change('blender/leonidas_ii/interiors.py',"(x1-.45,(y0+y1)/2,z+.28),(x1-.17,(y0+y1)/2,z+.28),(x1-.17,(y0+y1)/2,z+.21)","(x1-.45,y0+.38,z+.28),(x1-.17,y0+.38,z+.28),(x1-.17,y0+.38,z+.21)")
change('blender/leonidas_ii/interiors.py',"for x in np.arange(x0+1,x1-.5,4):lamp", "if width>=8:\n  for xx in np.arange(x0+3.6,x1-2.0,7.04):\n   place(m,table(2.25,.68),float(xx),cy,z)\n   for side in (-1,1):\n    yy=cy+side*.72;m.box((float(xx),yy,z+.45),(2.2,.28,.055),'Oak',.012)\n    for dx in (-.82,.82):\n     m.rod((float(xx)+dx,yy-.11,z+.02),(float(xx)+dx,yy,z+.43),.032,'Iron',7);m.rod((float(xx)+dx,yy+.11,z+.02),(float(xx)+dx,yy,z+.43),.032,'Iron',7)\n   m.tags['SteerageMessTable']+=1\n for x in np.arange(x0+1,x1-.5,4):lamp")
# The galley door leaf must not swing through its work bench.
change('blender/leonidas_ii/interiors.py',"for xx in np.arange(x0+2,x1-1.2,3.0):\n   place(m,table", "for xx in np.arange(x0+2,x1-1.2,3.0):\n   if xx<r['door_u'] and abs(xx-r['door_u'])<2:continue\n   place(m,table")
# Narrow lavatory: put washstand against side, not over the only doorway.
change('blender/leonidas_ii/interiors.py',"place(m,washstand(),xx,y1-.35,z);panel_mirror(m,xx,y1-.08,z+1.5)","if n==1 and r['door_wall']=='y1':\n     place(m,washstand(),x0+.29,cy+.55,z,math.pi/2);panel_mirror(m,x0+.08,cy+.55,z+1.5,ang=math.pi/2)\n    else:place(m,washstand(),xx,y1-.35,z);panel_mirror(m,xx,y1-.08,z+1.5)")
# Window glazing is a solid physical barrier: collider needs only doorway
# holes, not all the render mesh's intricate pane/panel subdivisions.
change('blender/leonidas_ii/interiors.py',"m.box(pos,size,'White' if above else 'Ivory');proxy(pos,size,tag=r['id']+'_wall')","m.box(pos,size,'White' if above else 'Ivory')")
change('blender/leonidas_ii/interiors.py',"# Fields of individually moulded wood joinery;", "# Native walls keep door openings, but include glazing as solid collision.\n solidholes=[h for h in holes if h[4]!='window']\n pu=sorted(set([u0,u1]+[v for a,b,_,_,_ in solidholes for v in (a,b)]));pz=sorted(set([z0,z1]+[v for _,_,a,b,_ in solidholes for v in (a,b)]))\n for a,b in zip(pu,pu[1:]):\n  for c,d in zip(pz,pz[1:]):\n   if any(h0<(a+b)/2<h1 and h2<(c+d)/2<h3 for h0,h1,h2,h3,_ in solidholes):continue\n   pos=((a+b)/2,fixed,(c+d)/2) if horizontal else (fixed,(a+b)/2,(c+d)/2);size=(b-a,.085,d-c) if horizontal else (.085,b-a,d-c);proxy(pos,size,tag=r['id']+'_wall')\n # Fields of individually moulded wood joinery;")
print('First-review geometry, circulation and camera corrections applied.')
