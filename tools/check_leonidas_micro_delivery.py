"""Byte/provenance/result gates over the ACTUALLY EXECUTED canonical audits.

Default fresh-build mode (--require-saved-sources): requires the ACTUAL saved
MASTER and GAME .blend/build-data bytes and checks them against their original
canonical audits and frozen exporter receipt. The ordered build uses this mode.

Explicit --delivered-package mode: revalidate retained MASTER/data/exporter
bytes, the unchanged frozen ACTUAL-export receipt, all 12 exact canonical audit
files/generator identities, regressions and GAME/kit bindings. Excluded GAME
rebuild scratch may be absent; its original identities then come ONLY from that
verified export receipt. This is explicitly recorded, NEVER described as
reading fresh saved GAME bytes. Any retained input must still match exactly;
changed files cannot fall back to the receipt. No geometry/result tolerance or
canonical audit is waived/skipped. This mode does NOT rerun geometry audits.

Neither mode runs Blender or approves pixels, continuous physics or Studio.
Use check_leonidas_delivery.py for ACTUAL kit archive/receipt contents,
exported GLB reports and exhaustive visual/gallery gates.
"""
from pathlib import Path
import hashlib,json,sys,collections
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shipdesign.leonidas_ii import ROOMS
DOC=ROOT/'docs/leonidas_ii';HERE=ROOT/'blender/leonidas_ii'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FAMILIES={'MICRO_GEOMETRY':'audit_fittings.py','ROOM_PART_GEOMETRY':'audit_room_parts.py','PLANT_PART_GEOMETRY':'audit_plant_parts.py','EXTERIOR_PART_GEOMETRY':'audit_exterior_parts.py','DOOR_SWEEP_GEOMETRY':'audit_door_sweeps.py','SHAFT_CLEARANCE':'audit_shaft_clearances.py'}
INPUT_PATHS={'master':'models/leonidas_ii/Aurelian_1889.blend','master_data':'exports/leonidas_ii/build_data.json','game':'exports/leonidas_ii/build/Aurelian_Game_Source.blend','game_data':'exports/leonidas_ii/build/build_data.json','exporter':'blender/leonidas_ii/export_game.py'}
checks=[]
def check(name,ok,detail=None):
 row=dict(check=name,status='PASS' if ok else 'FAIL',detail=detail);checks.append(row);print(row['status'],name,str(detail)[:170],flush=True)

def main(require_saved_sources=True):
 checks.clear()
 current={str(p.relative_to(ROOT)):H(p) for p in sorted(HERE.glob('*.py')) if p.name not in ('render.py','render_crew_details.py','audit_structure.py')}
 master=ROOT/INPUT_PATHS['master'];source=H(master);master_data=json.loads((ROOT/INPUT_PATHS['master_data']).read_text())
 receipt_path=DOC/'EXPORT_INPUT_IDENTITY.json';r=json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
 inputs=r.get('inputs',{});manifest_path=ROOT/'exports/leonidas_ii/game_manifest.json';manifest=json.loads(manifest_path.read_text());k=json.loads((ROOT/'exports/leonidas_ii/IMPORT_KIT_MANIFEST.json').read_text())
 expected_audits={f'docs/leonidas_ii/{family}_{quality}.json' for family in FAMILIES for quality in ('MASTER','GAME')}
 audit_rows=r.get('audit_reports',[]);audit_paths=[v.get('file') for v in audit_rows]
 frozen_ok=(r.get('status')=='VERIFIED_FROZEN_INPUTS_OVER_ACTUAL_EXPORT_RUN' and r.get('recorder_sha256')==H(ROOT/'tools/record_leonidas_export_inputs.py') and r.get('game_manifest_sha256')==H(manifest_path) and r.get('glb_sha256')==manifest.get('glb_sha256') and r.get('generator_sha256')==current and set(inputs)==set(INPUT_PATHS) and len(audit_paths)==len(expected_audits) and set(audit_paths)==expected_audits and all((ROOT/v['file']).is_file() and v.get('sha256')==H(ROOT/v['file']) for v in audit_rows))
 retained=[];receipt_only=[];invalid=[]
 for name,path in INPUT_PATHS.items():
  identity=inputs.get(name,{});p=ROOT/path;digest=identity.get('sha256','')
  valid=(identity.get('file')==path and isinstance(identity.get('bytes'),int) and identity['bytes']>0 and isinstance(digest,str) and len(digest)==64 and all(c in '0123456789abcdef' for c in digest))
  if p.is_file():
   valid=valid and p.stat().st_size==identity.get('bytes') and H(p)==digest;retained.append(name)
  elif name in ('game','game_data') and not require_saved_sources:
   receipt_only.append(name)
  else:valid=False
  if not valid:invalid.append(name)
 frozen_ok=frozen_ok and not invalid and inputs.get('master',{}).get('sha256')==source and manifest.get('source_sha256')==source
 modes={}
 for quality in ('MASTER','GAME'):
  input_key='master' if quality=='MASTER' else 'game';data_key='master_data' if quality=='MASTER' else 'game_data'
  model=ROOT/INPUT_PATHS[input_key];data_path=ROOT/INPUT_PATHS[data_key]
  saved=model.is_file() and data_path.is_file()
  modes[quality]=dict(mode='ACTUAL_RETAINED_SAVED_SOURCE_AND_DATA_BYTES' if saved else 'FROZEN_ACTUAL_EXPORT_IDENTITIES_GAME_SCRATCH_NOT_RETAINED',fresh_saved_source_and_data_bytes_checked=saved,source_sha256=inputs.get(input_key,{}).get('sha256'),build_data_sha256=inputs.get(data_key,{}).get('sha256'))
  if not saved and require_saved_sources:
   check(quality+' actual saved source/build data required',False,'Regenerate excluded GAME scratch and rerun its actual audits/export. A receipt-only delivery check cannot satisfy --require-saved-sources.');continue
  # Fixture/door enumeration is quality-independent. If GAME data is absent,
  # MASTER provides only those enumerations; all GAME geometry/result values
  # still come from the exact original GAME audit files, bound to its own
  # ORIGINAL source/data hashes in the frozen ACTUAL export receipt.
  d=json.loads(data_path.read_text()) if data_path.is_file() else master_data
  model_hash=H(model) if model.is_file() else inputs.get(input_key,{}).get('sha256')
  data_hash=H(data_path) if data_path.is_file() else inputs.get(data_key,{}).get('sha256')
  generator_bound=d.get('source_files_sha256')==current if data_path.is_file() else r.get('generator_sha256')==current
  check(quality+' all current generator keys and saved/frozen identities bound',generator_bound and frozen_ok,modes[quality])
  for family,script in FAMILIES.items():
   p=DOC/f'{family}_{quality}.json'
   if not p.is_file():check(quality+' '+family+' exists',False);continue
   a=json.loads(p.read_text());s=a.get('summary',{})
   check(quality+' '+family+' exact canonical source/data/auditor',a.get('source_sha256')==model_hash and a.get('build_data_sha256')==data_hash and a.get('source_file')==str(model.relative_to(ROOT)) and a.get('quality')==quality and a.get('auditor_sha256')==H(HERE/script) and a.get('status','SAVED_SOURCE_BOUND_SCREEN')=='SAVED_SOURCE_BOUND_SCREEN' and not a.get('generator_binding_mismatches'))
   binding=a.get('generator_sha256',{});check(quality+' '+family+' generator coverage',all(binding.get(key)==value for key,value in current.items()))
   if family=='MICRO_GEOMETRY':
    floor=a.get('saved_model_floor') or {};okay=bool(a.get('recipes')) and s.get('recipes_with_detached_clusters')==s.get('detached_clusters')==s.get('floor_floating_count')==s.get('floor_support_flags')==0 and floor.get('fixtures_tested')==len([f for f in d['fixtures'] if f['label']!='PlaceSetting']) and floor.get('missing_support_count')==floor.get('penetration_count')==floor.get('floating_count')==0 and a.get('tolerance_m')==.0006
   elif family=='ROOM_PART_GEOMETRY':okay=s.get('rooms')==len([room for room in ROOMS if room['kind'] not in ('machinery','steering')]) and s.get('detached_clusters')==s.get('saved_geometry_mismatches')==s.get('stair_column_bearing_flags')==0 and s.get('stair_columns')==12 and a.get('tolerance_m')==.0006
   elif family=='PLANT_PART_GEOMETRY':okay=s.get('captured_assemblies',0)>0 and s.get('mover_assemblies',0)>0 and s.get('static_detached_clusters')==s.get('mover_internal_detached_clusters')==s.get('saved_geometry_mismatches')==0
   elif family=='EXTERIOR_PART_GEOMETRY':okay=s.get('captured_assemblies',0)>0 and s.get('mover_assemblies',0)>0 and s.get('static_detached_clusters')==s.get('mover_internal_detached_clusters')==s.get('saved_geometry_mismatches')==0
   elif family=='DOOR_SWEEP_GEOMETRY':okay=a.get('schema')=='victoria.leonidas-ii.door-finite-sweep/1.3' and a.get('sample_interval_degrees')==2 and s.get('doors')==len(d['doors']) and s.get('poses')==sum(int(abs(v['angle_deg']))//2+1+(int(abs(v['angle_deg']))%2>0) for v in d['doors']) and s.get('doors_with_intersections')==0
   else:okay=s.get('pairs')==2 and s.get('poses')==48 and s.get('intersecting_poses')==s.get('saved_geometry_mismatches')==0 and s.get('negative_controls_passed')==s.get('negative_controls_expected')==4
   check(quality+' '+family+' scoped result gates',okay,s)
  p=DOC/'inspection'/f'MICRO_CONTACT_REGRESSIONS_{quality}.json';a=json.loads(p.read_text());tests=a.get('tests',[])
  check(quality+' all exact-source positive/negative regressions',a.get('quality')==quality and a.get('test_sha256')==H(HERE/'test_micro_contacts.py') and a.get('summary',{}).get('fail_count')==0 and len(tests)>=344 and a.get('summary',{}).get('pass_count')==len(tests) and len({v['test'] for v in tests})==len(tests) and all(v['status']=='PASS' for v in tests) and a.get('generator_sha256')=={p.name:H(p) for p in sorted(HERE.glob('*.py'))},a.get('summary'))
 check('Frozen actual-export receipt, retained input bytes and all original audit identities',frozen_ok,dict(retained_input_bytes_checked=retained,receipt_only_absent_GAME_scratch=receipt_only,invalid_inputs=invalid,require_saved_sources=require_saved_sources))
 check('Import kit bound to exact frozen export receipt/GAME source',receipt_path.is_file() and k.get('export_input_receipt_sha256')==H(receipt_path) and k.get('source_sha256')==source and k.get('game_source_sha256')==inputs.get('game',{}).get('sha256') and k.get('game_build_data_sha256')==inputs.get('game_data',{}).get('sha256'))
 report=dict(schema='victoria.leonidas-ii.micro-delivery-checks/1.1',source_sha256=source,validator_sha256=H(Path(__file__)),mode='REQUIRE_ACTUAL_SAVED_SOURCES' if require_saved_sources else 'DELIVERED_FROZEN_EXPORT_AND_CANONICAL_AUDIT_BINDINGS',input_verification=modes,receipt_only_absent_inputs=receipt_only,checks=checks,summary=dict(collections.Counter(v['status'] for v in checks)),limits=__doc__)
 (DOC/'MICRO_DELIVERY_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print('MICRO DELIVERY',report['summary'])
 return 1 if any(v['status']=='FAIL' for v in checks) else 0

if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 mode=parser.add_mutually_exclusive_group()
 mode.add_argument('--delivered-package',action='store_true',help='Explicit receipt-bound delivery recheck; absent GAME rebuild scratch is reported, not freshly inspected.')
 mode.add_argument('--require-saved-sources',action='store_true',help='Require actual saved MASTER/GAME inputs (the default). Missing excluded GAME scratch is a failure.')
 args=parser.parse_args()
 raise SystemExit(main(require_saved_sources=not args.delivered_package))
