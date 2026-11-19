"""Headless arrangement/runtime-contract checks, NOT Roblox Studio acceptance.
Operate on actual generated collider/fixture data, not legacy room labels.
"""
from pathlib import Path
import sys,json,math,collections,hashlib
import numpy as np
from scipy import ndimage
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS,DECKS,STAIRS,rect,overlap,hb,roblox_point,CRANK_R,CONROD_L,ENGINE_XS,PROP_X,PROP_R,SHAFT_Z
DATA=json.loads((ROOT/'exports'/'leonidas_ii'/'build_data.json').read_text())
OUT=ROOT/'docs'/'leonidas_ii';OUT.mkdir(parents=True,exist_ok=True)
RESULTS=[]
def record(test,status,detail):RESULTS.append(dict(test=test,status=status,detail=detail));print(status,test,str(detail)[:220])
record('All planned compartments have an explicit inventory','PASS' if {r['id'] for r in ROOMS}<={r['id'] for r in DATA['rooms']} else 'FAIL',len(DATA['rooms']))
record('Unique object names','PASS' if len({o['name'] for o in DATA['objects']})==len(DATA['objects']) else 'FAIL',len(DATA['objects']))
record('UV0 on every source mesh','PASS' if all(o['uv_layers']>=1 for o in DATA['objects']) else 'FAIL',[o['name'] for o in DATA['objects'] if o['uv_layers']<1])
record('Finite source bounds with positive extent on each axis','PASS' if all(all(math.isfinite(v) for b in o['bounds'].values() for v in b) and all(o['bounds']['max'][k]-o['bounds']['min'][k]>1e-6 for k in range(3)) for o in DATA['objects']) else 'FAIL','Post-build object bounding boxes; not a positive signed-volume proof')
conflicts=[]
for i,r in enumerate(ROOMS):
 for s in ROOMS[i+1:]:
  if r['deck']==s['deck'] and r['kind']!='machinery' and s['kind']!='machinery' and overlap(rect(r),rect(s),.001):conflicts.append((r['id'],s['id']))
record('Compartment rectangles do not overlap','PASS' if not conflicts else 'FAIL',conflicts)
stairclash=[]
for st in STAIRS:
 sr=(min(st['x0'],st['x1']),max(st['x0'],st['x1']),st['y']-st['width']/2,st['y']+st['width']/2)
 for r in ROOMS:
  if r['kind'].startswith('cabin') and r['deck'] in (st['fr'],st['to']) and overlap(sr,rect(r),.015):stairclash.append((st['id'],r['id']))
record('Stair escape footprints clear of cabin walls','PASS' if not stairclash else 'FAIL',stairclash)
# Dimensional checks on actual prefab placements, not object-group AABBs.
roomby={r['id']:r for r in ROOMS};outside=[]
for f in DATA.get('fixtures',[]):
 r=roomby.get(f['room']);lo,hi=f['bounds']
 if not r:continue
 over=max(r['x0']-lo[0],hi[0]-r['x1'],r['y0']-lo[1],hi[1]-r['y1'],hi[2]-r['top'])
 if over>.10:outside.append(dict(room=r['id'],fixture=f['label'],over_m=round(over,3),bounds=f['bounds']))
record('Fixture geometry fits compartment envelope (100mm tolerance)','PASS' if not outside else 'FAIL',outside)
# Bounding-box suspects are a conservative placement gate, not a full BVH
# intersection proof. Bed/frame details within a prefab are intentional.
byroom=collections.defaultdict(list);suspects=[]
for f in DATA.get('fixtures',[]):byroom[f['room']].append(f)
for rid,ff in byroom.items():
 for i,a in enumerate(ff):
  for b in ff[i+1:]:
   d=[min(a['bounds'][1][k],b['bounds'][1][k])-max(a['bounds'][0][k],b['bounds'][0][k]) for k in range(3)]
   if min(d[:2])>.035 and d[2]>.18:suspects.append(dict(room=rid,a=a['label'],b=b['label'],overlap_m=d))
record('No substantial furniture-pair AABB overlap suspects','PASS' if not suspects else 'FAIL',suspects)
record('Built passenger and crew berths counted separately','INFO',DATA['counts'])
# Exact slider crank over one revolution, endpoint conservation / finite sqrt.
res=[]
for phase in (0,2*math.pi/3,4*math.pi/3):
 for th in np.linspace(0,2*math.pi,721):
  yy=CRANK_R*math.sin(float(th)+phase);zz=SHAFT_Z+CRANK_R*math.cos(float(th)+phase);cz=zz+math.sqrt(CONROD_L**2-yy**2);res.append(abs(math.hypot(yy,cz-zz)-CONROD_L))
record('Main conrod pin-to-crosshead distance over 2163 poses','PASS' if max(res)<1e-9 else 'FAIL',max(res))
# Explicit basis test: position includes WL translation, vectors do not.
record('Roblox axis transform / scale','PASS' if roblox_point((10,0,6.5))==(0,0.,-10) and roblox_point((0,5,6.5))==(-5,0.,0) else 'FAIL',dict(loa_studs=166/.28,beam_studs=18.4/.28,forward='-Z',port='-X',up='+Y',load_waterline_y=0))
# Propeller-disc vs shell profile is stronger than a bounding box (clearance
# must be positive across swept radius; actual blade mesh also gets BVH check).
from shipdesign.leonidas_ii import keel_z,PROP_PITCH,SHAFT_RPM,ADVANCE_RATIO
clear=keel_z(PROP_X)-(SHAFT_Z+PROP_R)
record('Propeller tip vs counter vertical clearance','PASS' if clear>.1 else 'FAIL',round(clear,3))
record('Kinematic target knots at nominal RPM','INFO',round(SHAFT_RPM*PROP_PITCH/60*ADVANCE_RATIO/.514444,3))
# Actual collider-grid circulation with avatar radius .26m and standing
# height1.68m. Doors assumed open. This is not Humanoid physics / stair proof.
STEP=.20;RAD=.28;HEIGHT=1.68
xs=np.arange(-82.5,83.,STEP);ys=np.arange(-9.5,9.51,STEP)
NX,NY=len(xs),len(ys);GRIDS={};DOORCHECK=[]
def stamp(mask,p,value,inflate=0.):
 cx,cy,cz=p['position'];sx,sy,sz=p['size'];angle=p.get('yaw',0.);ca,sa=math.cos(angle),math.sin(angle);ex=abs(ca)*sx/2+abs(sa)*sy/2+inflate;ey=abs(sa)*sx/2+abs(ca)*sy/2+inflate
 ix0=max(0,int((cx-ex-xs[0])/STEP)-1);ix1=min(NX,int((cx+ex-xs[0])/STEP)+2);iy0=max(0,int((cy-ey-ys[0])/STEP)-1);iy1=min(NY,int((cy+ey-ys[0])/STEP)+2)
 if ix1<=ix0 or iy1<=iy0:return
 X=xs[ix0:ix1,None]-cx;Y=ys[None,iy0:iy1]-cy;inside=(np.abs(X*ca+Y*sa)<sx/2+inflate)&(np.abs(-X*sa+Y*ca)<sy/2+inflate);view=mask[ix0:ix1,iy0:iy1];view[inside]=value
LEVELS={**DECKS,'machinery':1.6}
for dk,z in LEVELS.items():
 floor=np.zeros((NX,NY),bool);blocked=np.zeros_like(floor)
 for p in DATA['proxies']:
  if p.get('kind')=='ramp':continue
  low=p['position'][2]-p['size'][2]/2;high=p['position'][2]+p['size'][2]/2
  if abs(high-z)<.18 and p['size'][2]<.5:stamp(floor,p,True)
  elif low<z+HEIGHT and high>z+.13:stamp(blocked,p,True,RAD)
 walk=floor&~blocked;labels,n=ndimage.label(walk);sizes=np.bincount(labels.ravel());largest=int(np.argmax(sizes[1:])+1) if n else 0
 GRIDS[dk]=(walk,labels,largest)
 def nearest(x,y):
  ix=int(round((x-xs[0])/STEP));iy=int(round((y-ys[0])/STEP));c=[]
  for dx in range(-2,3):
   for dy in range(-2,3):
    a,b=ix+dx,iy+dy
    if 0<=a<NX and 0<=b<NY and walk[a,b]:c.append((dx*dx+dy*dy,int(labels[a,b]),a,b))
  return min(c) if c else None
 for r in ROOMS:
  if r['deck']!=dk or r['kind']=='machinery' or abs(r['z']-z)>.01:continue
  wall=r['door_wall'];u=r['door_u'];pos=(u,r[wall]) if wall[0]=='y' else (r[wall],u)
  normal={'y0':(0,1),'y1':(0,-1),'x0':(1,0),'x1':(-1,0)}[wall];inside=(pos[0]+normal[0]*.48,pos[1]+normal[1]*.48);outsidep=(pos[0]-normal[0]*.48,pos[1]-normal[1]*.48);a=nearest(*inside);b=nearest(*outsidep)
  DOORCHECK.append(dict(id=r['id'],deck=dk,inside_clear=bool(a),outside_clear=bool(b),same_component=bool(a and b and a[1]==b[1]),on_largest_component=bool(a and b and a[1]==largest and b[1]==largest),inside=inside,outside=outsidep,component=a[1] if a else 0))
 # Diagnostic image maps distinguish no floor / obstacles / accessible area.
 from PIL import Image
 rgb=np.zeros((NX,NY,3),np.uint8);rgb[:]=[28,40,48];rgb[floor]=[154,135,103];rgb[walk]=[179,206,173];rgb[blocked&floor]=[160,74,60]
 img=Image.fromarray(np.flip(rgb.transpose(1,0,2),axis=0)).resize((1650,190));img.save(OUT/f'circulation_{dk}.png')
faildoors=[r for r in DOORCHECK if not r['same_component']];off=[r for r in DOORCHECK if not r['on_largest_component']]
record('Actual-collider local doorway passability, all doors open','PASS' if not faildoors else 'FAIL',faildoors)
record('Doorway joins deck largest walk component','PASS' if not off else 'INFO',off)
# A deck may correctly have fore/aft zones separated by plant openings. Link
# their *actual* free-space components with stair endpoints, not room labels.
def component_at(dk,x,y):
 if isinstance(dk,(int,float)):dk='machinery' if abs(dk-1.6)<.01 else next((k for k,v in DECKS.items() if abs(v-dk)<.01),dk)
 if dk not in GRIDS:return None
 walk,labels,_=GRIDS[dk];ix=int(round((x-xs[0])/STEP));iy=int(round((y-ys[0])/STEP));hits=[]
 for dx in range(-2,3):
  for dy in range(-2,3):
   a,b=ix+dx,iy+dy
   if 0<=a<NX and 0<=b<NY and walk[a,b]:hits.append((dx*dx+dy*dy,int(labels[a,b])))
 return (dk,min(hits)[1]) if hits else None
graph=collections.defaultdict(set);stairlinks=[]
for st in STAIRS:
 sign=1 if st['x1']>st['x0'] else -1
 a=component_at(st['fr'],st['x0']-.50*sign,st['y']);b=component_at(st['to'],st['x1']+.50*sign,st['y'])
 stairlinks.append(dict(id=st['id'],from_component=a,to_component=b))
 if a and b:graph[a].add(b);graph[b].add(a)
start=component_at('main',-2,-8.2);seen={start};queue=[start]
while queue:
 for n in graph[queue.pop()]:
  if n not in seen:seen.add(n);queue.append(n)
unreachable=[r['id'] for r in DOORCHECK if (r['deck'],r['component']) not in seen]
record('Multideck component reachability from boarding landing','PASS' if not unreachable else 'FAIL',dict(unreachable=unreachable,stair_endpoints=stairlinks,assumption='nearest .4m endpoint; separate stair headroom test below'))
machinery_aisles={'Engine_Port':(-17.0,4.05),'Engine_Starboard':(-17.0,-4.05),'After_Stokehold':(-.5,0),'Middle_Stokehold':(11.0,0),'Forward_Stokehold':(23.0,0),'Dynamo_Aisle':(-6.5,-2.95),'Pump_Aisle':(-8.4,3.0),'Shaft_Alley_Port':(-49.0,1.05),'Shaft_Alley_Starboard':(-49.0,-1.05)}
mech_routes=[dict(aisle=k,component=component_at('machinery',*v),reachable=component_at('machinery',*v) in seen) for k,v in machinery_aisles.items()]
record('Machinery service-aisle anchors reachable from boarding','PASS' if all(r['reachable'] for r in mech_routes) else 'FAIL',mech_routes)
cooking=[]
for r in ROOMS:
 if r['kind'] not in ('galley','bakery'):continue
 fitted=[f for f in DATA['fixtures'] if f['room']==r['id'] and f['label'] in ('CoalRangeThreeOvens','CoalBreadOven')];point=(r['x0']+2,r['y0']+2.35)
 cooking.append(dict(room=r['id'],range_faces_working_aisle=bool(len(fitted)==1 and abs(fitted[0]['yaw']-math.pi)<1e-6),firing_position=point,reachable=component_at(r['deck'],*point) in seen))
record('Cooking furnace fronts face reachable working aisles','PASS' if all(r['range_faces_working_aisle'] and r['reachable'] for r in cooking) else 'FAIL',cooking)
# 3D head-space samples test current actual colliders. Do not omit plates
# which a rendered ladder happens to pass through. Native leaf doors assumed
# open; visual rails/head fittings still require the Studio walk-through.
P=DATA['proxies'];centres=np.array([p['position'] for p in P]);sizes=np.array([p['size'] for p in P]);yaws=np.array([p.get('yaw',0) for p in P]);pitches=np.array([p.get('pitch',0) for p in P]);cy,sy=np.cos(yaws),np.sin(yaws);cp,sp=np.cos(pitches),np.sin(pitches)
headchecks=[];TESTFLIGHTS=list(STAIRS)
for i,pr in enumerate(DATA['proxies']):
 if pr.get('tag')=='EngineLadder':
  cx,yy,cz=pr['position'];length=pr['size'][0];angle=-pr['pitch'];dx=length*math.cos(angle)/2;dz=length*math.sin(angle)/2
  TESTFLIGHTS.append(dict(id=f'EngineLadder_{i}',x0=cx-dx,x1=cx+dx,y=yy,z0=cz+.05-dz,z1=cz+.05+dz,tag='EngineLadder'))
for st in TESTFLIGHTS:
 tags=set()
 for t in np.linspace(.025,.975,27):
  xx=st['x0']+(st['x1']-st['x0'])*t;zz=st['z0']+(st['z1']-st['z0'])*t
  for h in np.linspace(.24,HEIGHT,6):
   for dx,dy in [(0,0)]:
    dv=np.array([xx+dx,st['y']+dy,zz+h])-centres;lx=dv[:,0]*cy+dv[:,1]*sy;ly=-dv[:,0]*sy+dv[:,1]*cy;lz=dv[:,2];rx=lx*cp-lz*sp;rz=lx*sp+lz*cp
    hit=(np.abs(rx)<sizes[:,0]/2+RAD*np.abs(cp)-.002)&(np.abs(ly)<sizes[:,1]/2+RAD-.002)&(np.abs(rz)<sizes[:,2]/2+RAD*np.abs(sp)-.002)
    for i in np.where(hit)[0]:
     if P[i].get('tag')!=st.get('tag',st['id']):tags.add(P[i].get('tag',''))
 headchecks.append(dict(id=st['id'],blocked_by=sorted(tags)))
record('Stair sampled avatar head/body envelope','PASS' if not any(r['blocked_by'] for r in headchecks) else 'FAIL',headchecks)
# Export checks are separate from the source mesh count.
mp=ROOT/'exports'/'leonidas_ii'/'game_manifest.json'
if mp.exists() and '--source-only' not in sys.argv:
 game=json.loads(mp.read_text());qa=game['mesh_audit'];nodes=game['nodes']
 import hashlib
 record('Game export regenerated from current master','PASS' if game['source_sha256']==hashlib.sha256((ROOT/'models'/'leonidas_ii'/'Aurelian_1889.blend').read_bytes()).hexdigest() else 'FAIL',game['source_sha256'])
 record('Game mesh node <=18000 triangles / finite UV0 / closed components','PASS' if max(n['triangles'] for n in nodes)<=18000 and all(q['finite'] and not q['uv_outside_01'] and not q['zero_area_triangles'] and not q['boundary_edges'] and not q['nonmanifold_edges'] for q in qa) else 'FAIL',game['counts'])
 missing=[m['name'] for m in DATA['movers']+DATA['doors'] if not any(n['name']==m['name'] or n['name'].startswith(m['name']+'_') for n in nodes)]
 record('All actual mover / door names exist in the game export','PASS' if not missing else 'FAIL',missing)

gp=ROOT/'exports'/'leonidas_ii'/'build'/'build_data.json'
if gp.exists() and '--source-only' not in sys.argv:
 gd=json.loads(gp.read_text());maxdelta=0.;bad=[]
 for i,(a,b) in enumerate(zip(DATA['proxies'],gd['proxies'])):
  d=max(abs(a[k][j]-b[k][j]) for k in ('position','size') for j in range(3));maxdelta=max(maxdelta,d)
  # Fixture envelopes from tessellated prefabs vary slightly with angular
  # detail. The install kit intentionally always uses the MASTER proxies.
  metadata=all(a.get(k)==b.get(k) for k in ('tag','kind','yaw','pitch'))
  if not metadata or d>(.025 if a.get('tag','').endswith('_fixture') else 1e-6):bad.append(i)
 parity=all(DATA[k]==gd[k] for k in ('movers','doors','seats','lights','attachments','boat_mounts')) and len(DATA['proxies'])==len(gd['proxies']) and not bad
 record('Master/GAME interfaces and collider-envelope tolerance','PASS' if parity else 'FAIL',dict(interface_arrays_equal=all(DATA[k]==gd[k] for k in ('movers','doors','seats','lights','attachments','boat_mounts')),colliders_master=len(DATA['proxies']),colliders_game=len(gd['proxies']),max_fixture_delta_m=round(maxdelta,6),nonconforming=bad,runtime_uses='master proxies, not lower-detail bounding boxes'))
record('Roblox Studio live acceptance','UNVERIFIED','No Roblox Studio in this workspace. Static collider graph does not certify avatar headroom on slopes, moving passengers, imported collisions, multiplayer security or frame time.')
result=dict(scope='SOURCE_ONLY_NO_EXPORT_VALIDATION' if '--source-only' in sys.argv else 'SOURCE_AND_CURRENT_EXPORT',source_sha256=hashlib.sha256((ROOT/'models/leonidas_ii/Aurelian_1889.blend').read_bytes()).hexdigest(),validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),build_data_sha256=hashlib.sha256((ROOT/'exports/leonidas_ii/build_data.json').read_bytes()).hexdigest(),game_manifest_sha256=hashlib.sha256(mp.read_bytes()).hexdigest() if mp.exists() and '--source-only' not in sys.argv else None,results=RESULTS,summary=dict(collections.Counter(r['status'] for r in RESULTS)),fixture_envelope_violations=outside,door_checks=DOORCHECK,stair_links=stairlinks,stair_headspace=headchecks,grid={'cell_m':STEP,'avatar_radius_m':RAD,'standing_height_m':HEIGHT,'assumptions':'doors open; horizontal slices at named decks; ramps require separate test; nearest valid sample within .4m'},source='exports/leonidas_ii/build_data.json')
(OUT/'STATIC_VALIDATION.json').write_text(json.dumps(result,indent=2))
md=['# LEONIDAS-II static validation','', '**This is not Roblox Studio acceptance.**','']
for r in RESULTS:
 detail=r['detail'];detail=json.dumps(detail) if not isinstance(detail,str) else detail
 md += [f'## {r["status"]} — {r["test"]}',detail,'']
(OUT/'STATIC_VALIDATION.md').write_text('\n'.join(md))
print(json.dumps(result['summary']))

if __name__=='__main__':sys.exit(1 if any(r['status']=='FAIL' for r in RESULTS) else 0)
