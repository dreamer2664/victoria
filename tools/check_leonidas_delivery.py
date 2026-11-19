"""Delivered-package byte/provenance checks, never fresh geometry/Studio approval.
Run after packaging; --require-evidence/--require-reviewed require current exact
images and their independently recorded individual observations. The default
checks retained MASTER, actual kit bytes, original frozen exporter receipt and
all canonical audit identities even when excluded GAME rebuild scratch is gone.
--require-saved-sources additionally requires the actual saved GAME .blend/data;
without them it MUST fail. No geometry audit or visual review is rerun here.
"""
from pathlib import Path
import sys,json,hashlib,tarfile,xml.etree.ElementTree as ET,subprocess,collections
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS,DECKS
from tools.make_leonidas_render_gallery import expected_all,IDENTITY_KEYS
DOC=ROOT/'docs/leonidas_ii';EX=ROOT/'exports/leonidas_ii';ROB=ROOT/'roblox/leonidas_ii';REND=ROOT/'renders/leonidas_ii'
checks=[]
def check(name,ok,detail=''):
 checks.append(dict(check=name,status='PASS' if ok else 'FAIL',detail=detail));print(checks[-1]['status'],name,str(detail)[:160])
def unverified(name,detail):checks.append(dict(check=name,status='UNVERIFIED',detail=detail));print('UNVERIFIED',name)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def load(file):return json.loads(file.read_text())
D=load(EX/'build_data.json');M=load(EX/'game_manifest.json');K=load(EX/'IMPORT_KIT_MANIFEST.json');master=ROOT/'models/leonidas_ii/Aurelian_1889.blend';source_hash=sha(master.read_bytes())
check('Master / GAME / kit source identity',source_hash==M['source_sha256']==K['source_sha256'],source_hash)
check('Export uses the current exporter source',M.get('exporter_sha256')==sha((ROOT/'blender/leonidas_ii/export_game.py').read_bytes()))
check('Master inventory / physical-space inventory',len(D['rooms'])==len(ROOMS)==D['counts']['physical_compartments'],len(D['rooms']))
check('Placed triangles and visual-node totals agree',M['counts']['placed_triangles']==K['placed_triangles'] and M['counts']['mesh_nodes']==K['visual_nodes'])
visual=[n for n in M['nodes'] if n['kind']!='calibration'];unique={n['mesh']:n['triangles'] for n in visual}
check('Unique/reused GAME counts exclude calibration',M['counts']['unique_meshes']==len(unique) and M['counts']['reused_nodes']==len(visual)-len(unique) and M['counts']['unique_triangles']==sum(unique.values()),M['counts'])
FILES={'Aurelian_Install':'Aurelian_Install.luau','Aurelian_Runtime':'Aurelian_Runtime.luau','Aurelian_Data':'Aurelian_Data.luau','Aurelian_StudioAcceptance':'Aurelian_StudioAcceptance.luau','Aurelian_Server':'Aurelian_Server.server.luau','Aurelian_Client':'Aurelian_Client.client.luau'}
package=ROB/'Aurelian_Control_Package.rbxmx';xml=ET.fromstring(package.read_bytes());seen={}
for item in xml.iter('Item'):
 props=item.find('Properties')
 if props is None:continue
 name=props.find("string[@name='Name']");text=props.find("ProtectedString[@name='Source']")
 if name is not None and text is not None:seen[name.text]=text.text
check('RBXMX has all six exact current Luau sources',set(seen)==set(FILES) and all(seen.get(n)==(ROB/f).read_text() for n,f in FILES.items()),{n:sha((ROB/f).read_bytes()) for n,f in FILES.items()})
archive=EX/'Aurelian_Roblox_Import_Kit.tar.xz';entries={};batch_by_file={b['file']:b for b in K['batches']};script_bytes=None;kit_manifest_bytes=None;game_manifest_bytes=None;install_doc_bytes=None;input_receipt_bytes=None
with tarfile.open(archive,'r:xz') as t:
 for member in t:
  if not member.isfile():continue
  rel=Path(member.name).relative_to('Aurelian_Import_Kit');blob=t.extractfile(member).read();entries[str(rel)]=dict(bytes=len(blob),sha256=sha(blob))
  if str(rel) in batch_by_file:
   b=batch_by_file[str(rel)];check('Archive GLB hash '+str(rel),sha(blob)==b['sha256'] and len(blob)==b['bytes'])
  if str(rel)==package.name:script_bytes=blob
  elif str(rel)=='IMPORT_KIT_MANIFEST.json':kit_manifest_bytes=blob
  elif str(rel)=='game_manifest.json':game_manifest_bytes=blob
  elif str(rel)=='ROBLOX_INSTALL_AND_TEST.md':install_doc_bytes=blob
  elif str(rel)=='EXPORT_INPUT_IDENTITY.json':input_receipt_bytes=blob
check('Archive regional GLB set',{p for p in entries if p.endswith('.glb')}==set(batch_by_file),len(batch_by_file))
check('Archive control package is current',script_bytes==package.read_bytes())
check('Archive manifests are current',kit_manifest_bytes==(EX/'IMPORT_KIT_MANIFEST.json').read_bytes() and game_manifest_bytes==(EX/'game_manifest.json').read_bytes())
check('Archive installation document is current',install_doc_bytes==(DOC/'ROBLOX_INSTALL_AND_TEST.md').read_bytes())
receipt=DOC/'EXPORT_INPUT_IDENTITY.json'
check('Archive frozen-export input receipt is current',receipt.is_file() and input_receipt_bytes==receipt.read_bytes() and K.get('export_input_receipt_sha256')==sha(receipt.read_bytes()))
require_saved_sources='--require-saved-sources' in sys.argv
micro_runner=ROOT/'tools/check_leonidas_micro_delivery.py';micro_run=subprocess.run([sys.executable,str(micro_runner),'--require-saved-sources' if require_saved_sources else '--delivered-package'],cwd=ROOT,capture_output=True,text=True)
micro_file=DOC/'MICRO_DELIVERY_VALIDATION.json';micro=load(micro_file) if micro_file.exists() else {}
expected_mode='REQUIRE_ACTUAL_SAVED_SOURCES' if require_saved_sources else 'DELIVERED_FROZEN_EXPORT_AND_CANONICAL_AUDIT_BINDINGS'
check('All six both-quality canonical audit bindings and original frozen export identity',micro_run.returncode==0 and micro.get('source_sha256')==source_hash and micro.get('validator_sha256')==sha(micro_runner.read_bytes()) and micro.get('mode')==expected_mode and micro.get('summary',{}).get('PASS',0)>=42 and not micro.get('summary',{}).get('FAIL'),dict(summary=micro.get('summary'),mode=micro.get('mode'),receipt_only_absent_inputs=micro.get('receipt_only_absent_inputs'),diagnostics=(micro_run.stdout+micro_run.stderr)[-1800:] if micro_run.returncode else ''))
binding_runner=ROOT/'tools/test_leonidas_delivery_bindings.py';binding_run=subprocess.run([sys.executable,str(binding_runner)],cwd=ROOT,capture_output=True,text=True)
binding_file=DOC/'DELIVERY_BINDING_TESTS.json';binding_tests=load(binding_file) if binding_file.is_file() else {};binding_rows=binding_tests.get('tests',[])
check('Delivery/fresh-source mode distinction and isolated tamper regressions',binding_run.returncode==0 and binding_tests.get('runner_sha256')==sha(binding_runner.read_bytes()) and binding_tests.get('checker_sha256')==sha(micro_runner.read_bytes()) and binding_tests.get('source_sha256')==source_hash and binding_tests.get('export_input_receipt_sha256')==sha(receipt.read_bytes()) and binding_tests.get('original_inputs_unchanged') is True and len(binding_rows)>=52 and len({v.get('test') for v in binding_rows})==len(binding_rows) and all(v.get('status')=='PASS' for v in binding_rows) and not binding_tests.get('summary',{}).get('FAIL'),dict(summary=binding_tests.get('summary'),diagnostics=(binding_run.stdout+binding_run.stderr)[-1800:] if binding_run.returncode else ''))
check('Archive source maps and packed map present',all('Textures/Aurelian_'+n+'.png' in entries for n in ('basecolor','roughness','metallic','normal','emission','signs','metalrough')))
compile_file=DOC/'LUAU_COMPILE.json';compiled=load(compile_file) if compile_file.exists() else {};compile_rows=compiled.get('files',[]);runner_hash=sha((ROOT/'tools/test_leonidas_runtime.py').read_bytes())
check('All six exact current Luau sources compile; runner identity',len(compile_rows)==len(FILES) and {r.get('file') for r in compile_rows}=={'roblox/leonidas_ii/'+f for f in FILES.values()} and compiled.get('runner_sha256')==runner_hash and all(r.get('status')=='PASS' and r.get('exit_code')==0 and r.get('sha256')==sha((ROOT/r['file']).read_bytes()) for r in compile_rows),compiled.get('summary'))
logic=load(DOC/'RUNTIME_LOGIC_TESTS.json')
check('Runtime logic report uses exact runtime/data/runner/harness; at least 30 passing tests',logic.get('exit_code')==0 and logic.get('runtime_sha256')==sha((ROB/'Aurelian_Runtime.luau').read_bytes()) and logic.get('data_sha256')==sha((ROB/'Aurelian_Data.luau').read_bytes()) and logic.get('runner_sha256')==runner_hash and logic.get('harness_sha256')==sha((ROOT/'tools/leonidas_runtime_harness.luau').read_bytes()) and len(logic.get('tests',[]))>=30 and len({r.get('test') for r in logic.get('tests',[])})==len(logic.get('tests',[])) and all(r.get('status')=='PASS' for r in logic.get('tests',[])),len(logic.get('tests',[])))
gltf=load(DOC/'GLTF_VALIDATION.json')['rows']
check('Khronos report covers the actual archived GLBs',len(gltf)==len(batch_by_file) and all(r.get('sha256')==batch_by_file.get(r['file'],{}).get('sha256') and 'sha256' in r for r in gltf))
check('Khronos errors/warnings',all(r['errors']==r['warnings']==0 for r in gltf),{k:sum(r[k] for r in gltf) for k in ('errors','warnings','infos')})
component_file=DOC/'COMPONENT_VOLUME_AUDIT.json'
if component_file.exists():
 a=load(component_file);s=a['summary']
 check('Independent component audit covers current export/archive',a.get('source_sha256')==source_hash and a.get('auditor_sha256')==sha((ROOT/'tools/audit_leonidas_volumes.py').read_bytes()) and a.get('game_manifest_sha256')==sha((EX/'game_manifest.json').read_bytes()) and a.get('kit_manifest_sha256')==sha((EX/'IMPORT_KIT_MANIFEST.json').read_bytes()) and {r['file']:r['sha256'] for r in a.get('regional_files',[])}=={b['file']:b['sha256'] for b in K['batches']} and s['unique_visual_meshes']==M['counts']['unique_meshes'] and s['triangles']==M['counts']['unique_triangles'])
 gates=('negative_components','near_zero_components','normal_disagreement_triangles','opposing_normal_corners','degenerate_area_triangles','odd_unpaired_welded_edges','inconsistent_edge_winding','collapsed_triangle_edges')
 check('Independent exported volume / winding / normal / area gates',all(s.get(k,-1)==0 for k in gates),s)
else:unverified('Independent exported volume / winding / normal / area gates','Run tools/audit_leonidas_volumes.py against current regional files.')
structural=DOC/'STRUCTURE_GEOMETRY_AUDIT.json'
s=load(structural) if structural.exists() else {}
check('Actual structural regression audit matches master and auditor',s.get('source_sha256')==source_hash and s.get('auditor_sha256')==sha((ROOT/'blender/leonidas_ii/audit_structure.py').read_bytes()) and s.get('hull_spec_sha256')==sha((ROOT/'shipdesign/leonidas_ii.py').read_bytes()))
check('Internal structure / stern contacts / screw sweep regression gates',len(s.get('checks',[]))==3 and all(c.get('status')=='PASS' for c in s.get('checks',[])),s.get('summary'))
stair_rows=[]
for quality in ('MASTER','GAME'):
 p=DOC/f'STAIR_JOINERY_{quality}.json';a=load(p) if p.exists() else {};z=a.get('summary',{})
 receipt_data=load(DOC/'EXPORT_INPUT_IDENTITY.json') if (DOC/'EXPORT_INPUT_IDENTITY.json').exists() else {};identity=receipt_data.get('inputs',{}).get('master' if quality=='MASTER' else 'game',{})
 okay=a.get('status')=='SAVED_SOURCE_BOUND_SCREEN' and a.get('quality')==quality and a.get('source_sha256')==identity.get('sha256') and a.get('build_data_sha256')==receipt_data.get('inputs',{}).get('master_data' if quality=='MASTER' else 'game_data',{}).get('sha256') and a.get('generator_sha256')==receipt_data.get('generator_sha256') and len(a.get('rows',[]))==13 and a.get('auditor_sha256')==sha((ROOT/'tools/audit_leonidas_stair_joinery.py').read_bytes()) and a.get('convex_plane_tester_sha256')==sha((ROOT/'blender/leonidas_ii/test_micro_contacts.py').read_bytes()) and z.get('stairs')==13 and z.get('sides')==26 and z.get('saved_geometry_mismatches')==z.get('exposed_overlap_pairs')==z.get('flags')==0 and z.get('restored_old_full_width_riser_negative_detected') is True
 stair_rows.append(dict(quality=quality,okay=okay,summary=z))
check('Both saved stair meshes match authored faces and have no exposed side overlap',all(r['okay'] for r in stair_rows),stair_rows)
detail_file=DOC/'DETAIL_GEOMETRY_AUDIT.json';detail=load(detail_file) if detail_file.exists() else {}
check('Actual detail/contact audit matches source/data/auditor',detail.get('schema')=='victoria.leonidas-ii.detail-geometry-audit/1.2' and detail.get('source_sha256')==source_hash and detail.get('build_data_sha256')==sha((EX/'build_data.json').read_bytes()) and detail.get('auditor_sha256')==sha((ROOT/'blender/leonidas_ii/audit_details.py').read_bytes()) and detail.get('ladder_auditor_sha256')==sha((ROOT/'blender/leonidas_ii/audit_ladders.py').read_bytes()))
check('Fixture/rigging/exterior-ladder support and placement gates',len(detail.get('checks',[]))==7 and all(c.get('status')=='PASS' for c in detail.get('checks',[])) and detail.get('access_ladders',{}).get('summary',{}).get('ladders')==5 and detail.get('access_ladders',{}).get('summary',{}).get('failures')==0,[{k:v for k,v in c.items() if k!='issues'} for c in detail.get('checks',[])])
static=load(DOC/'STATIC_VALIDATION.json')
check('Full static report matches current source/data/export/validator',static.get('scope')=='SOURCE_AND_CURRENT_EXPORT' and static.get('source_sha256')==source_hash and static.get('validator_sha256')==sha((ROOT/'tools/validate_leonidas_ii.py').read_bytes()) and static.get('build_data_sha256')==sha((EX/'build_data.json').read_bytes()) and static.get('game_manifest_sha256')==sha((EX/'game_manifest.json').read_bytes()))
check('Full static geometry and circulation gates',bool(static.get('results')) and not any(c.get('status')=='FAIL' for c in static.get('results',[])),static.get('summary'))
# Image presence/freshness is separate from manual review. Roof-off diagnostic
# views must stay labelled as such, not counted as eye-level interior photos.
major=['Exterior_Bow_Port','Exterior_Stern_Starboard','Exterior_Broadside_Port','Exterior_Overhead','Machinery_Engine_Aisle','Engineering_Engine_Cutaway','Engineering_Crossheads_ValveGear','Machinery_Stokehold','Machinery_Stokehold_After','Machinery_Stokehold_Forward','Engineering_Stern_Aperture','Machinery_Shaft_Alley','Machinery_Steam_Steering','Machinery_Dynamos_And_Switchboard','Machinery_Feed_Pumps','Engineering_Structural_Skeleton']
major+=['Interior_'+s for s in ('Dining_First','Library','Smoking','Music','Writing','Grand_Stair','Dining_Second','Second_Lounge','Cabin_First','Cabin_Second','Third_Class','Crew','Captain','Officer','Wheelhouse','Chart_Signals','Galley','Bakery','Pantry','Bath','Lavatory','Hospital','Purser','Mail','Barber','Cargo','Cold_Store','Bar')]
major+=['Plan_'+d for d in DECKS]
expected=set(major+['Room_'+r['id'] for r in ROOMS]);registry=load(REND/'all_cameras.json') if (REND/'all_cameras.json').exists() else []
by_stem={Path(r['file']).stem:r for r in registry};missing=sorted(expected-set(by_stem));bad=[];renderer_hash=sha((ROOT/'blender/leonidas_ii/render.py').read_bytes())
for name in sorted(expected.intersection(by_stem)):
 r=by_stem[name];file=ROOT/r['file']
 if not file.exists():bad.append([name,'missing file']);continue
 if r['source_sha256']!=source_hash or r.get('renderer_sha256')!=renderer_hash:bad.append([name,'stale source/renderer'])
 if sha(file.read_bytes())!=r.get('sha256'):bad.append([name,'image hash missing/mismatch'])
 if list(Image.open(file).size)!=r['pixels']:bad.append([name,'pixel dimensions mismatch'])
 if name.startswith(('Room_','Plan_')) and not r['cutaway']:bad.append([name,'cutaway label missing'])
 if name=='Interior_Grand_Stair' and not r['cutaway']:bad.append([name,'wall-removed stair diagnostic label missing'])
 if name in major and name.startswith('Interior_') and min(r['pixels'])<1000:bad.append([name,'major interior resolution too small'])
if missing and '--require-evidence' not in sys.argv:unverified('Complete current-source evidence set',dict(missing=missing,invalid=bad))
else:check('Complete current-source evidence set',not missing and not bad,dict(expected=len(expected),major=len(major),rooms=len(ROOMS),missing=missing,invalid=bad))
# Three original upper plans still showed opaque weather roofs despite the
# ceiling filter. Require the actual fresh roof-off driver, not relabelled
# originals or a plan that silently drops the hidden rooms/furniture too.
plan_roofs={'Plan_promenade':['Hospital_WeatherRoof'],'Plan_boat':['After_DeckCabin_Continuous_CrownedRoof','Chart_Room_CrownedRoof','Officers_Continuous_CrownedRoof'],'Plan_bridge':['Wheelhouse_CrownedRoof']}
plan_driver='tools/render_leonidas_plan_rechecks.py';plan_hash=sha((ROOT/plan_driver).read_bytes());plan_bad=[]
for name,roofs in plan_roofs.items():
 v=by_stem.get(name,{});deck=name[5:];room_ids=sorted(r['id'] for r in ROOMS if r['deck']==deck)
 if v.get('detail_driver')!=plan_driver or v.get('detail_driver_sha256')!=plan_hash or v.get('omitted_weather_roof_objects')!=roofs or v.get('roof_off_furniture_rooms')!=room_ids or v.get('source_mesh_geometry_edited') is not False or v.get('cutaway') is not True:plan_bad.append(name)
if plan_bad and '--require-evidence' not in sys.argv:unverified('Upper-deck plans use explicit roof-off driver and retain every furnished room',plan_bad)
else:check('Upper-deck plans use explicit roof-off driver and retain every furnished room',not plan_bad,dict(plans=3,invalid=plan_bad))
# Dedicated correction views are additional diagnostics, never substitutes
# for a missing planned major view or roof-off compartment survey. Bind the
# small driver as well as the unchanged common renderer and original master.
supplementary={'Supplement_Crew_Mess_Port':'O_CrewP','Supplement_Crew_Mess_Starboard':'O_CrewS'}
detail_driver='blender/leonidas_ii/render_crew_details.py';detail_hash=sha((ROOT/detail_driver).read_bytes());supp_bad=[]
for name,rid in supplementary.items():
 v=by_stem.get(name,{})
 p=ROOT/v.get('file','__missing_supplementary__')
 if not p.is_file() or p.suffix!='.jpg':supp_bad.append([name,'missing final JPG']);continue
 if v.get('source_sha256')!=source_hash or v.get('renderer_sha256')!=renderer_hash or v.get('detail_driver')!=detail_driver or v.get('detail_driver_sha256')!=detail_hash:supp_bad.append([name,'stale source/renderer/detail driver'])
 if v.get('sha256')!=sha(p.read_bytes()) or v.get('pixels')!=[1600,1000] or list(Image.open(p).size)!=v.get('pixels'):supp_bad.append([name,'image identity/dimensions'])
 if v.get('cutaway') is not True or v.get('supplementary') is not True or v.get('room_id')!=rid:supp_bad.append([name,'diagnostic/room labels'])
if supp_bad and '--require-evidence' not in sys.argv:unverified('Supplementary crew-mess correction evidence',supp_bad)
else:check('Supplementary crew-mess correction evidence',not supp_bad,dict(expected=len(supplementary),invalid=supp_bad))
manual=DOC/'VISUAL_REVIEW.json'
if manual.exists():
 r=load(manual);check('Manual review register source matches',r.get('source_sha256')==source_hash)
 opened=r.get('major_images',[])+r.get('room_surveys',[]);coverage={v['image'] for v in opened};stale=[]
 for v in opened:
  p=ROOT/v['file'];entry=by_stem.get(v.get('image'),{})
  if not p.is_file() or v.get('sha256')!=sha(p.read_bytes()) or v.get('source_sha256')!=source_hash or v.get('renderer_sha256')!=renderer_hash or v.get('file')!=entry.get('file') or v.get('sha256')!=entry.get('sha256') or v.get('pixels')!=entry.get('pixels'):stale.append(v['image'])
 detail=dict(reviewed_major=len(set(major)&coverage),reviewed_surveys=len(coverage-set(major)),missing=sorted(expected-coverage),stale=stale,recorded_status=r.get('status'))
 if expected-coverage and '--require-reviewed' not in sys.argv:unverified('Manual review coverage and exact image hashes',detail)
 else:check('Manual review coverage and exact image hashes',not(expected-coverage) and not stale and len(opened)==len(expected),detail)
 sup_opened=r.get('supplementary_images',[]);sup_names=[v.get('image') for v in sup_opened];sup_stale=[]
 for v in sup_opened:
  p=ROOT/v.get('file','__missing_review__');entry=by_stem.get(v.get('image'),{})
  if not p.is_file() or v.get('sha256')!=sha(p.read_bytes()) or v.get('file')!=entry.get('file') or v.get('source_sha256')!=source_hash or v.get('renderer_sha256')!=renderer_hash or v.get('detail_driver_sha256')!=detail_hash or any(v.get(k)!=entry.get(k) for k in ('source_sha256','renderer_sha256','detail_driver_sha256')) or v.get('status') not in ('REVIEWED','REVIEWED_WITH_LIMITATIONS'):sup_stale.append(v.get('image'))
 sup_ok=r.get('expected_supplementary_images')==len(supplementary) and len(sup_names)==len(supplementary) and set(sup_names)==set(supplementary) and not sup_stale
 if not sup_ok and '--require-reviewed' not in sys.argv:unverified('Supplementary correction views manually reviewed',dict(reviewed=sup_names,invalid=sup_stale))
 else:check('Supplementary correction views manually reviewed',sup_ok,dict(reviewed=sup_names,invalid=sup_stale))
 tech=r.get('technical_sheets',[]);expected_tech={f'drawings/leonidas_ii/{n}.svg' for n in ('General_Arrangement','Dimensions_And_Datums','Machinery_Flow')}
 check('Opened analytical-sheet register matches current SVGs',{v['file'] for v in tech}==expected_tech and all((ROOT/v['file']).exists() and v.get('sha256')==sha((ROOT/v['file']).read_bytes()) for v in tech))
 if '--require-reviewed' in sys.argv:
  check('No unresolved visual blockers; reviewed statuses recorded',not r.get('blocking_issues') and r.get('status')=='VIEWS_REVIEWED_WITH_LIMITATIONS' and all(v.get('status') in ('REVIEWED','REVIEWED_WITH_LIMITATIONS') for v in opened),r.get('blocking_issues',[]) or r.get('status'))
 elif r.get('blocking_issues') or r.get('status')=='IN_PROGRESS':unverified('Visual acceptance / open exceptions',r.get('blocking_issues',[]) or r.get('status'))
else:unverified('Manual visual review','No manual review register yet; a rendered file is not visual acceptance.')
# The user's final gallery is title-only and must cover EVERY delivered JPG,
# including the additional underside/contact/ladder views, not just 254 majors
# and room panels. Its manual register is separate from image generation.
gallery_path=DOC/'EVIDENCE_INDEX.html';gallery_manifest=DOC/'RENDER_GALLERY.json';final_review=DOC/'FINAL_RENDER_REVIEW.json'
gallery_registry={v['file']:v for p in REND.rglob('all_cameras.json') if 'build' not in p.relative_to(REND).parts for v in load(p)}
def current_gallery_frame(v):
 p=ROOT/v['file'];r=gallery_registry.get(v['file'],{});driver=r.get('detail_driver')
 if not p.is_file() or p.suffix!='.jpg' or r.get('source_sha256')!=source_hash or r.get('renderer_sha256')!=renderer_hash:return False
 if driver and (not (ROOT/driver).is_file() or r.get('detail_driver_sha256')!=sha((ROOT/driver).read_bytes())):return False
 return v.get('source_sha256')==source_hash and v.get('sha256')==r.get('sha256')==sha(p.read_bytes()) and v.get('pixels')==r.get('pixels')==list(Image.open(p).size)
if gallery_manifest.exists() and final_review.exists():
 g=load(gallery_manifest);fr=load(final_review);images=g.get('images',[]);opened=fr.get('images',[]);disk={str(p.relative_to(ROOT)) for p in REND.rglob('*.jpg') if 'build' not in p.relative_to(REND).parts};body=gallery_path.read_text();import re
 check('Title-only offline gallery contains every final render',g.get('source_sha256')==source_hash and g.get('sha256')==sha(gallery_path.read_bytes()) and g.get('builder_sha256')==sha((ROOT/'tools/make_leonidas_render_gallery.py').read_bytes()) and g.get('final_review_sha256')==sha(final_review.read_bytes()) and len(images)==len(disk)==g.get('counts',{}).get('total') and {v['file'] for v in images}==disk and len(expected_all())==272 and expected_all()<={Path(v['file']).stem for v in images} and all(current_gallery_frame(v) for v in images) and body.count('<article>')==len(images) and not re.search(r'<(?:p|figcaption|footer)\b',body,re.I) and not re.search(r'(?:src|href)=[\"\']https?://',body),dict(renders=len(images),captions=False))
 check('Every final render individually reviewed with exact current hashes',fr.get('status')=='ALL_FINAL_RENDERS_INDIVIDUALLY_REVIEWED_WITH_LIMITATIONS' and fr.get('source_sha256')==source_hash and not fr.get('blocking_issues') and len(opened)==len(disk) and {v['file'] for v in opened}==disk and all(current_gallery_frame(v) and all(v.get(k)==gallery_registry.get(v['file'],{}).get(k) for k in IDENTITY_KEYS) and v.get('status') in ('REVIEWED','REVIEWED_WITH_LIMITATIONS') and v.get('observation') and v.get('pixel_association')=='VISIBLE_FILENAME_AND_SHA256_STRIP_WITH_BIT_IDENTICAL_NATIVE_RENDER_BODY' and v.get('decoded_rgb_sha256')==sha(Image.open(ROOT/v['file']).convert('RGB').tobytes()) for v in opened),dict(reviewed=len(opened),expected=len(disk),blockers=fr.get('blocking_issues')))
 qafile=DOC/'RENDER_GALLERY_VALIDATION.json';qa=load(qafile) if qafile.exists() else {}
 check('Exact embedded native images and offline desktop/mobile UI tests',qa.get('status')=='STRUCTURE_EMBEDDING_AND_OFFLINE_UI_PASS' and qa.get('gallery_sha256')==sha(gallery_path.read_bytes()) and qa.get('manifest_sha256')==sha(gallery_manifest.read_bytes()) and qa.get('final_review_sha256')==sha(final_review.read_bytes()) and qa.get('tester_sha256')==sha((ROOT/'tools/test_leonidas_render_gallery.py').read_bytes()) and qa.get('source_sha256')==source_hash and qa.get('images_verified')==len(disk) and qa.get('native_encoding_reproduced') is True and qa.get('external_requests')==qa.get('javascript_errors')==[] and len(qa.get('ui',[]))==2 and all(v.get('status')=='PASS' for v in qa.get('ui',[])) and qa.get('sandboxed_preview',{}).get('status')=='PASS' and qa.get('sandboxed_preview',{}).get('sandbox')=='allow-scripts',dict(images=qa.get('images_verified'),status=qa.get('status'),sandboxed_preview=qa.get('sandboxed_preview',{}).get('status')))
elif '--require-reviewed' in sys.argv or '--require-evidence' in sys.argv:
 check('Title-only offline gallery and exhaustive final review present',False,'Create after opening every corrected final image; never infer visual approval from a successful render.')
else:unverified('Title-only offline gallery and exhaustive final review','Final image review/gallery not complete.')
# Only our namespaced work and the two requested entry points may change.
allowed_prefixes=('blender/leonidas_ii/','docs/leonidas_ii/','drawings/leonidas_ii/','exports/leonidas_ii/','models/leonidas_ii/','reference/leonidas_ii/','renders/leonidas_ii/','roblox/leonidas_ii/','tools/leonidas_micro_corrections/')
allowed_files={'README.md','DIMENSION_MANIFEST.json','interfaces/leonidas_ii_ship.json','shipdesign/leonidas_ii.py'}
allowed_files.update('tools/'+n for n in ('build_leonidas_ii.sh','compact_leonidas_blend.py','denoise_leonidas_renders.py','draw_leonidas_ii.py','join_leonidas_render_tiles.py','leonidas_materials.py','leonidas_revision_fixes.py','leonidas_runtime_harness.luau','package_leonidas_ii.py','prepare_leonidas_game.py','render_leonidas_evidence.sh','restore_leonidas_checkout.py','publish_leonidas_dimensions.py','test_leonidas_runtime.py','test_leonidas_ladders.py','test_leonidas_refinement.py','validate_leonidas_gltf.cjs','validate_leonidas_ii.py','check_leonidas_delivery.py','make_leonidas_review.py','make_leonidas_refinement.py','audit_leonidas_volumes.py'))
allowed_files.update('tools/'+n for n in ('audit_leonidas_micro.sh','audit_leonidas_stair_joinery.py','check_leonidas_micro_delivery.py','diagnose_leonidas_cabin_door_contacts.py','diagnose_leonidas_door_jambs.py','diagnose_leonidas_saved_faces.py','make_leonidas_micro_pages.py','make_leonidas_render_gallery.py','prepare_leonidas_review_images.py','test_leonidas_render_gallery.py','record_leonidas_export_inputs.py','render_leonidas_contact_details.py','render_leonidas_contact_rechecks.py','render_leonidas_plan_rechecks.py','test_leonidas_delivery_bindings.py'))
try:
 paths=subprocess.check_output(['git','diff','--name-only','75bf4ac5770b803919b36c8dbdb5374df82d88ac'],cwd=ROOT,text=True).splitlines()+subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines()
 foreign=sorted(p for p in set(paths) if p not in allowed_files and not p.startswith(allowed_prefixes));check('Own-change scope; no other agents assets / projects tree',not foreign,foreign)
except subprocess.CalledProcessError:unverified('Git own-change scope','Cached Git metadata unavailable; restore before publication.')
unverified('Roblox Studio / live / FPS acceptance','No Studio, Humanoid physics, multiplayer replication/carry or target-device performance acceptance in this workspace.')
report=dict(schema='victoria.leonidas-ii.delivery-checks/1.1',source_sha256=source_hash,micro_input_verification_mode=micro.get('mode'),receipt_only_absent_GAME_rebuild_inputs=micro.get('receipt_only_absent_inputs'),require_actual_saved_sources=require_saved_sources,geometry_audits_rerun=False,archive=dict(file=str(archive.relative_to(ROOT)),bytes=archive.stat().st_size,sha256=sha(archive.read_bytes())),counts=dict(master=D['counts'],game=M['counts'],colliders=len(D['proxies']),doors=len(D['doors']),movers=len(D['movers']),seats=len(D['seats']),lights=len(D['lights'])),checks=checks,summary=dict(collections.Counter(r['status'] for r in checks)),limits=__doc__)
(DOC/'DELIVERY_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
print('DELIVERY CHECKS',report['summary'])
sys.exit(1 if any(r['status']=='FAIL' for r in checks) else 0)
