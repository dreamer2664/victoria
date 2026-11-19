"""Record unchanged, canonically audited inputs across the ACTUAL exporter run.
Run --begin immediately before Blender export_game.py and --complete after it.
This is byte provenance only, never geometry, visual or Studio approval.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];EX=ROOT/'exports/leonidas_ii';DOC=ROOT/'docs/leonidas_ii'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FAMILIES={'MICRO_GEOMETRY':'audit_fittings.py','ROOM_PART_GEOMETRY':'audit_room_parts.py','PLANT_PART_GEOMETRY':'audit_plant_parts.py','EXTERIOR_PART_GEOMETRY':'audit_exterior_parts.py','DOOR_SWEEP_GEOMETRY':'audit_door_sweeps.py','SHAFT_CLEARANCE':'audit_shaft_clearances.py'}

def inputs():
 files={'master':'models/leonidas_ii/Aurelian_1889.blend','master_data':'exports/leonidas_ii/build_data.json','game':'exports/leonidas_ii/build/Aurelian_Game_Source.blend','game_data':'exports/leonidas_ii/build/build_data.json','exporter':'blender/leonidas_ii/export_game.py'}
 rows={k:dict(file=f,sha256=H(ROOT/f),bytes=(ROOT/f).stat().st_size) for k,f in files.items()}
 audits=[]
 for quality in ('MASTER','GAME'):
  expected=rows['master' if quality=='MASTER' else 'game']['sha256'];data=rows['master_data' if quality=='MASTER' else 'game_data']['sha256']
  for family,script in FAMILIES.items():
   p=DOC/f'{family}_{quality}.json';a=json.loads(p.read_text())
   assert a.get('source_sha256')==expected and a.get('quality')==quality and a.get('build_data_sha256')==data,('Stale source/data audit',p.name)
   assert a.get('auditor_sha256')==H(ROOT/'blender/leonidas_ii'/script) and not a.get('generator_binding_mismatches'),('Stale/candidate auditor',p.name)
   assert a.get('status','SAVED_SOURCE_BOUND_SCREEN')=='SAVED_SOURCE_BOUND_SCREEN',('Candidate report is not acceptance',p.name)
   audits.append(dict(file=str(p.relative_to(ROOT)),sha256=H(p)))
 # Build provenance must contain all current generator/auditor files in BOTH
 # source builds, not just the keys present in an old saved build.
 here=ROOT/'blender/leonidas_ii';current={str(p.relative_to(ROOT)):H(p) for p in sorted(here.glob('*.py')) if p.name not in ('render.py','render_crew_details.py','audit_structure.py')}
 for key in ('master_data','game_data'):
  data=json.loads((ROOT/rows[key]['file']).read_text());assert data['source_files_sha256']==current,('Changed generator after audit',key)
 return dict(inputs=rows,audit_reports=audits,generator_sha256=current)

pending=EX/'build/EXPORT_INPUTS_PENDING.json'
if sys.argv[1:] == ['--begin']:
 receipt=inputs();receipt.update(recorder_sha256=H(Path(__file__)))
 pending.parent.mkdir(parents=True,exist_ok=True);pending.write_text(json.dumps(receipt,indent=2)+'\n');print('FROZEN EXPORT INPUTS RECORDED')
elif sys.argv[1:]==['--complete']:
 before=json.loads(pending.read_text());after=inputs()
 assert all(before[k]==v for k,v in after.items()) and before['recorder_sha256']==H(Path(__file__)),'Inputs/audits/recorder changed during actual export'
 m=EX/'game_manifest.json';manifest=json.loads(m.read_text());glb=EX/'build'/manifest['file']
 assert manifest['source_sha256']==after['inputs']['master']['sha256'] and manifest['exporter_sha256']==after['inputs']['exporter']['sha256']
 assert manifest['glb_sha256']==H(glb) and manifest['glb_bytes']==glb.stat().st_size
 report=dict(schema='victoria.leonidas-ii.frozen-export-inputs/1.0',status='VERIFIED_FROZEN_INPUTS_OVER_ACTUAL_EXPORT_RUN',**before,game_manifest_sha256=H(m),glb_sha256=manifest['glb_sha256'],limits=__doc__)
 (DOC/'EXPORT_INPUT_IDENTITY.json').write_text(json.dumps(report,indent=2)+'\n');pending.unlink();print('FROZEN INPUTS/ACTUAL EXPORT IDENTITY VERIFIED')
else:raise SystemExit('Use --begin before export or --complete immediately after it')
