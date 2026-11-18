"""
build2_rowing_cutter.py -- THEMISTOCLES-II 25 ft clinker rowing cutter (10-oared,
double-banked).  Assembles the complete boat in Blender 4.2 and saves the
.blend.  All geometry comes from boatgen's documented principal dimensions
(beam 6 ft 3 in) with second-generation construction detail.
"""
import os, sys, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO_BOATS = os.path.dirname(HERE)

import bpy
from them2.hull2 import Hull2
from them2 import structure2 as st
from them2 import parts2 as P
from them2 import boatlib2 as BL
from them2 import specs2 as S
from them2 import bl2
from them2 import geom2 as G
from them2.geom2 import MB, cyl, dome, torus, sphere, rot_z, lerp, clamp
import them2.mats2 as M


def main(quick=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    hull = S.rowing_cutter_hull()
    hull, loaded, light = S.reconcile(hull, S.ROW_WEIGHTS)

    objects = {}
    meta = {"id": "rowing_cutter_25ft", "loaded": loaded, "light": light,
            "weights": S.ROW_WEIGHTS, "pivots": {}}

    # ---- hull skins ----------------------------------------------------------
    plan = st.clinker_strakes(hull, 11, 0.016, nx=55, npb=12,
                              mat=0, mat_top=22)
    plan.mirror_y()
    objects["Planking_Clinker"] = plan

    keel = st.keel_assembly(hull, sided=0.048, depth=0.105, mat=2)
    keel.append(st.stem_post(hull, moulded=0.105, sided=0.050, mat=2))
    objects["Keel_Stem_Sternpost"] = keel

    objects["Transom"] = st.transom_plate(hull, thk=0.052, mat=0, mat_edge=2)

    fr = st.frames(hull, 11, 0.016, spacing=0.150, siding=0.022, mould_lo=0.042,
                   mould_hi=0.024, mat=2)
    fr.mirror_y()
    objects["Frames"] = fr

    ks = st.keelson(hull, depth=0.14, sided=0.075, mat=2)
    keelson = ks
    objects["Keelson"] = ks

    gw = st.gunwale_set(hull, 11, 0.016, cap_w=0.080, cap_h=0.030, mat_cap=1,
                        mat_inwale=2, mat_rub=10)
    gw.append(st.stem_band(hull, mat=3))
    gw.mirror_y()
    objects["Gunwale_Inwale_Rubstrake"] = gw

    bh = st.breasthook(hull, length=0.60, thk=0.038, mat=2)
    objects["Breasthook_Knees"] = bh

    # ---- rowing furniture ----------------------------------------------------
    stations_oar = [2.02, 1.18, 0.34, -0.50, -1.34]      # rowlock stations
    stations_thw = [x + 0.42 for x in stations_oar]       # thwarts fwd of rowlocks
    tinfo = BL.thwart_layout(hull, stations_thw, z_top=0.100, mat=1, mat_knee=2)
    objects["Thwarts"] = tinfo["thwarts"]
    objects["Thwart_Knees"] = tinfo["knees"]
    objects["Risers"] = tinfo["risers"]

    # stern sheets: side benches + after thwart (already a thwart at stern), bow sheets
    benches, knees = BL.side_bench_pair(hull, z=0.30, width=0.30,
                                        xi_range=(0.86, 0.985), mat=1)
    benches.mirror_y(); knees.mirror_y()
    objects["Stern_Sheets"] = benches
    objects["Stern_Knees"] = knees
    bowls, bknees = BL.side_bench_pair(hull, z=0.30, width=0.26,
                                       xi_range=(0.045, 0.13), mat=1)
    bowls.mirror_y(); bknees.mirror_y()
    objects["Bow_Sheets"] = bowls
    objects["Bow_Knees"] = bknees

    # foot gratings (slatted) between thwarts, two panels
    zgr = hull.keel_z(0.5) + 0.115
    gr = P.foot_grating(-1.20, -0.10, 0.26, zgr + 0.02, mat=1)
    gr.append(P.foot_grating(0.16, 1.30, 0.275, zgr + 0.03, mat=1))
    objects["Floor_Gratings"] = gr

    # stretchers under each thwart zone
    str_mb = MB("Stretchers")
    for xs in stations_oar:
        str_mb.append(P.stretcher(hull, (hull.loa / 2 - xs) / hull.loa,
                                  z=hull.keel_z(clamp((hull.loa / 2 - xs) / hull.loa, 0, 1)) + 0.34,
                                  w=0.42, mat=1))
    objects["Stretchers"] = str_mb

    # ---- rowlocks + oars -----------------------------------------------------
    row_mb, pivots = BL.rowlocks(hull, stations_oar, 0.0, sides=(-1, 1))
    objects["Rowlocks"] = row_mb
    meta["pivots"]["rowlocks"] = [{"x": p["x"], "y": round(float(p["y"]), 4),
                                   "z": round(float(p["z"]), 4), "side": p["side"]}
                                  for p in pivots]

    oar_set = BL.build_oar_set(hull, pivots, length=3.66, inboard_frac=0.34)
    oar_objs = []   # [(name, mb, pivot)]
    meta["pivots"]["oars_moving"] = []
    for i, oi in enumerate(oar_set):
        xs = oi["station_x"]
        station_i = stations_oar.index(xs) + 1
        side_tag = "P" if oi["side"] > 0 else "S"   # +Y = port (spec frame)
        pv = oi["pivot"]
        meta["pivots"]["oars_moving"].append({
            "part": f"Oar_{side_tag}{station_i}",
            "pivot_world": [round(float(v), 4) for v in pv],
            "side": "port(+Y)" if oi["side"] > 0 else "starboard(-Y)",
            "station_x": xs, "length_m": 3.66,
            "stowed_rot_z_deg_from_outboard": 90.0})
        oar_objs.append((f"Oar_{side_tag}{station_i}", oi["mb"], pv))
    # standalone stowed view mesh (single merged object is kept in the .blend only)

    # ---- rig (stowed): ketch dipping lug --------------------------------------
    rig = BL.rigging_stowed(hull, {
        "masts": [("main", 0.30, 5.10, 0.034), ("fore", 1.55, 4.30, 0.030)],
        "yards": [("main", 4.42, 0.030, 0.0), ("fore", 3.60, 0.026, 0.0)],
        "yard_x": -0.30,
    })
    rigm = MB("Rig_Stowed")
    for rmb in rig:
        rigm.append(rmb)
    objects["Rig_Stowed"] = rigm

    # mast step + clamp on the bow thwart (documented on SLR0719)
    objects["Mast_Fit"] = BL.mast_step_clamp(hull, x_step=0.30,
                                             z_kelson=hull.keel_z(0.5) + 0.12,
                                             thwart_x=stations_thw[0])
    # lifting eyes (documented pair on SLR1818)
    objects["Lifting_Eyes"] = BL.lifting_eyes(hull, [1.95, -1.60],
                                              z=hull.keel_z(0.5) + 0.26)
    meta["pivots"]["lifting_eyes_x"] = [1.95, -1.60]

    # ---- rudder + tiller -----------------------------------------------------
    rud, axis_pt, axis_dir = P.rudder_plate(hull, mat=0, mat_iron=4)
    objects["Rudder_Tiller"] = rud
    meta["pivots"]["rudder_axis"] = list(map(lambda v: round(float(v), 4), axis_pt))

    # ---- ring bolts + painter eye at stem --------------------------------------
    eyemb = MB("Ring_Bolts")
    for (xx, sgn) in ((hull.loa / 2 - 0.06, 1), (-hull.loa / 2 + 0.10, -1)):
        zr = hull.sheer_z(0.02 if sgn > 0 else 0.985)
        cyl(eyemb, (xx, 0, zr - 0.10), (xx, 0, zr + 0.02), 0.012, seg=10, mat=5)
        torus(eyemb, (xx, 0, zr + 0.05), 0.032, 0.010, seg=12, rseg=6, axis="Y", mat=5)
    objects["Ring_Bolts"] = eyemb

    # ---- standard gear ---------------------------------------------------------
    for name, gmb in BL.standard_gear(hull, kind="rowing"):
        objects[name] = gmb

    # compass on the after thwart (coxswain's), small binnacle
    objects["Compass"] = P.compass_binnacle((2.44 - 0.0, 0.0, 0.10 + 0.003),
                                            mat_brass=3)

    # ---- to Blender ------------------------------------------------------------
    coll = bpy.data.collections.new("ROWING_CUTTER")
    scene.collection.children.link(coll)
    made = {}
    for name, mb in objects.items():
        if len(mb.verts) == 0 or name == "Rudder_Tiller":
            continue
        made[name] = bl2.mb_to_object(mb, name, coll=coll)

    # moving parts with pivot origins
    rud = objects["Rudder_Tiller"]
    made["Rudder"] = bl2.mb_to_object(rud, "Rudder", coll=coll,
                                      origin_at=meta["pivots"]["rudder_axis"])
    for nm, omb, pv in oar_objs:
        made[nm] = bl2.mb_to_object(omb, nm, coll=coll, origin_at=pv)

    # ---- scene ------------------------------------------------------------------
    os.makedirs(os.path.join(REPO_BOATS, "blend"), exist_ok=True)
    blend_path = os.path.join(REPO_BOATS, "blend", "boat_b2_rowing_cutter.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    with open(os.path.join(REPO_BOATS, "blend", "boat_b2_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print("BUILT ROWING CUTTER: %d parts" % len(made))
    info = {k: bl2.mesh_info(o) for k, o in made.items()}
    for k, v in info.items():
        print("  %-26s v=%6d f=%6d tri=%6d dims=%s" % (k, v["verts"], v["faces"], v["tris"], v["dims"]))
    return made, meta, hull


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    main(quick=quick)
