"""Fresh roof-off replacements for three visually rejected upper-deck plans.

The original plans excluded ceilings but still retained separate weather-roof
objects. Actual pixel inspection caught the bridge completely hidden and the
boat/promenade plans partly obscured. Only the explicit source roof objects
below are hidden; all remaining original deck meshes are retained. No mesh,
material, MASTER file or common-renderer source is edited or saved.

Run serially after Blender/OIDN has finished, then denoise the root register:
  blender -b models/leonidas_ii/Aurelian_1889.blend -t 2 \
    --python-exit-code 1 -P tools/render_leonidas_plan_rechecks.py
Old pixels are never assigned this driver's hash. Reopen every fresh final.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sys
import bpy
ROOT=Path(__file__).resolve().parents[1];COMMON=ROOT/'blender/leonidas_ii/render.py'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
os.environ.pop('LII_RENDER_SUBDIR',None)
requested=os.environ.get('LII_ONLY');os.environ['LII_ONLY']='__INITIALISE_WITHOUT_RENDERING__'
sys.argv=[str(COMMON),'--','plans','100']
spec=importlib.util.spec_from_file_location('leonidas_roof_off_plan_common',COMMON)
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
if requested:os.environ['LII_ONLY']=requested
else:os.environ.pop('LII_ONLY',None)
driver=str(Path(__file__).relative_to(ROOT));driver_hash=H(Path(__file__))
ROOFS={
 'promenade':{'Hospital_WeatherRoof'},
 'boat':{'After_DeckCabin_Continuous_CrownedRoof','Officers_Continuous_CrownedRoof','Chart_Room_CrownedRoof'},
 'bridge':{'Wheelhouse_CrownedRoof'},
}
names={'Plan_'+deck for deck in ROOFS}
e.PERSISTED=[r for r in e.PERSISTED if Path(r['file']).stem not in names or r.get('detail_driver_sha256')==driver_hash]
for deck,omitted in ROOFS.items():
 name='Plan_'+deck
 if requested and name not in requested.split(','):continue
 for roof in omitted:
  assert roof in bpy.data.objects,('Expected separate actual source roof missing',roof)
  ob=bpy.data.objects[roof]
  assert ob.type=='MESH' and ob.get('LII_deck')==deck and ob.get('LII_kind')=='superstructure',('Unexpected roof source binding',roof)
 e.visibility(lambda o:o.get('LII_deck')==deck and o.get('LII_kind') not in ('ceiling','sign','glazing') and o.name not in omitted)
 expected_rooms={r['id'] for r in e.ROOMS if r['deck']==deck}
 visible_rooms={o.get('LII_room') for o in e.sc.objects if o.type=='MESH' and not o.hide_render and o.get('LII_kind')=='furniture'}
 assert visible_rooms==expected_rooms,('Roof-off plan must retain every original room furnishing mesh',deck,sorted(expected_rooms-visible_rooms))
 assert all(bpy.data.objects[n].hide_render for n in omitted)
 if deck=='bridge':
  camera=(37.4,0,120);target=(37.4,0,20);scale=16;res=(1800,1200)
 else:
  camera=(0,0,120);target=(0,0,0);scale=175;res=(2600,800)
 e.render(name,deck.title()+' deck — actual geometry, weather roofs and ceilings omitted',camera,target,ortho=scale,res=res,cutaway=True)
 for row in e.PERSISTED:
  if Path(row['file']).stem==name:
   row.update(detail_driver=driver,detail_driver_sha256=driver_hash,short_title=deck.title()+' Deck — Roof Off',omitted_weather_roof_objects=sorted(omitted),roof_off_furniture_rooms=sorted(visible_rooms),source_mesh_geometry_edited=False,diagnostic_limit='True roof-off deck diagnostic: only explicitly named separate weather-roof objects, ceilings, signs and glazing are omitted. Original deck, room walls and every room furniture mesh are retained. Not a photograph, hidden-contact proof or continuous avatar-access certification.')
 e.REGFILE.write_text(json.dumps(e.PERSISTED,indent=2));(e.OUT/'camera_register.json').write_text(json.dumps(e.REGISTER,indent=2))
 print('ROOF-OFF PLAN SOURCE INVENTORY',deck,len(visible_rooms),'furnished rooms; explicit omitted roofs',','.join(sorted(omitted)),flush=True)
print('THREE ROOF-OFF PLAN RECHECKS RENDERED; final denoising and individual pixel inspection remain required.',flush=True)
