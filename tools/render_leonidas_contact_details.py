"""Additional actual-source close-ups of repaired bearing/joint interfaces.
Wall/roof omissions are explicit CUTAWAYS, not enclosed-room photographs.
Serial Blender only; run standalone OIDN with LII_RENDER_SUBDIR=micro after exit.
No image generation, mesh edits, floor hiding or source saving.
"""
from pathlib import Path
import sys,os,json,hashlib,importlib.util,math
import bpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];COMMON=ROOT/'blender/leonidas_ii/render.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
os.environ['LII_RENDER_SUBDIR']='micro';requested=os.environ.get('LII_ONLY');os.environ['LII_ONLY']='__INITIALISE_WITHOUT_RENDERING__'
sys.argv=[str(COMMON),'--','public','100']
spec=importlib.util.spec_from_file_location('leonidas_contact_common',COMMON);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
if requested:os.environ['LII_ONLY']=requested
else:os.environ.pop('LII_ONLY',None)
driver=str(Path(__file__).relative_to(ROOT));driver_hash=sha(Path(__file__))
controlled=set(requested.split(',')) if requested else {'Micro_Dining_Tableware','Micro_Dining_Underside','Micro_Piano_Stool_Feet','Micro_Pantry_Crockery','Micro_Bunk_Ladder','Micro_Hospital_Trolley','Micro_Door_Hinge_Closed','Micro_Door_Hinge_Open','Micro_Thrust_Bearings'}
e.PERSISTED=[r for r in e.PERSISTED if Path(r['file']).stem not in controlled or r.get('detail_driver_sha256')==driver_hash]

def room(rid):return next(r for r in e.ROOMS if r['id']==rid)
def fixture(rid,label):return next(f for f in e.DATA['fixtures'] if f['room']==rid and f['label']==label)
def local(f,p):
 x,y,z=p;a=f.get('yaw',0);cx,cy,cz=f['position']
 return (cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),cz+z)
def cutaway(rid):e.visibility(lambda o:o.get('LII_room')==rid and o.get('LII_kind') not in ('wall','ceiling','sign','glazing'))
def shot(name,title,rid,pos,target,lens=45,pose=None):
 if name not in controlled:return
 r=room(rid);e.render(name,title,pos,target,lens,interior=(r['x0'],r['x1'],r['y0'],r['y1'],r['z'],r['top']),res=(1600,1000),cutaway=True,room_id=rid)
 for row in e.PERSISTED:
  if Path(row['file']).stem==name:
   row.update(detail_driver=driver,detail_driver_sha256=driver_hash,supplementary=True,short_title=title,diagnostic_limit='Close diagnostic with enclosure walls/roof omitted. Original furniture/floor retained, except the explicitly isolated shaft-bearing view; not a possible enclosed-room photograph or live/hidden-contact certification.')
   if pose:row['posed_door_degrees']=pose
 e.REGFILE.write_text(json.dumps(e.PERSISTED,indent=2));(e.OUT/'camera_register.json').write_text(json.dumps(e.REGISTER,indent=2))

r=room('S_Dining');z=r['z']+.0475;xx=r['x0']+2.90;yy=(r['y0']+r['y1'])/2-4.65;cutaway(r['id'])
shot('Micro_Dining_Tableware','Dining Tableware — Side Cutaway',r['id'],(xx-.38,yy+1.40,z+.90),(xx-.50,yy+.12,z+.77),60)
shot('Micro_Dining_Underside','Dining Table and Chair Supports — Cutaway',r['id'],(xx-.42,yy+1.15,z+.22),(xx+.12,yy,z+.43),33)
r=room('S_Music');z=r['z']+.0475;px=r['x0']+2.5;cy=(r['y0']+r['y1'])/2;cutaway(r['id'])
shot('Micro_Piano_Stool_Feet','Piano Casters and Stool Feet — Cutaway',r['id'],(px+2.5,cy-1.25,z+.22),(px+.65,cy,z+.28),43)
f=fixture('S_Pantry','ProvisionShelving');cutaway('S_Pantry')
shot('Micro_Pantry_Crockery','Pantry Crockery — Side Cutaway','S_Pantry',local(f,(.55,-1.25,.84)),local(f,(0,0,.72)),53)
f=fixture('C006','TwoBerthBunk');r=room('C006');cutaway(r['id']);x,y,z=f['position']
shot('Micro_Bunk_Ladder','Bunk Ladder and Mattress Slats — Cutaway',r['id'],(x+.95,y-.8,z+.64),(x+.18,y+.15,z+.98),31)
f=fixture('P_Hospital','MedicalInstrumentTrolley');cutaway('P_Hospital')
shot('Micro_Hospital_Trolley','Hospital Trolley Casters — Cutaway','P_Hospital',local(f,(-1,-1.2,.30)),local(f,(0,0,.35)),48)
r=room('A001');d=next(d for d in e.DATA['doors'] if d['id']==r['id']);hx,hy,hz=d['hinge'];cutaway(r['id'])
# Retain ACTUAL own-wall/jamb geometry for these hinge close-ups.
e.visibility(lambda o:o.get('LII_room')==r['id'] and o.get('LII_kind')!='ceiling')
shot('Micro_Door_Hinge_Closed','Cabin Door Hinge — Closed',r['id'],(hx+.62,hy+.80,hz+1.17),(hx+.04,hy-.03,hz+.99),63)
ob=bpy.data.objects[d['name']];original=ob.matrix_world.copy();pivot=Matrix.Translation(Vector(d['hinge']))
try:
 ob.matrix_world=pivot@Matrix.Rotation(math.radians(d['angle_deg']),4,'Z')@pivot.inverted()@original;bpy.context.view_layer.update()
 shot('Micro_Door_Hinge_Open','Cabin Door Hinge — Open',r['id'],(hx+.62,hy+.80,hz+1.17),(hx+.04,hy-.03,hz+.99),63,d['angle_deg'])
finally:ob.matrix_world=original;bpy.context.view_layer.update()
e.visibility(lambda o:o.get('LII_kind')=='shaft_support' or o.get('LII_mover')=='shaft')
shot('Micro_Thrust_Bearings','Thrust Collars and Bearings — Cutaway','E_Alley',(-30.3,-1.7,3.75),(-27.85,0,3.0),45)
print('ACTUAL-SOURCE MICRO CONTACT DETAILS COMPLETE; visual review remains separate.',flush=True)
