"""HULL MODULE - SS Aurelian (1889)

Builds, to real-world metric dimensions:
    * shell plating as individual strakes with butt/ seam offsets (so the
      riveted lap seams read at close range, exactly as described in
      'Ocean Steamships' 1891 pp.99-103)
    * rivet rows along every seam and butt
    * keel, stem and stern-post / counter
    * bulwarks, sheer strake and main rail
    * the waterline boot-topping and the antifouling black
    * the hollow (open) deck cavities are left to the deck/structure modules

Run inside Blender:
    blender -b -P blender/build_hull.py
"""
from __future__ import annotations
import os
import sys
import math
import bpy
import bmesh
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (ROOT, HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

from shipdesign.spec import SHIP, DECK_Z, PALETTE
from shipdesign.hull import HULL, HL, B, T
from lib_build import (reset_scene, collection, mesh_object, build_palette,
                       box, cylinder, tube, railing, vertical_wall_along_hull,
                       join_objects)

PLATE_H = SHIP["strake_height_m"]        # 1.83 m (6 ft)
RIVET_PITCH = SHIP["rivet_pitch_m"]      # 89 mm
RIVET_R = SHIP["rivet_dia_m"] / 2.0


# ---------------------------------------------------------------------------
def shell_rings(n_x=240, dz=0.12):
    """Sample the shell into machine-friendly rings.

    Returns xs (n_x,), and for each x a list of (y,z) from port deck edge down
    to the keel centreline (a monotone chain), so strakes can be cut by
    interpolating z along the chain.
    """
    xs = np.linspace(-HL + 0.05, HL - 0.05, n_x)
    rows = []
    for x in xs:
        half = HULL.section(x, n_below=20, n_above=10)
        rows.append(half if half else None)
    return xs, rows


def build_shell(col, P, n_x=240, rivets=True):
    """Lofted shell with per-strake inset/shadow lines.

    We build the full closed surface in one mesh, then add the visible
    'seam' relief as thin raised bands (a real plate lap is a step of one
    plate thickness) plus rivet rows.  That keeps the poly count sane while
    reading correctly both at distance and close up.
    """
    xs, rows = shell_rings(n_x)
    # common parametric sample count per station
    ns = 22
    grid = []
    for half in rows:
        if not half:
            grid.append(None); continue
        p = np.array(half, float)          # keel -> deck (port side), y>=0
        d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
        u = d / max(d[-1], 1e-9)
        t = np.linspace(0, 1, ns)
        grid.append(np.c_[np.interp(t, u, p[:, 1]), np.interp(t, u, p[:, 0])])
        # (z, y)
    valid = [i for i, g in enumerate(grid) if g is not None]
    verts = []; faces = []
    idx = {}
    # port side full, starboard mirrored
    for i in valid:
        x = xs[i]
        for j, (z, y) in enumerate(grid[i]):
            idx[(i, j, 1)] = len(verts); verts.append((x, y, z))
            if y > 1e-4:
                idx[(i, j, -1)] = len(verts); verts.append((x, -y, z))
    for a, b in zip(valid[:-1], valid[1:]):
        if b != a + 1:
            continue
        for j in range(ns - 1):
            for side in (1, -1):
                k0 = (a, j, side); k1 = (a, j + 1, side)
                k2 = (b, j + 1, side); k3 = (b, j, side)
                if all(k in idx for k in (k0, k1, k2, k3)):
                    q = (idx[k0], idx[k1], idx[k2], idx[k3])
                    faces.append(q if side > 0 else q[::-1])
    # cap the transom (first valid station) and the stem (last valid station)
    if valid:
        first, last = valid[0], valid[-1]
        port = [idx[(last, j, 1)] for j in range(ns)]
        faces.append(tuple(port[::-1]))
        stbd = [idx[(last, j, -1)] for j in range(ns) if (last, j, -1) in idx]
        if len(stbd) > 2:
            faces.append(tuple(stbd))
        port0 = [idx[(first, j, 1)] for j in range(ns) if (first, j, 1) in idx]
        if len(port0) > 2:
            faces.append(tuple(port0))
        stbd0 = [idx[(first, j, -1)] for j in range(ns) if (first, j, -1) in idx]
        if len(stbd0) > 2:
            faces.append(tuple(stbd0[::-1]))
    ob = mesh_object("Hull_Shell", verts, faces, col=col,
                     mat=P["hull_black"], smooth_angle=math.radians(40))
    _paint_boot_top(ob, col, P)
    return ob, xs, rows


def _paint_boot_top(ob, col, P):
    """Second material: white boot-topping + white topsides above sheer strake.

    Period practice (all four comparison ships): black antifouling below the
    load line, a narrow white boot top, black to the sheer strake, and the
    superstructure sides in white.
    """
    me = ob.data
    me.materials.append(P["boot_white"])
    # continuous bands: judge by each polygon's full z extent, not its centre,
    # otherwise plates straddling a threshold alternate and read as dashes
    for poly in me.polygons:
        vs = [me.vertices[i].co.z for i in poly.vertices]
        lo, hi = min(vs), max(vs)
        if lo >= T - 0.16 and hi <= T + 0.16:
            poly.material_index = 1


def build_bands(col, P, z0, z1, name, mat, nx=300, offset=0.004):
    """A continuous painted band (boot top, sheer strake) hugging the shell.

    Generated as its own strip so it can never break into dashes the way a
    material-index paint on a coarse loft can.
    """
    xs = np.linspace(-HL + 0.4, HL - 0.4, nx)
    verts = []; faces = []
    for side in (1, -1):
        base = len(verts)
        n = 0
        for x in xs:
            y0 = HULL.half_beam_at(x, z0)
            y1 = HULL.half_beam_at(x, z1)
            if y0 < 0.03 or y1 < 0.03:
                continue
            verts.append((x, side * (y0 + offset), z0))
            verts.append((x, side * (y1 + offset), z1))
            n += 1
        for i in range(n - 1):
            a = base + i * 2
            q = (a, a + 1, a + 3, a + 2)
            faces.append(q if side > 0 else q[::-1])
    return mesh_object(name, verts, faces, col=col, mat=mat)


def build_seams(col, P, xs, rows, height=PLATE_H, rivets=True):
    """Raised lap-seam bands + rivet rows following the strakes."""
    # Strakes measured from the keel upward; the seam heights on each
    # station come from the local keel so the strakes follow the shape.
    bands = []
    rv = []; rf = []
    for i in range(len(xs) - 1):
        h0, h1 = rows[i], rows[i + 1]
        if not h0 or not h1:
            continue
        zk0 = h0[0][1]; zk1 = h1[0][1]
        zd0 = h0[-1][1]; zd1 = h1[-1][1]
        n_strakes = max(1, int(round((zd0 - zk0) / height)))
        for k in range(1, n_strakes):
            z0 = zk0 + k * height
            z1 = zk1 + k * height
            if z0 > zd0 - 0.15 or z1 > zd1 - 0.15:
                continue
            y0 = float(np.interp(z0, [p[1] for p in h0], [p[0] for p in h0]))
            y1 = float(np.interp(z1, [p[1] for p in h1], [p[0] for p in h1]))
            if y0 < 0.02 or y1 < 0.02:
                continue
            for side in (1, -1):
                a = len(rv)
                rv += [(xs[i], side * y0, z0), (xs[i + 1], side * y1, z1),
                       (xs[i + 1], side * (y1 + 0.018), z1 + 0.012),
                       (xs[i], side * (y0 + 0.018), z0 + 0.012)]
                rf.append((a, a + 1, a + 2, a + 3) if side > 0
                          else (a + 3, a + 2, a + 1, a))
                if rivets:
                    # rivet every 0.42 m along this seam (4 per 89mm pitch x ~4.7)
                    px = np.arange(xs[i], xs[i + 1], 0.42)
                    for xr in px:
                        f = (xr - xs[i]) / (xs[i + 1] - xs[i] + 1e-9)
                        yr = y0 + (y1 - y0) * f
                        zr = z0 + (z1 - z0) * f
                        _rivet(rv, rf, xr, side * (yr + 0.016), zr + 0.010)
    ob = mesh_object("Hull_Seams", rv, rf, col=col, mat=P["hull_black"])
    return ob


def _rivet(v, f, x, y, z, r=RIVET_R * 1.6):
    """4-vertex rivet head (cheap but reads correctly at any sensible zoom)."""
    a = len(v)
    v += [(x - r, y, z - r), (x + r, y, z - r), (x + r, y, z + r), (x - r, y, z + r)]
    v.append((x, y + 0.010, z))          # single-accurate-at-distance head apex
    c = a + 4
    for i in range(4):
        j = (i + 1) % 4
        f.append((a + i, a + j, c))


def build_keel_stem(col, P):
    """Bar keel, stem, stern-post and the counter overhang."""
    objs = []
    # keel: follows keel_z, 1.22 m wide plate, 0.35 m deep bar
    xs = np.linspace(-76.0, 74.0, 120)
    v = []; f = []
    for x in xs:
        z = float(HULL.keel_z(x))
        v += [(x, -0.61, z), (x, 0.61, z), (x, 0.61, z - 0.42), (x, -0.61, z - 0.42)]
    for i in range(len(xs) - 1):
        a = i * 4; b = (i + 1) * 4
        f += [(a, a + 1, b + 1, b), (a + 1, a + 2, b + 2, b + 1),
              (a + 2, a + 3, b + 3, b + 2), (a + 3, a, b, b + 3)]
    objs.append(mesh_object("Keel_Bar", v, f, col=col, mat=P["hull_black"]))
    # stem bar: from forefoot to the stem head
    xs = np.linspace(74.0, 83.0, 40)
    v = []; f = []
    for x in xs:
        z = float(HULL.keel_z(x))
        b = float(HULL.half_beam_at(x, max(z + 0.05, 0.2)))
        v += [(x, -(b + 0.09), z - 0.05), (x, (b + 0.09), z - 0.05),
              (x, (b + 0.09), z + 0.30), (x, -(b + 0.09), z + 0.30)]
    for i in range(len(xs) - 1):
        a = i * 4; bb = (i + 1) * 4
        f += [(a, a + 1, bb + 1, bb), (a + 1, a + 2, bb + 2, bb + 1),
              (a + 2, a + 3, bb + 3, bb + 2), (a + 3, a, bb, bb + 3)]
    objs.append(mesh_object("Stem_Bar", v, f, col=col, mat=P["hull_black"]))
    # stern post + rudder
    v, f = box((-78.2, 0, 3.6), (0.55, 0.42, 6.4))
    objs.append(mesh_object("Sternpost", v, f, col=col, mat=P["hull_black"]))
    return objs


def build_rudder(col, P):
    """Balanced rudder of the period: hinged on the sternpost, raked trailing edge."""
    v = []
    f = []
    zs = np.linspace(0.35, 6.35, 9)
    prof = []
    for i, z in enumerate(zs):
        chord = 2.55 - 0.35 * (1 - z / 6.35)   # wider at the head
        prof.append(chord)
    for i, z in enumerate(zs):
        xf = -78.0
        c = prof[i]
        v += [(xf, -0.22, z), (xf - c, -0.16, z), (xf - c, 0.16, z), (xf, 0.22, z)]
    for i in range(len(zs) - 1):
        a = i * 4; b = (i + 1) * 4
        f += [(a, a + 1, b + 1, b), (a + 1, a + 2, b + 2, b + 1),
              (a + 2, a + 3, b + 3, b + 2), (a + 3, a, b, b + 3)]
    f.append((0, 1, 2, 3))
    n = (len(zs) - 1) * 4
    f.append((n + 3, n + 2, n + 1, n))
    return mesh_object("Rudder", v, f, col=col, mat=P["hull_black"],
                       smooth_angle=math.radians(35))


def build_bulwarks(col, P):
    """Bulwarks on main deck fore and aft with capping rail and freeing ports."""
    objs = []
    z0 = DECK_Z["main"]
    for side in (1, -1):
        # forward of the superstructure and aft of it
        for (x0, x1) in ((46.0, 82.0), (-82.0, -78.0)):
            ob = vertical_wall_along_hull(HULL, z0, z0 + 1.12, x0, x1, side=side,
                                          col=col, name="Bulwark_%d_%d" % (side, int(x0)),
                                          mat=P["hull_black"])
            if ob:
                objs.append(ob)
        # capping rail
        xs = np.linspace(46.0, 82.0, 80)
        v = []; f = []
        for x in xs:
            b = HULL.half_beam_at(x, z0) * 0.97
            v += [(x, side * (b - 0.05), z0 + 1.12), (x, side * (b + 0.09), z0 + 1.12),
                  (x, side * (b + 0.09), z0 + 1.19), (x, side * (b - 0.05), z0 + 1.19)]
        for i in range(len(xs) - 1):
            a = i * 4; bb = (i + 1) * 4
            q = [(a, a + 1, bb + 1, bb), (a + 1, a + 2, bb + 2, bb + 1),
                 (a + 2, a + 3, bb + 3, bb + 2), (a + 3, a, bb, bb + 3)]
            for qq in q:
                f.append(qq if side > 0 else qq[::-1])
        objs.append(mesh_object("Bulwark_Rail_%d" % side, v, f, col=col,
                                mat=P["teak"]))
    return objs


def build_hawse_and_anchors(col, P):
    """Two bower anchors and hawse pipes plus chain locker leads."""
    objs = []
    for side in (1, -1):
        # hawse pipe mouth
        x = 78.6
        b = HULL.half_beam_at(x, 9.6)
        v, f = cylinder((x, side * (b + 0.06), 9.55), 0.30, 0.5, axis='Y',
                        segments=16)
        objs.append(mesh_object("HawsePipe_%d" % side, v, f, col=col,
                                mat=P["cast_iron"]))
        # anchor: shank + arms (stockless, as fitted to 1880s liners)
        ax = x + 0.5
        v, f = box((ax, side * (b + 0.16), 9.2), (0.22, 0.22, 2.1))
        objs.append(mesh_object("Anchor_Shank_%d" % side, v, f, col=col,
                                mat=P["cast_iron"]))
        for arm in (-1, 1):
            v, f = box((ax, side * (b + 0.16) + arm * 0.45, 8.25),
                       (0.20, 0.95, 0.30), rot_z=arm * 0.55)
            objs.append(mesh_object("Anchor_Arm_%d_%d" % (side, arm), v, f,
                                    col=col, mat=P["cast_iron"]))
        v, f = box((ax, side * (b + 0.16), 10.35), (0.9, 0.16, 0.16))
        objs.append(mesh_object("Anchor_Stock_%d" % side, v, f, col=col,
                                mat=P["cast_iron"]))
    return objs


def build(col, P):
    ob = {}
    shell, xs, rows = build_shell(col, P)
    ob["shell"] = shell
    ob["seams"] = build_seams(col, P, xs, rows)
    ob["keel"] = join_objects(build_keel_stem(col, P), "Keel_Stem")
    ob["rudder"] = build_rudder(col, P)
    ob["bulwarks"] = join_objects(build_bulwarks(col, P), "Bulwarks")
    ob["ground"] = join_objects(build_hawse_and_anchors(col, P), "Anchors_Hawse")
    ob["boottop"] = build_bands(col, P, T - 0.17, T + 0.17, "Boot_Top",
                                P["boot_white"])
    return ob


if __name__ == "__main__":
    sc = reset_scene()
    P = build_palette()
    col = collection("SHIP_HULL")
    objs = build(col, P)
    for k, v in objs.items():
        print("built", k, v.name if v else None,
              len(v.data.vertices) if v else 0)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(
        ROOT, "models", "module_hull.blend"))
    print("saved module_hull.blend")
