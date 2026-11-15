"""INTERIORS - SS Aurelian (1889)

Builds every enclosed space defined in shipdesign/layout.py:
    * first class: grand staircase + dome, dining saloon, library, music room,
      smoking saloon, staterooms and side corridors
    * second class: dining saloon, smoking/library, staterooms
    * third class: forward and after berthing rooms, mess, dining saloon
    * crew: forecastle, officers' quarters, captain's cabin, chart room,
      wheelhouse interior, hospital, lavatories, pantries, bars
    * service: galley, bakery, scullery, linen store, drying room

Construction approach (this is what makes it explorable):
  each deck is a REAL floor plate clipped to the hull, each room gets walls on
  its own boundary, a doorway gap where layout.DOORS says so, a ceiling, and
  furniture built from period reference.  Corridors are the leftover space
  between room walls and the shell, so a player can physically walk from the
  grand staircase to any cabin.

Furniture vocabulary is deliberately narrow and period-correct (see
research/HISTORICAL_EVIDENCE.md): buttoned-leather settees in the smoking
room, long communal tables with swivel chairs in the saloon, glazed bookcases
and a ground-glass table in the library, brass bedsteads and marble-topped
washstands in the staterooms, iron-framed berths in third class.
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

from shipdesign.spec import SHIP, DECK_Z, PALETTE
from shipdesign import layout
from shipdesign.layout import ROOMS, DOORS, STAIRS, room_polygon, rooms_on
from shipdesign.hull import HULL, HL, T
from lib_build import (reset_scene, collection, mesh_object, build_palette, box,
                       cylinder, tube, join_objects, principled, railing)

COL = None
P = None
ROOM_OBJS = {}


# ---------------------------------------------------------------------------
# walls, floors, ceilings
# ---------------------------------------------------------------------------
def floor_plate(deck, mat, inset=0.06):
    """One floor for a deck, clipped to the hull, with hatch openings kept out."""
    z = DECK_Z[deck]
    x0, x1 = layout.DECK_EXT[deck]
    nx = max(24, int((x1 - x0) / 0.9))
    xs = np.linspace(x0, x1, nx)
    ys = []
    for x in xs:
        b = HULL.half_beam_at(x, z)
        if b < 0.4:
            b = HULL.half_beam_at(x, min(z, HULL.deck_z(x) - 0.02))
        ys.append(max(b - inset, 0.04))
    verts = []
    ny = 10
    for x, b in zip(xs, ys):
        for j in range(ny + 1):
            verts.append((x, -b + 2 * b * j / ny, z))
    faces = []
    for i in range(nx - 1):
        for j in range(ny):
            a = i * (ny + 1) + j
            faces.append((a, a + 1, a + ny + 2, a + ny + 1))
    return mesh_object("Floor_" + deck, verts, faces, col=COL, mat=mat)


def room_shell(r, wall_h, wall_mat, floor_mat, ceil_mat, door_gaps=()):
    """Walls + ceiling for one room, keeping door gaps open.

    The room rectangle is clipped to the ship's side by layout.room_polygon,
    and the ceiling is the DECK ABOVE (layout.room_ceiling_z), never an
    arbitrary storey height - otherwise ceilings can float above the deck
    that forms the real ceiling and rooms behind them go dark.
    """
    poly = room_polygon(r)
    if not poly:
        return []
    z0 = DECK_Z[r["deck"]] + 0.001
    # The wall MUST reach the deck above.  Capping it at a nominal storey
    # height left a black gap between the top of the wall and the real
    # ceiling (which is the deck above) - visible as a dark band round the
    # top of every small room.
    z1 = layout.room_ceiling_z(r["deck"])[1]
    if z1 - z0 < wall_h:            # only ever extend, never shorten
        z1 = z0 + wall_h
    objs = []
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        # is this edge crossed by a door gap?
        for g in door_gaps:
            gx, gy, gw = g
            d = edge_distance(x0, y0, x1, y1, gx, gy)
            if d > gw * 0.6:
                continue
            _wall_with_gap(objs, r["name"], (x0, y0), (x1, y1), gx, gy, gw,
                           z0, z1, wall_mat)
            break
        else:
            _wall(objs, r["name"], (x0, y0), (x1, y1), z0, z1, wall_mat)
    # ceiling
    v = []
    for (x, y) in poly:
        v.append((x, y, z1))
    if len(v) >= 3:
        faces = [tuple(range(len(v) - 1, -1, -1))]
        objs.append(mesh_object("Ceil_" + r["name"][:22], v, faces, col=COL,
                                mat=ceil_mat))
    return objs


def dado_and_panels(r, poly, z0, z1, dado_mat, panel_mat,
                    dado_h=0.92, panel_top=2.30):
    """Period wall treatment: a moulded dado to 0.92 m, raised panels above.

    Every 1880s first-class saloon was panelled in this way - a painted or
    tiled dado, a moulding, then panelled joinery to the cornice.  Bare plaster
    walls are what makes an interior look modern; this is the correction.
    """
    objs = []
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L < 0.8:
            continue
        ux, uy = dx / L, dy / L
        # orient the offset toward the room's interior: a fixed normal
        # direction puts half the panelling OUTSIDE the room, where it is
        # invisible and leaves the wall looking bare and dark
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        nxn, nyn = -uy, ux
        if (cx - mx) * nxn + (cy - my) * nyn < 0:
            nxn, nyn = -nxn, -nyn
        nx, ny = nxn * 0.045, nyn * 0.045
        # dado band
        v, f = _quad((ax + nx, ay + ny, z0), (bx + nx, by + ny, z0),
                     (bx + nx, by + ny, z0 + dado_h),
                     (ax + nx, ay + ny, z0 + dado_h))
        objs.append(mesh_object("Dado_" + r["name"][:16], v, f, col=COL,
                                mat=dado_mat))
        # dado moulding capping
        v, f = _quad((ax + nx * 1.9, ay + ny * 1.9, z0 + dado_h),
                     (bx + nx * 1.9, by + ny * 1.9, z0 + dado_h),
                     (bx + nx * 1.9, by + ny * 1.9, z0 + dado_h + 0.09),
                     (ax + nx * 1.9, ay + ny * 1.9, z0 + dado_h + 0.09))
        objs.append(mesh_object("Dado_Mould_" + r["name"][:12], v, f, col=COL,
                                mat=dado_mat))
        # raised panels above the dado
        zt = min(panel_top, z1 - 0.35)
        run = (zt - (z0 + dado_h + 0.14))
        if run < 0.35:
            continue
        w = 1.15
        npanel = max(1, int((L - 0.35) / (w + 0.16)))
        step = (L - 0.35) / npanel
        for k in range(npanel):
            s0 = 0.175 + k * step + 0.08
            s1 = s0 + step - 0.16
            if s1 > L - 0.1:
                s1 = L - 0.1
            p0 = (ax + ux * s0 + nx * 0.7, ay + uy * s0 + ny * 0.7)
            p1 = (ax + ux * s1 + nx * 0.7, ay + uy * s1 + ny * 0.7)
            v, f = _quad((p0[0], p0[1], z0 + dado_h + 0.14),
                         (p1[0], p1[1], z0 + dado_h + 0.14),
                         (p1[0], p1[1], z0 + dado_h + 0.14 + run),
                         (p0[0], p0[1], z0 + dado_h + 0.14 + run))
            objs.append(mesh_object("Panel_" + r["name"][:14], v, f, col=COL,
                                    mat=panel_mat))
        # cornice
        v, f = _quad((ax + nx * 2.4, ay + ny * 2.4, z1 - 0.26),
                     (bx + nx * 2.4, by + ny * 2.4, z1 - 0.26),
                     (bx + nx * 2.4, by + ny * 2.4, z1 - 0.02),
                     (ax + nx * 2.4, ay + ny * 2.4, z1 - 0.02))
        objs.append(mesh_object("Cornice_" + r["name"][:14], v, f, col=COL,
                                mat=dado_mat))
    return objs


def _quad(p0, p1, p2, p3):
    return [p0, p1, p2, p3], [(0, 1, 2, 3)]


def edge_distance(x0, y0, x1, y1, px, py):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    if L2 < 1e-9:
        return math.hypot(px - x0, py - y0)
    t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / L2))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def _wall(objs, tag, a, b, z0, z1, mat, t=0.08):
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.05 or z1 - z0 < 0.05:
        return
    ang = math.atan2(y1 - y0, x1 - x0)
    v, f = box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
               (L, t, z1 - z0), rot_z=ang)
    objs.append(mesh_object("W_" + tag[:18], v, f, col=COL, mat=mat))


def _wall_with_gap(objs, tag, a, b, gx, gy, gw, z0, z1, mat, door_h=2.05):
    """Wall with a doorway: two solid piers plus a header over the opening."""
    (x0, y0), (x1, y1) = a, b
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 0.05:
        return
    dx, dy = (x1 - x0) / L, (y1 - y0) / L
    # parameter of the gap centre along the edge
    tg = max(0.0, min(L, (gx - x0) * dx + (gy - y0) * dy))
    a0 = max(0.0, tg - gw / 2); a1 = min(L, tg + gw / 2)
    for (s, e, za, zb) in ((0, a0, z0, z1), (a1, L, z0, z1)):
        if e - s < 0.02:
            continue
        _wall(objs, tag, (x0 + dx * s, y0 + dy * s), (x0 + dx * e, y0 + dy * e),
              za, zb, mat)
    # header above the door
    _wall(objs, tag, (x0 + dx * a0, y0 + dy * a0), (x0 + dx * a1, y0 + dy * a1),
          z0 + door_h, z1, mat)


# ---------------------------------------------------------------------------
# furniture -- period vocabulary
# ---------------------------------------------------------------------------
def table(x, y, z, l, w, h=0.76, mat=None, cloth=False):
    objs = []
    v, f = box((x, y, z + h), (l, w, 0.055))
    objs.append(mesh_object("Table_Top", v, f, col=COL,
                            mat=P["cloth"] if cloth else mat or P["mahogany"]))
    for (dx, dy) in ((-l / 2 + 0.12, -w / 2 + 0.12), (l / 2 - 0.12, -w / 2 + 0.12),
                     (-l / 2 + 0.12, w / 2 - 0.12), (l / 2 - 0.12, w / 2 - 0.12)):
        v, f = box((x + dx, y + dy, z + h / 2), (0.075, 0.075, h))
        objs.append(mesh_object("Table_Leg", v, f, col=COL,
                                mat=mat or P["mahogany"]))
    return objs


def chair(x, y, z, facing=0.0, mat=None, seat_mat=None):
    """Period dining chair: square seat, turned front legs, high back."""
    objs = []
    m = mat or P["mahogany"]
    c, s = math.cos(facing), math.sin(facing)
    def T(dx, dy):
        return (x + dx * c - dy * s, y + dx * s + dy * c)
    v, f = box((x, y, z + 0.45), (0.46, 0.44, 0.05), rot_z=facing)
    objs.append(mesh_object("Chair_Seat", v, f, col=COL,
                            mat=seat_mat or P["carpet_red"]))
    for (dx, dy) in ((-0.19, -0.18), (0.19, -0.18), (-0.19, 0.18), (0.19, 0.18)):
        px, py = T(dx, dy)
        v, f = box((px, py, z + 0.22), (0.045, 0.045, 0.44))
        objs.append(mesh_object("Chair_Leg", v, f, col=COL, mat=m))
    # back: two slender stiles and three horizontal splats (period joinery),
    # not a solid slab
    for sx in (-0.19, 0.19):
        px, py = T(sx, 0.20)
        v, f = box((px, py, z + 0.72), (0.045, 0.04, 0.55), rot_z=facing)
        objs.append(mesh_object("Chair_Stile", v, f, col=COL, mat=m))
    for hz in (0.98, 0.86, 0.74):
        px, py = T(0, 0.20)
        v, f = box((px, py, z + hz), (0.40, 0.028, 0.075), rot_z=facing)
        objs.append(mesh_object("Chair_Splat", v, f, col=COL, mat=m))
    for (dx, dy) in ((-0.19, 0.18), (0.19, 0.18)):
        px, py = T(dx, dy)
        v, f = box((px, py, z + 0.69), (0.042, 0.042, 0.50))
        objs.append(mesh_object("Chair_RearLeg", v, f, col=COL, mat=m))
    return objs


def settee(x, y, z, l, facing=0.0, mat=None, seat=None):
    objs = []
    m = mat or P["leather"]; sm = seat or P["leather"]
    v, f = box((x, y, z + 0.42), (l, 0.78, 0.16), rot_z=facing)
    objs.append(mesh_object("Settee_Seat", v, f, col=COL, mat=sm))
    v, f = box((x, y, z + 0.20), (l, 0.72, 0.26), rot_z=facing)
    objs.append(mesh_object("Settee_Base", v, f, col=COL, mat=m))
    c, s = math.cos(facing), math.sin(facing)
    bx = x - 0.34 * s; by = y - 0.34 * c
    v, f = box((bx, by, z + 0.78), (l, 0.16, 0.62), rot_z=facing)
    objs.append(mesh_object("Settee_Back", v, f, col=COL, mat=sm))
    for dx in (-l / 2 + 0.10, l / 2 - 0.10):
        px = x + dx * c; py = y + dx * s
        v, f = box((px, py, z + 0.62), (0.14, 0.76, 0.42), rot_z=facing)
        objs.append(mesh_object("Settee_Arm", v, f, col=COL, mat=sm))
    return objs


def bed(x, y, z, l=1.95, w=1.15, mat=None, style="brass"):
    objs = []
    if style == "brass":
        for i in range(4):
            dx = -l / 2 + 0.08 + i * (l - 0.16) / 3
            for side in (-1, 1):
                px, py = x + dx - l / 2 + 0.08, y + side * (w / 2 - 0.06)
            # four posts
        for (dx, dy) in ((-l / 2, -w / 2), (-l / 2, w / 2),
                         (l / 2, -w / 2), (l / 2, w / 2)):
            v, f = cylinder((x + dx, y + dy, z + 0.55), 0.028, 1.10, segments=8)
            objs.append(mesh_object("Bed_Post", v, f, col=COL, mat=P["brass"]))
        # rails
        for dy in (-w / 2, w / 2):
            v, f = tube([(x - l / 2, y + dy, z + 1.05),
                         (x + l / 2, y + dy, z + 1.05)], 0.02, 6)
            objs.append(mesh_object("Bed_Rail", v, f, col=COL, mat=P["brass"]))
        v, f = tube([(x - l / 2, y - w / 2, z + 0.72),
                     (x - l / 2, y + w / 2, z + 0.72)], 0.02, 6)
        objs.append(mesh_object("Bed_Head", v, f, col=COL, mat=P["brass"]))
    # mattress + bedding
    v, f = box((x, y, z + 0.55), (l, w, 0.22))
    objs.append(mesh_object("Bed_Mattress", v, f, col=COL, mat=P["bed_linen"]))
    v, f = box((x + 0.12, y, z + 0.68), (l - 0.35, w + 0.03, 0.05))
    objs.append(mesh_object("Bed_Counterpane", v, f, col=COL,
                            mat=P["carpet_green"]))
    v, f = box((x - l / 2 + 0.28, y, z + 0.72), (0.42, w - 0.18, 0.12))
    objs.append(mesh_object("Bed_Pillow", v, f, col=COL, mat=P["bed_linen"]))
    return objs


def washstand(x, y, z, mat=None):
    objs = []
    v, f = box((x, y, z + 0.42), (0.62, 0.46, 0.84))
    objs.append(mesh_object("Washstand", v, f, col=COL, mat=mat or P["mahogany"]))
    v, f = box((x, y, z + 0.88), (0.70, 0.52, 0.05))
    objs.append(mesh_object("Washstand_Top", v, f, col=COL, mat=P["marble"]))
    v, f = cylinder((x, y, z + 0.96), 0.19, 0.11, segments=14)
    objs.append(mesh_object("Wash_Basin", v, f, col=COL,
                            mat=P["white_ceiling"]))
    v, f = cylinder((x + 0.24, y, z + 1.02), 0.10, 0.26, segments=10)
    objs.append(mesh_object("Wash_Jug", v, f, col=COL,
                            mat=P["white_ceiling"]))
    # mirror on the bulkhead
    v, f = box((x - 0.24, y, z + 1.42), (0.03, 0.5, 0.62))
    objs.append(mesh_object("Mirror", v, f, col=COL, mat=P["mirror"]))
    return objs


def wardrobe(x, y, z, w=0.95, h=2.05, mat=None, facing=0.0):
    v, f = box((x, y, z + h / 2), (w, 0.56, h), rot_z=facing)
    ob = mesh_object("Wardrobe", v, f, col=COL, mat=mat or P["mahogany"])
    return [ob]


def bookcase(x, y, z, w=2.4, h=2.2, facing=0.0, shelves=4):
    objs = []
    v, f = box((x, y, z + h / 2), (w, 0.32, h), rot_z=facing)
    objs.append(mesh_object("Bookcase", v, f, col=COL, mat=P["oak_light"]))
    c, s = math.cos(facing), math.sin(facing)
    for i in range(shelves):
        zz = z + 0.35 + i * (h - 0.5) / max(1, shelves - 1)
        v, f = box((x - 0.05 * s, y - 0.05 * c, zz), (w - 0.16, 0.26, 0.03),
                   rot_z=facing)
        objs.append(mesh_object("Shelf", v, f, col=COL, mat=P["oak_light"]))
        # a suggestion of books: coloured blocks at irregular widths
        for k in range(14):
            dx = -w / 2 + 0.14 + k * (w - 0.28) / 14
            hh = 0.22 + 0.05 * ((k * 7) % 3)
            px = x + dx * c; py = y + dx * s
            v, f = box((px, py, zz + hh / 2 + 0.02), (0.055, 0.20, hh),
                       rot_z=facing)
            mi = (k * 5) % 4
            objs.append(mesh_object("Book", v, f, col=COL,
                                    mat=[P["book_a"], P["book_b"],
                                         P["book_c"], P["book_d"]][mi]))
    return objs


def column(x, y, z0, z1, r=0.22, mat=None, capital=True):
    objs = []
    v, f = cylinder((x, y, (z0 + z1) / 2), r, z1 - z0, segments=16)
    objs.append(mesh_object("Column", v, f, col=COL, mat=mat or P["oak_light"]))
    if capital:
        for zz in (z0 + 0.06, z1 - 0.10):
            v, f = cylinder((x, y, zz), r * 1.35, 0.14, segments=16)
            objs.append(mesh_object("Capital", v, f, col=COL,
                                    mat=P["brass"] if zz > z0 else mat or P["oak_light"]))
    return objs


def skylight(x, y, z, l=1.6, w=1.1, h=0.5):
    objs = []
    v, f = box((x, y, z + h / 2), (l, w, h))
    objs.append(mesh_object("Skylight_Box", v, f, col=COL, mat=P["white_ceiling"]))
    v, f = box((x, y, z + h + 0.02), (l - 0.1, w - 0.1, 0.04))
    objs.append(mesh_object("Skylight_Glass", v, f, col=COL,
                            mat=P["glass_ground"]))
    return objs


def lamp(x, y, z, colour=None):
    objs = []
    v, f = cylinder((x, y, z - 0.08), 0.09, 0.16, segments=8)
    objs.append(mesh_object("Lamp_Base", v, f, col=COL, mat=P["brass"]))
    v, f = cylinder((x, y, z + 0.14), 0.13, 0.28, segments=12)
    objs.append(mesh_object("Lamp_Glass", v, f, col=COL,
                            mat=colour or P["lamp"]))
    return objs


def door_leaf(x, y, z, w=0.86, h=2.05, facing=0.0, mat=None, open_deg=0.0):
    """Panel door, optionally ajar - gives the interiors a lived-in feel."""
    objs = []
    c, s = math.cos(facing), math.sin(facing)
    ang = facing + math.radians(open_deg)
    v, f = box((x + (w / 2) * math.cos(ang), y + (w / 2) * math.sin(ang),
                z + h / 2), (w, 0.045, h), rot_z=ang)
    objs.append(mesh_object("Door", v, f, col=COL, mat=mat or P["mahogany"]))
    v, f = cylinder((x + 0.06 * s, y - 0.06 * c, z + 1.02), 0.028, 0.09,
                    segments=8)
    objs.append(mesh_object("Door_Knob", v, f, col=COL, mat=P["brass"]))
    return objs


# ---------------------------------------------------------------------------
# FIRST CLASS: grand staircase (three flights + gallery + dome)
# ---------------------------------------------------------------------------
def grand_staircase():
    """Grand staircase in the entrance hall, x = -9.0 .. 1.0.

    Period arrangement (Ocean Magazine, Sept 1889): a well in the middle of
    the hall with flights rising fore and aft, galleries round it on each
    deck, and a glazed dome above.  The well is 3.6 m long, leaving a clear
    2.2 m of open floor at each end and 1 m of gallery down both sides, so a
    passenger can actually stand in the hall and walk round the well.  Both
    storeys climb in the SAME direction, so one continuous open well serves
    the saloon and promenade decks.
    """
    objs = []
    z_main = DECK_Z["main"]; z_sal = DECK_Z["saloon"]; z_prom = DECK_Z["prom"]
    HW = 2.35                       # half width of the well
    WELL_X0, WELL_X1 = -7.4, -0.6   # well opening in the hall

    for (za, zb) in ((z_main, z_sal), (z_sal, z_prom)):
        # single flight up the middle of the well
        objs += _flight(x0=WELL_X0 + 0.2, x1=WELL_X1 - 0.2,
                        z_bottom=za, z_top=zb, y_left=-HW, y_right=HW)
        # balustrades round the well at the upper deck, on all four sides,
        # leaving a 1.1 m gap at the forward end as the stair opening
        for y in (-HW - 0.12, HW + 0.12):
            objs += railing([(WELL_X0, y), (WELL_X1, y)], zb, 0.95, 0.34,
                            0.045, col=COL, name="Stair_Rail",
                            mat_rail=P["mahogany"], mat_stanchion=P["mahogany"])
        objs += railing([(WELL_X1, -HW), (WELL_X1, HW)], zb, 0.95, 0.34,
                        0.045, col=COL, name="Stair_Rail",
                        mat_rail=P["mahogany"], mat_stanchion=P["mahogany"])
        # newel posts at the open end
        for y in (-HW - 0.12, HW + 0.12):
            v, f = cylinder((WELL_X0, y, zb + 0.55), 0.105, 1.10, segments=12)
            objs.append(mesh_object("Newel", v, f, col=COL, mat=P["mahogany"]))
    # colonnade down both sides of the hall, inside the walls
    for x in (-8.0, -4.0, 0.0):
        for y in (-4.2, 4.2):
            objs += column(x, y, z_sal, z_prom - 0.15, 0.19, P["marble"])
    # gallery soffit round the well (the underside of the gallery floor)
    for y in (-HW - 0.5, HW + 0.5):
        v, f = box((-4.0, y, z_prom + 0.06), (7.4, 0.90, 0.12))
        objs.append(mesh_object("Gallery_Soffit", v, f, col=COL,
                                mat=P["mahogany"]))
    # the dome over the well
    objs += _dome((WELL_X0 + WELL_X1) / 2, 0, z_prom + 0.04,
                  rx=3.1, ry=2.35, rise=1.30)
    return objs


def dining_saloon():
    r = next(x for x in ROOMS if x["name"].startswith("First Class Dining"))
    z = DECK_Z["saloon"]
    objs = []
    # long communal tables down the length, as in the Ocean Magazine photo
    x0, x1 = r["x0"] + 2.0, r["x1"] - 2.0
    for y in (-4.6, -1.6, 1.6, 4.6):
        objs += table((x0 + x1) / 2, y, z, (x1 - x0), 1.15, mat=P["mahogany"],
                      cloth=True)
        # chairs along both sides, facing the table
        n = int((x1 - x0) / 0.62)
        for i in range(n):
            xx = x0 + (i + 0.5) * (x1 - x0) / n
            objs += chair(xx, y - 0.78, z, facing=math.pi / 2)
            objs += chair(xx, y + 0.78, z, facing=-math.pi / 2)
    # columns
    for x in (x0 + 4, x0 + (x1 - x0) * 0.45, x1 - 4):
        for y in (-6.4, 6.4):
            objs += column(x, y, z, z + 2.85, 0.24, P["marble"])
    # sideboard / buffet at the forward end
    v, f = box((r["x1"] - 1.0, 0, z + 0.5), (0.8, 8.0, 1.0))
    objs.append(mesh_object("Sideboard", v, f, col=COL, mat=P["mahogany"]))
    # lamps on the tables
    for y in (-4.6, -1.6, 1.6, 4.6):
        for x in (x0 + 3, x0 + (x1 - x0) * 0.5, x1 - 3):
            objs += lamp(x, y, z + 0.76)
    # period wall treatment: oak dado, mahogany raised panels, cornice
    objs += dado_and_panels(r, room_polygon(r), z + 0.002,
                            layout.room_ceiling_z("saloon")[1],
                            P["oak_light"], P["mahogany"])
    objs += carpet(r, "saloon", P["carpet_red"])
    objs += ceiling_beams(r, room_polygon(r),
                          layout.room_ceiling_z("saloon")[1], 0.20,
                          P["oak_light"])
    return objs


def ceiling_beams(r, poly, z1, depth=0.16, mat=None, spacing=2.45):
    """Transverse deckhead beams, 0.16 m deep.

    Period public rooms had the deck beams exposed (cased or moulded) with
    plaster panels between; a bare flat ceiling is the single biggest giveaway
    of a modern interior.
    """
    objs = []
    m = mat or P["oak_light"]
    xs = [p[0] for p in poly]
    x0, x1 = min(xs), max(xs)
    n = max(2, int((x1 - x0) / spacing))
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        y0 = min(p[1] for p in poly if abs(p[0] - x) < 3.0) if any(
            abs(p[0] - x) < 3.0 for p in poly) else min(p[1] for p in poly)
        y1 = max(p[1] for p in poly if abs(p[0] - x) < 3.0) if any(
            abs(p[0] - x) < 3.0 for p in poly) else max(p[1] for p in poly)
        v, f = box((x, (y0 + y1) / 2, z1 - depth / 2),
                   (0.16, y1 - y0, depth))
        objs.append(mesh_object("Ceil_Beam", v, f, col=COL, mat=m))
    return objs


def carpet(r, deck, mat, inset=0.35):
    """A carpet/linoleum overlay just above the deck, as laid in period."""
    poly = room_polygon(r)
    if not poly:
        return []
    z = DECK_Z[deck] + 0.012
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    v = [(cx + (p[0] - cx) * (1 - inset / max(abs(p[0] - cx), 1e-3)),
          cy + (p[1] - cy) * (1 - inset / max(abs(p[1] - cy), 1e-3)), z)
         for p in poly]
    f = [tuple(range(len(v) - 1, -1, -1))]
    return [mesh_object("Carpet_" + r["name"][:16], v, f, col=COL, mat=mat)]


def _panel_room(objs, r, deck, dado, panel):
    objs += dado_and_panels(r, room_polygon(r), DECK_Z[deck] + 0.002,
                            layout.room_ceiling_z(deck)[1], dado, panel)
    return objs


def library():
    r = next(x for x in ROOMS if "Library" in x["name"])
    z = DECK_Z["prom"]
    objs = []
    cx, cy = (r["x0"] + r["x1"]) / 2, 0
    # the famous ground-glass central table, lit from below
    v, f = box((cx, cy, z + 0.78), (5.2, 3.2, 0.06))
    objs.append(mesh_object("Library_Table_Frame", v, f, col=COL,
                            mat=P["mahogany"]))
    v, f = box((cx, cy, z + 0.80), (4.9, 2.9, 0.02))
    objs.append(mesh_object("Library_Table_Glass", v, f, col=COL,
                            mat=P["glass_ground"]))
    for i in range(4):
        v, f = box((cx, cy, z + 0.70 - i * 0.11), (4.6 - i * 0.2,
                                                   2.6 - i * 0.2, 0.015))
        objs.append(mesh_object("Library_Band", v, f, col=COL,
                                mat=P["mahogany"]))
    # settees round the sides
    for y in (-4.0, 4.0):
        objs += settee(cx, y, z, 5.6, facing=0 if y > 0 else math.pi,
                       mat=P["fabric_gold"], seat=P["fabric_gold"])
    # bookcases on the bulkheads
    objs += bookcase(r["x0"] + 0.4, 0, z, 4.4, 2.2, facing=0)
    for y in (-3.4, 3.4):
        objs += bookcase(r["x1"] - 0.5, y, z, 2.4, 2.2, facing=math.pi / 2,
                         )
    # writing desks and chairs
    for x in (r["x0"] + 6.0, r["x1"] - 6.0):
        objs += table(x, 5.6, z, 1.6, 0.8, mat=P["oak_light"])
        objs += chair(x, 4.7, z, facing=0)
    objs += column(cx - 6.0, -3.6, z, z + 2.6, 0.2, P["oak_light"])
    objs += column(cx + 6.0, 3.6, z, z + 2.6, 0.2, P["oak_light"])
    # panelled in oak, with a dentil cornice
    objs = _panel_room(objs, r, "prom", P["oak_light"], P["oak_light"])
    objs += carpet(r, "prom", P["carpet_green"])
    objs += ceiling_beams(r, room_polygon(r),
                          layout.room_ceiling_z("prom")[1], 0.18,
                          P["oak_light"])
    # books on the shelves: staggered bands of varied spine colours
    import random
    rnd = random.Random(4)
    spines = [P["carpet_red"], P["oak_light"], P["mahogany"], P["fabric_gold"],
              P["carpet_green"]]
    for (bx, by, facing) in ((r["x0"] + 0.62, 0.0, 0.0),
                             (r["x1"] - 0.70, -3.4, 1.0),
                             (r["x1"] - 0.70, 3.4, 1.0)):
        for shelf in range(3):
            hz = z + 1.02 + shelf * 0.55
            xrun = 3.7 if facing == 0.0 else 2.0
            nbook = int(xrun / 0.058)
            for kb in range(nbook):
                off = -xrun / 2 + kb * 0.058
                px, py = (bx, by + off) if facing == 0.0 else (bx + off, by)
                bh = rnd.uniform(0.185, 0.255)
                size = (0.16, 0.044, bh) if facing == 0.0 else (0.044, 0.16, bh)
                v, f = box((px, py, hz + bh / 2), size)
                objs.append(mesh_object("Book", v, f, col=COL,
                                        mat=rnd.choice(spines)))
    return objs


def smoking_saloon():
    r = next(x for x in ROOMS if "Smoking" in x["name"] and x["deck"] == "prom")
    z = DECK_Z["prom"]
    objs = []
    cx = (r["x0"] + r["x1"]) / 2
    # leather settees round the walls (cf. Teutonic smoke room photograph)
    for y in (-4.8, 4.8):
        objs += settee(cx, y, z, 12.0, facing=0 if y > 0 else math.pi)
    for x in (r["x0"] + 2.4, r["x1"] - 2.4):
        objs += settee(x, 0, z, 6.0, facing=math.pi / 2)
    # small tables and revolving chairs
    for x in (cx - 6, cx - 2, cx + 2, cx + 6):
        objs += table(x, 0, z, 1.1, 1.1, h=0.72, mat=P["mahogany"])
        for k in range(4):
            a = k * math.pi / 2 + 0.4
            objs += chair(x + 0.95 * math.cos(a), 0.95 * math.sin(a), z,
                          facing=-a + math.pi / 2)
    # fireplace with a coal fire glow
    v, f = box((r["x0"] + 0.3, 0, z + 1.25), (0.35, 2.2, 1.3))
    objs.append(mesh_object("Fireplace", v, f, col=COL, mat=P["marble"]))
    v, f = box((r["x0"] + 0.45, 0, z + 0.85), (0.12, 1.2, 0.7))
    objs.append(mesh_object("Fire", v, f, col=COL, mat=P["fire"]))
    # big painting + clock over the fireplace (period smoke rooms always had them)
    v, f = box((r["x0"] + 0.32, 0, z + 2.15), (0.05, 2.6, 1.0))
    objs.append(mesh_object("Painting", v, f, col=COL, mat=P["painting"]))
    # the smoke room was panelled to the cornice in mahogany
    objs = _panel_room(objs, r, "prom", P["mahogany"], P["mahogany"])
    objs += carpet(r, "prom", P["carpet_red"])
    objs += ceiling_beams(r, room_polygon(r),
                          layout.room_ceiling_z("prom")[1], 0.18,
                          P["mahogany"])
    return objs


def music_room():
    r = next(x for x in ROOMS if "music" in x["name"])
    z = DECK_Z["saloon"]
    objs = []
    cx = (r["x0"] + r["x1"]) / 2
    for y in (-3.6, 3.6):
        objs += settee(cx, y, z, 8.0, facing=0 if y > 0 else math.pi,
                       mat=P["carpet_red"], seat=P["carpet_red"])
    objs += table(cx, 0, z, 2.4, 1.2, mat=P["mahogany"])
    # piano
    v, f = box((cx + 4.5, 0, z + 0.62), (1.7, 0.9, 1.24))
    objs.append(mesh_object("Piano", v, f, col=COL, mat=P["mahogany"]))
    v, f = box((cx + 4.0, 0, z + 0.92), (0.7, 0.78, 0.06))
    objs.append(mesh_object("Piano_Keys", v, f, col=COL, mat=P["ivory"]))
    objs += chair(cx + 3.4, 0, z, facing=0)
    return objs


# ---------------------------------------------------------------------------
# STATEROOMS  (first & second class)
# ---------------------------------------------------------------------------
def staterooms():
    objs = []
    for r in ROOMS:
        if r["use"] not in ("first", "second"):
            continue
        if not any(k in r["name"] for k in ("stateroom", "Stateroom",
                                            "cabins", "Staterooms")):
            continue
        poly = room_polygon(r)
        if not poly:
            continue
        z = DECK_Z[r["deck"]]
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        n_cab = max(1, int((x1 - x0) / 3.05))
        for i in range(n_cab):
            cx = x0 + (i + 0.5) * (x1 - x0) / n_cab
            d = (x1 - x0) / n_cab
            two_berth = (i % 3 != 2)
            objs += bed(cx, -1.35 if y1 - y0 > 5 else 0.0, z, 1.95, 1.15,
                        style="brass")
            if two_berth:
                objs += bed(cx, 1.35 if y1 - y0 > 5 else 2.2, z, 1.95, 1.15,
                            style="brass")
            objs += washstand(cx + d / 2 - 0.55, y1 - 0.7, z)
            objs += wardrobe(cx - d / 2 + 0.5, y1 - 0.65, z, 0.95, 2.05)
            # dividing bulkheads
            _wall(objs, "Cabin_Bulkhead", (cx + d / 2, y0), (cx + d / 2, y1),
                  z, z + 2.30, P["cabin_panel"])
            objs += door_leaf(cx + d / 2, (y0 + y1) / 2 + 1.4, z,
                              mat=P["mahogany"], open_deg=18)
    return objs


# ---------------------------------------------------------------------------
# THIRD CLASS
# ---------------------------------------------------------------------------
def third_class():
    objs = []
    for r in ROOMS:
        if r["use"] != "third":
            continue
        poly = room_polygon(r)
        if not poly:
            continue
        z = DECK_Z[r["deck"]]
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        x0, x1 = min(xs), max(xs); y0, y1 = min(ys), max(ys)
        if "dining" in r["name"].lower() or "mess" in r["name"].lower():
            for y in (y0 + 1.8, (y0 + y1) / 2, y1 - 1.8):
                objs += table((x0 + x1) / 2, y, z, (x1 - x0) - 1.6, 1.0,
                              mat=P["oak_light"], cloth=True)
                n = int((x1 - x0) / 0.72)
                for i in range(n):
                    xx = x0 + 0.8 + (i + 0.5) * ((x1 - x0) - 1.6) / n
                    objs += chair(xx, y - 0.62, z, facing=math.pi / 2,
                                  mat=P["oak_light"])
                    objs += chair(xx, y + 0.62, z, facing=-math.pi / 2,
                                  mat=P["oak_light"])
            continue
        # berthing: iron-framed two-tier berths, spacing as on emigrant ships
        rows = max(1, int((y1 - y0) / 1.15))
        cols = max(1, int((x1 - x0) / 1.95))
        for i in range(cols):
            for j in range(rows):
                bx = x0 + (i + 0.5) * (x1 - x0) / cols
                by = y0 + (j + 0.5) * (y1 - y0) / rows
                # lower berth
                v, f = box((bx, by, z + 0.42), (1.85, 0.82, 0.10))
                objs.append(mesh_object("Berth_Lower", v, f, col=COL,
                                        mat=P["bed_linen"]))
                v, f = box((bx, by, z + 0.20), (1.80, 0.78, 0.16))
                objs.append(mesh_object("Berth_Frame", v, f, col=COL,
                                        mat=P["cast_iron"]))
                # upper berth
                v, f = box((bx, by, z + 1.45), (1.85, 0.82, 0.10))
                objs.append(mesh_object("Berth_Upper", v, f, col=COL,
                                        mat=P["bed_linen"]))
                v, f = box((bx, by, z + 1.24), (1.80, 0.78, 0.16))
                objs.append(mesh_object("Berth_Frame_U", v, f, col=COL,
                                        mat=P["cast_iron"]))
                for (dx, dy) in ((-0.9, -0.4), (-0.9, 0.4), (0.9, -0.4), (0.9, 0.4)):
                    v, f = cylinder((bx + dx, by + dy, z + 0.9), 0.03, 1.8,
                                    segments=6)
                    objs.append(mesh_object("Berth_Post", v, f, col=COL,
                                            mat=P["cast_iron"]))
        # a long table down the centre for the berthing rooms
        objs += table((x0 + x1) / 2, (y0 + y1) / 2, z + 0.02, 2.4, 0.8,
                      mat=P["oak_light"])
    return objs


# ---------------------------------------------------------------------------
# SERVICE: galley, pantry, lavatories, hospital, wheelhouse interior
# ---------------------------------------------------------------------------
def galley():
    objs = []
    r = next(x for x in ROOMS if "Galley" in x["name"])
    z = DECK_Z["saloon"]
    cx, cy = (r["x0"] + r["x1"]) / 2, 0
    # coal range with two ovens and a stock pot
    v, f = box((cx + 2.6, 0, z + 0.55), (2.6, 1.4, 1.1))
    objs.append(mesh_object("Range", v, f, col=COL, mat=P["cast_iron"]))
    v, f = box((cx + 2.6, 0, z + 1.16), (2.5, 1.2, 0.10))
    objs.append(mesh_object("Range_Top", v, f, col=COL, mat=P["steel"]))
    for dx in (-0.7, 0.0, 0.7):
        v, f = cylinder((cx + 2.6 + dx, 0, z + 1.34), 0.24, 0.26, segments=12)
        objs.append(mesh_object("Pot", v, f, col=COL, mat=P["copper"]))
    # ranges' flue
    v, f = cylinder((cx + 2.6, 0, z + 1.9), 0.18, 1.4, segments=10)
    objs.append(mesh_object("Range_Flue", v, f, col=COL, mat=P["cast_iron"]))
    # work tables, dressers, sinks
    for x in (cx - 2.4, cx - 0.2, cx + 1.2):
        objs += table(x, -3.0, z, 2.0, 0.9, mat=P["steel"])
        objs += table(x, 3.0, z, 2.0, 0.9, mat=P["steel"])
    v, f = box((cx - 2.8, 0, z + 1.0), (3.6, 0.4, 2.0))
    objs.append(mesh_object("Dresser", v, f, col=COL, mat=P["oak_light"]))
    for i in range(6):
        v, f = box((cx - 4.4 + i * 0.6, 0, z + 1.35), (0.44, 0.30, 0.06))
        objs.append(mesh_object("Dresser_Shelf", v, f, col=COL,
                                mat=P["oak_light"]))
    return objs


def lavatories_and_baths():
    objs = []
    for r in ROOMS:
        if not any(k in r["name"] for k in ("Barber", "lavatories", "bathrooms")):
            continue
        poly = room_polygon(r)
        if not poly:
            continue
        z = DECK_Z[r["deck"]]
        xs = [p[0] for p in poly]
        x0, x1 = min(xs), max(xs)
        for i in range(3):
            x = x0 + (i + 0.6) * (x1 - x0) / 3
            # marble washstand + mirror
            v, f = box((x, 3.6, z + 0.45), (0.9, 0.5, 0.9))
            objs.append(mesh_object("Wash_Stand", v, f, col=COL,
                                    mat=P["marble"]))
            v, f = cylinder((x, 3.6, z + 0.95), 0.22, 0.12, segments=12)
            objs.append(mesh_object("Basin", v, f, col=COL,
                                    mat=P["white_ceiling"]))
            v, f = box((x, 3.9, z + 1.55), (0.7, 0.04, 0.8))
            objs.append(mesh_object("Mirror", v, f, col=COL, mat=P["mirror"]))
            # W.C. cubicle
            v, f = box((x, -3.4, z + 0.85), (0.9, 0.55, 0.42))
            objs.append(mesh_object("WC", v, f, col=COL,
                                    mat=P["white_ceiling"]))
            _wall(objs, "Cubicle", (x - 0.6, -5.2), (x - 0.6, -2.0), z,
                  z + 2.1, P["cabin_panel"], t=0.05)
        # bath tub
        v, f = box((x1 - 1.4, 0, z + 0.35), (1.7, 0.8, 0.70))
        objs.append(mesh_object("Bath", v, f, col=COL,
                                mat=P["white_ceiling"]))
    return objs


def hospital_and_officers():
    objs = []
    for r in ROOMS:
        if r["name"].startswith("Hospital"):
            z = DECK_Z[r["deck"]]
            objs += bed((r["x0"] + r["x1"]) / 2 - 1.6, 0, z)
            objs += bed((r["x0"] + r["x1"]) / 2 + 1.6, 0, z)
            objs += table((r["x0"] + r["x1"]) / 2, 2.6, z, 1.2, 0.6,
                          mat=P["oak_light"])
        if "Officers" in r["name"] or "Captain" in r["name"]:
            z = DECK_Z[r["deck"]]
            cx = (r["x0"] + r["x1"]) / 2
            objs += bed(cx - 2.4, 0, z)
            objs += table(cx + 1.0, 0, z, 1.6, 0.9, mat=P["mahogany"])
            objs += chair(cx + 1.0, -0.85, z, facing=math.pi / 2)
            objs += chair(cx + 1.0, 0.85, z, facing=-math.pi / 2)
            objs += wardrobe(cx + 3.4, 2.2, z, 1.1, 2.05)
    return objs


def wheelhouse_interior():
    objs = []
    z = DECK_Z["bridge"]
    # binnacle, telegraphs and the wheel itself (period: 8-spoke teak wheel)
    v, f = cylinder((18.4, 0, z + 1.05), 0.62, 0.09, axis='X', segments=24)
    objs.append(mesh_object("Wheel_Rim", v, f, col=COL, mat=P["teak"]))
    for k in range(8):
        a = 2 * math.pi * k / 8
        v, f = box((18.4, 0.5 * math.cos(a), z + 1.05 + 0.5 * math.sin(a)),
                   (0.06, 0.95, 0.07), rot_z=0)
        objs.append(mesh_object("Wheel_Spoke", v, f, col=COL, mat=P["teak"]))
    v, f = cylinder((18.4, 0, z + 1.05), 0.12, 0.14, axis='X', segments=12)
    objs.append(mesh_object("Wheel_Hub", v, f, col=COL, mat=P["brass"]))
    objs += table(15.0, 0, z, 2.2, 0.8, h=0.92, mat=P["mahogany"])  # chart table
    return objs


# ---------------------------------------------------------------------------
def public_room_windows():
    """Rows of windows for the first/second-class public rooms.

    On the saloon deck these are the hull's side windows (the ship's shell
    there is above the waterline); on the promenade deck they are set in the
    deckhouse side.  Both are visible in the 1889 photographs: a long row of
    rectangles with the light streaming in.
    """
    objs = []
    for r in ROOMS:
        if r["use"] not in ("first", "second"):
            continue
        if not any(k in r["name"] for k in ("Dining", "Library", "Smoking",
                                            "music", "staterooms")):
            continue
        poly = room_polygon(r)
        if not poly:
            continue
        z = DECK_Z[r["deck"]]
        xs = [p[0] for p in poly]
        x0, x1 = min(xs), max(xs)
        n = max(1, int((x1 - x0) / 2.3))
        for side in (1, -1):
            for i in range(n):
                xc = x0 + (i + 0.5) * (x1 - x0) / n
                b = layout.hull_side_halfbeam(xc, z) - 0.05
                if b < 1.6:
                    continue
                y = side * b
                # sash window: frame + glass, 0.60 x 1.05, sill 1.05
                v, f = box((xc, y, z + 1.62), (0.78, 0.10, 1.28))
                objs.append(mesh_object("Win_Frame", v, f, col=COL,
                                        mat=P["white_ceiling"]))
                v, f = box((xc, y - side * 0.03, z + 1.62), (0.60, 0.05, 1.05))
                objs.append(mesh_object("Win_Glass", v, f, col=COL,
                                        mat=P["daylight"]))
                # brass catch
                v, f = box((xc, y - side * 0.06, z + 1.14), (0.10, 0.04, 0.05))
                objs.append(mesh_object("Win_Catch", v, f, col=COL,
                                        mat=P["brass"]))
    return objs


def build(col, P_):
    global COL, P
    COL, P = col, P_
    groups = {}

    # floors for every deck
    floors = []
    for key, name, z, ext in layout.DECKS:
        mat = P["deck_wood"] if key in ("prom", "boat", "bridge") else \
              P["cabin_floor"] if key in ("saloon",) else P["steel_floor"]
        floors.append(floor_plate(key, mat))
    groups["floors"] = join_objects(floors, "Interior_Floors")

    # room shells
    walls = []
    for r in ROOMS:
        h = 2.45 if r["use"] in ("third", "crew") else 2.75
        wm = P["cabin_panel"] if r["use"] in ("first", "second") else \
             P["paint_cream"] if r["use"] == "crew" else P["steel_paint"]
        cm = P["ceiling_panel"] if r["use"] in ("first", "second") else \
             P["white_ceiling"]
        gaps = [(d["x"], d["y"], d["w"]) for d in DOORS if d["deck"] == r["deck"]]
        walls += room_shell(r, h, wm, P["cabin_floor"], cm, gaps)
    groups["rooms"] = join_objects(walls, "Interior_Rooms")

    groups["grand_stair"] = join_objects(grand_staircase(), "Grand_Staircase")
    groups["dining"] = join_objects(dining_saloon(), "Dining_Saloon_1C")
    groups["library"] = join_objects(library(), "Library")
    groups["smoking"] = join_objects(smoking_saloon(), "Smoking_Saloon_1C")
    groups["music"] = join_objects(music_room(), "Music_Room")
    groups["staterooms"] = join_objects(staterooms(), "Staterooms")
    groups["third"] = join_objects(third_class(), "Third_Class")
    groups["galley"] = join_objects(galley(), "Galley")
    groups["baths"] = join_objects(lavatories_and_baths(), "Lavatories")
    groups["officers"] = join_objects(hospital_and_officers(), "Officers_Captain")
    groups["wheelhouse"] = join_objects(wheelhouse_interior(), "Wheelhouse_Fittings")
    groups["windows"] = join_objects(public_room_windows(), "Interior_Windows")
    return groups


if __name__ == "__main__":
    sc = reset_scene()
    P = build_palette()
    # extra interior materials
    P["cloth"] = principled("Table_Cloth", (0.86, 0.85, 0.80, 1), 0.9)
    P["bed_linen"] = principled("Bed_Linen", (0.90, 0.89, 0.84, 1), 0.9)
    P["marble"] = principled("Marble", (0.86, 0.84, 0.79, 1), 0.18)
    P["mirror"] = principled("Mirror", (0.70, 0.74, 0.75, 1), 0.05, metal=1.0)
    P["cabin_panel"] = principled("Cabin_Panel", (0.30, 0.18, 0.10, 1), 0.45)
    P["cabin_floor"] = principled("Cabin_Floor", (0.28, 0.16, 0.10, 1), 0.55)
    P["ceil"] = P["white_ceiling"]
    P["ceiling_panel"] = principled("Ceiling_Panel", (0.84, 0.82, 0.76, 1), 0.8)
    P["steel_paint"] = principled("Steel_Paint", (0.55, 0.56, 0.55, 1), 0.6)
    P["paint_cream"] = principled("Paint_Cream", (0.78, 0.74, 0.62, 1), 0.7)
    P["steel_floor"] = principled("Steel_Floor", (0.30, 0.31, 0.30, 1), 0.7)
    P["book_a"] = principled("Book_A", (0.32, 0.10, 0.08, 1), 0.7)
    P["book_b"] = principled("Book_B", (0.10, 0.20, 0.14, 1), 0.7)
    P["book_c"] = principled("Book_C", (0.18, 0.14, 0.26, 1), 0.7)
    P["book_d"] = principled("Book_D", (0.35, 0.26, 0.12, 1), 0.7)
    P["painting"] = principled("Painting", (0.25, 0.30, 0.24, 1), 0.5)
    P["fire"] = principled("Fire_Glow", (1.0, 0.42, 0.12, 1), 0.4,
                           emit=(1.0, 0.35, 0.08, 1), emit_strength=5.0)
    P["ivory"] = principled("Ivory", (0.88, 0.86, 0.78, 1), 0.35)
    P["daylight"] = principled("Daylight_Glass", (0.80, 0.86, 0.92, 1), 0.05,
                               alpha=0.30, emit=(1.0, 0.98, 0.92, 1),
                               emit_strength=2.2)
    col = collection("SHIP_INTERIOR")
    groups = build(col, P)
    for k, v in groups.items():
        print("built", k, v.name if v else None,
              len(v.data.vertices) if v else 0)
    out = os.path.join(ROOT, "models", "module_interiors.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print("saved", out)
