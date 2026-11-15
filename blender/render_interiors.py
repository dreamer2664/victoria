"""Interior render pass - camera inside each principal space, period lighting."""
import os, sys, math, bpy
from mathutils import Vector
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
for p in (ROOT,HERE):
    if p not in sys.path: sys.path.insert(0,p)
from shipdesign.spec import DECK_Z

def setup(samples=64, res=(1280,800)):
    sc=bpy.context.scene
    sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=samples
    sc.cycles.use_denoising=True; sc.cycles.max_bounces=4
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform='AgX'
    sc.view_settings.look='AgX - Medium High Contrast'
    w=bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world=w; w.use_nodes=True
    bg=w.node_tree.nodes.get("Background")
    if bg: bg.inputs[0].default_value=(0.05,0.055,0.06,1); bg.inputs[1].default_value=0.35

def add_light(loc, energy=120, size=2.2, colour=(1.0,0.93,0.84), name="L"):
    l=bpy.data.lights.new(name,'AREA'); l.size=size; l.energy=energy; l.color=colour
    ob=bpy.data.objects.new(name,l); bpy.context.scene.collection.objects.link(ob)
    ob.location=loc
    return ob

def point_at(ob, target):
    d=Vector(target)-Vector(ob.location)
    ob.rotation_mode='QUATERNION'
    ob.rotation_quaternion=d.to_track_quat('-Z','Y')

def cam(loc, target, lens=24):
    c=bpy.data.cameras.new("ICam"); c.lens=lens; c.clip_start=0.03; c.clip_end=400
    ob=bpy.data.objects.new("ICam",c); bpy.context.scene.collection.objects.link(ob)
    ob.location=loc; point_at(ob,target); bpy.context.scene.camera=ob
    return ob

# Camera/light heights are DERIVED from the deck schedule - never hard-coded,
# so a change to the deck heights can never leave a camera under the floor
# again.
def v(deck, dz, loc, target, lens, lights, dt=None):
    """Build a view; clamp camera and lights UNDER the real ceiling of the
    deck (ceilings are the deck above, so a naive offset can put a lamp in
    the void above the ceiling and render the room black)."""
    import sys as _s
    sys.path.insert(0, ROOT)
    from shipdesign import layout as _lay
    z = DECK_Z[deck]
    ceil = _lay.room_ceiling_z(deck)[1]
    zc = min(z + dz, ceil - 0.25)
    lt = []
    for l in lights:
        zz = min(z + l[2], ceil - 0.18)
        lt.append((l[0], l[1], max(zz, z + 0.35), l[3]))
    return dict(loc=(loc[0], loc[1], zc),
                target=(target[0], target[1],
                        min(z + dz * 0.42, ceil - 0.3)),
                lens=lens, lights=lt)

VIEWS = {
 "grand_staircase": v("saloon", 1.70, (6.8, -1.9, 0), (-6.0, 0.2), 18,
                      [(0.0, 0, 2.3, 420), (-6.0, 0, 1.4, 300)]),
 "dining_saloon":  v("saloon", 1.65, (-10.0, -1.0, 0), (-42.0, 0.0, 0.3), 20,
                      [(-16, 0, 2.3, 520), (-27, 0, 2.3, 520), (-38, 0, 2.3, 520)]),
 "library":        v("prom", 1.70, (25.0, -1.2, 0), (12.0, 0.0), 20,
                      [(20, 0, 2.3, 520), (15, 0, 1.2, 320)]),
 "smoking_saloon": v("prom", 1.70, (-11.0, -2.4, 0), (-22.0, 0.0, 0.1), 20,
                      [(-14, 0, 2.3, 480), (-20, 0, 2.3, 480)]),
 "music_room":     v("saloon", 1.70, (26.0, -1.4, 0), (13.0, 0.0, 0.2), 20,
                      [(21, 0, 2.3, 420), (16, 0, 2.3, 380)]),
 "grand_staircase2": v("prom", 1.70, (6.0, -1.6, 0), (-4.0, 0.0, -1.2), 20,
                      [(2, 0, 2.3, 420)]),
 "stateroom":      v("main", 1.60, (13.5, -3.4, 0), (19.5, 1.2, 0.4), 16,
                      [(17, 0, 2.2, 220)]),
 "third_class":    v("lower", 1.55, (46.0, -2.0, 0), (62.0, 0.0, 0.3), 18,
                      [(52, 0, 2.1, 380), (60, 0, 2.1, 380)]),
 "galley":         v("saloon", 1.65, (-46.0, -2.4, 0), (-55.0, 0.0, 0.2), 18,
                      [(-50, 0, 2.3, 420)]),
 "forecastle":     v("main", 1.55, (68.0, -1.6, 0), (77.0, 0.0, 0.2), 16,
                      [(73, 0, 2.2, 260)]),
 "wheelhouse":     v("bridge", 1.40, (12.5, -2.2, 0), (19.0, 0.0, 0.1), 16,
                      [(17, 0, 1.9, 160), (14, 0, 1.6, 120)]),
}

if __name__=="__main__":
    argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    outdir=argv[0] if argv else os.path.join(ROOT,"renders","interiors_wip")
    only=argv[1].split(",") if len(argv)>1 else None
    samples=int(argv[2]) if len(argv)>2 else 48
    os.makedirs(outdir,exist_ok=True)
    setup(samples)
    for name,v in VIEWS.items():
        if only and name not in only: continue
        for i,lt in enumerate(v["lights"]):
            add_light(lt[:3], lt[3], name="%s_L%d"%(name,i))
        cam(v["loc"], v["target"], v["lens"])
        bpy.context.scene.render.filepath=os.path.join(outdir,name+".png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED",name)
        # remove lights again for the next room
        for ob in list(bpy.data.objects):
            if ob.type=='LIGHT': bpy.data.objects.remove(ob, do_unlink=True)
        for ob in list(bpy.data.objects):
            if ob.type=='CAMERA': bpy.data.objects.remove(ob, do_unlink=True)
