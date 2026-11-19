"""Trace numeric saved/source correspondence; diagnostic only."""
from pathlib import Path
import sys,collections,json
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'blender/leonidas_ii'),str(ROOT)]
from audit_room_parts import regenerate,face_hash,saved_face_hash
from shipdesign.leonidas_ii import ROOMS
bpy.context.view_layer.update();r=next(r for r in ROOMS if r['id']=='M_Entrance');m=regenerate(r)
obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('LII_room')==r['id'] and o.get('LII_kind')=='furniture']
vv=[];ff=[]
for ob in obs:
 off=len(vv);vv.extend(ob.matrix_world@v.co for v in ob.data.vertices);ff.extend(tuple(off+i for i in p.vertices) for p in ob.data.polygons)
def counter(vv,ff):return collections.Counter(tuple(sorted(tuple(round(float(vv[i][k]),4) for k in range(3)) for i in f)) for f in ff)
a,b=counter(m.v,m.f),counter(vv,ff)
print('COUNTS',len(m.v),len(vv),len(m.f),len(ff),'different generated',sum((a-b).values()),'different saved',sum((b-a).values()),flush=True)
for p in list((a-b).keys())[:5]:print('GENERATED ONLY',p,flush=True)
for p in list((b-a).keys())[:5]:print('SAVED ONLY',p,flush=True)
f32=[tuple(float(np.float32(x)) for x in v) for v in m.v]
print('FLOAT32 CANONICAL GENERATED',face_hash(f32,m.f),'SAVED',saved_face_hash(obs),'MATCH',face_hash(f32,m.f)==saved_face_hash(obs),flush=True)
