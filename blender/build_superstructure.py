"""SUPERSTRUCTURE / EXTERIOR FITTINGS - SS Aurelian (1889)

Deckhouses (white-painted), promenade shelter, bridge & wheelhouse, funnels
with caps and steam pipes, masts with yards and standing rigging, lifeboats on
Trotman davits, ventilator cowls, skylights, hatches, winches, capstans,
bollards, rails and navigation lights.

Reference basis is recorded in research/HISTORICAL_EVIDENCE.md; the strongest
visual anchors are the 1889 Ocean Magazine photographs of Teutonic (white
sheer-strake house with a long row of rectangular windows, buff funnels with
black tops, schooner rig, boats on the boat deck), the Umbria/Etruria
profile, and 'Ocean Steamships' (1891) for deck machinery.
"""
from __future__ import annotations
import os
import sys
import math
import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from shipdesign.spec import SHIP, FUNNELS, MASTS, DECK_Z, LIFEBOATS, PALETTE
from shipdesign import layout
from shipdesign.hull import HULL, HL, T
from lib_build import (reset_scene, collection, mesh_object, build_palette, box,
                       cylinder, tube, railing, join_objects, principled)

COL = None
P = None


# ---------------------------------------------------------------------------
# generic building blocks
# ---------------------------------------------------------------------------
def wall_with_windows(name, x0, x1, y, z0, z1, thickness=0.10, win_h=1.15,
                      win_w=0.72, pitch=1.55, sill=1.02, mat=None,
                      glass=None, facing=1):
    """A long house side with a regular row of windows.

    Window reveals are modelled as recessed frames (dark) with a glass pane
    set 6 cm inboard, which is how period deckhouses read in photographs.
    """
    objs = []
    # lower panel, sill band, head band
    for (za, zb) in ((z0, z0 + sill), (z0 + sill + win_h, z1)):
        v, f = box(((x0 + x1) / 2, y, (za + zb) / 2),
                   (x1 - x0, thickness, zb - za))
        objs.append(mesh_object(name + "_panel", v, f, col=COL, mat=mat))
    n = max(1, int((x1 - x0) // pitch))
    for i in range(n):
        xc = x0 + (i + 0.5) * (x1 - x0) / n
        # mullions between windows
        v, f = box((xc + (x1 - x0) / n / 2, y, z0 + sill + win_h / 2),
                   (pitch - win_w, thickness, win_h))
        objs.append(mesh_object(name + "_mull", v, f, col=COL, mat=mat))
        # glazing
        v, f = box((xc, y - facing * 0.012, z0 + sill + win_h / 2),
                   (win_w, 0.02, win_h))
        objs.append(mesh_object(name + "_glass", v, f, col=COL, mat=glass))
        # storm frame
        v, f = box((xc, y + facing * 0.052, z0 + sill + win_h / 2),
                   (win_w + 0.10, 0.03, win_h + 0.10))
        objs.append(mesh_object(name + "_frame", v, f, col=COL, mat=mat))
    return objs


def house(name, x0, x1, y_half, z0, z1, mat, roof_mat=None, windows=True,
          win_pitch=1.6, end_windows=True):
    """A rectangular deckhouse with windowed sides and a slightly cambered roof."""
    objs = []
    yh = y_half
    for side in (1, -1):
        if windows:
            objs += wall_with_windows(name + "_side%d" % side, x0, x1, side * yh,
                                      z0, z1, mat=mat, glass=P["glass"],
                                      facing=side)
        else:
            v, f = box(((x0 + x1) / 2, side * yh, (z0 + z1) / 2),
                       (x1 - x0, 0.10, z1 - z0))
            objs.append(mesh_object(name + "_side", v, f, col=COL, mat=mat))
    # front / aft bulkheads
    for x in (x0, x1):
        v, f = box((x, 0, (z0 + z1) / 2), (0.10, 2 * yh, z1 - z0))
        objs.append(mesh_object(name + "_end", v, f, col=COL, mat=mat))
    # roof: gently cambered plate
    nx, ny = 24, 8
    xs = np.linspace(x0, x1, nx); ys = np.linspace(-yh - 0.05, yh + 0.05, ny)
    verts = []
    for x in xs:
        for y in ys:
            camber = 0.10 * (1 - (y / (yh + 0.05)) ** 2)
            verts.append((x, y, z1 + camber))
    faces = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            a = i * ny + j
            faces.append((a, a + 1, a + ny + 1, a + ny))
    objs.append(mesh_object(name + "_roof", verts, faces, col=COL,
                            mat=roof_mat or mat))
    return objs


def deck_edge_halfbeam(x, z, inset=0.10):
    """Half breadth available for an open deck or a fitting at height z."""
    b = hb_local(x, z) - inset
    return float(b) if b == b and abs(b) < 1e6 else 0.0


# ---------------------------------------------------------------------------
# deck 1: saloon deck house (the long white house with rows of windows)
# ---------------------------------------------------------------------------
def saloon_deck_house():
    # One continuous white block from the main deck to the promenade deck, as
    # on Teutonic: the lower tier (saloon deck) carries the first-class public
    # rooms, the upper tier is the promenade deck house.
    z0 = DECK_Z["main"] - 0.30
    z1 = DECK_Z["prom"]
    x0, x1 = -60.0, 54.0
    objs = []
    # side plating follows the hull a little: build as a lofted wall
    for side in (1, -1):
        objs += _lofted_house_side("SaloonHouse", x0, x1, z0, z1, side,
                                   inset=0.42, mat=P["upper_white"],
                                   win_rows=(_win_row(DECK_Z["saloon"], 0.85), None))
    # forward/after ends (tapered with the hull)
    objs.append(_house_end("SaloonHouse_fwd", 52.0, z0, z1, P["upper_white"]))
    objs.append(_house_end("SaloonHouse_aft", -58.0, z0, z1, P["upper_white"]))
    # promenade deck plating on top (the open deck)
    objs.append(_deck_plate("SaloonDeck_Plate", DECK_Z["saloon"], -58.0, 52.0,
                            P["deck_wood"]))
    return objs


def _win_row(z0, sill):
    return (z0 + sill, 1.20)


HOUSE_WALL_GAIN = 1.0   # house walls stand on deck, just inside the shell


def _lofted_house_side(name, x0, x1, z0, z1, side, inset, mat, win_rows):
    """House side that follows the ship's side, with window openings."""
    xs = np.linspace(x0, x1, 70)
    verts = []; faces = []
    # sill band, window band handled separately: build solid wall then cut
    # visually by adding dark recess boxes (cheaper and robust than booleans)
    nz = 6
    for x in xs:
        for j in range(nz + 1):
            fz = j / nz
            z = z0 + (z1 - z0) * fz
            b = hb_local(x, z) - inset
            if not (b == b) or b < 0.4:
                b = 2.2
            verts.append((x, side * b))
    for i in range(len(xs) - 1):
        for j in range(nz):
            a = i * (nz + 1) + j
            q = (a, a + 1, a + nz + 2, a + nz + 1)
            faces.append(q if side > 0 else q[::-1])
    ob = mesh_object(name + "_%d" % side, verts, faces, col=COL, mat=mat)
    # window row
    zz = win_rows[0]
    if zz:
        objs = [ob]
        n = int((x1 - x0) / 1.55)
        rows = [zz]
        # second row for the upper (promenade) tier
        rows.append((zz[0] + 2.55, zz[1]))
        for (z_s, z_h) in rows:
            for i in range(n):
                xc = x0 + (i + 0.5) * (x1 - x0) / n
                b = hb_local(xc, z_s + 0.6) - inset
                if not (b == b) or b < 1.2:
                    continue
                v, f = box((xc, side * (b - side * 0.015), z_s + z_h / 2),
                           (0.76, 0.03, z_h))
                objs.append(mesh_object("{}_win".format(name), v, f, col=COL,
                                        mat=P["glass"]))
                v, f = box((xc, side * (b + side * 0.02), z_s + z_h / 2),
                           (0.92, 0.05, z_h + 0.14))
                objs.append(mesh_object("{}_wf".format(name), v, f, col=COL,
                                        mat=mat))
        return objs
    return [ob]


def _house_end(name, x, z0, z1, mat, inset=0.95):
    """End bulkhead of a house - a wall across the full width of the ship's
    side at that height (so the house never leaves an open gap to the shell)."""
    seq = 8
    verts = []; faces = []
    for j in range(seq + 1):
        fz = j / seq
        z = z0 + (z1 - z0) * fz
        b = hb_local(x, z) - inset
        if not (b == b) or b < 0.8:
            b = 1.2
        verts.append((x, -b, z)); verts.append((x, b, z))
    for j in range(seq):
        a = j * 2
        faces.append((a, a + 1, a + 3, a + 2))
    ob = mesh_object(name, verts, faces, col=COL, mat=mat)
    solid = ob.modifiers.new("Solidify", 'SOLIDIFY')
    solid.thickness = 0.10
    return ob


# The modules are built and joined in a FRESH, EMPTY scene (module_superstructure
# .blend contains only superstructure objects, no hull).  So deckhouse and deck
# fitting heights must come from the SPEC, never from sampling the hull - there
# is no hull in that scene to sample.
def hb_local(x, z):
    """Half breadth at (x, z), from the spec rather than from hull geometry."""
    from shipdesign.hull import HULL as _H
    b = _H.half_beam_at(x, z)
    if b > 0.5:
        return b
    zdeck = float(_H.deck_z(x))
    base = _H.half_beam_at(x, zdeck - 0.05)
    if base > 0.5:
        return max(base - 0.42 - 0.05 * (z - zdeck), 0.8)
    return max(base, 0.8)


def _deck_plate(name, z, x0, x1, mat, nx=90, ny=10, inset=0.30):
    verts = []; faces = []
    xs = np.linspace(x0, x1, nx)
    keep = []
    for x in xs:
        b = deck_edge_halfbeam(x, z, inset)
        keep.append(b)
    keep = np.array(keep)
    if keep.max() < 0.5:
        return None
    for x, b in zip(xs, keep):
        b = max(b, 0.08)
        for j in range(ny + 1):
            verts.append((x, -b + 2 * b * j / ny, z))
    for i in range(nx - 1):
        for j in range(ny):
            a = i * (ny + 1) + j
            faces.append((a, a + 1, a + ny + 2, a + ny + 1))
    return mesh_object(name, verts, faces, col=COL, mat=mat)


# ---------------------------------------------------------------------------
# promenade-deck houses (library, smoking saloon, music room)
# ---------------------------------------------------------------------------
def promenade_houses():
    objs = []
    z0 = DECK_Z["prom"] + 0.02
    z1 = DECK_Z["boat"] - 0.10
    for deck_room in layout.rooms_on("prom"):
        # public rooms get houses, others are formed by the boat deck above
        if deck_room["use"] not in ("first", "second"):
            continue
        yh = min(abs(deck_room["y1"]), abs(deck_room["y0"]))
        if yh < 2.0:
            continue
        mat = P["oak_light"] if "Library" in deck_room["name"] else P["mahogany"]
        roof = P["white_ceiling"]
        objs += house("Prom_" + deck_room["name"].split()[0],
                      deck_room["x0"], deck_room["x1"], yh, z0, z1, mat,
                      roof_mat=roof, win_pitch=1.75)
    return objs


# ---------------------------------------------------------------------------
# boat deck, rails, bridge
# ---------------------------------------------------------------------------
def boat_deck_and_rails():
    objs = []
    z = DECK_Z["boat"]
    objs.append(_deck_plate("BoatDeck_Plate", z + 0.02, -40.0, 36.0,
                            P["deck_wood"], nx=70, ny=8))
    # perimeter rail with stanchions, following the deck edge
    for side in (1, -1):
        pts = []
        for x in np.linspace(-45.0, 41.0, 60):
            b = deck_edge_halfbeam(x, DECK_Z["boat"], 0.28)
            if b < 0.4:
                continue
            pts.append((x, side * b))
        if len(pts) > 2:
            objs += railing(pts, DECK_Z["boat"], height=1.05, col=COL,
                            name="BoatDeck_Rail", mat_rail=P["teak"],
                            mat_stanchion=P["upper_white"])
    return objs


def promenade_rails_and_columns():
    """Open promenade rail at the ship's side plus the slim columns that carry
    the boat-deck overhang (the 'sheltered promenade' of 1889 practice)."""
    objs = []
    z = DECK_Z["prom"]
    for side in (1, -1):
        pts = []
        for x in np.linspace(-62.0, 54.0, 90):
            b = deck_edge_halfbeam(x, z, 0.08)
            if b < 0.4:
                continue
            pts.append((x, side * b))
        if len(pts) > 2:
            objs += railing(pts, z, height=1.07, col=COL, name="Prom_Rail",
                            mat_rail=P["teak"], mat_stanchion=P["upper_white"])
        # columns
        for x in np.arange(-30.0, 40.0, 5.6):
            b = deck_edge_halfbeam(x, z, 0.26)
            if b < 0.6:
                continue
            v, f = cylinder((x, side * b, z + (DECK_Z["boat"] - z) / 2),
                            0.075, DECK_Z["boat"] - z, segments=8)
            objs.append(mesh_object("Prom_Col", v, f, col=COL,
                                    mat=P["upper_white"]))
    return objs


def build_bridge():
    objs = []
    zb = DECK_Z["bridge"]
    # wheelhouse (teak, cambered front, large windows)
    x0, x1, yh = 12.0, 22.0, 4.9
    v, f = box(((x0 + x1) / 2, 0, zb + 1.35), (x1 - x0, 2 * yh, 2.7))
    objs.append(mesh_object("Wheelhouse", v, f, col=COL, mat=P["teak"]))
    # windows all round
    for side in (1, -1):
        for i in range(4):
            xc = x0 + 1.4 + i * 2.2
            v, f = box((xc, side * (yh + 0.02), zb + 1.95), (1.7, 0.06, 0.95))
            objs.append(mesh_object("WH_Glass", v, f, col=COL, mat=P["glass"]))
    for i in range(4):
        yc = -3.0 + i * 2.0
        v, f = box((x1 + 0.02, yc, zb + 1.95), (0.06, 1.5, 0.95))
        objs.append(mesh_object("WH_Glass_F", v, f, col=COL, mat=P["glass"]))
    # bridge wings + dodger
    for side in (1, -1):
        v, f = box((15.0, side * (yh + 1.1), zb + 0.06), (13.0, 2.4, 0.12))
        objs.append(mesh_object("Bridge_Wing", v, f, col=COL, mat=P["teak"]))
        objs += railing([(9.0, side * (yh + 2.2)), (21.6, side * (yh + 2.2))],
                        zb + 0.12, 1.05, col=COL, name="Wing_Rail",
                        mat_rail=P["teak"], mat_stanchion=P["upper_white"])
    # canvas dodger (wind screen) across the front
    v, f = box((x1 + 0.35, 0, zb + 1.05), (0.05, 2 * yh + 1.6, 1.1))
    objs.append(mesh_object("Dodger", v, f, col=COL, mat=P["canvas"]))
    # engine-room telegraphs and binnacle on the bridge wing
    for side in (1, -1):
        v, f = cylinder((19.0, side * 1.3, zb + 0.75), 0.16, 1.1, segments=10)
        objs.append(mesh_object("Telegraph", v, f, col=COL, mat=P["brass"]))
        v, f = box((19.0, side * 1.3, zb + 1.32), (0.42, 0.24, 0.30))
        objs.append(mesh_object("Telegraph_Face", v, f, col=COL,
                                mat=P["white_ceiling"]))
    v, f = cylinder((17.4, 0, zb + 0.62), 0.30, 1.24, segments=14,
                    radius_top=0.22)
    objs.append(mesh_object("Binnacle", v, f, col=COL, mat=P["brass"]))
    # bridge deck plating
    objs.append(_deck_plate("Bridge_Deck", zb, 8.0, 32.0, P["teak"],
                            nx=26, ny=6))
    return objs


# ---------------------------------------------------------------------------
# funnels
# ---------------------------------------------------------------------------
def build_funnels():
    objs = []
    from shipdesign.spec import FUNNEL_COLORS
    z_base = DECK_Z["boat"] - 0.2
    for i, f in enumerate(FUNNELS):
        x, d, top = f["x"], f["dia"], f["top_z"]
        r = d / 2
        # slight taper and an elliptical plan (wider fore-aft) as in the photos
        n_theta = 40
        prof = [(r * 1.02, z_base), (r, z_base + 4.0), (r * 0.94, top - 2.2),
                (r * 0.94, top - 2.2), (r * 0.96, top)]
        verts = []; faces = []
        for (rr, z) in prof:
            for k in range(n_theta):
                a = 2 * math.pi * k / n_theta
                verts.append((x + rr * 1.28 * math.cos(a),
                              rr * math.sin(a), z))
        for j in range(len(prof) - 1):
            for k in range(n_theta):
                k2 = (k + 1) % n_theta
                a = j * n_theta + k; b = j * n_theta + k2
                c = (j + 1) * n_theta + k2; e = (j + 1) * n_theta + k
                faces.append((a, b, c, e))
        ob = mesh_object("Funnel_%d" % i, verts, faces, col=COL,
                         mat=P["funnel"], smooth_angle=math.radians(50))
        ob.data.materials.append(P["funnel_top"])
        ob.data.materials.append(P["funnel_inner"])
        me = ob.data
        for poly in me.polygons:
            z = poly.center.z
            if z > top - 2.22:
                poly.material_index = 1
            if (poly.normal.z < -0.5):
                poly.material_index = 2
        objs.append(ob)
        # black inner mouth disc
        v, f = cylinder((x, 0, top - 0.35), r * 0.90, 0.05, segments=24)
        objs.append(mesh_object("Funnel_Mouth_%d" % i, v, f, col=COL,
                                mat=P["funnel_inner"]))
        # steam pipe up the after side + whistle
        v, f = cylinder((x - r * 1.12, 0.55, (z_base + top) / 2 - 1.0),
                        0.10, top - z_base - 2.0, segments=8)
        objs.append(mesh_object("SteamPipe_%d" % i, v, f, col=COL,
                                mat=P["steel"]))
        v, f = cylinder((x - r * 1.12, 0.55, top - 3.2), 0.14, 0.5, segments=10)
        objs.append(mesh_object("Whistle_%d" % i, v, f, col=COL,
                                mat=P["brass"]))
        # ladder
        for k in range(22):
            zz = z_base + 0.4 + k * 0.62
            if zz > top - 0.5:
                break
            v, f = box((x + r * 1.30, 0.0, zz), (0.10, 0.52, 0.035))
            objs.append(mesh_object("Funnel_Rung_%d" % i, v, f, col=COL,
                                    mat=P["steel"]))
        # casing / uptake into the deckhouse
        v, f = box((x, 0, z_base - 0.3), (d * 1.35, d * 1.2, 0.9))
        objs.append(mesh_object("Funnel_Casing_%d" % i, v, f, col=COL,
                                mat=P["upper_white"]))
    return objs


# ---------------------------------------------------------------------------
# masts and rigging
# ---------------------------------------------------------------------------
def build_masts():
    objs = []
    for m in MASTS:
        x = m["x"]; h = m["height_m"]; d = m["diameter"]
        base = 10.6
        rake = math.tan(math.radians(m["rake_deg"]))
        n = 10
        prof = []
        for k in range(n + 1):
            f = k / n
            prof.append((d / 2 * (1 - 0.45 * f), base + h * f))
        verts = []; faces = []
        nt = 14
        for (r, z) in prof:
            xx = x + (z - base) * rake
            for k in range(nt):
                a = 2 * math.pi * k / nt
                verts.append((xx + r * math.cos(a), r * math.sin(a), z))
        for j in range(len(prof) - 1):
            for k in range(nt):
                k2 = (k + 1) % nt
                a = j * nt + k; b = j * nt + k2
                c = (j + 1) * nt + k2; e = (j + 1) * nt + k
                faces.append((a, b, c, e))
        # truck
        faces.append(tuple(range(nt - 1, -1, -1)))
        top = len(verts) - nt
        faces.append(tuple(range(top, top + nt)))
        objs.append(mesh_object("Mast_" + m["name"], verts, faces, col=COL,
                                mat=P["oak_light"], smooth_angle=math.radians(50)))
        xtop = x + (base + h - base) * rake
        # crosstrees / top (two platforms)
        for f, w in ((0.62, 1.6), (0.80, 1.1)):
            zz = base + h * f
            v, ff = box((x + (zz - base) * rake, 0, zz), (2 * w, 0.28, 0.12))
            objs.append(mesh_object("Crosstree", v, ff, col=COL,
                                    mat=P["oak_light"]))
        # foremast: two square yards
        if m["name"] == "foremast":
            for f, w in ((0.55, 9.5), (0.78, 6.5)):
                zz = base + h * f
                v, ff = cylinder((x + (zz - base) * rake, 0, zz), 0.16,
                                 2 * w, axis='Y', segments=10)
                objs.append(mesh_object("Yard", v, ff, col=COL,
                                        mat=P["oak_light"]))
        # gaff + boom for the fore-and-aft sails on main & mizzen
        if m["name"] in ("mainmast", "mizzenmast"):
            zz = base + h * 0.72
            v, ff = box((x - 3.0, 0, zz), (6.2, 0.16, 0.20))
            objs.append(mesh_object("Gaff", v, ff, col=COL, mat=P["oak_light"]))
            zz2 = base + h * 0.40
            v, ff = box((x - 5.0, 0, zz2), (10.4, 0.20, 0.24))
            objs.append(mesh_object("Boom", v, ff, col=COL, mat=P["oak_light"]))
        # masthead light + truck
        v, f = cylinder((xtop, 0, base + h + 0.15), 0.10, 0.3, segments=8)
        objs.append(mesh_object("Mast_Light", v, f, col=COL, mat=P["lamp"]))
    return objs


def build_rigging():
    """Wire standing rigging: shrouds, stays, backstays (Teutonic rigged
    schooner, no royal yards)."""
    objs = []
    v = []; f = []
    tops = {}
    for m in MASTS:
        base = 10.6
        tops[m["name"]] = (m["x"] + (m["height_m"]) * math.tan(math.radians(1.5)),
                           base + m["height_m"] * 0.80)
    # shrouds from each masthead to the deck edge
    for m in MASTS:
        xt, zt = tops[m["name"]]
        for side in (1, -1):
            for k in range(4):
                xd = xt - 2.4 - k * 1.25
                yd = side * (HULL.half_beam_at(xd, DECK_Z["prom"]) - 0.45)
                vv, ff = tube([(xt, side * 0.35, zt),
                               (xd, yd, DECK_Z["prom"] + 1.0)], 0.022, 5)
                off = len(v); v += vv
                f += [tuple(i + off for i in q) for q in ff]
    # forestays between mastheads
    chain = [("foremast", "mainmast"), ("mainmast", "mizzenmast")]
    for a, b in chain:
        xa, za = tops[a]; xb, zb = tops[b]
        vv, ff = tube([(xa, 0, za), (xb, 0, zb)], 0.026, 5)
        off = len(v); v += vv
        f += [tuple(i + off for i in q) for q in ff]
    # stay from foremast head to the stem
    xa, za = tops["foremast"]
    vv, ff = tube([(xa, 0, za), (82.5, 0, 11.0)], 0.030, 5)
    off = len(v); v += vv
    f += [tuple(i + off for i in q) for q in ff]
    # backstay from mizzen to the stern
    xa, za = tops["mizzenmast"]
    vv, ff = tube([(xa, 0, za), (-81.5, 0, 10.2)], 0.026, 5)
    off = len(v); v += vv
    f += [tuple(i + off for i in q) for q in ff]
    if v:
        objs.append(mesh_object("Rigging", v, f, col=COL, mat=P["rope"]))
    return objs


# ---------------------------------------------------------------------------
# boats and davits
# ---------------------------------------------------------------------------
def boat_hull(name, x, y, z, loa, beam, depth=0.85, colour=None):
    """Clinker-built ship's boat: lofted double-ended hull with thwarts."""
    n = 16
    verts = []; faces = []
    xs = np.linspace(-loa / 2, loa / 2, n)
    for xi in xs:
        u = xi / (loa / 2)
        b = beam / 2 * math.cos(u * math.pi / 2) ** 0.62
        sheer = 0.22 * u ** 2
        for (zb, bb) in ((0.0, b * 0.62), (depth * 0.5, b * 0.92),
                         (depth + sheer, b)):
            verts.append((x + xi, y - bb, z + zb))
            verts.append((x + xi, y + bb, z + zb))
    for i in range(n - 1):
        a = i * 6
        for k in range(2):
            faces.append((a + k, a + k + 2, a + k + 8, a + k + 6))
        # transom-ish closure at the ends is implicit by pinching
    # closing bottom
    for i in range(n - 1):
        a = i * 6
        faces.append((a, a + 6, a + 7, a + 1))
    ob = mesh_object(name, verts, faces, col=COL,
                     mat=colour or P["upper_white"],
                     smooth_angle=math.radians(55))
    return ob


def build_boats():
    objs = []
    zb = DECK_Z["boat"] + 0.02
    # Inboard boat rows (the ship's own lifeboat outfit) + the two craft
    # reserved for Agent 02 on outboard davits.
    from shipdesign.spec import STARBOARD_BOATS, PORT_BOATS
    # lifeboats: 4 per side on the boat deck
    for side in (1, -1):
        for i, x in enumerate((36.0, 20.0, -12.0, -28.0)):
            y = side * 6.6
            objs.append(boat_hull("Lifeboat_%d_%d" % (side, i), x, y,
                                  zb + 0.75, 8.6, 2.9, 1.05,
                                  colour=P["upper_white"]))
            # davits
            for dx in (-4.2, 4.2):
                objs += _davit(x + dx, y, zb, side)
            # boat cover
            v, f = box((x, y, zb + 1.85), (8.2, 2.75, 0.06))
            objs.append(mesh_object("Boat_Cover", v, f, col=COL,
                                    mat=P["canvas"]))
    # Agent 02 craft: 25 ft steam cutter (stbd), rowing cutter (port)
    for side, spec_list in ((1, STARBOARD_BOATS), (-1, PORT_BOATS)):
        for (x, kind) in spec_list:
            b = LIFEBOATS[kind]
            y = side * (HULL.half_beam_at(x, DECK_Z["prom"]) - 0.55)
            objs.append(boat_hull("Agent02_" + kind, x, y, zb + 0.95,
                                  b["loa"], b["beam"], 0.95,
                                  colour=P["teak"] if "steam" in kind
                                  else P["upper_white"]))
            for dx in (-b["loa"] * 0.38, b["loa"] * 0.38):
                objs += _davit(x + dx, y, zb, side, height=2.9)
    return objs


def _davit(x, y, z0, side, height=2.6):
    """Trotman-type radial davit: curved arm on a swivel post."""
    objs = []
    v, f = cylinder((x, y * 0.98, z0 + height / 2), 0.075, height, segments=8)
    objs.append(mesh_object("Davit_Post", v, f, col=COL, mat=P["steel"]))
    pts = [(x, y * 0.98, z0 + height)]
    for k in range(1, 6):
        th = k / 5 * math.pi / 2
        pts.append((x, y * 0.98 - side * 1.15 * math.sin(th),
                    z0 + height + 0.55 * math.sin(th) * -1 + 0.55 * (1 - math.cos(th))))
    vv, ff = tube(pts, 0.065, 6)
    objs.append(mesh_object("Davit_Arm", vv, ff, col=COL, mat=P["steel"]))
    return objs


# ---------------------------------------------------------------------------
# deck machinery & details
# ---------------------------------------------------------------------------
def cowl(x, y, z, height=2.2, dia=0.62, facing=1, colour=None):
    """Ventilator cowl - one of the most characteristic fittings of the era."""
    objs = []
    v, f = cylinder((x, y, z + height / 2), 0.13, height, segments=10)
    objs.append(mesh_object("Cowl_Post", v, f, col=COL, mat=P["steel"]))
    # the cowl head: a bent elbow with a flared mouth, built from rings
    verts = []; faces = []
    nt = 14
    N = 7
    for k in range(N):
        f_ = k / (N - 1)
        ang = f_ * math.pi * 0.55
        r = dia / 2 * (1 + 0.42 * f_)
        cx = x + facing * (0.30 * math.sin(ang)) * 1.1
        cz = z + height + 0.30 * (1 - math.cos(ang)) + 0.02
        for i in range(nt):
            a = 2 * math.pi * i / nt
            verts.append((cx, y + r * math.cos(a),
                          cz + r * math.sin(a) * 0.95))
    for j in range(N - 1):
        for i in range(nt):
            i2 = (i + 1) % nt
            a = j * nt + i; b = j * nt + i2
            c = (j + 1) * nt + i2; e = (j + 1) * nt + i
            faces.append((a, b, c, e))
    objs.append(mesh_object("Cowl_Head", verts, faces, col=COL,
                            mat=colour or P["upper_white"],
                            smooth_angle=math.radians(50)))
    return objs


def hatch(x, z, w=3.4, l=4.6, coaming=0.55):
    objs = []
    v, f = box((x, 0, z + coaming / 2), (l, w, coaming))
    objs.append(mesh_object("Hatch_Coaming", v, f, col=COL, mat=P["steel"]))
    v, f = box((x, 0, z + coaming + 0.03), (l + 0.12, w + 0.12, 0.06))
    objs.append(mesh_object("Hatch_Board", v, f, col=COL, mat=P["canvas"]))
    return objs


def capstan(x, y, z, r=0.55):
    objs = []
    v, f = cylinder((x, y, z + 0.35), r, 0.7, segments=12, radius_top=r * 0.82)
    objs.append(mesh_object("Capstan", v, f, col=COL, mat=P["cast_iron"]))
    for k in range(8):
        a = 2 * math.pi * k / 8
        v, f = box((x + (r + 0.18) * math.cos(a), y + (r + 0.18) * math.sin(a),
                    z + 0.66), (0.3, 0.14, 0.12), rot_z=a)
        objs.append(mesh_object("Capstan_Bar", v, f, col=COL,
                                mat=P["cast_iron"]))
    return objs


def bollards(x, y, z, n=2):
    objs = []
    for k in range(n):
        v, f = cylinder((x + k * 0.62, y, z + 0.30), 0.11, 0.60, segments=10,
                        radius_top=0.14)
        objs.append(mesh_object("Bollard", v, f, col=COL, mat=P["cast_iron"]))
    return objs


def winch(x, y, z):
    objs = []
    v, f = box((x, y, z + 0.30), (2.4, 0.85, 0.55))
    objs.append(mesh_object("Winch_Bed", v, f, col=COL, mat=P["cast_iron"]))
    v, f = cylinder((x, y, z + 0.62), 0.30, 1.8, axis='X', segments=12)
    objs.append(mesh_object("Winch_Drum", v, f, col=COL, mat=P["steel"]))
    for dx in (-0.75, 0.75):
        v, f = cylinder((x + dx, y, z + 0.62), 0.36, 0.10, axis='X', segments=12)
        objs.append(mesh_object("Winch_Flange", v, f, col=COL, mat=P["steel"]))
    return objs


def deck_machinery():
    objs = []
    zm = DECK_Z["main"] + 0.02
    zp = DECK_Z["prom"] + 0.02
    # forecastle
    for side in (1, -1):
        objs += bollards(76.0, side * 5.6, zm, 2)
    objs += capstan(74.0, 0, zm + 0.02, 0.62)
    v, f = box((70.5, 0, zm + 0.55), (1.9, 3.0, 1.1))
    objs.append(mesh_object("Windlass", v, f, col=COL, mat=P["cast_iron"]))
    # cargo hatches on the main deck
    for x in (55.0, -52.0):
        objs += hatch(x, zm, 3.6, 4.8)
        for side in (1, -1):
            objs += winch(x + 3.4, side * 5.2, zm)
    # ventilators
    for (x, y, h, fac) in ((44.0, 5.6, 2.4, 1), (44.0, -5.6, 2.4, 1),
                           (-4.0, 6.6, 2.0, -1), (-4.0, -6.6, 2.0, -1),
                           (16.0, 6.9, 1.9, 1), (-24.0, 6.9, 1.9, 1),
                           (16.0, -6.9, 1.9, 1), (-24.0, -6.9, 1.9, 1)):
        objs += cowl(x, y, zp, h, 0.62, fac)
    # skylights (engine & boiler rooms)
    for x in (24.0, -3.0):
        v, f = box((x, 0, DECK_Z["boat"] + 0.45), (3.2, 2.4, 0.9))
        objs.append(mesh_object("Skylight", v, f, col=COL,
                                mat=P["upper_white"]))
        v, f = box((x, 0, DECK_Z["boat"] + 0.92), (3.0, 2.2, 0.05))
        objs.append(mesh_object("Skylight_Glass", v, f, col=COL,
                                mat=P["glass_ground"]))
    # mooring bitts aft
    for side in (1, -1):
        objs += bollards(-76.0, side * 4.6, zm, 2)
    return objs


def navigation_lights():
    objs = []
    # side lights on the bridge wings: red port, green starboard
    for side, col in ((1, (0.5, 0.06, 0.05)), (-1, (0.05, 0.35, 0.10))):
        mat = principled("NavLight_%d" % side, (*col, 1), 0.2,
                         emit=(*col, 1), emit_strength=3.0)
        v, f = box((12.5, side * 7.4, DECK_Z["bridge"] + 1.3), (0.55, 0.4, 0.5))
        objs.append(mesh_object("NavLight", v, f, col=COL, mat=mat))
    return objs


# ---------------------------------------------------------------------------
def build(col, P_):
    global COL, P
    COL, P = col, P_
    groups = {}
    sh = saloon_deck_house()
    plates = [o for o in sh if o and o.name.startswith("SaloonDeck_Plate")]
    walls = [o for o in sh if o and o not in plates]
    groups["saloon_house"] = join_objects(walls, "DeckHouse_SaloonDeck")
    groups["saloon_prom_decks"] = join_objects(plates, "Decks_SaloonProm")
    groups["prom_houses"] = join_objects(promenade_houses(), "DeckHouse_Promenade")
    groups["prom_rails"] = join_objects(promenade_rails_and_columns(),
                                        "Promenade_Rails")
    groups["boat_deck"] = join_objects(boat_deck_and_rails(), "BoatDeck")
    groups["bridge"] = join_objects(build_bridge(), "Bridge")
    groups["funnels"] = join_objects(build_funnels(), "Funnels")
    groups["masts"] = join_objects(build_masts(), "Masts")
    groups["rigging"] = join_objects(build_rigging(), "Rigging")
    groups["boats"] = join_objects(build_boats(), "Boats_Davits")
    groups["machinery"] = join_objects(deck_machinery(), "DeckMachinery")
    groups["navlights"] = join_objects(navigation_lights(), "NavLights")
    return groups


if __name__ == "__main__":
    sc = reset_scene()
    P = build_palette()
    col = collection("SHIP_SUPERSTRUCTURE")
    groups = build(col, P)
    for k, v in groups.items():
        print("built", k, v.name if v else None,
              len(v.data.vertices) if v else 0)
    out = os.path.join(ROOT, "models", "module_superstructure.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print("saved", out)
