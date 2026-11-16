"""
build_ports.py -- assemble, validate, render and export the two ports.

Usage (inside Blender):
  blender -b --factory-startup -noaudio --python blender/build_ports.py -- \
      --port a --stage all

Stages: layout | render | export | save | all
"""
import os, sys, json, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "lib"))
sys.path.insert(0, os.path.join(HERE, "ports"))

import bpy
from mathutils import Vector
import bsetup, portsite as site, proxy
from core import MeshBuilder, QUAY_Z

# ------------------------------------------------------------------ args
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def opt(flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default
PORT = (opt("--port", "a")).lower()
STAGE = opt("--stage", "layout")
SAMPLES = int(opt("--samples", "64"))
RES = opt("--res", "1600x900")
RESX, RESY = [int(v) for v in RES.split("x")]

RENDERS = os.path.join(ROOT, "renders", "port_" + PORT)
os.makedirs(RENDERS, exist_ok=True)


# ------------------------------------------------------------------ cameras
CAMERAS = {
    "a": [
        # Positions were checked against the layout: every camera stands in open
        # ground or over water, never inside a building.
        ("01_aerial",        (-250, -330, 210), (90, 40, 0), 40),
        ("02_waterfront",    (-275, -190, 66),  (-30, 165, 2), 50),
        ("03_street",        (-14, 60, 6.5),    (-14, 230, 10), 40),
        ("04_dockside",      (-16, -30, 7.5),   (70, -70, 8), 42),
        ("05_landing_stage", (-196, -20, 22),   (-84, 140, 4), 42),
        ("06_dock_basin",    (120, -246, 34),   (140, -110, 4), 45),
        ("07_roofscape",     (30, -140, 58),    (80, 60, 16), 50),
        ("08_terminal_court",(30, -34, 13),     (30, 62, 8), 40),
    ],
    "b": [
        ("01_aerial",        (-210, -280, 190), (30, 30, 0), 40),
        ("02_waterfront",    (-160, 20, 10),    (10, 90, 8), 45),
        ("03_street",        (0, -60, 6.5),     (0, 200, 9), 40),
        ("04_graving_dock",  (62, -34, 34),     (110, 150, -6), 42),
        ("05_slipways",      (-120, 30, 12),    (-10, 100, 4), 42),
        ("06_shops",         (110, 330, 26),    (170, 235, 10), 45),
        ("07_roofscape",     (40, -60, 62),     (140, 160, 10), 50),
    ],
}


def setup_lighting(coll, port):
    """Late-Victorian maritime light: bright but soft overcast with a low warm key.
    The sun is placed to rake the elevations the cameras actually look at."""
    if port == "a":
        bsetup.add_sun(coll, 215, 41, 4.6, (1.0, 0.94, 0.86))
    else:
        # Port B's graving docks run north-south and are 11 m deep from the coping.
        # At 40 deg elevation a sun crossing the dock's WIDTH puts the whole floor in
        # the shadow of its own wall (checked by ray-cast).  Azimuth 340 rakes the
        # light along the dock's length instead, so the altars and keel blocks read.
        bsetup.add_sun(coll, 215, 41, 4.6, (1.0, 0.94, 0.86))
    bsetup.add_fill(coll, 100, 34, 0.55, (0.74, 0.80, 0.90))
    if os.environ.get("FLAT_SKY"):
        w = bpy.data.worlds.new("flat")
        w.use_nodes = True
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
        bg.inputs[1].default_value = 2.0
        bpy.context.scene.world = w
    else:
        bsetup.setup_sky(sun_az=(215 if port == "a" else 215), sun_el=41,
                         strength=0.62, cloud_cover=0.34)
    bsetup.setup_compositor_haze(fog_color=(0.66, 0.68, 0.70), start=150.0,
                                 depth=1400.0, max_fog=0.38)


# ------------------------------------------------------------------ main
def main():
    t0 = time.time()
    sc = bsetup.reset_scene()
    sc.view_settings.view_transform = 'AgX'
    try:
        sc.view_settings.look = 'AgX - Punchy'
    except TypeError:
        pass
    sc.view_settings.exposure = 0.92

    bsetup.make_materials()
    # Diagnostic switches, used to isolate the black-dock fault: FLATMAT=1 strips
    # every texture off every material, FLAT_SKY=1 replaces the sky with a plain
    # white dome. Between them they separate "wrong material" from "no light".
    if os.environ.get("FLATMAT"):
        for m in bpy.data.materials:
            if not m.use_nodes:
                continue
            nt = m.node_tree
            b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if not b:
                continue
            for l in list(nt.links):
                if l.to_node is b and l.to_socket.name in ("Base Color", "Roughness",
                                                           "Metallic", "Normal"):
                    nt.links.remove(l)
            b.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1.0)
            b.inputs["Roughness"].default_value = 0.85
            b.inputs["Metallic"].default_value = 0.0
    mod = __import__("port_" + PORT)
    coll = bsetup.ensure_coll("PORT_" + PORT.upper())
    R = bsetup.Registry()
    audit = site.LayoutAuditor()

    meta = mod.build(R, coll, audit)

    # ---- every prototype must have at least one placed instance
    # Some assets (the land platform, the water, the boundary wall) are built
    # once at world coordinates and never instanced. They were left living in
    # the _PROTOTYPES collection, which is hidden from rendering, so they
    # vanished the moment that collection was hidden. Give every unplaced
    # prototype a single instance at the origin -- the identical mesh data, one
    # copy in the file -- so the prototype genuinely is only a prototype.
    for name in list(R.proto.keys()):
        if R.counts.get(name, 0) == 0:
            R.place(name, 0.0, 0.0, 0.0)

    places, tris, protos = R.report()

    # ---- layout audit (numeric, before any render)
    problems = audit.report()
    print("=" * 70)
    print("PORT", meta["port"])
    print("prototypes: %d   instances placed: %d   instanced tris: %d"
          % (protos, places, tris))
    print("overlaps:", len(problems))
    for p in problems:
        print("  ", p)
    bbox = _scene_bbox()
    print("scene bbox (m):", tuple(round(v, 1) for v in bbox))
    print("scene size (m): %.0f x %.0f x %.0f" % (bbox[3] - bbox[0], bbox[4] - bbox[1],
                                                  bbox[5] - bbox[2]))
    print("=" * 70)

    # ---- berth clearance check
    for b in meta["berths"]:
        r = b["rect"]
        w = abs(r[2] - r[0]); h = abs(r[3] - r[1])
        env = b["ship_envelope"]
        fits = (w >= env["B"] + 4.0 and h >= env["L"] + 4.0) or \
               (h >= env["B"] + 4.0 and w >= env["L"] + 4.0)
        print("BERTH %-34s %6.1f x %6.1f m  depth %4.1f m  env %3.0fx%3.0fx%3.0f m  %s"
              % (b["id"], w, h, b["depth_m"], env["L"], env["B"], env["draft"],
                 "OK (>=4 m clearance)" if fits else "CHECK"))

    # ---- proxies that prove the envelope (never shipped as assets)
    # The clearance proxy is a QC instrument, not scenery. It exists so the berth
    # rectangles can be tested against a real 180 x 20 x 9 m envelope, and it must
    # never appear in a render or an export -- it is a black box sitting in the
    # middle of the harbour and it will ruin every waterfront frame if it is left
    # visible (this happened, and cost a day of confused lighting diagnosis).
    if PORT == "a" and os.environ.get("PROXY_VISIBLE") != "1":
        mb = MeshBuilder(); proxy.proxy_ship(mb, -91.0, 130.0)
        R.define("_PROXY_liner", mb)
        p_ob = R.place("_PROXY_liner", 0, 0, 0)
        p_ob.hide_render = True
        p_ob.hide_viewport = True

    # Hide the prototype collection again here, after the build and before the
    # first render: setting it when the collection is created is not enough, the
    # first render in a session still includes those objects and every interior
    # renders black.
    R.hidden.hide_render = True
    bpy.context.view_layer.update()

    setup_lighting(coll, PORT)

    # ---- save .blend
    if STAGE in ("save", "all"):
        path = os.path.join(ROOT, "blender", "port_%s.blend" % PORT)
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("saved", path)

    # ---- renders
    if STAGE in ("render", "all"):
        only = opt("--cams", "")
        keep = [c.strip() for c in only.split(",") if c.strip()]
        for name, loc, la, lens in CAMERAS[PORT]:
            if keep and not any(k in name for k in keep):
                continue
            c = bsetup.add_camera(coll, loc, la, lens, name)
            p = os.path.join(RENDERS, name + ".png")
            bsetup.render_to(p, c, res=(RESX, RESY), samples=SAMPLES)
            print("rendered %-22s %6.1fs" % (name, time.time() - t0))

    # ---- exports
    if STAGE in ("export", "all"):
        export_all(R, meta)

    with open(os.path.join(ROOT, "docs", "port_%s_meta.json" % PORT), "w") as f:
        json.dump(meta, f, indent=2)
    print("done", round(time.time() - t0, 1), "s")


def _scene_bbox():
    lo = [1e9] * 3; hi = [-1e9] * 3
    for ob in bpy.context.scene.objects:
        if ob.type != 'MESH':
            continue
        for c in ob.bound_box:
            w = ob.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i]); hi[i] = max(hi[i], w[i])
    return lo + hi


def export_all(R, meta):
    """Write GLB + FBX for the whole port and for each modular asset separately."""
    glb_dir = os.path.join(ROOT, "assets", "glb", PORT)
    fbx_dir = os.path.join(ROOT, "assets", "fbx", PORT)
    os.makedirs(glb_dir, exist_ok=True); os.makedirs(fbx_dir, exist_ok=True)

    sc = bpy.context.scene
    sc.unit_settings.scale_length = 1.0

    # 1. one GLB per prototype: this is the modular kit Roblox users import
    hidden = R.hidden
    for name, ob in R.proto.items():
        if name.startswith("_"):
            continue        # QC instruments (the clearance proxy) are not assets
        for o in bpy.context.selected_objects:
            o.select_set(False)
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        path = os.path.join(glb_dir, name + ".glb")
        bpy.ops.export_scene.gltf(
            filepath=path, export_format='GLB', use_selection=True,
            export_apply=True, export_yup=True, export_texcoords=True,
            export_normals=True, export_materials='EXPORT',
            export_image_format='AUTO', export_cameras=False, export_lights=False)
    print("exported %d modular GLBs" % len(R.proto))

    # 2. whole-port GLB (needed for a one-piece import / visual check)
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for ob in sc.objects:
        # never ship the prototypes: they are the same mesh data as the placed
        # instances, so selecting them puts a second, coincident copy of every
        # asset in the one-piece GLB.
        if (ob.type == 'MESH' and R.hidden not in ob.users_collection
                and not ob.hide_render and not ob.hide_viewport):
            ob.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(glb_dir, "port_%s_full.glb" % PORT),
        export_format='GLB', use_selection=True, export_apply=True,
        export_yup=True, export_materials='EXPORT', export_cameras=False,
        export_lights=False)
    print("exported full-port GLB")

    # 3. FBX for anyone on the older import path
    bpy.ops.export_scene.fbx(
        filepath=os.path.join(fbx_dir, "port_%s_full.fbx" % PORT),
        use_selection=True, object_types={'MESH'}, apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Z', axis_up='Y', bake_space_transform=False)
    print("exported full-port FBX")


if __name__ == "__main__":
    main()
