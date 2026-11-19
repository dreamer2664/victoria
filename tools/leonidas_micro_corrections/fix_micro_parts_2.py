from pathlib import Path
R=Path('/home/user/victoria/blender/leonidas_ii')
def load(n):return (R/n).read_text()
def save(n,s):compile(s,str(R/n),'exec');(R/n).write_text(s)
def sub(s,a,b,n=1):
 assert s.count(a)==n,(a[:100],s.count(a),n)
 return s.replace(a,b)
def fn(s,name,next_name,new):
 start=s.index('@lru_cache(None)\ndef '+name) if '@lru_cache(None)\ndef '+name in s else s.index('def '+name)
 end=s.index('\n\n',s.index('\ndef '+next_name,start)-len('@lru_cache(None)\n')-2) if False else s.index('def '+next_name,start)
 # Preserve any decorator belonging to the next function.
 if s[:end].endswith('@lru_cache(None)\n'):end-=len('@lru_cache(None)\n')
 return s[:start]+new.rstrip()+'\n\n\n'+s[end:]
a=load('period_detail.py')
a=sub(a," for a in (0,math.tau/3,2*math.tau/3):m.tube([(0,0,.22),(.22*math.cos(a),.22*math.sin(a),.09),(.40*math.cos(a),.40*math.sin(a),.045)],.035,wood,8)"," for a in (0,math.tau/3,2*math.tau/3):\n  m.tube([(0,0,.22),(.22*math.cos(a),.22*math.sin(a),.09),(.40*math.cos(a),.40*math.sin(a),.045)],.035,wood,8)\n  m.cylinder((.40*math.cos(a),.40*math.sin(a),.012),.040,.024,wood,10)")
a=sub(a,"  for y in (-.20,.20):m.rod((x*1.15,y*1.15,.02),(x,y,.44),.024,wood,8)","  for y in (-.20,.20):\n   m.cylinder((x*1.15,y*1.15,.013),.027,.026,wood,8)\n   m.rod((x*1.15,y*1.15,.02),(x,y,.44),.024,wood,8)")
a=sub(a,"   # Sole penetrates the 5–8mm finish offset used by cabin/weather floors;\n   # the leg's former 15mm start left a visible unsupported air gap.\n   m.cylinder((x,y,.008),.044,.030,'Iron',12)","   # Flat soles sit on the common finished surface, not a nominal spacer.\n   m.cylinder((x,y,.015),.044,.030,'Iron',12)")
a=sub(a,"  if back:m.tube([(x,.16,.40)","  # Each of the three independent slats bears on an actual cross bearer.\n  m.box((x,0,.427),(.080,.47,.045),'Iron',.006)\n  if back:m.tube([(x,.16,.40)")
a=sub(a," m=Mesh();h=0\n for i in range(2+variant%2):"," m=Mesh();h=.003\n for i in range(2+variant%2):")
a=sub(a,"h+=th+.007","h+=th+.0058")
a=sub(a,"m.box((x,y,z+.004),(.23,.31,.006)","m.box((x,y,z+.0028),(.23,.31,.006)")
a=sub(a,"y-.09+i*.036,z+.008)","y-.09+i*.036,z+.006)")
a=sub(a,"m.lathe((x-.10,y,z+.03)","m.lathe((x-.10,y,z+.0278)")
a=sub(a,"m.lathe((x-.10,y,z+.25)","m.lathe((x-.10,y,z+.2478)")
a=sub(a,"m.lathe((x+.16,yy,z+.032)","m.lathe((x+.16,yy,z+.0278)")
a=sub(a,"m.ring((x+.213,yy,z+.105)","m.ring((x+.213,yy,z+.1008)")
a=fn(a,'billiard_table','game_board', '''@lru_cache(None)
def billiard_table():
 # A three-ball carom table is period-appropriate and has NO pockets.
 # The old six black discs were raised solids, not real pocket openings.
 m=Mesh();l,w=3.0,1.62
 for x in (-1.12,1.12):
  for y in (-.55,.55):m.lathe((x,y,0),[(0,.08),(.09,.10),(.20,.075),(.31,.11),(.42,.095),(.68,.105)],'Mahogany',12)
 m.box((0,0,.72),(l,w,.22),'Mahogany',.035);m.box((0,0,.846),(l-.25,w-.25,.035),'BilliardBaize',.01)
 for y in (-w/2+.07,w/2-.07):m.box((0,y,.875),(l,.16,.10),'Walnut',.025)
 for x in (-l/2+.07,l/2-.07):m.box((x,0,.875),(.16,w,.10),'Walnut',.025)
 for x,y,t in ((-.65,.15,'Porcelain'),(.37,-.21,'Red'),(.63,.33,'Ivory')):
  m.lathe((x,y,.8633),[(0,.004),(.01,.023),(.027,.028),(.05,.015),(.055,.002)],t,16)
 v=len(m.v);m.rod((-.95,-.35,.90),(.75,.22,.90),.009,'Oak',8);m.rest(v,.8635)
 m.tags['BilliardTable']+=1;m.tags['PocketlessThreeBallCaromTable']+=1;return m''')
a=sub(a,"m.lathe((xx,yy,z+.038)","m.lathe((xx,yy,z+.0343)")
a=sub(a,"m.box((x-.11+j*.075,y,z+.046)","m.box((x-.11+j*.075,y,z+.0443)")
a=sub(a,"m.cylinder((x-.11+j*.075,y-.026+q*.015,z+.058)","m.cylinder((x-.11+j*.075,y-.026+q*.015,z+.0553)")
a=fn(a,'grand_piano','piano_stool', '''@lru_cache(None)
def grand_piano():
 """85-note grand; every carrier, string group, pedal and caster is finite."""
 m=Mesh();outline=[(-.88,-.55),(.88,-.55),(.89,.10),(.86,.52),(.70,1.05),(.45,1.44),(.12,1.64),(-.21,1.67),(-.54,1.48),(-.77,1.10),(-.88,.58)]
 n=len(outline);vv=[(x,y,z) for z in (.73,.97) for x,y in outline]
 vv += [(x*.94,y*.95,z) for z in (.73,.97) for x,y in outline];ff=[]
 for i in range(n):
  j=(i+1)%n;ff.extend([(i,j,j+n,i+n),(2*n+i,3*n+i,3*n+j,2*n+j),(n+i,n+j,3*n+j,3*n+i),(i,2*n+i,2*n+j,j)])
 m.add(vv,ff,'Walnut')
 # Full outline soundboard reaches the tail leg. Former short box ended
 # 440mm before that leg, and left the harp hovering above the soundboard.
 ff=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 m.add([(x,y,z) for z in (.71,.755) for x,y in outline],ff,'Walnut')
 m.box((0,.38,.777),(1.48,1.52,.050),'Brass',.014)
 for yy in (-.26,1.04):m.box((0,yy,.819),(1.48,.055,.036),'Walnut',.006)
 for i in range(32):m.rod((-.69+i*.042,-.26,.83),(-.53+i*.029,1.04,.83),.0018,'Copper',6)
 # Lid terminates behind the music rack. It no longer slices through the
 # sheet music. Its prop starts on the actual harp, not in empty air.
 lidoutline=[(x,max(-.25,y)) for x,y in outline]
 lid=Mesh();lid.add([(x,y,z) for z in (0,.026) for x,y in lidoutline],ff,'Walnut')
 lid.v=[(x,y,1.00+z+.30*(x+.88)/1.76) for x,y,z in lid.v];m.append(lid)
 m.rod((.64,.65,.800),(.64,.65,1.269),.016,'Walnut',8)
 for y in (-.17,.78):m.cylinder((-.875,y,.987),.018,.16,'Brass',12,(0,1,0))
 m.box((0,-.41,.93),(1.69,.28,.050),'Walnut',.008)
 m.box((0,-.65,.77),(1.75,.33,.11),'Walnut',.018)
 white=1.65/50
 for i in range(50):m.box((-.825+(i+.5)*white,-.665,.837),(white-.0015,.30,.019),'Porcelain',.002)
 for i in range(49):
  if i%7 not in (2,6):m.box((-.825+(i+1)*white,-.59,.862),(.019,.16,.038),'Black',.002)
 for x,y in ((-.72,-.37),(.72,-.37),(-.10,1.35)):
  m.lathe((x,y,.045),[(0,.045),(.06,.065),(.14,.037),(.39,.060),(.62,.042),(.71,.075)],'Walnut',12)
  m.cylinder((x,y,.040),.033,.036,'Brass',16,(1,0,0))
  m.ring((x,y,.040),.032,.008,'Iron',16,8,(1,0,0))
 m.box((0,-.40,1.08),(.66,.038,.27),'Walnut',.008)
 m.box((0,-.422,1.09),(.53,.012,.23),'Paper')
 # A suspended lyre, rather than three unsupported bent rods.
 for x in (-.20,.20):m.rod((x,.13,.15),(x,.13,.735),.025,'Walnut',10)
 m.box((0,.13,.155),(.46,.12,.07),'Walnut',.008)
 for x in (-.13,0,.13):m.tube([(x,.13,.14),(x,-.34,.13),(x,-.49,.08)],.013,'Brass',8)
 m.tags['Pianoforte']+=1;m.tags['ConnectedSoundboardHarpLidAndPedalLyre']+=1;return m''')
a=sub(a," # Thin textile lies on the actual finished floor, not above it.\n m.box((x,y,z+.004),(length,width,.008),cloth,.002)\n for yy in (y-width/2+.07,y+width/2-.07):m.box((x,yy,z+.008),(length-.165,.025,.003),'GoldCloth')\n for xx in (x-length/2+.07,x+length/2-.07):m.box((xx,y,z+.008),(.025,width-.10,.003),'GoldCloth')", " # A fitted textile INLAY in the 25mm floor finish, not a hovering mat\n # or an 8mm slab driven up through already floor-seated furniture feet.\n m.box((x,y,z-.0035),(length,width,.008),cloth,.002)\n for yy in (y-width/2+.07,y+width/2-.07):m.box((x,yy,z+.00055),(length-.165,.025,.0007),'GoldCloth')\n for xx in (x-length/2+.07,x+length/2-.07):m.box((xx,y,z+.00055),(.025,width-.10,.0007),'GoldCloth')")
a=sub(a,"z+1.04),math.pi/2,scale=(.65,.60,.65)","z+1.0373),math.pi/2,scale=(.65,.60,.65)")
a=sub(a," # A low leather case uses the already open space BELOW the lower berth.\n m.box((x0+.54,cy-.37,z+.19),(.58,.65,.24),'Leather',.018)\n for yy0 in (cy-.57,cy-.20):m.box((x0+.54,yy0,z+.315),(.56,.026,.012),'Brass',.003)"," # Only single-berth cabins receive this floor-seated case. Two-tier\n # bunks already have their own supported stowage; do not intersect it.\n if r['kind'] not in ('cabin_second','cabin_officer'):\n  m.box((x0+.54,cy-.37,z+.12),(.58,.65,.24),'Leather',.018)\n  for yy0 in (cy-.57,cy-.20):m.box((x0+.54,yy0,z+.245),(.56,.026,.012),'Brass',.003)")
save('period_detail.py',a)
a=load('public_rooms.py');a=sub(a,'from furnishings import chair,sofa,table,desk,wardrobe,service_setting,bookcase','from furnishings import chair,sofa,table,desk,wardrobe,service_setting,bookcase,TABLE_WOOD_TOP,TABLE_CLOTH_TOP,DESK_PAD_TOP')
a=sub(a,"yy+side*.30,z+.798","yy+side*.30,z+TABLE_CLOTH_TOP-.0002")
a=sub(a,"m.lathe((xx,yy,z+.800)","m.lathe((xx,yy,z+TABLE_CLOTH_TOP-.0002)")
a=sub(a,"m.cylinder((xx,yy,z+.817)","m.cylinder((xx,yy,z+TABLE_CLOTH_TOP+.0173)")
a=sub(a,"m.lathe((xx+dx,yy,z+.836)","m.lathe((xx+dx,yy,z+TABLE_CLOTH_TOP+.0346)")
a=sub(a,"(h-.18,.15),(h-.05,.16)","(h-.18,.15),(h+.006,.16)")
a=sub(a,"m.box((xx,yy,z+.789),(.58,1.95,.009)","m.box((xx,yy,z+TABLE_WOOD_TOP+.0045),(.58,1.95,.009)")
a=sub(a,"q=recolour(service_setting(),{'Brass':'Porcelain'});place(m,q,xx+sx*.25,yy+dy,z+.795", "q=recolour(service_setting(.009),{'Brass':'Porcelain'});place(m,q,xx+sx*.25,yy+dy,z+TABLE_WOOD_TOP+.0088")
a=sub(a,"tea_tray(m,x0+.33,cy,z+1.0)","tea_tray(m,x0+.33,cy,z+.9923)")
a=sub(a,"t.lathe((0,0,.05),[(0,.16),(.08,.18),(.16,.095),(.54,.09),(.62,.16)]", "t.lathe((0,0,0),[(0,.16),(.08,.18),(.16,.095),(.54,.09),(.675,.16)]")
a=sub(a,"z+.787))","z+TABLE_WOOD_TOP-.0002))")
a=sub(a,"reading_lamp(cx+dx,cy,z+.788)","reading_lamp(cx+dx,cy,z+TABLE_WOOD_TOP-.0002)")
a=sub(a,"reading_lamp(xx-.40,y1-.50,z+.811)","reading_lamp(xx-.40,y1-.50,z+DESK_PAD_TOP-.0002)")
a=sub(a,"paper_and_ink(m,xx+dx,yy+side*.25,z+.785", "paper_and_ink(m,xx+dx,yy+side*.25,z+TABLE_WOOD_TOP-.0002")
a=a.replace('z+.772','z+.7698').replace('z+.773','z+.7698').replace('z-.006,','z,')
a=sub(a,"inventory='Supported baize billiard table with balls/cue,", "inventory='Pocketless three-ball carom billiard table with cloth-seated balls/cue,")
save('public_rooms.py',a)
print('Applied actual-surface corrections to public furnishings, piano mechanism and cabin accessories.')
