"""
build2_steam_cutter.py -- 25 ft steam cutter (1888), full machinery fit:
lagged vertical boiler (fire door open, coal visible), compound vertical engine
with Stephenson link, shaft + two-blade prop, funnel w/ guy stays, fore state
cabin, helm + steering chain, canopy tracks, sea-going gear.
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
from them2 import machinery2 as MC
from them2 import boatlib2 as BL
from them2 import specs2 as S
from them2 import bl2
from them2.geom2 import MB, cyl, dome, torus, sphere, rot_z, rot_x, lerp, clamp


def main(quick=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    hull = S.steam_cutter_hull()
    hull, loaded, light = S.reconcile(hull, S.STEAM_WEIGHTS)

    objects = {}
    meta = {"id": "steam_cutter_1888", "loaded": loaded, "light": light,
            "weights": S.STEAM_WEIGHTS, "pivots": {}}

    # ---- hull: double-diagonal skin ------------------------------------------
    skin = st.double_skin(hull, n_diag=26, spacing=0.085, nx=56, nt=24,
                          mat_outer=25, mat_inner=21)
    skin.mirror_y()
    objects["Planking_DoubleDiagonal"] = skin

    keel = st.keel_assembly(hull, sided=0.050, depth=0.115, mat=2)
    keel.append(st.stem_post(hull, moulded=0.115, sided=0.052, mat=2))
    objects["Keel_Stem_Sternpost"] = keel
    objects["Transom"] = st.transom_plate(hull, thk=0.052, mat=25, mat_edge=2)
    fr = st.frames(hull, 26, 0.016, spacing=0.165, siding=0.024, mould_lo=0.048,
                   mould_hi=0.028, mat=2)
    fr.mirror_y()
    objects["Frames"] = fr
    objects["Keelson"] = st.keelson(hull, depth=0.16, sided=0.080, mat=2, cap_w=0.11)
    gw = st.gunwale_set(hull, 26, 0.016, cap_w=0.082, cap_h=0.030, mat_cap=1,
                        mat_inwale=2, mat_rub=10, rub_off=0.008)
    gw.mirror_y()
    gw.append(st.stem_band(hull, mat=3))   # on the centreline: after the mirror
    objects["Gunwale_Inwale_Rub"] = gw
    objects["Breasthook"] = st.breasthook(hull, length=0.62, thk=0.038, mat=2)
    # machinery bearers (documented heavy fore-and-afters, bolted)
    bear = MB("Engine_Bearers")
    z_b = hull.keel_z(0.5) + 0.30
    for xi in (0.34, 0.56):
        xs = hull.X(clamp(xi, 0, 1))
        bear.append(MC.engine_bearer(hull, xi0=0.30 if xi < 0.5 else 0.58,
                                  xi1=0.50 if xi < 0.5 else 0.66, width=0.075, mat=2))
    objects["Engine_Bearers"] = bear

    # ---- flooring + gusset plates --------------------------------------------
    x_eq = hull.X(0.50)
    z_floor = hull.keel_z(0.5) + 0.24
    zgr = hull.keel_z(0.5) + 0.135
    # GEN-1: flooring = bottom boards landed ON the floors fore and aft of
    # the machinery space (the old foot gratings floated at a fixed height).
    zfn = BL.floor_top_fn(hull, 0.016)
    fl = MB("Flooring")
    fl.append(BL.bottom_boards(hull, xi0=0.10, xi1=0.30, z_fn=zfn, mat=21))
    fl.append(BL.bottom_boards(hull, xi0=0.62, xi1=0.86, z_fn=zfn, mat=21))
    objects["Flooring"] = fl
    board_top = lambda x, y=0.15: zfn(x, y) + 0.008 + 0.016
    gus = MB("Gusset_Plates")
    for xi in np.linspace(0.12, 0.88, 8):
        xs = hull.X(xi)
        zt = hull.keel_z(xi) + 0.10
        for sgn in (-1, 1):
            t = hull.arc_to_t(xi, 0.12, 0.0)
            p = hull.section_pt(xi, t, -0.05)
            gus.add_plate([(sgn * (abs(p[1]) - 0.16), 0.0), (sgn * abs(p[1]), 0.0),
                           (sgn * (abs(p[1]) - 0.02), 0.10), (sgn * (abs(p[1]) - 0.20), 0.10)],
                          0.010, origin=(xs - 0.005, 0, zt), mat=4,
                          basis=((0, 1, 0), (0, 0, 1), (1, 0, 0)))
    objects["Gusset_Plates"] = gus

    # ---- helm + steering ------------------------------------------------------
    helm_x = hull.X(0.88)
    helm, helm_piv = MC.helm_station(hull, helm_x)
    objects["Helm_Station"] = helm
    meta["pivots"].update(helm_piv)
    # steering chain along the sheer to aft quadrant
    chain = MC.steering_chain(hull, mat=5)
    objects["Steering_Chain"] = chain
    # rudder + quadrant under tiller
    rud, axis_pt, _dir2 = P.rudder_plate(hull, mat=0, mat_iron=4)
    objects["Rudder_Tiller"] = rud
    meta["pivots"]["rudder_axis"] = [round(float(v), 4) for v in axis_pt]

    # ---- boiler + machinery ---------------------------------------------------
    boiler_info = MC.vertical_boiler((x_eq, 0, z_floor), dia=0.80, h_shell=0.72)
    objects["Boiler"] = boiler_info["mb"]
    meta["pivots"]["boiler_face"] = [round(v, 3) for v in boiler_info["face_pt"]]
    meta["pivots"]["boiler_top"] = [round(v, 3) for v in boiler_info["top_pt"]]
    # mountings onto the boiler
    bmounts = MC.boiler_mountings(boiler_info["face_pt"], boiler_info["top_pt"], boiler_info["shell_r"])
    objects["Boiler_Mountings"] = bmounts

    eng_x = hull.X(0.44)
    eng = MC.vertical_engine((eng_x, 0, z_floor + 0.55), n_cyl=2)
    objects["Engine"] = eng["mb"]
    meta["pivots"]["engine"] = eng["pivots"]

    shaft = MC.shaft_line(hull, (eng_x, 0, z_floor + 0.42), 0.985)
    objects["Shaft_Line"] = shaft["mb"]
    prop_mb = MC.propeller_two_blade(shaft["end_pt"], shaft["axis_dir"], d=0.60,
                                     pitch=0.80)
    objects["__prop_mb__"] = prop_mb
    meta["pivots"]["propeller"] = {"hub_pt": [round(v, 4) for v in shaft["end_pt"]],
                                   "axis_dir": [round(v, 4) for v in shaft["axis_dir"]]}
    # stern tube + bracket under the counter
    objects["Shaft_Bracket"] = MC.stern_bracket(hull, shaft["end_pt"], shaft["axis_dir"])

    # funnel w/ sliding extension + stays
    fun = MC.funnel((x_eq, 0, boiler_info["top_pt"][2] - 0.30), r=0.135, h=1.42)
    objects["Funnel"] = fun["mb"]
    meta["pivots"]["funnel_top"] = [round(v, 3) for v in fun["top_pt"]]

    # safety valve + whistle + gauge glass already on mountings; lagged pipes
    pipes = MB("Steam_Pipes")
    MC.lagged_pipe(pipes, [(eng_x + 0.10, 0, z_floor + 0.40), (x_eq, 0, z_floor + 0.66)])
    MC.lagged_pipe(pipes, [(eng_x - 0.20, -0.10, z_floor + 0.42),
                           (hull.X(0.80), -0.22, hull.keel_z(0.8) + 0.42)])
    objects["Steam_Pipes"] = pipes
    # feed tank fwd + hand pump + connector
    tank = MC.feed_tank((x_eq + 0.85, 0.28, z_floor + 0.16), r=0.15, l=0.40)
    pump = MC.hand_pump((x_eq + 0.55, 0.30, z_floor + 0.05))
    pipes2 = MB("Feed_Pipe")
    MC.lagged_pipe(pipes2, [(x_eq + 0.85, 0.28, z_floor + 0.16),
                            (x_eq + 0.30, 0.02, z_floor + 0.30)], mat_lag=14)
    objects["Feed_Tank"] = tank
    objects["Hand_Pump"] = pump
    objects["Feed_Pipe"] = pipes2
    # coal bunker + irons
    objects["Coal_Bunker"] = MC.coal_bunker(hull, xi_range=(0.60, 0.72))
    objects["Fire_Irons"] = MC.fire_irons((x_eq - 0.02, 0.34, z_floor + 0.10))
    # chequer-plate steel sole through the machinery space
    objects["Floor_Plates"] = MC.floor_plates(eng_x - 0.55, x_eq + 0.62, 0.30,
                                              z_floor + 0.010)
    # exhaust uptake: lagged pipe from the engine stop valve up into the funnel
    up = MB("Exhaust_Uptake")
    MC.lagged_pipe(up, [(eng_x, 0, z_floor + 1.02), (eng_x, 0, z_floor + 1.42),
                        (x_eq + 0.02, 0, z_floor + 1.50)], r=0.042)
    objects["Exhaust_Uptake"] = up
    # mushroom ventilators for the machinery space
    vents = MB("Ventilators")
    vents.append(MC.ventilator_mushroom((x_eq + 1.00, -0.30, 0.34)))
    vents.append(MC.ventilator_mushroom((hull.X(0.70), 0.30, 0.34)))
    objects["Ventilators"] = vents
    # polished brass guard rail around the machinery bay
    objects["Engine_Guard"] = MC.engine_guard_rail(eng_x - 0.58, x_eq + 0.66,
                                                   0.34, z_floor + 0.06, h=0.38)

    # ---- accommodation + outfit ----------------------------------------------
    # fore state cabin (aft cabin on the cutter is documented)
    cab = MC.state_cabin(hull, xi_range=(0.80, 0.985), mat=21)
    objects["Fore_Cabin"] = cab["mb"]
    meta["pivots"]["cabin"] = cab["info"]
    xi_cab = 0.8925
    z_cab_roof = hull.keel_z(xi_cab) + 0.18 + 0.58 + 0.115
    objects["Cabin_Skylight"] = MC.glazed_skylight((hull.X(xi_cab), 0,
                                                    z_cab_roof + 0.018))
    # canopy supports: dagger boards only stored (per outfit)
    dag = MC.dagger_boards_stowed((-0.9, 0.30, hull.keel_z(0.3) + 0.45))
    objects["Dagger_Boards"] = dag
    sail_tracks = MC.canopy_tracks(hull)
    objects["Canopy_Tracks"] = sail_tracks
    # stern seat + awning stanchion sockets
    sb, sk = BL.side_bench_pair(hull, z=0.33, width=0.30, xi_range=(0.91, 0.985), mat=21)
    objects["Stern_Sheets"] = sb
    objects["Stern_Knees"] = sk
    # bow sheets for the crew
    bb, bk = BL.side_bench_pair(hull, z=0.33, width=0.26, xi_range=(0.07, 0.15), mat=21)
    # side_bench_pair builds both sides: no mirror (GEN-1 duplicate fix)
    objects["Bow_Sheets"] = bb
    objects["Bow_Knees"] = bk

    # lifting eyes (through keelson, brass/iron)
    objects["Lifting_Eyes"] = BL.lifting_eyes(hull, [2.10, -1.85],
                                              z=hull.keel_z(0.5) + 0.26, mat=3)
    meta["pivots"]["lifting_eyes_x"] = [2.10, -1.85]

    # nav lamps, compass, bell, gear
    objects["Sidelights"] = MC.sidelight_pair(hull)
    objects["Compass"] = P.compass_binnacle((helm_x + 0.02, 0.0, 0.36), mat_brass=3)
    # bell on a gallows bracket standing on the breasthook, abaft the stem
    xb = hull.X(0.045)
    objects["Ships_Bell"] = P.ships_bell((xb, 0.0, hull.sheer_z(0.045) + 0.004),
                                         facing_y=False)
    gear = []
    gear.append(("Painter", P.painter_coil((hull.loa / 2 - 0.80, 0.24, hull.keel_z(0.06) + 0.10))))
    # GEN-1: anchor + grapnel stowed lying on the after flooring (they used
    # to stand upright at keel level and broke out through the bottom).
    xa = hull.X(0.80)
    gear.append(("Anchor", P.stocked_anchor((xa, -0.02, board_top(xa, 0.10) + 0.002),
                                            scale=0.62, lie=True)))
    xg = hull.X(0.70)
    gear.append(("Grapnel", P.grapnel((xg, 0.20, board_top(xg, 0.20) + 0.002),
                                      s=0.80, lie=True)))
    fends = MB("Fenders")
    for xf in (2.7, 0.6, -1.6):
        for sgn in (-1, 1):
            xi = clamp((hull.loa / 2 - xf) / hull.loa, 0, 1)
            t = hull.arc_to_t(xi, 0.995)
            p = hull.section_pt(xi, t, 0.0)
            fends.append(P.fender((xf, sgn * (abs(p[1]) + 0.06), p[2] + 0.02)))
    gear.append(("Fenders", fends))
    bh = MB("BoatHooks")
    for i, sgn in enumerate((-1, 1)):
        bh.append(P.boat_hook((0.7, sgn * 0.40, hull.keel_z(0.4) + 0.22 + 0.03 * i),
                              length=hull.loa * 0.60, along=(1, 0, 0)))
    gear.append(("BoatHooks", bh))
    gear.append(("Baler", P.baler((-1.2, 0.30, hull.keel_z(0.66) + 0.29))))
    gear.append(("Bucket", P.bucket((-0.95, 0.0, hull.keel_z(0.62) + 0.20))))
    gear.append(("Breaker", P.breaker((0.9, 0.0, hull.keel_z(0.4) + 0.30), r=0.115, l=0.38)))
    for name, gmb in gear:
        objects[name] = gmb

    # ---- flags ---------------------------------------------------------------
    flags = P.white_ensign((-hull.loa / 2 + 0.05, 0, hull.sheer_z(0.985) + 0.10),
                           size=(0.56, 0.28))
    objects["Flags"] = flags

    # ---- to Blender -----------------------------------------------------------
    coll = bpy.data.collections.new("STEAM_CUTTER")
    scene.collection.children.link(coll)
    made = {}
    for name, mb in objects.items():
        if len(mb.verts) == 0:
            continue
        if name == "Rudder_Tiller":
            continue
        if name == "__prop_mb__":
            made["Propeller"] = bl2.mb_to_object(mb, "Propeller", coll=coll,
                origin_at=meta["pivots"]["propeller"]["hub_pt"])
            continue
        made[name] = bl2.mb_to_object(mb, name, coll=coll)
    made["Rudder"] = bl2.mb_to_object(objects["Rudder_Tiller"], "Rudder", coll=coll,
                                      origin_at=meta["pivots"]["rudder_axis"])

    os.makedirs(os.path.join(REPO_BOATS, "blend"), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(REPO_BOATS, "blend", "boat_a2_steam_cutter.blend"))
    with open(os.path.join(REPO_BOATS, "blend", "boat_a2_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("BUILT STEAM CUTTER: %d parts" % len(made))
    for k, o in made.items():
        v = bl2.mesh_info(o)
        print("  %-26s tri=%6d dims=%s" % (k, v["tris"], v["dims"]))
    return made, meta, hull


if __name__ == "__main__":
    quick = "--quick" in sys.argv
    main(quick=quick)
