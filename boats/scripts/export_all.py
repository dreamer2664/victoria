"""
export_all.py -- export every finished boat to GLB and FBX, one file per
logical part (so that moving parts keep their own pivot), plus a manifest that
the Roblox importer reads.

    blender -b --python export_all.py -- [steam|rowing|both]

Output layout:
    boats/exports/<boat>/<part>.glb
    boats/exports/<boat>/<part>.fbx
    boats/exports/<boat>/manifest.json     <- pivots, sizes, roles
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bmesh
import bpy
from mathutils import Vector

ROOT = "/home/user/victoria"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["both"]
WHICH = ARGS[0] if ARGS else "both"
STUD = 1.0 / 0.28
# Roblox refuses a MeshPart over 20 000 triangles, so each part is reduced to
# fit before export.  The reduction is by edge collapse on the *export copy*
# only: the .blend keeps the full-resolution model that the renders, the
# drawings and the verification are all made from.
TRI_LIMIT = 19000

BLENDS = {
    "steam": ("boats/blend/boat_a_steam_cutter.blend", "steam_cutter_1888"),
    "rowing": ("boats/blend/boat_b_rowing_cutter.blend", "rowing_cutter_25ft"),
    "whaler": ("boats/blend/boat_c_whaler.blend", "whaler_27ft"),
}

# role of each part in the game model
ROLES = {
    "Planking_Carvel": "hull", "Inner_Diagonal_Skin": "hull", "Planking_Clinker": "hull",
    "Frames": "structure", "Keel_Stem_Frames_Gunwale": "structure",
    "Keel_Stem_Sternpost": "structure", "Transom": "structure",
    "Keelson_Gunwale": "structure", "Structure_Details": "structure",
    "Engine_Bearers_Floors": "structure",
    "Decks": "deck", "Coamings": "deck", "Canopy_Frame": "deck", "Canopy_Cover": "deck",
    "Funnel": "machinery", "Boiler": "machinery", "Boiler_Internals": "machinery",
    "Engine": "machinery", "Pipework_Fittings": "machinery", "Shafting": "machinery",
    "Propeller": "moving", "Rudder": "moving",
    "Seats": "furniture", "Thwarts_Benches": "furniture", "Thwart_Knees": "furniture",
    "Quarter_Knees": "furniture", "Floorboards": "furniture", "Mast_Clamp": "furniture",
    "Rowlocks": "gear", "Fittings": "gear", "Gear_Nav_Safety": "gear",
    "Fenders": "gear",
    "Keel_Stems": "structure", "Centreboard": "structure",
    "Masts_Yards_Rigging": "rig", "Mast_Clamp": "rig",
}


def export_boat(key):
    blend, boat_id = BLENDS[key]
    bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT, blend))
    outdir = os.path.join(ROOT, "boats", "exports", key)
    os.makedirs(outdir, exist_ok=True)
    manifest = {"boat_id": boat_id, "units": "metres", "roblox_stud_per_m": STUD,
                "source": blend, "parts": []}

    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    # objects whose names look like Oar_* are moving parts too
    for ob in sorted(meshes, key=lambda o: o.name):
        role = ROLES.get(ob.name, "moving" if ob.name.startswith("Oar") else "other")
        # triangle count: loop_triangles is empty until it is calculated, and
        # the old code silently fell back to counting quads and ngons, which
        # under-reported the real load a Roblox import would see
        ob.data.calc_loop_triangles()
        tris = len(ob.data.loop_triangles)
        reduced = 0
        if tris > TRI_LIMIT:
            mod = ob.modifiers.new("Decimate", "DECIMATE")
            mod.ratio = TRI_LIMIT / float(tris)
            mod.use_collapse_triangulate = True
            bpy.context.view_layer.objects.active = ob
            bpy.ops.object.modifier_apply(modifier=mod.name)
            ob.data.calc_loop_triangles()
            reduced = tris
            tris = len(ob.data.loop_triangles)
        # a UV layer, so the part can take a texture rather than only a colour
        if not ob.data.uv_layers:
            ob.data.uv_layers.new(name="UVMap")
        # world-space bounds
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        org = ob.matrix_world.translation
        manifest["parts"].append({
            "name": ob.name,
            "role": role,
            "origin_m": [round(v, 4) for v in org],
            "bounds_min_m": [round(v, 4) for v in mn],
            "bounds_max_m": [round(v, 4) for v in mx],
            "size_m": [round(v, 4) for v in (mx - mn)],
            "size_studs": [round(v * STUD, 3) for v in (mx - mn)],
            "vertices": len(ob.data.vertices),
            "triangles": tris,
            "triangles_before_decimation": reduced or tris,
            "uv_layers": len(ob.data.uv_layers),
            "smooth_shaded": True,
        })
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        safe = ob.name.replace(" ", "_")
        bpy.ops.export_scene.gltf(filepath=os.path.join(outdir, safe + ".glb"),
                                  export_format="GLB", use_selection=True,
                                  export_apply=True, export_yup=True)
        bpy.ops.export_scene.fbx(filepath=os.path.join(outdir, safe + ".fbx"),
                                 use_selection=True, object_types={"MESH"},
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z",
                                 axis_up="Y", mesh_smooth_type="FACE", use_mesh_modifiers=True)
        ob.select_set(False)
    # whole-boat GLB for preview / quick import
    bpy.ops.object.select_all(action="DESELECT")
    for ob in meshes:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.export_scene.gltf(filepath=os.path.join(outdir, "boat_complete.glb"),
                              export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True)
    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("EXPORTED", key, len(meshes), "parts ->", outdir)


for k in (list(BLENDS) if WHICH == "both" else [WHICH]):
    export_boat(k)
print("EXPORT COMPLETE")
