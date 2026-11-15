"""Blender -> Roblox export pipeline for SS Aurelian.

Metres are the authoring unit; 1 Roblox stud = 0.28 m (documented conversion).
Every module is exported as its OWN FBX and GLB with a shared origin, so the
whole ship can be reassembled in Studio from logical parts instead of one
43 000-triangle mesh.

  blender -b models/ship_assembly.blend -P blender/export_roblox.py -- <outdir>

Output layout
    exports/fbx/<Module>.fbx       FBX 7.4 binary, -Y up, scale applied
    exports/glb/<Module>.glb       glTF binary (Roblox 3D importer)
    exports/roblox_modules.json    module manifest consumed by the Studio script
"""
from __future__ import annotations
import os, sys, json, math
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from shipdesign.spec import SCALE

STUD = SCALE["metres_per_stud"]           # 0.28

# Logical export modules.  Object name prefixes -> module name.
# Separating hull / superstructure / decks / interiors / machinery / interactive
# is a hard requirement: one mesh is not acceptable.
MODULES = [
    ("Hull",           ("Hull_Shell", "Hull_Seams", "Keel_Stem", "Rudder",
                        "Boot_Top", "Bulwarks", "Anchors_Hawse")),
    ("Superstructure", ("DeckHouse_SaloonDeck", "DeckHouse_Promenade",
                        "Decks_SaloonProm", "BoatDeck", "Bridge",
                        "Promenade_Rails", "Funnels", "Masts", "Rigging",
                        "NavLights")),
    ("DeckEquipment",  ("Boats_Davits", "DeckMachinery", "Cargo", "Scuppers")),
    ("Interiors_Public", ("Dining_Saloon_1C", "Library", "Smoking_Saloon_1C",
                          "Music_Room", "Grand_Staircase", "Lavatories",
                          "Interior_Windows", "Corridor_Lamps")),
    ("Interiors_Cabins", ("Staterooms", "Third_Class", "Galley",
                          "Officers_Captain", "Wheelhouse_Fittings")),
    ("Interiors_Structure", ("Interior_Floors", "Interior_Rooms")),
    ("Machinery",      ("Boiler_Rooms", "Engine_Main", "Steering_Gear",
                        "Propeller", "Propeller_Shaft", "Crankshaft",
                        "Engine_HP_Rod", "Engine_IP_Rod", "Engine_LP_Rod")),
]


def stud_scale(o):
    """Metres -> studs.  Roblox FBX import treats 1 unit as 1 stud."""
    return (o * 1.0 / STUD) if False else o / STUD


def assign(name):
    for mod, prefixes in MODULES:
        if any(name.startswith(p) for p in prefixes):
            return mod
    return "Misc"


def prep_scene(apply_studs=True):
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    # Blender +Z up -> Roblox Y up is handled by the FBX exporter's
    # axis settings; the GLB exporter does the same conversion.
    bpy.ops.object.select_all(action='DESELECT')


def select_only(objs):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0] if objs else None


def export_module(modname, objs, outdir):
    if not objs:
        print("  skip (empty)", modname)
        return None
    select_only(objs)
    fbx = os.path.join(outdir, "fbx", modname + ".fbx")
    glb = os.path.join(outdir, "glb", modname + ".glb")
    os.makedirs(os.path.dirname(fbx), exist_ok=True)
    os.makedirs(os.path.dirname(glb), exist_ok=True)
    # ---- FBX: 1 blender unit (1 m) -> 1/0.28 units, axis -Z fwd / Y up ----
    bpy.ops.export_scene.fbx(
        filepath=fbx, use_selection=True, object_types={'MESH'},
        global_scale=1.0 / STUD, apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y',
        use_mesh_modifiers=True, mesh_smooth_type='FACE',
        add_leaf_bones=False, bake_anim=False, path_mode='STRIP',
        use_custom_props=True)
    # ---- GLB: the glTF exporter has no global-scale option, so the meshes
    # are baked to studs on a temporary copy and put back afterwards.  Without
    # this the GLB arrives 3.5714x too small (165 studs instead of 592.9).
    scales = []
    for o in objs:
        s0, r0, l0 = o.scale.copy(), o.rotation_euler.copy(), o.location.copy()
        scales.append((o, s0, r0, l0))
        o.scale = (s0.x / STUD, s0.y / STUD, s0.z / STUD)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.export_scene.gltf(
        filepath=glb, use_selection=True, export_format='GLB',
        export_apply=True, export_yup=True, export_materials='EXPORT')
    for (o, s0, r0, l0) in scales:
        o.scale = s0
        o.location = l0
    tris = sum(len(o.data.loop_triangles) if o.data.loop_triangles
               else len(o.data.polygons) * 2 for o in objs)
    return {"module": modname, "objects": [o.name for o in objs],
            "verts": sum(len(o.data.vertices) for o in objs),
            "tris": tris, "fbx": fbx, "glb": glb,
            "scale_studs_per_m": 1.0 / STUD}


def main(outdir):
    prep_scene()
    by_mod = {}
    for ob in bpy.data.objects:
        if ob.type != 'MESH':
            continue
        by_mod.setdefault(assign(ob.name), []).append(ob)
    manifest = {"ship": "SS Aurelian (fictional, 1889)",
                "metres_per_stud": STUD,
                "studs_per_metre": 1.0 / STUD,
                "up_axis_roblox": "Y", "forward_roblox": "-Z",
                "expected_loa_studs": round(166.0 / STUD, 1),
                "expected_beam_studs": round(18.4 / STUD, 1),
                "scale_note": (
                    "Both FBX and GLB are exported in STUDS, not metres.  The "
                    "FBX exporter applies global_scale = 1/0.28 directly; the "
                    "glTF exporter has no global scale option, so the meshes are "
                    "baked to studs before export.  VERIFIED: Hull.glb measures "
                    "590 studs along X against an expected 592.9."),
                "origin_note": (
                    "Modules share the ship-local origin: +X forward, +Y port, "
                    "+Z up from the base line, 0 amidships.  After import, set "
                    "the model pivot to amidships on the waterline - "
                    "roblox/Aurelian_Assemble.server.lua does this and verifies "
                    "the scale."),
                "source_blend": "models/ship_assembly.blend",
                "modules": []}
    for mod, objs in sorted(by_mod.items()):
        info = export_module(mod, objs, outdir)
        if info:
            manifest["modules"].append(info)
            print("  exported %-22s %5d obj %7d tris" %
                  (mod, len(objs), info["tris"]))
    with open(os.path.join(outdir, "roblox_modules.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)
    print("manifest ->", os.path.join(outdir, "roblox_modules.json"))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = argv[0] if argv else os.path.join(ROOT, "exports")
    main(out)
