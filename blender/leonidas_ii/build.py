"""Reproducible LEONIDAS-II build. Blender 4.2 LTS, native metres.
  LD_LIBRARY_PATH=/var/tmp/blender/lib /var/tmp/blender/blender -b -t 2 \
    -P blender/leonidas_ii/build.py

Default output keeps legacy models untouched for an honest before/after.
All generated files live in the repository's existing directories.
"""
import sys,os,json,time,hashlib
from pathlib import Path
import bpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT)]
from meshkit import *
import structure,interiors,machinery,topsides
from optimize import merge_proxies
from shipdesign import leonidas_ii as spec

start=time.time();GAME=os.getenv('LII_GAME_DETAIL')=='1'
GEN=ROOT/'exports'/'leonidas_ii'/'build'
if GAME:GEN.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1.;sc['Vessel']='SS Aurelian';sc['Period']=1889;sc['Fictional']=True;sc['LEONIDAS_II']='New reconstruction, metric +X bow / +Y port / +Z baseline'
materials()
for label,fn in [('Hull',structure.build_hull),('Structure',structure.build_frames),('Decks',structure.build_decks),('Hull collision',structure.hull_collision_boundaries),('Stairs',structure.build_stairs),('Interiors',interiors.build),('Machinery',machinery.build),('Topsides',topsides.build)]:
 print('START',label,round(time.time()-start,1),flush=True);fn();print('DONE',label,round(time.time()-start,1),flush=True)
# Native metric locators for exact interaction names; their exported location
# is also in build_data.json and in the generated Studio module.
for a in spec.ATTACHMENTS:
 ob=bpy.data.objects.new(a['id'],None);collection('Locators').objects.link(ob);ob.location=a['position'];ob.empty_display_type='SPHERE';ob.empty_display_size=.15;ob['kind']=a['kind']
# Add explicit inventory entries for engineering spaces handled componentwise.
for r in spec.ROOMS:
 if any(v['id']==r['id'] for v in interiors.ROOM_REPORT):continue
 if r['kind']=='machinery':
  obs=[o for o in sc.objects if o.type=='MESH' and o.get('LII_room')==r['id']]
  inventories={'E_Engine':'Cast bedplate, bearing blocks, three graduated cylinders, A-frame standards, crosshead guides, three-throw crankshaft, piston/conrods, separate eccentric/valve links, control gauges, connected receivers and working platforms.','E_Boilers_A':'Three single-ended Scotch boilers, four dished furnace doors each, ashdoors, gauges, water columns, stay bolts, saddles, safety valves, connected steam/feed/flue branches, coal shutters and fire tools.','E_Boilers_M':'Three single-ended Scotch boilers with full furnace fittings, connected steam/feed/flue branches and a clear stoke aisle.','E_Boilers_F':'Three single-ended Scotch boilers, connected forward-funnel uptake, feed/steam headers and furnace fittings.','E_Dynamos':'Two period dynamo housings, copper windings/commutators, slate switchboards, analog instruments, knife switches and workshop bench/vice.','E_Pumps':'Reciprocating feed pumps, hotwell and sea circulation/feed/condensate connections.','E_Alley':'Aligned shaft segments/couplings, thrust collars/bearings, stern tube, guard rails, lamps, service-steam main and elevated accommodation-side access.'}
  interiors.ROOM_REPORT.append(dict(id=r['id'],name=r['name'],kind='machinery',deck='machinery',bounds=spec.rect(r),z=r['z'],top=r['top'],floor_area_m2=round((r['x1']-r['x0'])*(r['y1']-r['y0']),2),inventory=inventories[r['id']],triangles=sum(len(o.data.polygons)*2 for o in obs)))
# Neutral studio world; delivered source includes no water plane that hides
# the underwater stern. Render scripts add actual stage lighting separately.
world=bpy.data.worlds.new('Aurelian Neutral World');sc.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.20,.23,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=100;sc.view_settings.view_transform='AgX'
# Convenient starting view, no nonportable absolute texture path dependency.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_distance=120
out=GEN if GAME else ROOT/'models'/'leonidas_ii';out.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/('Aurelian_Game_Source.blend' if GAME else 'Aurelian_1889.blend')),compress=True)
# Recompute the ACTUAL post-modifier geometry, not preliminary estimates.
objects=[]
for ob in sc.objects:
 if ob.type!='MESH':continue
 me=ob.data;me.calc_loop_triangles();bb=[tuple(ob.matrix_world@Vector(c)) for c in ob.bound_box]
 objects.append(dict(name=ob.name,kind=ob.get('LII_kind'),deck=ob.get('LII_deck'),room=ob.get('LII_room'),mover=ob.get('LII_mover'),triangles=len(me.loop_triangles),vertices=len(me.vertices),uv_layers=len(me.uv_layers),materials=[m.name for m in me.materials],bounds={'min':[min(c[k] for c in bb) for k in range(3)],'max':[max(c[k] for c in bb) for k in range(3)]}))
PROXIES[:]=merge_proxies(PROXIES)
data=dict(schema='victoria.leonidas-ii.build/2.0',source='models/leonidas_ii/Aurelian_1889.blend',units='metres, +X bow, +Y port, +Z baseline',dimensions={'loa':166.,'beam':18.4,'draft':6.5},objects=objects,rooms=interiors.ROOM_REPORT,doors=interiors.DOORS,movers=MOVERS,proxies=PROXIES,lights=LIGHTS,seats=SEATS,fixtures=FIXTURES,fixture_mounts=FIXTURE_MOUNTS,rigging_lines=RIGGING_LINES,rigging_feet=RIGGING_FEET,access_ladders=ACCESS_LADDERS,detail_revision='Purpose-specific plans, supported fixtures and weather architecture',source_files_sha256={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(HERE.glob('*.py')) if f.name not in ('render.py','render_crew_details.py','audit_structure.py')},attachments=spec.ATTACHMENTS,boat_mounts=spec.BOAT_MOUNTS,pipe_network=machinery.CONNECTIONS,counts={'mesh_objects':len(objects),'triangles':sum(o['triangles'] for o in objects),'physical_compartments':len(interiors.ROOM_REPORT),'actual_first_berths':sum(r.get('actual_berths',0) for r in interiors.ROOM_REPORT if r['kind']=='cabin_first'),'actual_second_berths':sum(r.get('actual_berths',0) for r in interiors.ROOM_REPORT if r['kind']=='cabin_second'),'actual_third_berths':sum(r.get('actual_berths',0) for r in interiors.ROOM_REPORT if r['kind']=='dorm_third'),'actual_crew_berths':sum(r.get('actual_berths',0) for r in interiors.ROOM_REPORT if r['kind'] in ('dorm_crew','cabin_officer','cabin_captain'))},limitations=['No Studio import/playtest/benchmark yet.','Design hydrostatics are not a stability/strength assessment.','Full original nominal passenger capacity not asserted; actual built berths are counted.','Three host craft mounts, not a certified complete lifesaving inventory.'])
p=GEN if GAME else ROOT/'exports'/'leonidas_ii';p.mkdir(parents=True,exist_ok=True);(p/'build_data.json').write_text(json.dumps(data,indent=2))
if not GAME:(ROOT/'docs'/'leonidas_ii'/'ROOM_INVENTORY.json').write_text(json.dumps(interiors.ROOM_REPORT,indent=2))
print('LEONIDAS-II BUILD',json.dumps(data['counts']),round(time.time()-start,1),'seconds',flush=True)
