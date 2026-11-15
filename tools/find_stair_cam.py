import bpy, sys
sys.path.insert(0,"/home/user/victoria"); sys.path.insert(0,"/home/user/victoria/blender")
from mathutils import Vector
from shipdesign.spec import DECK_Z
from shipdesign import layout

def first(L,T,skip=()):
    d=(Vector(T)-Vector(L)).normalized(); best=None
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.name in skip: continue
        inv=ob.matrix_world.inverted()
        try: ok,h,n,i=ob.ray_cast(inv@Vector(L),(inv.to_3x3()@d).normalized())
        except Exception: continue
        if ok:
            p=ob.matrix_world@h; dist=(p-Vector(L)).length
            if best is None or dist<best[0]: best=(dist,ob.name)
    return best

z=DECK_Z["saloon"]; ceil=layout.room_ceiling_z("saloon")[1]
best=None
for x in [v*0.25 for v in range(-34,6)]:
    for y in [-3.6,-2.8,-2.0,0.0,2.0,2.8,3.6]:
        for zz in [1.2,1.6,2.0,2.4]:
            L=(x,y,min(z+zz,ceil-0.25))
            T=(-4.0,0.0,z+0.6)
            r=first(L,T)
            d=r[0] if r else 0
            if r and r[1]!='Masts' and d>best[0] if best else True:
                cand=(d,(round(x,2),round(y,2),round(L[2],2)),r[1])
                if best is None or d>best[0]: best=cand
print("BEST",best)
# also print the top few
res=[]
for x in [v*0.5 for v in range(-17,3)]:
    for y in [-2.6,-1.4,0.0,1.4,2.6]:
        for zz in [1.4,1.8,2.2]:
            L=(x,y,min(z+zz,ceil-0.25)); T=(-4.0,0.0,z+0.7)
            r=first(L,T)
            if r: res.append((round(r[0],2),(round(x,1),round(y,1),round(L[2],2)),r[1]))
res.sort(reverse=True)
for q in res[:8]: print("CAND",q)
