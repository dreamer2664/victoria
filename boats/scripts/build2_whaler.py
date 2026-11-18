"""
build2_whaler.py -- 27 ft double-ended whaler (5-oared, dipping lug rig stowed,
centreboard).  Same library chain as the rowing cutter; distinctive features:
double-ended hull, centreboard + case, rubboard, 5 thwarts, harpoon locker,
painter at both stems.
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
from them2.geom2 import MB, cyl, dome, torus, sphere, rot_z, lerp, clamp
from them2.structure2 import aft_stem


def main(quick=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    hull = S.whaler_hull()
    hull, loaded, light = S.reconcile(hull, S.WHALER_WEIGHTS)

    objects = {}
    meta = {"id": "whaler_27ft", "loaded": loaded, "light": light,
            "weights": S.WHALER_WEIGHTS, "pivots": {}}

    plan = st.clinker_strakes(hull, 9, 0.016, nx=48, npb=10, mat=25, mat_top=22)
    plan.mirror_y()
    objects["Planking_Clinker"] = plan
    keel = st.keel_assembly(hull, sided=0.048, depth=0.105, mat=2)
    keel.append(st.stem_post(hull, moulded=0.105, sided=0.050, mat=2))
    # double-ended: stem-like sternpost at xi=1 (separate object for material order)
    objects["Stern_Post"] = aft_stem(hull, moulded=0.105, sided=0.050, mat=2)
    # (GEN-1: a second, coincident "Bow_Stem" copy of the stem was removed)
    objects["Keel"] = keel
    fr = st.frames(hull, 9, 0.016, spacing=0.160, siding=0.022, mould_lo=0.040,
                   mould_hi=0.024, mat=2)
    fr.mirror_y()
    objects["Frames"] = fr
    objects["Keelson"] = st.keelson(hull, depth=0.13, sided=0.070, mat=2)
    gw = st.gunwale_set(hull, 9, 0.016, cap_w=0.078, cap_h=0.028, mat_cap=1,
                        mat_inwale=2, mat_rub=10)
    gw.mirror_y()
    objects["Gunwale_Set"] = gw
    objects["Breasthooks"] = st.breasthook(hull, length=0.55, thk=0.036)  # fwd hook

    # centreboard + case (lowered plate shown, per davit spec)
    z_k = hull.keel_z(0.48)
    cb = P.centreboard((hull.X(0.48), 0, z_k + 0.02), lowered=True, mat=4)
    objects["Centreboard"] = cb
    case = P.centreboard_case(hull, xi=0.48, length=1.55, mat=1)
    objects["Centreboard_Case"] = case
    meta["pivots"]["centreboard"] = {"axis_x": round(float(hull.X(0.48)), 3),
                                     "axis_z": round(float(z_k + 0.02), 3)}

    # five thwarts slung BELOW the case via cleats, bow thwart lowered for the sail
    stations_oar = [1.90, 1.10, 0.30, -0.50, -1.30]
    stations_thw = [x + 0.42 for x in stations_oar]
    tinfo = BL.thwart_layout(hull, stations_thw, z_top=0.135, mat=1, mat_knee=2)
    objects["Thwarts"] = tinfo["thwarts"]
    objects["Thwart_Knees"] = tinfo["knees"]
    objects["Risers"] = tinfo["risers"]

    # stern sheets (double-ended: small stern bench + platform)
    sb, sk = BL.side_bench_pair(hull, z=0.28, width=0.26, xi_range=(0.90, 0.985), mat=1)
    # (side_bench_pair builds both sides: no mirror -- GEN-1 duplicate fix)
    objects["Stern_Sheets"] = sb
    objects["Stern_Bench_Knees"] = sk
    bb, bk = BL.side_bench_pair(hull, z=0.28, width=0.24, xi_range=(0.05, 0.12), mat=1)
    # (side_bench_pair builds both sides: no mirror -- GEN-1 duplicate fix)
    objects["Bow_Sheets"] = bb
    objects["Bow_Bench_Knees"] = bk

    zfloor = hull.keel_z(0.5) + 0.135
    gr = P.foot_grating(-1.55, -0.30, 0.24, zfloor + 0.02, mat=1)
    gr.append(P.foot_grating(0.10, 1.35, 0.24, zfloor + 0.03, mat=1))
    objects["Floor_Gratings"] = gr
    # loose-laid bottom boards over the floors
    objects["Bottom_Boards"] = BL.bottom_boards(hull)

    # rowlocks + oars: FIVE oars single-banked, alternating sides (stations 1..5
    # P,S,P,S,P with stroke handled on #1).  17 ft service oars.
    OAR_LEN = 17 * 0.3048     # 5.18 m, documented pattern
    row_mb, pivots_all = BL.rowlocks(hull, stations_oar, 0.0)
    objects["Rowlocks"] = row_mb
    side_plan = [1, -1, 1, -1, 1]     # S,P,S,P,S in our +Y-starboard frame; port=+Y
    pivots = []
    for sgn, xs in zip(side_plan, stations_oar):
        for p in pivots_all:
            if abs(p["x"] - xs) < 1e-6 and p["side"] == sgn:
                pivots.append(p)
    meta["pivots"]["rowlocks"] = [{"x": p["x"], "y": round(float(p["y"]), 4),
                                   "z": round(float(p["z"]), 4), "side": p["side"]}
                                  for p in pivots]
    oar_set = BL.build_oar_set(hull, pivots, length=OAR_LEN, inboard_frac=0.30)
    oar_objs = []
    meta["pivots"]["oars_moving"] = []
    for i, oi in enumerate(oar_set):
        xs = oi["station_x"]
        station_i = stations_oar.index(xs) + 1
        side_tag = "P" if oi["side"] > 0 else "S"
        pv = oi["pivot"]
        meta["pivots"]["oars_moving"].append({
            "part": f"Oar_{side_tag}{station_i}",
            "pivot_world": [round(float(v), 4) for v in pv],
            "side": "port(+Y)" if oi["side"] > 0 else "starboard(-Y)",
            "station_x": xs, "length_m": round(float(OAR_LEN), 3),
            "single_banked": True,
            "stowed_rot_z_deg_from_outboard": 90.0})
        oar_objs.append((f"Oar_{side_tag}{station_i}", oi["mb"], pv))

    # lug rig stowed (main + mizzen)
    rig = BL.rigging_stowed(hull, {
        "masts": [("main", 0.42, 5.63, 0.036), ("mizzen", -2.35, 3.90, 0.028)],
        "yards": [("main", 4.57, 0.030, 0.0), ("mizzen", 3.00, 0.024, 0.0)],
        "yard_x": -0.45,
    })
    rigm = MB("Rig_Stowed")
    for r in rig:
        rigm.append(r)
    objects["Rig_Stowed"] = rigm

    objects["Mast_Fit"] = BL.mast_step_clamp(hull, x_step=0.42,
                                             z_kelson=hull.keel_z(0.5) + 0.11,
                                             thwart_x=stations_thw[0])
    objects["Lifting_Eyes"] = BL.lifting_eyes(hull, [1.85, -1.72],
                                              z=hull.keel_z(0.5) + 0.26)
    meta["pivots"]["lifting_eyes_x"] = [1.85, -1.72]

    # rudder with drop-in box half-rudder fits double ender; for simplicity use plate rudder
    rud, axis_pt, _ = P.rudder_plate(hull, mat=0, mat_iron=4)
    objects["Rudder_Tiller"] = rud
    meta["pivots"]["rudder_axis"] = [round(float(v), 4) for v in axis_pt]

    # harpoons + line tub (whaler fittings)
    harpoons = P.harpoon_sheathed((0.9, -0.35, zfloor + 0.10))
    harp2 = P.harpoon_sheathed((0.95, -0.42, zfloor + 0.13))
    objects["Harpoons"] = harpoons
    objects["Harpoons"].append(harp2)
    objects["Line_Tub"] = P.line_tub((-0.9, -0.20, zfloor + 0.02))
    # second whale-line tub forward (whalers carried line at both ends)
    objects["Line_Tub_Fwd"] = P.line_tub((hull.loa / 2 - 1.35, 0.22, zfloor + 0.02))
    # brass fairlead sheaves on both stemheads (double-ended boat)
    fl = MB("Stem_Fairleads")
    fl.append(BL.stem_fairlead(hull))
    fl.append(BL.stem_fairlead(hull, aft=True))
    objects["Stem_Fairleads"] = fl

    # gunwale fenders outside + painters at both stems, gear set
    fends = MB("Fenders")
    for xf in (2.6, 0.4, -1.9):
        for sgn in (-1, 1):
            xi = clamp((hull.loa / 2 - xf) / hull.loa, 0, 1)
            t = hull.arc_to_t(xi, 0.995)
            p = hull.section_pt(xi, t, 0.0)
            fends.append(P.fender((xf, sgn * (abs(p[1]) + 0.06), p[2] + 0.02)))
    objects["Fenders"] = fends
    eyemb = MB("Ring_Bolts")
    for sign, xi in ((1, 0.02), (-1, 0.985)):
        zr = hull.sheer_z(xi)
        xw = hull.X(xi)
        cyl(eyemb, (xw, 0, zr - 0.10), (xw, 0, zr + 0.02), 0.012, seg=10, mat=5)
        torus(eyemb, (xw, 0, zr + 0.05), 0.032, 0.010, seg=12, rseg=6, axis="Y", mat=5)
    objects["Ring_Bolts"] = eyemb
    objects["Painter_Fwd"] = P.painter_coil((hull.loa / 2 - 0.7, 0.18, zfloor + 0.10))
    objects["Painter_Aft"] = P.painter_coil((-hull.loa / 2 + 0.75, 0.18, zfloor + 0.10))

    gear = []
    gear.append(("Grapnel", P.grapnel((-hull.loa / 2 + 1.15, -0.30, zfloor + 0.02), s=0.95)))
    bh = MB("BoatHooks")
    for i, sgn in enumerate((-1, 1)):
        bh.append(P.boat_hook((0.15, sgn * 0.42, zfloor + 0.05 + 0.03 * i),
                              length=hull.loa * 0.60, along=(1, 0, 0)))
    gear.append(("BoatHooks", bh))
    gear.append(("Baler", P.baler((-1.4, 0.26, zfloor + 0.09))))
    gear.append(("Bucket", P.bucket((-1.15, -0.20, zfloor))))
    gear.append(("Breaker", P.breaker((0.15, 0.0, zfloor + 0.14), r=0.115, l=0.38)))
    gear.append(("Compass", P.compass_binnacle((2.30, 0.0, 0.135 + 0.003), mat_brass=3)))
    for name, gmb in gear:
        objects[name] = gmb

    # ---- to Blender -----------------------------------------------------------
    coll = bpy.data.collections.new("WHALER")
    scene.collection.children.link(coll)
    made = {}
    for name, mb in objects.items():
        if len(mb.verts) == 0 or name == "Rudder_Tiller":
            continue
        made[name] = bl2.mb_to_object(mb, name, coll=coll)
    rud = objects["Rudder_Tiller"]
    made["Rudder"] = bl2.mb_to_object(rud, "Rudder", coll=coll,
                                      origin_at=meta["pivots"]["rudder_axis"])
    for nm, omb, pv in oar_objs:
        made[nm] = bl2.mb_to_object(omb, nm, coll=coll, origin_at=pv)

    os.makedirs(os.path.join(REPO_BOATS, "blend"), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(REPO_BOATS, "blend", "boat_c2_whaler.blend"))
    with open(os.path.join(REPO_BOATS, "blend", "boat_c2_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("BUILT WHALER: %d parts" % len(made))
    for k, o in made.items():
        v = bl2.mesh_info(o)
        print("  %-26s tri=%6d dims=%s" % (k, v["tris"], v["dims"]))
    return made, meta, hull


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    main(quick=quick)
