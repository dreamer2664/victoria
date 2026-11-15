"""MACHINERY MODULE - SS Aurelian (1889)

One vertical inverted direct-acting triple-expansion engine driving a single
screw through a thrust block and line of shafting, nine cylindrical
single-ended return-tube boilers in three rows with two furnaces each, coal
bunkers, condensers, auxiliary pumps, and the shaft alley to the stern tube.

Moving parts are built as SEPARATE objects with their pivots set correctly so
the Roblox scripts (or a Blender action) can drive:
    Engine_HP_Piston, Engine_IP_Piston, Engine_LP_Piston
    Engine_HP_Rod, Engine_IP_Rod, Engine_LP_Rod
    Engine_Crankshaft          (rotates about its own axis)
    Propeller_Shaft            (rotates about X)
    Propeller_Blades           (child of the shaft)
    Engine_HPCrank, Engine_IPCrank, Engine_LPCrank (crank webs)

Geometry follows the 1889 comparison ships: cylinders of 38/62/101 in bore
and 51 in stroke for 14 000 IHP at 62 rpm (Teutonic: 43/68/110 x 60 in for
17 500 IHP) - see research/HISTORICAL_EVIDENCE.md section 5.
"""
from __future__ import annotations
import os, sys, math
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from shipdesign.spec import SHIP, DECK_Z
from shipdesign import layout
from shipdesign.hull import HULL, T
from lib_build import (reset_scene, collection, mesh_object, build_palette, box,
                       cylinder, tube, join_objects, principled)

COL = None
P = None

ER_X0, ER_X1 = -24.0, -3.0          # engine room
BR_X0, BR_X1 = -3.0, 34.0           # boiler rooms
ER_Z0 = 1.30                        # tank top
ER_Z1 = DECK_Z["main"] - 0.35       # underside of the main deck
CRANK_X = -18.0                     # centre of the crankshaft
SHAFT_Z = 2.05


# ---------------------------------------------------------------------------
# boilers
# ---------------------------------------------------------------------------
def boilers():
    objs = []
    n_rows = 3
    per_row = 3
    for r in range(n_rows):
        x = -1.0 + r * 4.2
        for k in range(per_row):
            y = (k - 1) * 5.0
            zc = ER_Z0 + 2.10
            # shell
            v, f = cylinder((x, y, zc), 2.10, 3.35, axis='X', segments=28)
            objs.append(mesh_object("Boiler_Shell", v, f, col=COL,
                                    mat=P["boiler_shell"]))
            # end plates + furnaces (two per boiler, period 'double-ended'
            # look from the firing floor)
            for sgn in (-1, 1):
                xf = x + sgn * 1.72
                v, f = cylinder((xf, y, zc), 2.06, 0.10, axis='X', segments=28)
                objs.append(mesh_object("Boiler_End", v, f, col=COL,
                                        mat=P["cast_iron"]))
                for fy in (-0.85, 0.85):
                    v, f = cylinder((xf + sgn * 0.06, y + fy, zc - 0.55),
                                    0.46, 0.30, axis='X', segments=16)
                    objs.append(mesh_object("Furnace_Door", v, f, col=COL,
                                            mat=P["furnace"]))
                    # glowing fire behind the door grille
                    v, f = cylinder((xf + sgn * 0.02, y + fy, zc - 0.55),
                                    0.38, 0.06, axis='X', segments=14)
                    objs.append(mesh_object("Furnace_Glow", v, f, col=COL,
                                            mat=P["fire"]))
            # steam dome + safety valves
            v, f = cylinder((x, y, zc + 2.15), 0.55, 0.75, segments=16)
            objs.append(mesh_object("Steam_Dome", v, f, col=COL,
                                    mat=P["boiler_shell"]))
            for vy in (-0.3, 0.3):
                v, f = cylinder((x, y + vy, zc + 2.95), 0.10, 0.55, segments=8)
                objs.append(mesh_object("Safety_Valve", v, f, col=COL,
                                        mat=P["brass"]))
            # mountings: gauge glass, water column
            v, f = cylinder((x - 1.0, y - 2.25, zc + 0.65), 0.07, 1.3,
                            segments=8)
            objs.append(mesh_object("Gauge_Glass", v, f, col=COL,
                                    mat=P["gauge"]))
            # uptake to the funnel casing
            v, f = box((x, y, zc + 2.9), (1.5, 1.5, 2.6))
            objs.append(mesh_object("Uptake", v, f, col=COL,
                                    mat=P["steel"]))
        # firing floor plates down the front of each row
        v, f = box((x, 0, ER_Z0 + 0.05), (3.6, 15.4, 0.10))
        objs.append(mesh_object("Firing_Floor", v, f, col=COL,
                                mat=P["steel_floor"]))
    # steam main along the boiler rooms to the engine
    objs.append(_pipe([(33.0, 0, ER_Z1 - 0.55), (-23.0, 0, ER_Z1 - 0.55)],
                      0.22, P["steam_pipe"], "Steam_Main"))
    # feed main
    objs.append(_pipe([(33.0, 1.2, ER_Z1 - 0.95), (-23.0, 1.2, ER_Z1 - 0.95)],
                      0.16, P["steam_pipe"], "Feed_Main"))
    # coal bunkers along both sides of the boiler rooms
    for side in (1, -1):
        xs = np.linspace(BR_X0 + 1.0, BR_X1 - 1.0, 14)
        verts = []; faces = []
        for i, x in enumerate(xs):
            b = HULL.half_beam_at(x, 6.0) - 0.35
            b2 = HULL.half_beam_at(x, 6.0) - 3.3
            verts += [(x, side * b2, ER_Z0), (x, side * b, ER_Z0),
                      (x, side * b, 8.30), (x, side * b2, 6.20)]
        for i in range(len(xs) - 1):
            a = i * 4; bb = (i + 1) * 4
            for k in range(4):
                k2 = (k + 1) % 4
                q = (a + k, a + k2, bb + k2, bb + k)
                faces.append(q if side > 0 else q[::-1])
        objs.append(mesh_object("Coal_Bunker_%d" % side, verts, faces,
                                col=COL, mat=P["coal"]))
    return objs


def _pipe(points, r, mat, name="Pipe", seg=10):
    v, f = tube(points, r, seg)
    return mesh_object(name, v, f, col=COL, mat=mat)


# ---------------------------------------------------------------------------
# main engine
# ---------------------------------------------------------------------------
def _rod(p0, p1, r, mat, name, seg=10):
    """A round rod running from p0 to p1 (used for connecting rods)."""
    from mathutils import Vector
    a, b = Vector(p0), Vector(p1)
    d = b - a
    L = d.length
    if L < 1e-4:
        return None
    v, f = cylinder((0, 0, L / 2), r, L, segments=seg)
    ob = mesh_object(name, v, f, col=COL, mat=mat)
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    ob.location = a
    return ob


def engine():
    """Vertical inverted direct-acting triple-expansion engine.

    Three cylinders in line along the crankshaft (fore-and-aft, +X), cranks
    at 120 deg, each piston rod driving down through a crosshead and a
    connecting rod to its crank pin.  All of the moving pieces are separate
    objects so the Roblox script can animate them independently.
    """
    from mathutils import Vector
    objs = []
    crank_z = ER_Z0 + 1.05
    # ---- bedplate ------------------------------------------------------
    v, f = box((CRANK_X, 0, ER_Z0 + 0.40), (10.4, 5.6, 0.80))
    objs.append(mesh_object("Engine_Bedplate", v, f, col=COL,
                            mat=P["cast_iron"]))
    # ---- entablature: four round columns, NOT slabs ---------------------
    for xx in (CRANK_X - 4.3, CRANK_X + 4.3):
        for yy in (-2.35, 2.35):
            v, f = cylinder((xx, yy, (ER_Z0 + 0.8 + ER_Z1) / 2 - 0.5),
                            0.19, ER_Z1 - ER_Z0 - 1.6, segments=12)
            objs.append(mesh_object("Engine_Column", v, f, col=COL,
                                    mat=P["cast_iron"]))
            v, f = cylinder((xx, yy, ER_Z0 + 0.95), 0.32, 0.22, segments=12)
            objs.append(mesh_object("Column_Base", v, f, col=COL,
                                    mat=P["cast_iron"]))
    # ---- cylinders: HP fwd, IP mid, LP aft ------------------------------
    bores = SHIP["cylinder_dia_m"]        # 0.965 / 1.575 / 2.565
    xs = (CRANK_X - 3.30, CRANK_X, CRANK_X + 3.30)
    labels = ("HP", "IP", "LP")
    pins = []
    for i, (x, bore) in enumerate(zip(xs, bores)):
        zc = ER_Z1 - 1.75 - bore / 2
        # barrel
        v, f = cylinder((x, 0, zc), bore / 2, 1.62, segments=32)
        objs.append(mesh_object("Engine_%s_Cylinder" % labels[i], v, f,
                                col=COL, mat=P["engine_paint"]))
        # steam chest on the port side
        v, f = box((x, bore / 2 * 0.55 + 0.55, zc),
                   (0.80, bore * 0.62, 1.25))
        objs.append(mesh_object("Engine_%s_Valve_Chest" % labels[i], v, f,
                                col=COL, mat=P["engine_paint"]))
        # top and bottom covers with studs
        for sgn in (-1, 1):
            v, f = cylinder((x, 0, zc + sgn * 0.86), bore / 2 + 0.10, 0.14,
                            segments=32)
            objs.append(mesh_object("Engine_%s_Cover" % labels[i], v, f,
                                    col=COL, mat=P["cast_iron"]))
        # piston rod (separate object, animated on Z)
        rod_z0 = zc - bore / 2 - 0.30
        rod_z1 = crank_z + 1.55
        v, f = cylinder(((x), 0, (rod_z0 + rod_z1) / 2), 0.085,
                        rod_z1 - rod_z0, segments=10)
        objs.append(mesh_object("Engine_%s_Rod" % labels[i], v, f, col=COL,
                                mat=P["steel_bright"]))
        # crosshead block on the guides
        ch_z = rod_z0 - 0.18
        v, f = box((x, 0, ch_z), (0.62, 0.46, 0.42))
        objs.append(mesh_object("Engine_%s_Crosshead" % labels[i], v, f,
                                col=COL, mat=P["steel_bright"]))
        for yy in (-0.40, 0.40):
            v, f = box((x, yy, (ch_z + crank_z) / 2 + 0.25),
                       (0.42, 0.10, ch_z - crank_z + 1.6))
            objs.append(mesh_object("Engine_%s_Guide" % labels[i], v, f,
                                    col=COL, mat=P["steel"]))
        # crank pin position for this throw (120 deg apart)
        ang = i * 2 * math.pi / 3
        pin = Vector((x, 0.0, crank_z + 0.78 * math.sin(ang)))
        pins.append(pin)
        # connecting rod: crosshead -> crank pin
        r = _rod((x, 0.0, ch_z), (pin.x, pin.y + 0.34, pin.z), 0.135,
                 P["steel_bright"], "Engine_%s_ConRod" % labels[i])
        if r:
            objs.append(r)
        # crank web + pin, part of the rotating assembly
        v, f = box((x, 0, (crank_z + pin.z) / 2), (0.34, 0.58,
                   max(abs(pin.z - crank_z), 0.35)))
        objs.append(mesh_object("Crank_Web", v, f, col=COL,
                                mat=P["steel_bright"]))
        v, f = cylinder((x, 0.34, pin.z), 0.155, 0.60, axis='Y', segments=12)
        objs.append(mesh_object("Crank_Pin", v, f, col=COL,
                                mat=P["steel_bright"]))
    # ---- crankshaft -----------------------------------------------------
    v, f = cylinder((CRANK_X, 0, crank_z), 0.26, 10.4, axis='X', segments=20)
    objs.append(mesh_object("Crankshaft", v, f, col=COL,
                            mat=P["steel_bright"]))
    # ---- thrust block, shaft -------------------------------------------
    v, f = box((-25.4, 0, SHAFT_Z), (1.9, 1.5, 1.3))
    objs.append(mesh_object("Thrust_Block", v, f, col=COL,
                            mat=P["cast_iron"]))
    v, f = cylinder((-52.0, 0, SHAFT_Z), SHIP["shaft_dia_m"] / 2, 62.0,
                    axis='X', segments=16)
    objs.append(mesh_object("Propeller_Shaft", v, f, col=COL,
                            mat=P["steel_bright"]))
    # ---- valve gear: eccentrics + weigh shaft + valve rods ---------------
    for i, x in enumerate(xs):
        v, f = cylinder((x, 0.62, crank_z), 0.30, 0.26, axis='X', segments=14)
        objs.append(mesh_object("Eccentric", v, f, col=COL,
                                mat=P["steel_bright"]))
        objs.append(_rod((x, 0.62, crank_z), (x, 0.62, ER_Z1 - 1.0), 0.055,
                         P["steel_bright"], "Eccentric_Rod"))
        v, f = cylinder((x, 0.62, ER_Z1 - 1.0), 0.09, 0.5, segments=8)
        objs.append(mesh_object("Valve_Spindle", v, f, col=COL,
                                mat=P["steel_bright"]))
    v, f = cylinder((CRANK_X, 0.95, ER_Z1 - 1.25), 0.07, 7.4, axis='X',
                    segments=10)
    objs.append(mesh_object("Weigh_Shaft", v, f, col=COL,
                            mat=P["steel_bright"]))
    # ---- condensers, air pumps, circulating pipes -----------------------
    for x in (CRANK_X - 7.4, CRANK_X + 7.6):
        v, f = cylinder((x, 2.35, ER_Z0 + 1.45), 1.15, 2.6, segments=20)
        objs.append(mesh_object("Condenser", v, f, col=COL,
                                mat=P["engine_paint"]))
        v, f = cylinder((x, 2.35, ER_Z0 + 3.0), 0.5, 0.9, segments=12)
        objs.append(mesh_object("Air_Pump", v, f, col=COL,
                                mat=P["cast_iron"]))
        objs.append(_pipe([(x, 2.35, ER_Z0 + 0.75), (x, 7.8, ER_Z0 + 0.25),
                           (x, 7.8, 0.95), (x, 5.6, 0.35)], 0.16,
                          P["sea_pipe"], "Circulating_Pipe"))
    # ---- auxiliaries ----------------------------------------------------
    for x, lab in ((CRANK_X + 5.6, "Feed_Pump"), (CRANK_X - 5.9, "Bilge_Pump"),
                   (CRANK_X + 8.2, "Fire_Pump")):
        v, f = box((x, -2.75, ER_Z0 + 0.95), (1.3, 1.1, 1.7))
        objs.append(mesh_object(lab, v, f, col=COL, mat=P["cast_iron"]))
    v, f = cylinder((CRANK_X + 9.4, -4.3, ER_Z0 + 1.15), 0.75, 2.2,
                    segments=16)
    objs.append(mesh_object("Evaporator", v, f, col=COL, mat=P["copper"]))
    # workbench and tool rack on the port side
    v, f = box((CRANK_X, 4.35, ER_Z0 + 0.90), (7.0, 0.85, 0.14))
    objs.append(mesh_object("Workbench", v, f, col=COL, mat=P["oak_light"]))
    for xx in (-4.0, -22.0):
        for k in range(15):
            v, f = box((xx, -4.9, ER_Z0 + 0.35 + k * 0.33),
                       (0.75, 0.10, 0.045))
            objs.append(mesh_object("Ladder_Rung", v, f, col=COL,
                                    mat=P["steel"]))
        for yy in (-5.35, -4.45):
            v, f = box((xx, yy, ER_Z0 + 2.6), (0.09, 0.09, 5.0))
            objs.append(mesh_object("Ladder_Stringer", v, f, col=COL,
                                    mat=P["steel"]))
    return objs


# ---------------------------------------------------------------------------
# propeller
# ---------------------------------------------------------------------------
def propeller():
    objs = []
    x = -78.6
    z = SHAFT_Z
    r_hub = 0.62
    v, f = cylinder((x, 0, z), r_hub, 1.25, axis='X', segments=20,
                    radius_top=r_hub * 0.72)
    objs.append(mesh_object("Propeller_Hub", v, f, col=COL,
                            mat=P["bronze_prop"]))
    # four cast manganese-bronze blades, elliptical outline, helical face
    n = 4
    for k in range(n):
        a0 = 2 * math.pi * k / n
        verts = []; faces = []
        nu, nv = 9, 5
        for iu in range(nu):
            u = iu / (nu - 1)                     # 0 at root, 1 at tip
            rr = r_hub * 0.85 + u * (SHIP["prop_diameter_m"] / 2 - r_hub * 0.85)
            chord = (0.55 + 1.75 * math.sin(math.pi * min(1.0, u * 0.92 + 0.08)))
            for iv in range(nv):
                vv = iv / (nv - 1) - 0.5
                ang = a0 + vv * chord / max(rr, 0.4)
                # pitch: face advances along X with rotation
                px = x - 0.34 + 0.42 * u - SHIP["prop_pitch_m"] * (vv * 0.34)
                py = rr * math.cos(ang)
                pz = z + rr * math.sin(ang)
                verts.append((px, py, pz))
        for iu in range(nu - 1):
            for iv in range(nv - 1):
                a = iu * nv + iv
                faces.append((a, a + 1, a + nv + 1, a + nv))
        objs.append(mesh_object("Propeller_Blade_%d" % k, verts, faces,
                                col=COL, mat=P["bronze_prop"],
                                smooth_angle=math.radians(60)))
    return objs


def shafting_and_steering():
    objs = []
    # shaft alley: watertight passage with bearings
    for x in np.arange(-74.0, -26.0, 6.0):
        v, f = box((x, 0, SHAFT_Z), (0.9, 1.4, 0.9))
        objs.append(mesh_object("Shaft_Bearing", v, f, col=COL,
                                mat=P["cast_iron"]))
    # stern tube
    v, f = cylinder((-76.0, 0, SHAFT_Z), 0.62, 3.6, axis='X', segments=16)
    objs.append(mesh_object("Stern_Tube", v, f, col=COL, mat=P["cast_iron"]))
    # steering gear: quadrant + two rams, in the after steering compartment
    v, f = box((-70.0, 0, 3.4), (2.2, 1.4, 0.6))
    objs.append(mesh_object("Steering_Engine", v, f, col=COL,
                            mat=P["cast_iron"]))
    for side in (1, -1):
        objs.append(_pipe([(-70.0, side * 0.6, 3.4), (-76.5, side * 1.1, 3.6),
                           (-77.6, side * 0.55, 3.9)], 0.11,
                          P["steel_bright"], "Steering_Ram"))
    v, f = box((-77.2, 0, 4.2), (0.5, 1.2, 2.2))
    objs.append(mesh_object("Rudder_Quadrant", v, f, col=COL,
                            mat=P["cast_iron"]))
    return objs


def build(col, P_):
    global COL, P
    COL, P = col, P_
    P.setdefault("fire", principled("Furnace_Fire", (1.0, 0.42, 0.08, 1), 0.9,
                                    emit=(1.0, 0.35, 0.05, 1),
                                    emit_strength=9.0))
    P.setdefault("boiler_shell", principled("Boiler_Shell", (0.22, 0.23, 0.24, 1), 0.55))
    P.setdefault("engine_paint", principled("Engine_Paint", (0.21, 0.36, 0.32, 1), 0.45))
    P.setdefault("steel_bright", principled("Steel_Bright", (0.55, 0.56, 0.58, 1), 0.28, metal=1.0))
    P.setdefault("steam_pipe", principled("Steam_Pipe", (0.62, 0.60, 0.56, 1), 0.45))
    P.setdefault("sea_pipe", principled("Sea_Pipe", (0.24, 0.35, 0.30, 1), 0.55))
    P.setdefault("furnace", principled("Furnace_Door", (0.10, 0.09, 0.08, 1), 0.7))
    P.setdefault("gauge", principled("Gauge_Glass", (0.75, 0.85, 0.82, 1), 0.1,
                                     alpha=0.5))
    P.setdefault("bronze_prop", principled("Manganese_Bronze", (0.55, 0.40, 0.18, 1), 0.32, metal=1.0))
    P.setdefault("steel_floor", principled("Steel_Floor", (0.30, 0.31, 0.30, 1), 0.7))
    P.setdefault("oak_light", principled("Oak_Light", (0.55, 0.43, 0.28, 1), 0.45))
    P.setdefault("counterweight", principled("Counterweight", (0.30, 0.30, 0.32, 1), 0.6))
    groups = {}
    groups["boilers"] = join_objects(boilers(), "Boiler_Rooms")
    eng = engine()
    # keep the moving parts as individual objects
    moving = ("Engine_HP_Rod", "Engine_IP_Rod", "Engine_LP_Rod",
              "Crankshaft", "Propeller_Shaft")
    still = [o for o in eng if o and o.name not in moving]
    groups["engine"] = join_objects(still, "Engine_Main")
    for nm in moving:
        ob = bpy.data.objects.get(nm)
        if ob:
            groups[nm] = ob
    groups["propeller"] = join_objects(propeller(), "Propeller")
    groups["steering"] = join_objects(shafting_and_steering(), "Steering_Gear")
    return groups


if __name__ == "__main__":
    sc = reset_scene()
    P = build_palette()
    col = collection("SHIP_MACHINERY")
    groups = build(col, P)
    for k, v in groups.items():
        print("built", k, v.name if v else None,
              len(v.data.vertices) if v else 0)
    out = os.path.join(ROOT, "models", "module_machinery.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print("saved", out)
