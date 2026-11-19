"""Correct four diagnostic cameras after actually opening the first pixels.
The first bunk close-up stood INSIDE the washstand; first hinge targets looked
between the two real hinges; the low trolley framing cropped the nearest tyre.
These views are freshly rendered, never relabelled old pixels. The other five
retain their original driver hashes. No geometry/source is altered or saved.
"""
from pathlib import Path
import sys,os,json,hashlib,importlib.util,math
import bpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];COMMON=ROOT/'blender/leonidas_ii/render.py'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
os.environ['LII_RENDER_SUBDIR']='micro';requested=os.environ.get('LII_ONLY');os.environ['LII_ONLY']='__INITIALISE_WITHOUT_RENDERING__'
sys.argv=[str(COMMON),'--','public','100']
spec=importlib.util.spec_from_file_location('leonidas_contact_recheck_common',COMMON);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
if requested:os.environ['LII_ONLY']=requested
else:os.environ.pop('LII_ONLY',None)
driver=str(Path(__file__).relative_to(ROOT));driver_hash=H(Path(__file__))
names={'Micro_Bunk_Ladder','Micro_Door_Hinge_Closed','Micro_Door_Hinge_Open','Micro_Hospital_Trolley'}
e.PERSISTED=[r for r in e.PERSISTED if Path(r['file']).stem not in names or r.get('detail_driver_sha256')==driver_hash]

def room(rid):return next(r for r in e.ROOMS if r['id']==rid)
def shot(name,title,rid,pos,target,lens=45,pose=None):
 if requested and name not in requested.split(','):return
 r=room(rid);e.render(name,title,pos,target,lens,interior=(r['x0'],r['x1'],r['y0'],r['y1'],r['z'],r['top']),res=(1600,1000),cutaway=True,room_id=rid)
 for row in e.PERSISTED:
  if Path(row['file']).stem==name:
   row.update(detail_driver=driver,detail_driver_sha256=driver_hash,supplementary=True,short_title=title,diagnostic_limit='Close diagnostic, ceiling omitted; original furniture/floor retained. Bunk camera is outside the explicitly omitted front wall, with target feet/posts frustum-checked; not an enclosed photograph. Door view retains actual own jambs. Not live/hidden-contact certification.')
   if pose:row['posed_door_degrees']=pose
 e.REGFILE.write_text(json.dumps(e.PERSISTED,indent=2));(e.OUT/'camera_register.json').write_text(json.dumps(e.REGISTER,indent=2))
r=room('C006');f=next(f for f in e.DATA['fixtures'] if f['room']==r['id'] and f['label']=='TwoBerthBunk');x,y,z=f['position']
e.visibility(lambda o:o.get('LII_room')==r['id'] and o.get('LII_kind') not in ('wall','ceiling','sign','glazing'))
# A clear eye is not sufficient: the first aisle recheck still cropped
# the ladder and looked mostly at the mattress underside. This explicit
# wall-removed front diagnostic frames the full target bunk, including
# its actual floor feet, five rungs and both berth-frame attachments.
pos=(x+.90,y-4.0,z+1.12);target=(x,y-.10,z+1.12);lens=28
assert not any(all(a[k]-.08<pos[k]<b[k]+.08 for k in range(3)) for a,b in (v['bounds'] for v in e.DATA['fixtures'] if v['room']==r['id'])),'Bunk camera lies inside visible subject furniture'
rotation=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y');a,b=f['bounds']
for xx in (a[0],b[0]):
 for yy in (a[1],b[1]):
  for zz in (a[2],b[2]):
   q=rotation.inverted()@(Vector((xx,yy,zz))-Vector(pos));depth=-q.z
   assert depth>0 and abs(q.x/(depth*18/lens))<.94 and abs(q.y/(depth*11.25/lens))<.94,('Target bunk feet/posts must fit inside full native frame',xx,yy,zz,tuple(q))
shot('Micro_Bunk_Ladder','Bunk Ladder and Berth Frames — Cutaway',r['id'],pos,target,lens)
r=room('A001');d=next(d for d in e.DATA['doors'] if d['id']==r['id']);hx,hy,hz=d['hinge']
e.visibility(lambda o:o.get('LII_room')==r['id'] and o.get('LII_kind')!='ceiling')
pos=(hx+.42,hy+.62,hz+1.88);target=(hx+.025,hy,hz+1.70)
shot('Micro_Door_Hinge_Closed','Cabin Door Hinge — Closed, Roof Off',r['id'],pos,target,63)
ob=bpy.data.objects[d['name']];original=ob.matrix_world.copy();pivot=Matrix.Translation(Vector(d['hinge']))
try:
 ob.matrix_world=pivot@Matrix.Rotation(math.radians(d['angle_deg']),4,'Z')@pivot.inverted()@original;bpy.context.view_layer.update()
 # A closed-pose clear eye was behind the swung leaf in the actual open
 # pixels. Select the opposite-side eye only after testing its sightlines
 # against EVERY render-visible source mesh in this posed room. Nothing
 # (including the own jamb or leaf) is removed to make the joint visible.
 deps=bpy.context.evaluated_depsgraph_get()
 visible=[(o,BVHTree.FromObject(o,deps),o.matrix_world.copy()) for o in e.sc.objects if o.type=='MESH' and not o.hide_render]
 def hinge_ray(eye,axis):
  eye,axis=Vector(eye),Vector(axis);direction=(axis-eye).normalized();hits=[]
  for obj,tree,world in visible:
   inv=world.inverted();p=inv@eye;q=inv@(eye+direction);hit,normal,index,distance=tree.ray_cast(p,(q-p).normalized())
   if hit is not None:
    point=world@hit;hits.append(((point-eye).length,point,obj.name))
  if not hits:return False,None
  distance,point,name=min(hits,key=lambda v:v[0]);return (point-axis).length<.028,dict(object=name,point=list(point),axis=list(axis),distance=distance)
 probes=[(hx,hy,hz+1.70+zz) for zz in (-.0475,0,.0475)]
 candidates=[(hx-.42,hy+.62,hz+1.88),(hx+.42,hy-.62,hz+1.88),(hx-.55,hy+.32,hz+1.84)]
 selected=next(((eye,[hinge_ray(eye,p)[1] for p in probes]) for eye in candidates if all(hinge_ray(eye,p)[0] for p in probes)),None)
 assert selected is not None,'Open hinge must have three actual unobstructed knuckle sightlines, not a plausible camera coordinate'
 open_pos,sightlines=selected
 shot('Micro_Door_Hinge_Open','Cabin Door Hinge — Open, Roof Off',r['id'],open_pos,(hx,hy,hz+1.70),63,d['angle_deg'])
 for row in e.PERSISTED:
  if Path(row['file']).stem=='Micro_Door_Hinge_Open':row['open_pose_visible_knuckle_rays']=sightlines
 e.REGFILE.write_text(json.dumps(e.PERSISTED,indent=2))
 print('OPEN HINGE ACTUAL VISIBLE KNUCKLE RAYS',json.dumps(sightlines),flush=True)
finally:ob.matrix_world=original;bpy.context.view_layer.update()
r=room('P_Hospital');f=next(f for f in e.DATA['fixtures'] if f['room']==r['id'] and f['label']=='MedicalInstrumentTrolley');x,y,z=f['position']
e.visibility(lambda o:o.get('LII_room')==r['id'] and o.get('LII_kind') not in ('wall','ceiling','sign','glazing'))
shot('Micro_Hospital_Trolley','Hospital Trolley Casters — Cutaway',r['id'],(x-1.3,y-1.8,z+.80),(x,y,z+.35),50)
print('FOUR CONTACT CAMERA RECHECKS RENDERED; individual pixel review remains required.',flush=True)
