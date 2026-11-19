from pathlib import Path
R=Path('/home/user/victoria/blender/leonidas_ii')
def load(n):return (R/n).read_text()
def save(n,s):compile(s,str(R/n),'exec');(R/n).write_text(s)
def sub(s,a,b,n=1):
 assert s.count(a)==n,(a[:100],s.count(a),n)
 return s.replace(a,b)
def fn(s,name,next_name,new):
 start=s.index('@lru_cache(None)\ndef '+name);end=s.index('@lru_cache(None)\ndef '+next_name,start)
 return s[:start]+new.rstrip()+'\n\n\n'+s[end:]
a=load('service_fittings.py');a=sub(a,'from meshkit import Mesh,bolts,handwheel','from meshkit import Mesh,bolts,handwheel,drop_pull')
a=sub(a,"m.box((0,0,1.048),(2.40,1.28,.009)","m.box((0,0,1.047),(2.40,1.28,.009)")
a=sub(a,"m.box((-.18,y,1.065)","m.box((-.18,y,1.0603)")
a=sub(a,"m.rod((x,-.10,1.075),(x+.05,.015,1.075)","m.rod((x,-.10,1.0703),(x+.05,.015,1.0703)")
a=sub(a," m.ring((.60,.20,1.073)"," first=len(m.v)\n m.ring((.60,.20,1.073)")
a=sub(a," return m\n\n\n@lru_cache(None)\ndef mail_cubby", " m.rest(first,1.0515)\n return m\n\n\n@lru_cache(None)\ndef mail_cubby")
a=fn(a,'mail_cubby','drinks_rack', '''@lru_cache(None)
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
 return m''')
a=sub(a,"m.box((0,0,.44),(1.42,.54,.84)","m.box((0,0,.43),(1.42,.54,.86)")
a=sub(a,"m.box((0,-.015,.90),(1.49,.65,.065)","m.box((0,-.015,.8925),(1.49,.65,.065)")
a=sub(a,"m.ring((x+.18,-.331,.49),.024,.006,'Brass',12,5,(1,0,0))","drop_pull(m,(x+.18,-.341,.49),.024)")
a=sub(a,"bottle(m,-.54+i*.215,.025,z+.025", "bottle(m,-.54+i*.215,.025,z+.0173")
a=sub(a,"m.lathe((x,-.24,.94)","m.lathe((x,-.28,.9248)")
a=sub(a,"   for zz in (z-.29,z+.29):m.box((x-.29,-.42,zz),(.14,.035,.055),'Iron',.008)","   for zz in (z-.29,z+.29):\n    hx=x+(-.29 if x<0 else .29)\n    m.box((hx,-.365,zz),(.14,.12,.055),'Iron',.008)\n    m.cylinder((hx,-.419,zz),.016,.075,'Brass',10)")
a=sub(a,"  m.tube([(-.13,y,.59)","  for xx in (-.13,.13):m.cylinder((xx,side*.485,.59),.018,.070,'Iron',10,(0,1,0))\n  m.tube([(-.13,y,.59)")
a=sub(a,"m.ring((x,-.215,.33),.023,.006,'Brass',12,5,(1,0,0))","drop_pull(m,(x,-.233,.33),.023)")
a=sub(a," for row,z in enumerate((.59,1.00,1.41)):"," for row,shelf in enumerate((.57,.98,1.39)):\n  z=shelf+.0173")
a=sub(a,"   if row==1 and i<2:m.cylinder((x,-.015,z+.085),.065,.17,'Linen',14,(0,1,0))\n   else:bottle(m,x,.025,z+.02,'BookBlue' if i%2 else 'BookRed',.27)","   if row==1 and i<2:\n    first=len(m.v);m.cylinder((x,-.015,z+.065),.065,.17,'Linen',14,(0,1,0));m.rest(first,shelf+.0175)\n   else:bottle(m,x,.025,z,'BookBlue' if i%2 else 'BookRed',.27)")
a=sub(a," handwheel(m,(.06,-.43,.61)"," m.cylinder((.06,-.414,.61),.026,.060,'Steel',12,(0,1,0))\n handwheel(m,(.06,-.43,.61)")
a=sub(a,"m.cylinder((-.15,-.425,.75),.045,.028", "m.cylinder((-.15,-.425,.75),.045,.060")
a=sub(a,"m.rod((x,y,.10),(x,y,.80),.019,'Iron',8);m.ring((x,y,.065),.045,.012,'Iron',14,6,(1,0,0))","m.rod((x,y,.10),(x,y,.80),.019,'Iron',8)\n   m.cylinder((x,y,.057),.047,.026,'Iron',16,(1,0,0));m.ring((x,y,.057),.045,.012,'Iron',16,8,(1,0,0))")
a=sub(a," for y in (-.23,.23):m.rod((-.35,y,.86),(.35,y,.86),.012,'Brass',8)"," for y in (-.23,.23):\n  for x in (-.35,.35):m.rod((x,y,.80),(x,y,.86),.012,'Brass',8)\n  m.rod((-.35,y,.86),(.35,y,.86),.012,'Brass',8)")
a=sub(a,"m.lathe((-.15,0,.83)","m.lathe((-.15,0,.8173)")
a=sub(a," for x in (.04,.12,.20):m.rod((x,-.12,.83),(x,.10,.83),.006,'Steel',7)"," for x in (.04,.12,.20):\n  first=len(m.v);m.rod((x,-.12,.83),(x,.10,.83),.006,'Steel',7);m.rest(first,.8175)")
a=sub(a,"m.lathe((x,0,z+.025)","m.lathe((x,0,z+.0198)",2)
a=sub(a,"m.cylinder((x,0,z+.42)","m.cylinder((x,0,z+.4171)")
a=sub(a,"m.ring((x,0,z+.39)","m.ring((x,0,z+.3848)")
a=sub(a," for x in (-.26,.26):\n  m.rod((x,-.06,.02)"," for x in (-.26,.26):\n  for yy in (-.06,.12):m.cylinder((x,yy,.010),.025,.020,'Teak',8)\n  m.rod((x,-.06,.02)")
save('service_fittings.py',a)
a=load('furnishings.py');a=sub(a,'def desk(width=1.25):','def desk(width=1.25,bare=False):')
start=a.index(' m.box((.04,-.03,DESK_PAD_TOP');end=a.index(" m.tags['WritingDesk']",start)
a=a[:start]+' if not bare:\n'+''.join(' '+line+'\n' for line in a[start:end].splitlines())+a[end:];save('furnishings.py',a)
a=load('working_detail.py');a=sub(a,'from meshkit import Mesh,bolts','from meshkit import Mesh,bolts\nfrom furnishings import WASHSTAND_TOP,DESK_PAD_TOP')
a=sub(a,"  m.rod((x-.14,-.68,.91),(x+.14,-.68,.91),.018,'Brass',8)","  for dx in (-.14,.14):m.rod((x+dx,-.627,.91),(x+dx,-.68,.91),.012,'Brass',8)\n  m.rod((x-.14,-.68,.91),(x+.14,-.68,.91),.018,'Brass',8)")
a=sub(a,"  for dz in (-.14,.14):m.cylinder((x-.41,-.66,.87+dz),.018,.10,'Steel',8)","  for dz in (-.14,.14):\n   m.box((x-.41,-.648,.87+dz),(.080,.055,.12),'Iron',.006)\n   m.cylinder((x-.41,-.66,.87+dz),.018,.10,'Steel',8)")
a=a.replace("z-.005)","z-.0047)")
a=sub(a,"   for i in range(3):\n    m.cushion((xx-.62+i*.55,yy,z+.985),(.40,.22,.14),'Bread')\n    for q in range(3):m.rod((xx-.75+i*.55+q*.10,yy-.06,z+1.041),(xx-.72+i*.55+q*.10,yy+.06,z+1.05),.004,'Ivory',5)","   for i,dx in enumerate((-.70,0,.70)):\n    surface=.935 if i==1 else .90\n    m.cushion((xx+dx,yy,z+surface+.0698),(.40,.22,.14),'Bread')\n    for q in range(3):m.rod((xx+dx-.12+q*.10,yy-.06,z+surface+.139),(xx+dx-.09+q*.10,yy+.06,z+surface+.139),.004,'Ivory',5)")
a=sub(a,"m.box((bx,by,z+.39),(.70,.65,.73)","m.box((bx,by,z+.365),(.70,.65,.73)")
a=sub(a,"m.box((bx,by,z+.77),(.74,.69,.045)","m.box((bx,by,z+.7525),(.74,.69,.045)")
a=sub(a,"m.lathe((bx,by,z+.805)","m.lathe((bx,by,z+.7748)")
a=sub(a,"m.rod((bx,by,z+.87),(bx+.22,by,z+.87)","m.rod((bx,by,z+.84),(bx+.22,by,z+.84)")
a=sub(a,"m.box((x0+.14,cy,z+.24),(.055,.34,.44)","m.box((x0+.14,cy,z+.22),(.055,.34,.44)")
a=sub(a,"m.lathe((xx,yy,z+.903)","m.lathe((xx,yy,z+.9348)")
a=sub(a,"m.lathe((xx-.12,yy,z+.92+i*.018)","m.lathe((xx-.12,yy,z+.9178+i*.0178)")
a=sub(a,"m.box((xx+.22,yy,z+.947)","m.box((xx+.22,yy,z+.9478)")
a=sub(a,"m.lathe((xx+.23,yy+.09,z+.98)","m.lathe((xx+.23,yy+.09,z+.9776)")
start=a.index('  # Soap dishes really sit');end=a.index('  if x1-x0>2:',start)
a=a[:start]+'''  # Use the SAME washstand stations and rotations as fit_service. The
  # former general x0+1.1/y1-.29 rule left soap between multiple basins.
  if k=='bath':stations=[(cx,y1-.30)]
  elif k=='barber':stations=[(x0+1.10,y1-.40),(x1-1.10,y1-.40)]
  else:
   n=max(1,int((x1-x0)/1.3))
   stations=[] if n==1 and r['door_wall']=='y1' else [(x0+(i+.5)*(x1-x0)/n,y1-.35) for i in range(n)]
  for wx,wy in stations:
   sx,sy=wx-.245,wy-.17
   m.lathe((sx,sy,z+WASHSTAND_TOP-.0002),[(0,.035),(.01,.055),(.022,.060),(.026,.05)],'Porcelain',14)
   m.box((sx,sy,z+WASHSTAND_TOP+.0416),(.065,.04,.032),'Ivory',.006)
'''+a[end:]
a=sub(a,"   m.ring((xx,cy+1.35,z+2.04)","   m.box((xx,cy+1.35+(i%2)*.0125,z+2.012),(.033,.052,.045),'Linen',.004)\n   m.ring((xx,cy+1.35,z+2.04)")
a=sub(a,"z+.812))","z+DESK_PAD_TOP+.0076))")
a=sub(a,"  for dx in (-.043,.043):", "  first=len(m.v)\n  for dx in (-.043,.043):")
a=sub(a,"  m.rod((xx-.043,yy,z+.855),(xx+.043,yy,z+.855),.008,'Brass',7)","  m.rod((xx-.043,yy,z+.855),(xx+.043,yy,z+.855),.008,'Brass',7)\n  m.rest(first,z+DESK_PAD_TOP+.0078)")
save('working_detail.py',a)
a=load('interiors.py')
a=sub(a,"     m.ring((xx,yy,zz-.008)","     m.box((xx,(fy+yy)/2,zz-.025),(.030,abs(fy-yy)+.026,.026),curtain,.003)\n     m.ring((xx,yy,zz-.008)")
a=sub(a,"   m.box((float(xx),y1-.6,z+.918)","   m.box((float(xx),y1-.6,z+.9173)")
a=sub(a,"m.lathe((float(xx)+.5,y1-.60,z+.936)","m.lathe((float(xx)+.5,y1-.60,z+.8998)")
a=sub(a,"place(m,staved_barrel() if i%3==1 else cargo_crate(),float(xx),yy,z+.015", "place(m,staved_barrel() if i%3==1 else cargo_crate(),float(xx),yy,z+(0 if i%3==1 else .0125)")
a=sub(a,"xx=x1-.50;m.box((xx,cy,z+.08),(.82,.98,.12)","xx=x1-.50;m.box((xx,cy,z+.06),(.82,.98,.12)")
a=sub(a,"place(m,desk(1.2),x0+1.0,cy,z,math.pi/2)","place(m,desk(1.2,True),x0+1.0,cy,z,math.pi/2)")
a=sub(a,"z+.85),(.28,.20,.075)","z+DESK_PAD_TOP+.0373),(.28,.20,.075)")
a=sub(a,"m.lathe((xx-.20,y1-.40,z+.85)","m.lathe((xx+.255,y1-.22,z+WASHSTAND_TOP-.0002)")
a=sub(a,"m.cylinder((xx-.20,y1-.40,z+1.015)","m.cylinder((xx+.255,y1-.22,z+1.015)")
a=sub(a,"m.box((xx-.20,y1-.64,z+.86)","m.box((xx-.10,y1-.61,z+WASHSTAND_TOP+.0073)")
a=sub(a,"   m.box((xx+.22,y1-.66,z+.46)","   m.tube([(xx+.22,y1-.60,z+.74),(xx+.22,y1-.655,z+.74),(xx+.22,y1-.655,z+.69)],.008,'Brass',8)\n   m.box((xx+.22,y1-.66,z+.46)")
a=sub(a,"place(m,desk(1.6),float(xx),y1-.65,z)","place(m,desk(1.6,True),float(xx),y1-.65,z)")
a=sub(a,"m.box((float(xx),y1-.65,z+.82)","m.box((float(xx),y1-.65,z+DESK_PAD_TOP+.0038)")
a=sub(a,"      yy=yy0+(i+.5)*step;m.cylinder", "      first=len(m.v);yy=yy0+(i+.5)*step;m.cylinder")
a=sub(a,"      m.ring((x1-.38,yy,z+zz+.13),.095,.008,'Rope',12,5,(1,0,0))", "      m.ring((x1-.38,yy,z+zz+.13),.095,.008,'Rope',12,5,(1,0,0))\n      m.rest(first,z+zz+.0175)")
a=sub(a,"     m.rod((float(xx)+dx,yy-.11,z+.02)","     for dy in (-.11,.11):m.cylinder((float(xx)+dx,yy+dy,z+.010),.035,.020,'Iron',8)\n     m.rod((float(xx)+dx,yy-.11,z+.02)")
a=sub(a,"   for dy in (-.09,.09):m.rod((xx+dx,bench_y+dy,z+.02),(xx+dx,bench_y,z+.43),.025,'Iron',7)","   for dy in (-.09,.09):\n    m.cylinder((xx+dx,bench_y+dy,z+.010),.028,.020,'Iron',8)\n    m.rod((xx+dx,bench_y+dy,z+.02),(xx+dx,bench_y,z+.43),.025,'Iron',7)")
save('interiors.py',a)
a=load('weather_detail.py');a=sub(a,"(xx,yy,14.414)","(xx,yy,14.409)");save('weather_detail.py',a)
print('Applied service-room finite bearings, wrapped parcel ties, drawer hinges, tool supports, curtain tabs and small-content placements.')
