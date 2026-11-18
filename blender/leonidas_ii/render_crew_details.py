"""Two supplementary actual-source crew-mess detail cutaways.

Run AFTER the normal public batch, serially, never beside Blender/OIDN:
  blender -b models/leonidas_ii/Aurelian_1889.blend -t 2 \
    --python-exit-code 1 -P blender/leonidas_ii/render_crew_details.py
Then run tools/denoise_leonidas_renders.py as for the ordinary evidence.

The common renderer is reused without changing its hash or the previously
reviewed 254 planned views. Its public preset must already be complete and
is skipped by exact-pose/source/renderer/sample resume checks on import.
These are explicitly WALL/ROOF-REMOVED DETAILS, not enclosed photographs:
the joined room wall object and ceiling are omitted for a close oblique view
of bench seats, legs and table relationship from outside the wall. Original
floor, furniture and bunks are retained unchanged. No ship mesh changes.
"""
from pathlib import Path
import sys,os,json,hashlib,importlib.util
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
COMMON=HERE/'render.py';REG=ROOT/'renders/leonidas_ii/all_cameras.json'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
source=sha(ROOT/'models/leonidas_ii/Aurelian_1889.blend');renderer=sha(COMMON);driver=sha(Path(__file__))
rows=json.loads(REG.read_text());by={Path(r['file']).stem:r for r in rows}
public=['Interior_'+n for n in ('Dining_First','Library','Smoking','Music','Writing','Grand_Stair','Dining_Second','Second_Lounge')]
for name in public:
 r=by[name];p=ROOT/r['file']
 assert p.suffix=='.jpg' and p.is_file() and r['sha256']==sha(p)
 assert r['source_sha256']==source and r['renderer_sha256']==renderer and r['pixels']==[1600,1000] and r['cycles_samples']>=12
os.environ['LII_RESUME']='1';os.environ['LII_SAMPLES']='12'
sys.argv=[str(COMMON),'--','public','100']
spec=importlib.util.spec_from_file_location('leonidas_common_evidence',COMMON);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
names={'Supplement_Crew_Mess_Port','Supplement_Crew_Mess_Starboard'}
e.PERSISTED=[r for r in e.PERSISTED if Path(r['file']).stem not in names or r.get('detail_driver_sha256')==driver]
for rid,side in [('O_CrewP','Port'),('O_CrewS','Starboard')]:
 r=next(r for r in e.ROOMS if r['id']==rid)
 table=[f for f in e.DATA['fixtures'] if f['room']==rid and f['label']=='TurnedDiningTable'];assert len(table)==1
 xx,yy,_=table[0]['position'];z=r['z'];sign=1 if r['door_wall']=='y1' else -1
 edge=r['y0'] if sign>0 else r['y1']
 # The first overhead attempt exposed only a thin bench sliver. Omit the
 # joined wall/ceiling objects explicitly, NOT obstructing bunks/furniture,
 # for an oblique detail that can show seat tops and floor-contacting legs.
 e.visibility(lambda o,rid=rid:o.get('LII_room')==rid and o.get('LII_kind') not in ('ceiling','wall'))
 pos=(xx+1.1,edge-sign*1.5,z+1.7);target=(xx,yy-sign*.24,z+.55)
 e.render('Supplement_Crew_Mess_'+side,side+' crew mess alcove — wall/roof-removed table/bench diagnostic',pos,target,36,interior=(r['x0'],r['x1'],r['y0'],r['y1'],z,r['top']),res=(1600,1000),cutaway=True,room_id=rid)
 for row in e.PERSISTED:
  if Path(row['file']).stem=='Supplement_Crew_Mess_'+side:
   row['detail_driver']='blender/leonidas_ii/render_crew_details.py';row['detail_driver_sha256']=driver;row['supplementary']=True
   row['diagnostic_limit']='Close oblique diagnostic with joined room walls and ceiling omitted; original floor, table/bench and all bunks retained unchanged. Camera is outside the omitted wall, not a possible enclosed-room photograph. No live seating/avatar or hidden-contact certification.'
 e.REGFILE.write_text(json.dumps(e.PERSISTED,indent=2))
 (e.OUT/'camera_register.json').write_text(json.dumps(e.REGISTER,indent=2))
print('SUPPLEMENTARY CREW DETAILS RENDERED: two authentic current-master cutaways; visual inspection still required.',flush=True)
