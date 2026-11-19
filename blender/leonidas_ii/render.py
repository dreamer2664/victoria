"""Actual Blender evidence, never generated concept imagery.
blender -b models/leonidas_ii/Aurelian_1889.blend -t 2 -P .../render.py -- preview
Preset modes preview / exterior / interiors / engineering / plans / rooms / all / complete.
Every view is kept in the camera register. Cutaways are explicitly named.
"""
import sys,math,json,time,os,hashlib,subprocess
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];sys.path[:0]=[str(HERE),str(ROOT)]
from shipdesign.leonidas_ii import ROOMS,DECKS
DATA=json.loads((ROOT/'exports'/'leonidas_ii'/'build_data.json').read_text())
OUT=ROOT/'renders'/'leonidas_ii'/os.getenv('LII_RENDER_SUBDIR','');OUT.mkdir(parents=True,exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['preview'];mode=args[0];quality=int(args[1]) if len(args)>1 else 100
sc=bpy.context.scene
assert Path(bpy.data.filepath).resolve()==(ROOT/'models/leonidas_ii/Aurelian_1889.blend').resolve(),'Evidence must open the actual delivered MASTER, not an arbitrary scene'
# Render only contains authentic source meshes; cameras/lights are a stage.
for ob in list(sc.objects):
 if ob.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(ob,do_unlink=True)
sc.render.engine=os.getenv('LII_ENGINE','CYCLES');sc.cycles.device='CPU';sc.cycles.samples=int(os.getenv('LII_SAMPLES','10' if mode=='preview' else '12'));sc.cycles.use_denoising=False;sc.cycles.max_bounces=5;sc.cycles.transparent_max_bounces=4;sc.render.resolution_percentage=quality;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False;sc.render.threads_mode='FIXED';sc.render.threads=2;sc.view_settings.view_transform='AgX'
if sc.render.engine=='BLENDER_EEVEE_NEXT':sc.eevee.taa_render_samples=16
sc.cycles.use_adaptive_sampling=True;sc.cycles.adaptive_threshold=.20;sc.cycles.adaptive_min_samples=2
sc.cycles.diffuse_bounces=2;sc.cycles.glossy_bounces=2;sc.cycles.transmission_bounces=4;sc.cycles.sample_clamp_indirect=3.0
# Bound texture memory for evidence rendering; original packed 2K maps are
# never overwritten. A separate process can denoise after Blender exits.
for image in bpy.data.images:
 if image.size[0]>1024 and image.size[1]>1024:image.scale(1024,1024)
# Atlas emission is mostly BLACK texels shared by every furnishing/wall.
# Sampling all those triangles as area lights wastes rays and produces
# severe noise. Retain the actual emissive pixels, but light the scene
# from the registered practical fixture points below instead of sampling
# every non-emitting face of the shared atlas as a potential light source.
for material in bpy.data.materials:
 if material.name.startswith('Aurelian_OriginalPBR_Atlas'):material.cycles.emission_sampling='NONE'
SOURCE_HASH=hashlib.sha256((ROOT/'models'/'leonidas_ii'/'Aurelian_1889.blend').read_bytes()).hexdigest()
RENDERER_HASH=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
REGFILE=OUT/'all_cameras.json'
PERSISTED=json.loads(REGFILE.read_text()) if REGFILE.exists() else []
PERSISTED=[r for r in PERSISTED if r.get('source_sha256')==SOURCE_HASH]
REGISTER=[];lights=[]

def register(entry):
 global PERSISTED
 REGISTER.append(entry);key=Path(entry['file']).stem
 PERSISTED=[r for r in PERSISTED if Path(r['file']).stem!=key]+[entry]
 (OUT/'camera_register.json').write_text(json.dumps(REGISTER,indent=2))
 REGFILE.write_text(json.dumps(PERSISTED,indent=2))

def light(name,pos,energy,size,target=None,color=(1,.85,.65)):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size;data.color=color;ob=bpy.data.objects.new(name,data);sc.collection.objects.link(ob);ob.location=pos
 if target is not None:ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 lights.append(ob);return ob

def setup(pos,target,lens=30,ortho=None,interior=None):
 for ob in lights:
  if ob.name in bpy.data.objects:bpy.data.objects.remove(ob,do_unlink=True)
 lights.clear();cam=bpy.data.objects.get('EvidenceCamera')
 if not cam:data=bpy.data.cameras.new('EvidenceCamera');cam=bpy.data.objects.new('EvidenceCamera',data);sc.collection.objects.link(cam)
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.clip_start=.045;cam.data.clip_end=700;cam.data.type='ORTHO' if ortho else 'PERSP'
 if ortho:cam.data.ortho_scale=ortho
 sc.camera=cam
 if interior:
  x0,x1,y0,y1,z,top=interior
  sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
  # Soft practical fixtures + window-like fill, all on real room side.
  for x in [x0+(x1-x0)*.25,x0+(x1-x0)*.70]:
   light('Ceiling practical',(x,(y0+y1)/2,top-.26),85 if x1-x0<6 else 220,1.1,(x,(y0+y1)/2,z),(1,.79,.53))
  light('Window bounce',((x0+x1)/2,y1-.17,z+1.7),70 if x1-x0<6 else 300,1.8,((x0+x1)/2,y0,z+1),(0.72,.85,1.0))
  light('Camera fill',pos,40 if x1-x0<6 else 160,.30,target,(1,.86,.66))
  # Illuminate from the registered modeled fixture locations as well as
  # the diagnostic photographic fill. Ceiling-only staging is occluded by
  # the actual machinery working flats and gave an unreadable dark aisle.
  # Points sit just below the bulb/shade, never inside an opaque bulb mesh.
  for i,fixture in enumerate(DATA['lights']):
   fx,fy,fz=fixture['position']
   if x0-.25<=fx<=x1+.25 and y0-.25<=fy<=y1+.25 and z+.3<=fz<=top+.1:
    data=bpy.data.lights.new('Modeled fixture '+str(i),'POINT');data.energy=65*fixture.get('brightness',.8);data.color=(1,.80,.57);data.shadow_soft_size=.065
    ob=bpy.data.objects.new(data.name,data);sc.collection.objects.link(ob);ob.location=(fx,fy,fz-.20);lights.append(ob)
 else:
  sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
  light('Key',(45,-85,135),230000,85,(0,0,8),(1,.88,.68));light('Sky',(-60,55,100),180000,95,(0,0,8),(.68,.83,1));light('Rim',(-100,-15,60),85000,65,(-20,0,8),(1,.75,.45))
  if pos[2]<0:light('Underbody diagnostic fill',(15,50,-75),220000,80,(-5,0,3),(.85,.92,1))
 return cam

def visibility(keep=None):
 for ob in sc.objects:
  if ob.type!='MESH':continue
  ob.hide_render=not keep(ob) if keep else False

def render(name,title,pos,target,lens=30,ortho=None,interior=None,res=(1600,1000),cutaway=False,room_id=None):
 if os.getenv('LII_ONLY') and Path(name).name not in os.getenv('LII_ONLY').split(','):return
 if mode=='refinement':res=(1120,700)
 pixels=[int(res[0]*quality/100),int(res[1]*quality/100)]
 if os.getenv('LII_RESUME')=='1':
  for previous in PERSISTED:
   final=ROOT/previous['file']
   if Path(previous['file']).stem==Path(name).name and previous.get('source_sha256')==SOURCE_HASH and previous.get('renderer_sha256')==RENDERER_HASH and previous.get('camera')==list(pos) and previous.get('target')==list(target) and previous.get('lens')==lens and previous.get('orthographic_scale')==ortho and previous.get('cutaway')==cutaway and previous.get('room_id')==room_id and previous.get('pixels')==pixels and previous.get('cycles_samples',0)>=sc.cycles.samples and final.is_file() and final.suffix=='.jpg' and previous.get('sha256')==hashlib.sha256(final.read_bytes()).hexdigest():
    print('RESUMED VERIFIED PIXELS',name,flush=True);return
 # Raw images stay in excluded scratch even between batch stages. Only
 # the registered full-resolution processed JPGs consume saved-file budget.
 raw_file=OUT/'build'/'pending'/(name+'.png');raw_file.parent.mkdir(parents=True,exist_ok=True)
 cam=setup(pos,target,lens,ortho,interior);sc.render.resolution_x=res[0];sc.render.resolution_y=res[1];sc.render.filepath=str(raw_file)
 px,py=int(res[0]*quality/100),int(res[1]*quality/100)
 if px*py>800000:
  # Border tiles bound CPU denoising memory on the 1.9GiB build host. Camera
  # projection, geometry and full-frame pixel resolution are unchanged.
  scratch=OUT/'build'/name;scratch.mkdir(parents=True,exist_ok=True);tiles=[];sc.render.use_border=True;sc.render.use_crop_to_border=True
  for row in range(2):
   for col in range(2):
    x0,x1=px*col//2,px*(col+1)//2;y0,y1=py*row//2,py*(row+1)//2
    bx0,bx1=max(0,x0-32),min(px,x1+32);by0,by1=max(0,y0-32),min(py,y1+32)
    sc.render.border_min_x=bx0/px;sc.render.border_max_x=bx1/px;sc.render.border_min_y=1-by1/py;sc.render.border_max_y=1-by0/py
    file=scratch/f'{row}_{col}.png';sc.render.filepath=str(file);bpy.ops.render.render(write_still=True)
    tiles.append(dict(file=str(file),box=[x0,y0,x1,y1],source_origin=[bx0,by0]))
  sc.render.use_border=False;sc.render.use_crop_to_border=False
  plate=dict(size=[px,py],output=str(raw_file),tiles=tiles);jp=scratch/'tiles.json';jp.write_text(json.dumps(plate));subprocess.run(['python3',str(ROOT/'tools'/'join_leonidas_render_tiles.py'),str(jp)],check=True)
 else:bpy.ops.render.render(write_still=True)
 register(dict(file=str(raw_file.relative_to(ROOT)),title=title,camera=list(pos),target=list(target),lens=lens,orthographic_scale=ortho,cutaway=cutaway,room_id=room_id,source='models/leonidas_ii/Aurelian_1889.blend',source_sha256=SOURCE_HASH,renderer_sha256=RENDERER_HASH,pixels=pixels,cycles_samples=sc.cycles.samples,staging='Registered fixture points plus photographic fill; atlas emission visible but not sampled as area lights; diffuse/glossy bounces 2/2'))
 print('RENDERED',name,flush=True)


def clear_camera(r,p):
 # A photographic eye must have a plausible standing space, not merely a
 # clear pixel ray inside a mattress, bookcase or oven. Conservative actual
 # fixture bounds and rotated native collision boxes select a free vantage.
 x,y,z=p;low=r['z']+.30;high=z+.12;pad=.10
 for f in DATA['fixtures']:
  if f['room']!=r['id']:continue
  a,b=f['bounds']
  if a[0]-pad<x<b[0]+pad and a[1]-pad<y<b[1]+pad and a[2]<high and b[2]>low:return False
 for a in DATA['proxies']:
  if a.get('kind')=='ramp':continue
  cx,cy,cz=a['position'];sx,sy,sz=a['size']
  if cz-sz/2>=high or cz+sz/2<=low:continue
  angle=a.get('yaw',0.);dx=x-cx;dy=y-cy
  if abs(dx*math.cos(angle)+dy*math.sin(angle))<sx/2+pad and abs(-dx*math.sin(angle)+dy*math.cos(angle))<sy/2+pad:return False
 return True


def room_camera(r):
 x0,x1,y0,y1=r['x0'],r['x1'],r['y0'],r['y1'];z=r['z'];cx=(x0+x1)/2;cy=(y0+y1)/2
 desired=(x0+.55,cy if r['kind'].startswith('dorm') else y0+.60,z+1.62)
 if r['kind']=='galley':desired=(x0+5.8,y0+2.85,z+1.62)
 elif r['kind']=='bakery':desired=(x1-.50,y1-1.0,z+1.62)
 elif r['kind']=='music':desired=(x0+5.0,cy-2.9,z+1.62)
 elif r['kind']=='chart':desired=(x0+1.15,y0+.80,z+1.62)
 elif r['kind']=='wheelhouse':
  # Aft of the telegraphs, with a clear oblique line past (not through)
  # the wheel to the forward-port clock/bell corner.
  desired=(34.6,-2.6,z+1.62)
 elif r['kind']=='bath':desired=(cx,y0+.50,z+1.62)
 wall=r['door_wall'];u=r['door_u'];door=(u,y0+.55,z+1.62) if wall=='y0' else (u,y1-.55,z+1.62) if wall=='y1' else (x0+.55,u,z+1.62) if wall=='x0' else (x1-.55,u,z+1.62)
 candidates=[desired,(x0+.55,y1-.60,z+1.62),(x1-.55,y0+.60,z+1.62),(x1-.55,y1-.60,z+1.62),door,(x0+.55,cy,z+1.62),(x1-.55,cy,z+1.62)]
 candidates += [(x0+(x1-x0)*a,y0+(y1-y0)*b,z+1.62) for a in (.12,.88,.3,.7,.5) for b in (.15,.85,.5)]
 pos=next((p for p in candidates if clear_camera(r,p)),None);assert pos is not None,(r['id'],'no furniture-clear camera position')
 # Look across the room from the selected side. In dormitories retain the
 # real central aisle instead of placing an eye inside an outer berth row.
 target=(x1-1.10 if pos[0]<=cx else x0+1.10,(cy+.3 if r['kind'].startswith('dorm') else y1-.85 if pos[1]<=cy else y0+.85),z+1.38)
 if r['kind'] in ('galley','bakery'):target=(x0+2.0,y0+1.0,z+.95)
 elif r['kind']=='music':target=(x0+2.1,cy,z+.95)
 elif r['kind']=='chart':target=(cx+.20,cy,z+1.10)
 elif r['kind']=='wheelhouse':target=(39.0,-.7,z+1.40)
 elif r['kind']=='bath':target=(cx,cy-.20,z+.55)
 return pos,target


def roomshot(id,name=None):
 r=next(r for r in ROOMS if r['id']==id);x0,x1,y0,y1=r['x0'],r['x1'],r['y0'],r['y1'];z,top=r['z'],r['top']
 # Every wall, floor and ceiling of this compartment is retained. Exterior
 # shell/ports plus its own adjacent structure remain, rather than opening
 # a wall to make an impossible photographic vantage.
 def keep(o):
  rr=o.get('LII_room','');kind=o.get('LII_kind','')
  return rr==id or (id=='S_Steering' and o.name.startswith('Rudder_Stock_Blade')) or kind=='shell' or (kind in ('deck','ceiling','wall','glazing','door') and o.get('LII_deck')==r['deck']) or kind=='superstructure' or (kind=='stair' and r['kind']=='stairhall')
 visibility(keep)
 if r['kind'].startswith('cabin'):
  pos=((x0+x1)/2+.15,y0+.16 if r['door_wall']=='y0' else y1-.16,z+1.50);target=(x0+.55,y1-.35 if r['door_wall']=='y0' else y0+.35,z+1.05);lens=19
 elif r['kind']=='stairhall':
  visibility(lambda o:o.get('LII_kind') in ('stair','rail','skylight','deck','glazing') or o.get('LII_room') in ('M_Entrance','S_Stair','P_Stair'))
  pos=(-5.25,-4.80,10.42);target=(-.5,.0,12.0);lens=23
 else:pos,target=room_camera(r);lens=21 if r['kind']=='bath' else 24
 # The stair-hall visibility above deliberately omits its enclosure walls.
 # Keep that diagnostic distinction in the renderer/registry, not just prose.
 stair_diagnostic=r['kind']=='stairhall'
 title=r['name']+' — wall-removed stair diagnostic' if stair_diagnostic else r['name']
 render(name or id,title,pos,target,lens,interior=(x0,x1,y0,y1,z,top),res=(1600,1000),cutaway=stair_diagnostic,room_id=id)


def exterior():
 # Internal lower-deck details cannot be visible through opaque shell. Their
 # geometry is retained in source and in dedicated interior evidence.
 visibility(lambda o: o.get('LII_kind')!='furniture' and not(o.get('LII_deck') in ('orlop','lower','main','machinery') and o.get('LII_kind') in ('finish','wall','door','ceiling','sign')))
 render('Exterior_Bow_Port','SS Aurelian — port bow, actual new geometry',(195,155,88),(-2,0,12),55,res=(2400,1400))
 render('Exterior_Stern_Starboard','Starboard after quarter',(-195,-146,72),(-7,0,11),55,res=(2400,1400))
 render('Exterior_Broadside_Port','Port broadside / 166m envelope',(0,205,51),(0,0,14),ortho=182,res=(2600,1050))
 render('Exterior_Overhead','Upper decks / rig / boat sockets',(119,-161,195),(0,0,12),52,res=(2400,1600))


def engineering():
 visibility(lambda o:o.get('LII_room')=='E_Engine' or o.get('LII_kind') in ('engine','mover','pipe','platform','auxiliary','shaft_support','bulkhead','structure','shell','deck','superstructure') and not o.name.startswith('Gangway') and o.name!='HelmWheel')
 render('Machinery_Engine_Aisle','Engine working aisle — inboard view, no walls removed',(-27.3,-4.4,3.25),(-16.0,-1.2,5.5),26,interior=(-28,-9.7,-5.1,5.1,1.6,11.7),res=(1800,1200),room_id='E_Engine')
 visibility(lambda o:o.get('LII_kind') in ('engine','mover','pipe','platform','auxiliary','shaft_support','steering') and not o.name.startswith('Gangway') and o.name!='HelmWheel')
 render('Engineering_Engine_Cutaway','Triple expansion, connected moving parts — isolated technical cutaway',(-33,-18,12),(-17,0,5.6),48,res=(2200,1500),cutaway=True)
 visibility(lambda o:o.get('LII_kind') in ('engine','mover','pipe','platform') and not o.name.startswith('Gangway') and o.name!='HelmWheel')
 render('Engineering_Crossheads_ValveGear','Three-throw crank / exact slider-crank — technical close-up',(-24.7,-4.6,5.5),(-18.4,0,5.1),30,interior=(-28,-9,-5,5,1.6,10.8),res=(1800,1200),cutaway=True)
 # Keep the real tank top, overhead deck and framing in working-aisle
 # images. Omitting them would be a cutaway, not a closed stokehold photo.
 visibility(lambda o:o.get('LII_kind') in ('boiler','pipe','equipment','bulkhead','shell','deck','structure','superstructure') and o.get('LII_deck')!='saloon')
 render('Machinery_Stokehold','Middle stokehold, furnace-side actual working aisle',(10.0,-5.8,3.3),(14.0,1.0,3.9),26,interior=(9.4,21.8,-6.9,6.9,1.6,8.6),res=(1800,1200),room_id='E_Boilers_M')
 for rid,x,nm in [('E_Boilers_A',3.0,'After'),('E_Boilers_F',28.0,'Forward')]:
  render('Machinery_Stokehold_'+nm,nm+' stokehold — connected boiler row',(x-5.5,-5.8,3.3),(x-1.5,1.0,3.9),26,interior=(x-5.8,x+6.0,-6.9,6.9,1.6,8.6),res=(1800,1200),room_id=rid)
 visibility(lambda o:o.get('LII_kind') in ('shaft_support','mover','shell','structure') and (not o.get('LII_mover') or o.get('LII_mover') in ('shaft','rudder')))
 render('Engineering_Stern_Aperture','Shaft / pitched screw / separate rudder, dry inspection',(-88.5,-11,6.2),(-77.4,0,3.3),47,res=(2000,1400),cutaway=True)
 visibility(lambda o:o.get('LII_room')=='E_Alley' or o.name=='TankTop' or o.get('LII_kind')=='shell' or o.get('LII_mover')=='shaft' or (o.get('LII_kind')=='deck' and o.get('LII_deck') in ('lower','orlop')))
 render('Machinery_Shaft_Alley','Shaft alley and actual bearing line',(-31.5,1.1,3.75),(-62,1.05,3.1),24,interior=(-70,-28,-1.5,1.5,1.6,4.7),res=(1800,1100),room_id='E_Alley')
 roomshot('S_Steering','Machinery_Steam_Steering')
 # Auxiliary rooms use actual geometric plant assembly, not generic furniture.
 visibility(lambda o:o.get('LII_kind') in ('auxiliary','pipe','deck','shell','bulkhead','structure','wall','engine','boiler','platform','shaft_support','mover') and o.get('LII_deck') not in ('main','saloon','promenade','boat','bridge') and not o.name.startswith('Gangway') and o.name!='HelmWheel')
 render('Machinery_Dynamos_And_Switchboard','Period electrical room / dynamos and inboard-facing slate switchboards',(-8.9,-2.9,3.55),(-5.3,-4.5,3.30),26,interior=(-9.4,-3.4,-5.5,-2.65,1.6,5.1),res=(1800,1100),room_id='E_Dynamos')
 render('Machinery_Feed_Pumps','Open-crosshead feed pumps / detailed hotwell and separately ported circulating pump',(-8.9,2.8,3.60),(-5.8,4.15,2.75),24,interior=(-9.4,-3.4,2.65,5.5,1.6,5.1),res=(1800,1100),room_id='E_Pumps')


def interiors(group=None):
 for id,nm in [('S_Dining','Interior_Dining_First'),('P_Library','Interior_Library'),('P_Smoking','Interior_Smoking'),('S_Music','Interior_Music'),('P_Writing','Interior_Writing'),('M_Entrance','Interior_Grand_Stair'),('S_SecondDining','Interior_Dining_Second'),('P_SecondLounge','Interior_Second_Lounge'),('A030','Interior_Cabin_First'),('C006','Interior_Cabin_Second'),('M_ForwardThird','Interior_Third_Class'),('O_CrewP','Interior_Crew'),('B_Captain','Interior_Captain'),('B_Officer_1','Interior_Officer'),('N_Wheelhouse','Interior_Wheelhouse'),('B_Chart','Interior_Chart_Signals'),('S_Galley','Interior_Galley'),('S_Bakery','Interior_Bakery'),('S_Pantry','Interior_Pantry'),('S_Bath_P','Interior_Bath'),('S_Bath_S','Interior_Lavatory'),('P_Hospital','Interior_Hospital'),('S_Purser','Interior_Purser'),('S_Mail','Interior_Mail'),('P_Barber','Interior_Barber'),('O_Hold','Interior_Cargo'),('S_ColdStore','Interior_Cold_Store'),('P_Bar','Interior_Bar')]:
  r=next((r for r in ROOMS if r['id']==id),None)
  if not r:continue
  cls='accommodation' if r['kind'].startswith(('cabin','dorm')) else 'public' if r['kind'] in ('dining','library','smoking','music','writing','stairhall','dining_second','lounge_second') else 'service'
  if group is None or group==cls:roomshot(id,nm)


def plans():
 visibility(lambda o:o.get('LII_kind') in ('structure','bulkhead'))
 render('Engineering_Structural_Skeleton','Actual keel / framing / beams / bulkheads — underbody diagnostic fill, shell/tank top/furniture removed',(40,140,-42),(0,0,5),ortho=178,res=(2400,1100),cutaway=True)
 for dk,z in DECKS.items():
  visibility(lambda o: (o.get('LII_deck')==dk and o.get('LII_kind') not in ('ceiling','sign','glazing')) or (dk=='orlop' and o.get('LII_kind') in ('engine','boiler','shaft_support','auxiliary')))
  # Ceilings and upper decks deliberately omitted, explicitly technical.
  if dk=='bridge':render('Plan_'+dk,'Bridge — focused actual geometry deck cutaway',(37.4,0,120),(37.4,0,20),ortho=16,res=(1800,1200),cutaway=True)
  else:render('Plan_'+dk,dk.title()+' — actual geometry deck cutaway',(0,0,120),(0,0,0),ortho=175,res=(2600,800),cutaway=True)

def room_audits():
 original_samples=sc.cycles.samples;sc.cycles.samples=int(os.getenv('LII_AUDIT_SAMPLES','4'))
 for r in ROOMS:
  rid=r['id'];x0,x1,y0,y1=r['x0'],r['x1'],r['y0'],r['y1'];z=r['z'];length=x1-x0;width=y1-y0;cx=(x0+x1)/2;cy=(y0+y1)/2
  if r['kind']=='machinery':
   def keep(o):
    return o.name=='TankTop' or o.get('LII_kind') in ('engine','boiler','mover','pipe','platform','auxiliary','shaft_support','equipment','bulkhead') and not o.name.startswith('Gangway') and o.name!='HelmWheel'
  else:
   def keep(o):
    return (o.get('LII_room')==rid and o.get('LII_kind')!='ceiling') or (rid=='S_Steering' and o.name.startswith('Rudder_Stock_Blade')) or (r['kind']=='stairhall' and o.get('LII_kind')=='stair')
  visibility(keep)
  pos=(cx-length*.08,cy-width*.32,z+max(7.,max(length,width)*1.25));target=(cx,cy,z+.55)
  render('rooms/Room_'+rid,rid+' · '+r['name']+' — roof-off diagnostic',pos,target,ortho=max(length,width*1.25)*1.15,interior=(x0,x1,y0,y1,z,r['top']),res=(640,480),cutaway=True,room_id=rid)
 sc.cycles.samples=original_samples

if mode=='preview':
 exterior_view=lambda o:o.get('LII_kind')!='furniture' and not(o.get('LII_deck') in ('orlop','lower','main','machinery') and o.get('LII_kind') in ('finish','wall','door','ceiling','sign'))
 visibility(exterior_view);render('Preview_Exterior','New reconstruction — work-in-progress actual geometry',(186,-147,79),(0,0,12),53,res=(1500,900))
 roomshot('S_Dining','Preview_Dining');roomshot('P_Library','Preview_Library');roomshot('A030','Preview_Cabin')
elif mode=='refinement':
 # Replace the old unregistered wheelhouse-framing precheck with a real,
 # current-source supplementary view; preserve the original in history.
 roomshot('N_Wheelhouse','Detail_Wheelhouse_Framing')
 interiors('public')
 for rid,nm in [('A030','Interior_Cabin_First'),('C006','Interior_Cabin_Second'),('B_Captain','Interior_Captain'),('B_Officer_1','Interior_Officer'),('S_Galley','Interior_Galley'),('S_Bakery','Interior_Bakery'),('S_Pantry','Interior_Pantry'),('P_Hospital','Interior_Hospital'),('P_Barber','Interior_Barber'),('O_CrewP','Interior_Crew'),('N_Wheelhouse','Interior_Wheelhouse')]:roomshot(rid,nm)
 exterior()
 visibility(lambda o:o.get('LII_kind')!='furniture' and not(o.get('LII_deck') in ('orlop','lower','main','machinery') and o.get('LII_kind') in ('finish','wall','door','ceiling','sign')))
 render('Detail_Exterior_Bridge','Revised wheelhouse roof, eaves, wing fittings and officer deckhouses',(56,-27,32),(30,0,20),45,res=(1120,700))
 render('Detail_Exterior_Promenade','Revised after deckhouse roof, mast collar and outboard stay landings',(-57,-23,26),(-35,0,17.6),48,res=(1120,700))
 render('Detail_Promenade_Bench','Promenade slat bench and sheltered weather planking — actual eye-level view',(-34,-6.6,16.0),(-31,-8.0,14.9),40,res=(1120,700))
 render('Detail_Mast_Ladder','Foremast climbing ladder — continuous rails, rungs and pole-clamp stand-offs',(62.0,-3.5,17.0),(66.9,0,16.3),43,res=(1120,700))
 render('Detail_Funnel_Ladder','After funnel ladder — actual side rails and shell stand-off brackets',(8.8,-4.2,21.7),(6.228,-.15,21.0),65,res=(1120,700))
 render('Detail_Lifebuoy_Hook','Boat-deck lifebuoy — actual bracket hooks over the top rail',(-35.0,-9.7,18.6),(-37.0,-7.416,17.9),55,res=(1120,700))
elif mode=='exterior':exterior()
elif mode=='interiors':interiors()
elif mode in ('public','accommodation','service'):interiors(mode)
elif mode=='engineering':engineering()
elif mode=='plans':plans()
elif mode=='rooms':room_audits()
elif mode in ('all','complete'):
 exterior();interiors();engineering();plans()
 if mode=='complete':room_audits()
else:roomshot(mode)
print('ACTUAL MODEL EVIDENCE DONE',len(REGISTER),'new views /',len(PERSISTED),'current-source registered views',flush=True)
