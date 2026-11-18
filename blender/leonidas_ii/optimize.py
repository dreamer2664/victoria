"""Lossless native collision-box merging; no rooms/cutouts are bridged.
Only adjacent axis-aligned boxes with identical other extents/tag merge.
"""
from collections import defaultdict

def merge_proxies(records):
 out=[dict(p) for p in records]
 before=len(out)
 for iteration in range(3):
  old=len(out)
  for axis in (1,0,2):
   fixed=[];groups=defaultdict(list)
   for p in out:
    if p.get('kind')!='box' or abs(p.get('yaw',0))>1e-5:
     fixed.append(p);continue
    others=[k for k in range(3) if k!=axis]
    key=(p['tag'],tuple(round(p['position'][k],4) for k in others),tuple(round(p['size'][k],4) for k in others))
    groups[key].append(p)
   for group in groups.values():
    group.sort(key=lambda p:p['position'][axis]);current=None
    for p in group:
     if current is None:current=dict(p);current['position']=list(p['position']);current['size']=list(p['size']);continue
     hi=current['position'][axis]+current['size'][axis]/2;lo=p['position'][axis]-p['size'][axis]/2
     if abs(hi-lo)<.001:
      a=current['position'][axis]-current['size'][axis]/2;b=p['position'][axis]+p['size'][axis]/2;current['position'][axis]=(a+b)/2;current['size'][axis]=b-a
     else:fixed.append(current);current=dict(p);current['position']=list(p['position']);current['size']=list(p['size'])
    if current is not None:fixed.append(current)
   out=fixed
  if old==len(out):break
 print('LOSSLESS COLLIDER MERGE',before,'->',len(out),flush=True)
 return out
