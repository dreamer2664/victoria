"""Trace saved-source cabin-door hits to actual reconstructed primitives."""
from pathlib import Path
import sys,json,bisect
import bpy
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'blender/leonidas_ii'),str(ROOT)]
from audit_room_parts import regenerate
from audit_fittings import parts
from shipdesign.leonidas_ii import ROOMS
r=next(r for r in ROOMS if r['id']=='A001');m=regenerate(r);ps=parts(m)
print('ROOM',r,flush=True)
data=json.loads((ROOT/'exports/leonidas_ii/build_data.json').read_text())
print('DOOR',next(d for d in data['doors'] if d['id']==r['id']),flush=True)
for f in data['fixtures']:
 if f['room']==r['id']:print('FIXTURE',f,flush=True)
for poly in (2139,2143,2151):
 i=bisect.bisect_right(m.groups,poly);p=ps[i]
 print('ACTUAL HIT PRIMITIVE',poly,i,list(p['lo']),list(p['hi']),p['tiles'],flush=True)
