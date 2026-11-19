from pathlib import Path
R=Path('/home/user/victoria/blender/leonidas_ii')
def load(n):return (R/n).read_text()
def save(n,s):compile(s,str(R/n),'exec');(R/n).write_text(s)
def sub(s,a,b,n=1):
 assert s.count(a)==n,(a[:100],s.count(a),n)
 return s.replace(a,b)

a=load('visual_design.py');a=sub(a,'CABIN_TYPES=(','''# The actual 25mm finish is centred at deck+35mm. Furniture, accessories
# and finish meshes share this bearing datum; no nominal 55mm spacer.
FLOOR_FINISH_TOP=.0475

def finished_floor(r):return r['z']+FLOOR_FINISH_TOP

CABIN_TYPES=(''');save('visual_design.py',a)
a=load('meshkit.py');a=sub(a,' def emit(self,name,col,kind=', ''' def rest(self,first_vertex,surface_z,inset=.0002):
  """Seat this explicitly selected new assembly by its ACTUAL finite bottom.
  Call only for a known horizontal bearing (e.g. a lying rod or a stack),
  never as a substitute for checking its internal joints or every foot.
  """
  assert 0<=first_vertex<len(self.v)
  dz=surface_z-inset-min(p[2] for p in self.v[first_vertex:])
  self.v[first_vertex:]=[(x,y,z+dz) for x,y,z in self.v[first_vertex:]]
  return self
 def emit(self,name,col,kind=''')
a=sub(a," for zz in (z-.13,z-.32):m.ring", " # Four radial cage hangers actually enter the socket; the old basket\n # was a closed but completely detached ring/rod component.\n for a in (0,math.pi/2,math.pi,3*math.pi/2):\n  m.rod((x+.030*math.cos(a),y+.030*math.sin(a),z-.105),(x+.080*math.cos(a),y+.080*math.sin(a),z-.13),.008,'Iron',8)\n for zz in (z-.13,z-.32):m.ring")
a += '''\n\ndef drop_pull(m,c,r=.025,t='Brass'):
 # Local cabinet front faces -Y. Ring lies IN the front plane; a finite
 # top eye enters the door instead of relying on an edge-on torus to touch.
 x,y,z=c
 m.cylinder((x,y+.013,z+r),.012,.040,t,10,(0,1,0))
 m.ring((x,y,z),r,.006,t,12,6,(0,1,0))
''';save('meshkit.py',a)
a=load('furnishings.py');a=sub(a,'from meshkit import Mesh,handwheel,bolts','''from meshkit import Mesh,handwheel,bolts,drop_pull
# Physical top surfaces, used by their own contents and room placements.
TABLE_WOOD_TOP=.7825
TABLE_CLOTH_TOP=.7945
DESK_WOOD_TOP=.8025
DESK_PAD_TOP=.8145
WASHSTAND_TOP=.8425''')
a=sub(a,"(.38,.095),(.41,.20)","(.38,.095),(.423,.20)")
a=sub(a,"m.tube([(x,-.15,.48),(x,-.17,.68),(x,.19,.73)],.023,wood,8)","m.tube([(x*.84,-.12,.47),(x,-.17,.68),(x*.80,.19,.73)],.023,wood,8)")
a=sub(a,"m.cylinder((x,.167,z)","m.cylinder((x,.183,z)")
a=sub(a,"m.cylinder((x,.163,.74)","m.cylinder((x,.173,.74)")
a=sub(a,"(.52,.08),(.57,.14)","(.52,.08),(.605,.10),(.625,.14)")
a=sub(a,"m.box((x,0,.055),(.38,w*.85,.07)","m.box((x,0,.035),(.38,w*.85,.07)")
a=sub(a,"m.box((0,0,.791),(l+.025,w+.025,.012)","m.box((0,0,TABLE_WOOD_TOP+.006),(l+.025,w+.025,.012)")
a=sub(a,'def service_setting():','def service_setting(cup_drop=0.):')
a=sub(a," m.lathe((.21,.14,.015)"," cup_first=len(m.v)\n m.lathe((.21,.14,.015)")
a=sub(a," m.box((-.20,-.015,.006)"," # Second-class cups stand on bare wood OUTSIDE the narrow runner;\n # plates/cutlery are on the runner. Do not lower the whole setting.\n if cup_drop:m.v[cup_first:]=[(x,y,z-cup_drop) for x,y,z in m.v[cup_first:]]\n m.box((-.20,-.015,.006)")
a=sub(a," for x in (-w/2,w/2):m.rod((x,-l/2,.42),(x,l/2,.42),.024,'Iron',6)"," for x in (-w/2,w/2):m.rod((x,-l/2,.42),(x,l/2,.42),.024,'Iron',6)\n # Real cross slats bridge the rails under the mattress's inset lower crown.\n for yy in (-.74,-.50,-.25,0,.25,.50,.74):m.box((0,yy,.422),(w,.065,.030),'Oak',.004)")
a=sub(a,"m.box((0,y,.309),(.57,.025,.015)","m.box((0,y,.3045),(.57,.025,.015)")
a=sub(a," m.rod((-.08,-.363,.20),(.08,-.363,.20),.010,'Iron',7)"," for xx in (-.08,.08):m.rod((xx,-.345,.20),(xx,-.365,.20),.010,'Iron',8)\n m.rod((-.08,-.363,.20),(.08,-.363,.20),.010,'Iron',7)")
a=sub(a,"m.ring((w*.27,-.325,h*.49),.026,.007,'Brass',10,4,(1,0,0))","drop_pull(m,(w*.27,-.322,h*.49),.026)")
a=sub(a,"m.box((0,-.244,.73),(.46,.025,.10),'Mahogany',.01);m.ring((0,-.27,.73),.025,.006,'Brass',10,4,(1,0,0))","m.box((0,-.233,.73),(.46,.025,.10),'Mahogany',.01);drop_pull(m,(0,-.268,.73))")
a=sub(a,"m.lathe((-.06,0,.844)","m.lathe((-.06,0,WASHSTAND_TOP-.0002)")
a=sub(a,"m.lathe((.215,.07,.844)","m.lathe((.215,.07,WASHSTAND_TOP-.0002)")
a=sub(a,"(.65,.035),(.72,.043)","(.65,.035),(.752,.043)")
a=sub(a,"m.ring((x,-.38,.65),.023,.006,'Brass',10,4,(1,0,0))","drop_pull(m,(x,-.379,.65),.023)")
a=sub(a,"m.box((0,-.02,.808),(w*.65,.41,.012)","m.box((0,-.02,DESK_WOOD_TOP+.006),(w*.65,.41,.012)")
a=sub(a,"m.box((.04,-.03,.82),(.28,.32,.004)","m.box((.04,-.03,DESK_PAD_TOP+.0018),(.28,.32,.004)")
a=sub(a,"m.lathe((w*.35,.15,.81)","m.lathe((w*.37,.15,DESK_WOOD_TOP-.0002)")
a=sub(a,"m.rod((w*.35,.15,.88),(w*.36,.13,1.08)","m.rod((w*.37,.15,.88),(w*.38,.13,1.08)")
a=sub(a,"m.box((xx,-.157,z+.025+zz)","m.box((xx,-.1535,z+.025+zz)")
a=sub(a,"m.ring((0,.36,z),.033,.008", "m.ring((0,.36,z),.031,.008")
a=sub(a," m.rod((.24,.26,1.65)"," m.rod((.18,.26,1.65),(.27,.26,1.65),.009,'Brass',8)\n m.rod((.24,.26,1.65)")
a=sub(a," for y in (-.13,.13):m.cylinder((.67,y,.018),.044,.035,'Brass',12)"," for y in (-.13,.13):\n  m.cylinder((.67,y,.018),.044,.036,'Brass',12)\n  m.rod((.67,y,.77),(.67,y,.83),.012,'Brass',10)")
a=sub(a,"m.box((0,0,.14),(2.9,1.24,.20)","m.box((0,0,.12),(2.9,1.24,.24)")
a=sub(a,"m.box((x,-.61,.70),(.71,.09,.55)","m.box((x,-.585,.70),(.71,.14,.55)")
a=sub(a,"m.lathe((x,0,1.17)","m.lathe((x,0,1.1648)")
a=sub(a,"m.lathe((x,0,1.20)","m.lathe((x,0,1.1946)")
a=sub(a,"m.lathe((xx,0,z+.03+k*.018)","m.lathe((xx,0,z+.0223+k*.0178)")
a=sub(a,"    m.box((xx,0,z+.17),(.27,.37,.23+((j+i+variant)%3)*.025),'Canvas' if (i+j+variant)%2 else 'Linen',.025)\n    m.box((xx,-.195,z+.17),(.11,.008,.09),'Paper')","    hh=.23+((j+i+variant)%3)*.025;centre=z+.0223+hh/2\n    m.box((xx,0,centre),(.27,.37,hh),'Canvas' if (i+j+variant)%2 else 'Linen',.025)\n    m.box((xx,-.1855,centre),(.11,.008,.09),'Paper')")
save('furnishings.py',a)
# Room bearing datums only. Surface-specific worktop placements are below.
for name in ('interiors.py','public_rooms.py','period_detail.py','working_detail.py'):
 a=load(name)
 a=a.replace('from visual_design import design,ceiling_anchor','from visual_design import design,ceiling_anchor,finished_floor').replace('from visual_design import design,ceiling_holes','from visual_design import finished_floor,design,ceiling_holes')
 if name in ('public_rooms.py','working_detail.py'):a=sub(a,'from visual_design import design','from visual_design import design,finished_floor')
 assert "r['z']+.055" in a,name
 a=a.replace("r['z']+.055","finished_floor(r)");save(name,a)
print('Applied first verified contact corrections: finite subparts and shared finished-floor datum.')
