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

# ---------------------------------------------------------------------------
# Views are DERIVED from the room polygons, not hand-placed.  A hand-placed
# camera lands inside a bulkhead or a settee every time the plan changes;
# deriving it from layout.room_polygon() keeps it in the room for good.
# ---------------------------------------------------------------------------
from shipdesign import layout as _lay
from shipdesign.layout import ROOMS, room_polygon


def _room(name_part, deck):
    for r in ROOMS:
        if name_part.lower() in r["name"].lower() and r["deck"] == deck:
            return r
    raise KeyError(name_part)


def room_view(name_part, deck, eye=1.62, look_from=0.80, look_to=0.18,
              y_bias=0.0, lens=20.0, light_fracs=(0.25, 0.5, 0.75),
              power=420.0, light_h=2.25):
    """Camera at one end of a room looking down its long axis.

    look_from / look_to are fractions of the room's length; the camera stands
    just inside the wall at look_from and looks toward look_to.
    """
    r = _room(name_part, deck)
    poly = room_polygon(r)
    xs = [p[0] for p in poly]
    x0, x1 = min(xs), max(xs)
    L = x1 - x0
    cz = DECK_Z[deck]
    ceil = _lay.room_ceiling_z(deck)[1]
    zc = min(cz + eye, ceil - 0.30)
    cam_x = x0 + L * look_from
    tgt_x = x0 + L * look_to
    # stand clear of the end bulkhead and of any furniture against it
    if look_from > 0.5:
        cam_x = x0 + L * look_from - 1.6
    else:
        cam_x = x0 + L * look_from + 1.6
    tgt_x = x0 + L * look_to
    # keep both points inside the local breadth of the room
    def half_width(x):
        pts = [p[1] for p in poly if abs(p[0] - x) < max(2.0, L * 0.12)]
        return min(max(abs(v) for v in pts), r["y1"]) if pts else r["y1"]
    cy = y_bias * half_width(cam_x)
    ty = y_bias * half_width(tgt_x) * 0.5
    lights = []
    for f in light_fracs:
        lx = x0 + L * f
        zz = min(cz + light_h, ceil - 0.20)
        lights.append((lx, y_bias * half_width(lx) * 0.6, zz, power))
    return dict(loc=(cam_x, cy, zc),
                target=(tgt_x, ty, min(cz + eye * 0.62, ceil - 0.35)),
                lens=lens, lights=lights)


def _first_hit(loc, tgt):
    """Distance to the first surface along the camera axis."""
    from mathutils import Vector
    import bpy as _b
    d = (Vector(tgt) - Vector(loc)).normalized()
    best = None
    for ob in _b.data.objects:
        if ob.type != 'MESH' or not ob.visible_get():
            continue
        inv = ob.matrix_world.inverted()
        try:
            ok, hit, n, idx = ob.ray_cast(inv @ Vector(loc),
                                          (inv.to_3x3() @ d).normalized())
        except Exception:
            continue
        if ok:
            dist = ((ob.matrix_world @ hit) - Vector(loc)).length
            if best is None or dist < best:
                best = dist
    return best if best is not None else 1e6


def _nudge(view, min_clear=3.0):
    """Move the camera back until it has an unobstructed view.

    Hand-placed cameras land inside a settee, a stove or a stair far too
    easily; this measures the view and slides the camera toward the near end
    of the room until it is clear, which is exactly what a photographer does.
    """
    import bpy as _b
    loc = list(view["loc"]); tgt = list(view["target"])
    if _first_hit(loc, tgt) >= min_clear:
        return view
    direction = [tgt[i] - loc[i] for i in range(3)]
    best = (loc[:], _first_hit(loc, tgt))
    for step in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]:
        for sgn in (-1, 1):
            cand = [loc[i] - direction[i] / 1.0 * 0.0 + sgn * step *
                    (1.0 if i == 0 else 0.0) for i in range(3)]
            cand = [loc[0] + sgn * step, loc[1], loc[2]]
            clear = _first_hit(cand, tgt)
            if clear > best[1]:
                best = (cand, clear)
            if clear >= min_clear:
                view = dict(view)
                view["loc"] = tuple(cand)
                return view
    view = dict(view)
    view["loc"] = tuple(best[0])
    return view


VIEWS = {
 "grand_staircase": room_view("Entrance Hall", "saloon", eye=1.68,
                              look_from=0.92, look_to=0.10, lens=17,
                              power=430, light_fracs=(0.3, 0.6, 0.85)),
 "dining_saloon":  room_view("First Class Dining", "saloon", eye=1.66,
                             look_from=0.93, look_to=0.06, lens=19,
                             power=520, light_fracs=(0.2, 0.45, 0.7, 0.9)),
 "library":        room_view("Library", "prom", eye=1.70,
                             look_from=0.92, look_to=0.12, lens=19,
                             power=520, light_fracs=(0.3, 0.62, 0.88)),
 "smoking_saloon": room_view("Smoking", "prom", eye=1.68,
                             look_from=0.90, look_to=0.10, lens=19,
                             power=470, light_fracs=(0.3, 0.62, 0.88)),
 "music_room":     room_view("Music", "saloon", eye=1.66,
                             look_from=0.92, look_to=0.10, lens=19,
                             power=400, light_fracs=(0.35, 0.7)),
 "stateroom":      room_view("First Class staterooms", "main", eye=1.58,
                             look_from=0.14, look_to=0.88, lens=17,
                             power=230, light_fracs=(0.5,)),
 "third_class":    room_view("Third Class", "lower", eye=1.55,
                             look_from=0.12, look_to=0.9, lens=17,
                             power=380, light_fracs=(0.35, 0.7)),
 "galley":         room_view("Galley", "saloon", eye=1.62,
                             look_from=0.90, look_to=0.10, lens=17,
                             power=440, light_fracs=(0.35, 0.7)),
 "chart_house":    room_view("Chart house", "boat", eye=1.55,
                             look_from=0.10, look_to=0.9, lens=16,
                             power=190, light_fracs=(0.5,)),
 "officers_cabin": room_view("Officers", "boat", eye=1.55,
                             look_from=0.88, look_to=0.15, lens=17,
                             power=230, light_fracs=(0.4, 0.75)),
 "wheelhouse":     room_view("Wheelhouse", "bridge", eye=1.55,
                             look_from=0.10, look_to=0.9, lens=16,
                             power=180, light_fracs=(0.45, 0.8)),
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
        v = _nudge(v)
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
