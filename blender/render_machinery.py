"""ENGINE-ROOM CUTAWAY + MACHINERY RENDERS

Produces the two required technical-mood shots:
  * engine_room_cutaway  - looking aft along the shaft line, the ship's side
                           and decks cut away, boilers and engine lit
  * machinery_detail      - close three-quarter of the engine, cylinders,
                            connecting rods and crankshaft

The cutaway is made by hiding the shell and deck "skin" objects, not by
boolean-cutting the mesh, so the exported model stays intact.
"""
from __future__ import annotations
import os, sys, math
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from shipdesign.spec import DECK_Z
from lib_build import build_palette

# The cutaway is produced by bisecting every object on the centreline and
# discarding the port half, so the machinery is seen through the opened ship's
# side exactly as in a builder's cutaway drawing.  These top-sides objects go
# entirely: cutting them away is what makes it a *cutaway* rather than a
# section.
SECTION_ONLY = ("Hull_Shell", "Hull_Seams", "Keel_Stem", "Rudder",
                "Boot_Top", "Bulwarks")

REMOVE_ENTIRELY = ("Funnels", "Masts", "Rigging", "Boats_Davits", "BoatDeck",
                   "Bridge", "DeckHouse_Promenade", "DeckHouse_SaloonDeck",
                   "Decks_SaloonProm", "Promenade_Rails", "DeckMachinery",
                   "NavLights", "Anchors_Hawse", "Boot_Top", "Bulwarks",
                   "Interior_Rooms", "Interior_Floors", "Interior_Windows",
                   "Staterooms", "Third_Class", "Galley", "Library",
                   "Music_Room", "Smoking_Saloon_1C", "Dining_Saloon_1C",
                   "Grand_Staircase", "Lavatories", "Officers_Captain",
                   "Wheelhouse_Fittings")


def clear_scene_extras():
    for ob in list(bpy.data.objects):
        if ob.type in ("CAMERA", "LIGHT"):
            bpy.data.objects.remove(ob, do_unlink=True)


def setup_cutaway(bisect=True):
    clear_scene_extras()
    keep = []
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH':
            continue
        if any(ob.name.startswith(h) for h in REMOVE_ENTIRELY):
            bpy.data.objects.remove(ob, do_unlink=True)
        else:
            keep.append(ob)
    if bisect:
        # Cut ONLY the hull structure on the centreline; the machinery is left
        # whole.  A section drawing that halves a cylinder shows an open
        # shell - a cutaway keeps the plant intact and removes the ship's side
        # in front of it.  This is the cutaway convention and it is far more
        # legible.
        for ob in keep:
            if ob.name.startswith(SECTION_ONLY):
                _bisect_keep_neg_y(ob)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    world = bpy.data.worlds.new("W")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.02, 0.022, 0.025, 1)
    bg.inputs[1].default_value = 1.0


def _bisect_keep_neg_y(ob):
    """Delete everything with y > 0 from an object (Blender mesh bisect)."""
    import bmesh
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0),
                           plane_no=(0, 1, 0), clear_outer=True,
                           clear_inner=False)
    bm.to_mesh(me)
    bm.free()
    # give the opened edge a little thickness so it reads as plate, not paper
    sol = ob.modifiers.new("CutFace", 'SOLIDIFY')
    sol.thickness = 0.05
    sol.offset = 0.0


def add_light(loc, power, size, color=(1, 1, 1), name="L"):
    d = bpy.data.lights.new(name, 'AREA')
    d.energy = power; d.size = size; d.color = color
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    v = Vector((0, 0, 0)) - Vector(loc)
    ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    return ob


def add_cam(loc, tgt, lens=24.0, name="Cam"):
    d = bpy.data.cameras.new(name); d.lens = lens
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    v = Vector(tgt) - Vector(loc)
    ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = ob
    return ob


def render(path, w=1600, h=1000, samples=48):
    sc = bpy.context.scene
    sc.render.resolution_x = w; sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.render.filepath = path
    sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)


def cutaway_views(outdir):
    os.makedirs(outdir, exist_ok=True)
    # fill light standing in the opened port half (soft, from outboard)
    for x in (-64.0, -44.0, -24.0, -4.0, 16.0):
        add_light((x, 6.5, 9.0), 900, 9.0, (1.0, 0.82, 0.62), "FillX")
    for x in (-2.0, 9.0, 20.0):
        add_light((x, 2.0, 7.6), 380, 3.0, (1.0, 0.62, 0.32), "BoilerGlow")
    add_light((-18.0, 2.0, 7.0), 420, 3.2, (1.0, 0.70, 0.42), "EngLamp")
    add_light((-46.0, 2.0, 3.4), 260, 3.0, (0.72, 0.84, 1.0), "ShaftLamp")
    add_light((-74.0, 1.5, 3.0), 220, 3.0, (0.62, 0.78, 1.0), "SternLamp")

    # ---- 1. orthographic longitudinal section, engine -> propeller -----
    cd = bpy.data.cameras.new("SectionCam")
    cd.type = 'ORTHO'
    cd.ortho_scale = 88.0
    cam = bpy.data.objects.new("SectionCam", cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (-33.0, 70.0, 9.5)
    v = Vector((-33.0, 0.0, 9.5)) - Vector(cam.location)
    cam.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = cam
    render(os.path.join(outdir, "engine_room_cutaway.png"), 1800, 640, 96)

    # ---- 2. perspective three-quarter of the main engine ---------------
    add_cam((-9.0, 9.5, 7.2), (-19.5, 0.2, 3.8), 32.0, "EngineCam")
    render(os.path.join(outdir, "machinery_detail.png"), 1400, 1000, 72)

    # ---- 3. down the shaft alley to the stern tube and propeller -------
    add_cam((-34.0, 5.6, 3.9), (-76.0, 0.0, 2.0), 34.0, "ShaftCam")
    render(os.path.join(outdir, "shaft_alley.png"), 1600, 760, 64)


if __name__ == "__main__":
    argv = sys.argv
    outdir = os.path.join(ROOT, "renders", "machinery")
    if "--" in argv:
        rest = argv[argv.index("--") + 1:]
        if rest:
            outdir = rest[0]
    setup_cutaway()
    cutaway_views(outdir)
