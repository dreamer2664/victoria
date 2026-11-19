"""One-off physical door/berth/fixture layout corrections. Never rerun."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'blender/leonidas_ii'
staged={}
def load(n):return (ROOT/n).read_text()
def sub(s,a,b):
 assert s.count(a)==1,(a[:120],s.count(a))
 return s.replace(a,b)
def stage(n,s):compile(s,str(ROOT/n),'exec');staged[n]=s
s=load('furnishings.py')
s=sub(s,'def bunk(variant=0):','def bunk(variant=0,ladder_side=0):')
s=sub(s," ladder_y=-l/2-.025\n for x in (-.23,.23):\n  m.cylinder((x,ladder_y,.013),.032,.026,'Iron',10)\n  m.rod((x,ladder_y,.013),(x,ladder_y,1.77),.019,'Iron',8)\n  for z in (.45,1.46):m.rod((x,-l/2+.035,z),(x,ladder_y,z),.016,'Iron',8)\n for z in (.27,.56,.85,1.14,1.43):m.rod((-.23,ladder_y,z),(.23,ladder_y,z),.014,'Iron',7)"," if ladder_side:\n  # Longitudinal dormitory rows need an AISLE-facing long-side ladder,\n  # not an end ladder trapped in the 30-120mm gap to the next berth.\n  assert ladder_side in (-1,1)\n  lx=ladder_side*(w/2+.035);ya,yb=-.75,-.35\n  for yy in (ya,yb):\n   m.cylinder((lx,yy,.013),.032,.026,'Iron',10)\n   m.rod((lx,yy,.013),(lx,yy,1.77),.019,'Iron',8)\n   for zz in (.45,1.46):m.rod((ladder_side*(w/2-.025),yy,zz),(lx,yy,zz),.016,'Iron',8)\n  for zz in (.27,.56,.85,1.14,1.43):m.rod((lx,ya,zz),(lx,yb,zz),.014,'Iron',7)\n  m.tags['AisleFacingLongSideBunkLadder']+=1\n else:\n  ladder_y=-l/2-.025\n  for x in (-.23,.23):\n   m.cylinder((x,ladder_y,.013),.032,.026,'Iron',10)\n   m.rod((x,ladder_y,.013),(x,ladder_y,1.77),.019,'Iron',8)\n   for zz in (.45,1.46):m.rod((x,-l/2+.035,zz),(x,ladder_y,zz),.016,'Iron',8)\n  for zz in (.27,.56,.85,1.14,1.43):m.rod((-.23,ladder_y,zz),(.23,ladder_y,zz),.014,'Iron',7)")
stage('furnishings.py',s)
s=load('interiors.py')
s=sub(s," ang=0 if horizontal else math.pi/2;hx=x-w/2 if horizontal else x;hy=y if horizontal else y-w/2", " ang=0 if horizontal else math.pi/2;hx=x-w/2 if horizontal else x;hy=y if horizontal else y-w/2\n swing=92 if wall in ('y0','x1') else -92;hinge_offset=math.copysign(.035,swing)\n pivot=(hx-math.sin(ang)*hinge_offset,hy+math.cos(ang)*hinge_offset,z)")
s=sub(s," for zz in (.20,1.70):\n  leaf.cylinder((.015,0,zz),.018,.13,'Brass',8)", " for zz in (.20,1.70):\n  # The real pivot is on the opening-side face, not through the middle\n  # of the timber thickness. A bored middle knuckle and attached leaf\n  # plate rotate around two stationary end knuckles/pin.\n  leaf.lathe((0,hinge_offset,zz),[(-.025,.018),(.025,.018),(.025,.0095),(-.025,.0095)],'Brass',12,caps=False,closed=True)\n  leaf.box((.045,hinge_offset*.75,zz),(.075,.012,.040),'Brass',.002)\n  hinge=Mesh()\n  for dz in (-.0475,.0475):\n   hinge.lathe((0,hinge_offset,zz+dz),[(-.0175,.018),(.0175,.018),(.0175,.0095),(-.0175,.0095)],'Brass',12,caps=False,closed=True)\n   hinge.box((-.035,hinge_offset*.75,zz+dz),(.05,.012,.035),'Brass',.002)\n  hinge.cylinder((0,hinge_offset,zz),.0075,.15,'Steel',10)\n  hinge.cylinder((0,hinge_offset,zz+.0728),.012,.016,'Steel',10)\n  m.append(hinge,(hx,hy,z),ang)")
s=sub(s,"origin=(hx,hy,z),mover='door'", "origin=pivot,mover='door'")
s=sub(s,"hinge=(hx,hy,z),yaw=ang,width=w,height=h,angle_deg=92 if wall in ('y0','x1') else -92", "hinge=pivot,yaw=ang,width=w,height=h,angle_deg=swing")
s=sub(s,"positions=[x0+.50,x1-.50] if w>2.5 and r.get('berths',2)>2 else [x0+.55]", "positions=[x0+.44,x1-.44] if w>2.5 and r.get('berths',2)>2 else [x0+.44]")
s=sub(s,"x,cy+.28,z+1.0),(.76,1.96,2)","x,cy+.28,z+1.12),(.78,2.04,2.24)")
s=sub(s,"place(m,bed('first',scheme['cloth']),x0+.54,cy,z);proxy((x0+.54,cy", "place(m,bed('first',scheme['cloth']),x0+.49,cy,z);proxy((x0+.49,cy")
s=sub(s,"x1-.39,y0+.34,z,math.pi", "x1-.39,y0+.48,z,math.pi")
helper='''def clear_side_door_row(r,centres,half_length,gap=.03):
 # Preserve the ACTUAL number of existing units. Pack complete finite
 # extents on the two sides of the full door approach, never by checking
 # only the furniture centre or deleting a colliding berth.
 assert r['door_wall'][0]=='y'
 n=len(centres);u=r['door_u'];half_door=r['door_width']/2
 left=(r['x0']+.07,u-half_door-.25);right=(u+half_door+.25,r['x1']-.07)
 def fit(interval,count):
  lo,hi=interval
  if not count:return []
  if hi-lo<count*2*half_length+(count-1)*gap-1e-7:return None
  return [(lo+hi)/2] if count==1 else [float(x) for x in np.linspace(lo+half_length,hi-half_length,count)]
 choices=[]
 for nl in range(n+1):
  a=fit(left,nl);b=fit(right,n-nl)
  if a is not None and b is not None:choices.append((abs(nl-sum(x<u for x in centres)),a+b))
 assert choices,(r['id'],'Cannot preserve all units with full door clearance',n,half_length)
 result=min(choices,key=lambda q:q[0])[1]
 assert len(result)==n
 return result


'''
s=sub(s,'def fit_dorm(m,r):',helper+'def fit_dorm(m,r):')
s=sub(s,"  for i,x in enumerate(np.arange(x0+1.15,x1-.9,2.12)):\n   if abs(x-r['door_u'])<1.1 and r['door_wall'][0]=='y':continue\n   for yy in ys:\n    place(m,bunk((i+(1 if yy>cy else 0))%3),float(x),yy,z,math.pi/2);proxy((float(x),yy,z+1.1),(.76,1.96,2.2),math.pi/2,tag=r['id']+'_bunk');actual+=2", "  centres=[float(x) for x in np.arange(x0+1.15,x1-.9,2.12) if not (r['door_wall'][0]=='y' and abs(x-r['door_u'])<1.1)]\n  if r['door_wall'][0]=='y':centres=clear_side_door_row(r,centres,.983)\n  for i,x in enumerate(centres):\n   for yy in ys:\n    side=-1 if yy>cy else 1\n    place(m,bunk((i+(1 if yy>cy else 0))%3,ladder_side=side),float(x),yy,z,math.pi/2);proxy((float(x),yy,z+1.12),(.86,1.97,2.24),math.pi/2,tag=r['id']+'_bunk');actual+=2")
s=sub(s,"if xx<r['door_u'] and abs(xx-r['door_u'])<2:continue", "if r['door_wall'][0]=='y' and abs(xx-r['door_u'])<2:continue")
s=sub(s,"   m.box((x0+3.1,y0+.09,z+1.80),(4.8,.06,.08),'Oak',.008)\n   for xx in np.arange(x0+1.1,x0+5.2,.55):m.tube([(float(xx),y0+.12,z+1.80),(float(xx),y0+.25,z+1.75),(float(xx),y0+.29,z+1.82)],.012,'Brass',8)", "   for a,b in ((x0+.7,r['door_u']-r['door_width']/2-.13),(r['door_u']+r['door_width']/2+.13,x0+5.5)):\n    if b>a:m.box(((a+b)/2,y0+.09,z+1.80),(b-a,.06,.08),'Oak',.008)\n   for xx in np.arange(x0+1.1,x0+5.2,.55):\n    if abs(xx-r['door_u'])<r['door_width']/2+.18:continue\n    m.tube([(float(xx),y0+.12,z+1.80),(float(xx),y0+.25,z+1.75),(float(xx),y0+.29,z+1.82)],.012,'Brass',8)")
s=sub(s,"    for stock_i,xx in enumerate(np.arange(x0+1,x1-.6,1.7)):", "    stocks=[float(x) for x in np.arange(x0+1,x1-.6,1.7)]\n    if kind=='store' and y1-y0<2.0 and r['door_wall'][0]=='y':stocks=clear_side_door_row(r,stocks,.70,.05)\n    for stock_i,xx in enumerate(stocks):")
s=sub(s,"    else:place(m,washstand(),xx,y1-.35,z);panel_mirror(m,xx,y1-.08,z+1.5)", "    else:\n     wx=[x0+.40,r['door_u']-r['door_width']/2-.70,r['door_u']+r['door_width']/2+.70,x1-.40][i] if r['id']=='P_Wash' else xx\n     place(m,washstand(),wx,y1-.35,z);panel_mirror(m,wx,y1-.08,z+1.5)")
s=sub(s,"for xx in (x0+1.1,x1-1.1):place(m,bed('hospital','ClothBlue')", "for xx in (x0+1.75,x1-1.1):place(m,bed('hospital','ClothBlue')")
s=sub(s,"if r['id']=='P_Stair' else [(xx,yy)","if y1-y0<=8 else [(xx,yy)")
stage('interiors.py',s)
s=load('public_rooms.py');s=sub(s,"xs=[x0+2.20,x0+6.60,x1-7.00,x1-2.60]", "xs=[x0+2.90,x0+6.60,x1-7.00,x1-2.60]")
stage('public_rooms.py',s)
s=load('audit_fittings.py');s=sub(s,"    for variant in range(3):yield 'bunk_'+str(variant),F.bunk(variant)", "    for variant in range(3):yield 'bunk_'+str(variant),F.bunk(variant)\n    for side in (-1,1):yield 'bunk_aisle_ladder_'+str(side),F.bunk(0,ladder_side=side)")
stage('audit_fittings.py',s)
for n,s in staged.items():(ROOT/n).write_text(s)
print('APPLIED staged correction 8:',', '.join(staged))
