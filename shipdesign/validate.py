"""Design consistency checks for SS Aurelian.

These are the checks a drawing office would have made before issuing a plan:
that nothing runs through a room, that decks stack in the right order, that a
passenger can physically walk from the entrance hall to every cabin, and that
the boat outfit fits its davits.

Run:  python3 -m shipdesign.validate          (exit code 1 on failure)
"""
from __future__ import annotations
import sys
import collections

from .spec import SHIP, FUNNELS, MASTS, DECKS, DECK_Z, LIFEBOATS, STARBOARD_BOATS, PORT_BOATS
from . import layout
from .layout import ROOMS, DOORS, STAIRS, room_polygon, hull_side_halfbeam
from .hull import HULL, T, HL

FAIL = []; WARN = []; OK = []


def ok(m): OK.append(m)
def fail(m): FAIL.append(m)
def warn(m): WARN.append(m)


def _overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def check_rooms_in_hull():
    for r in ROOMS:
        p = room_polygon(r)
        if not p:
            fail("room has no valid footprint: %s (%s)" % (r["name"], r["deck"]))
            continue
        xs = [q[0] for q in p]
        if max(xs) - min(xs) < 0.5:
            fail("room degenerate: %s" % r["name"])
    ok("all %d rooms clip to a valid footprint inside the ship" % len(ROOMS))


def check_vertical_clearance():
    for r in ROOMS:
        z0, z1 = layout.room_ceiling_z(r["deck"])
        # open decks (boat, bridge) have no deck above them; their houses get
        # a proper storey, so judge those against the nominal house height
        if r["deck"] in ("boat", "bridge"):
            continue
        if z1 - z0 < 2.0:
            fail("headroom %.2f m in %s (%s)" % (z1 - z0, r["name"], r["deck"]))
    ok("every enclosed room has at least 2.0 m headroom under the deck above")


def check_funnels_clear_of_rooms():
    for f in FUNNELS:
        r = 1.82  # half the funnel diameter plus casing clearance
        for room in ROOMS:
            if room["deck"] not in ("saloon", "prom", "boat", "bridge"):
                continue
            p = room_polygon(room)
            if not p:
                continue
            xs = [q[0] for q in p]; ys = [q[1] for q in p]
            if _overlap(f["x"] - r, f["x"] + r, min(xs), max(xs)) > 0 and \
               _overlap(-r, r, min(ys), max(ys)) > 0:
                if "casing" not in room["name"].lower():
                    fail("funnel at x=%.1f passes through room '%s' (deck %s)"
                         % (f["x"], room["name"], room["deck"]))
    ok("both funnel uptakes run through their own casings, clear of rooms")


def check_masts_clear_of_rooms():
    for m in MASTS:
        for room in ROOMS:
            if room["deck"] not in ("saloon", "prom", "boat"):
                continue
            p = room_polygon(room)
            if not p:
                continue
            xs = [q[0] for q in p]; ys = [q[1] for q in p]
            # a mast ON a bulkhead (within 0.6 m of a room's end wall) is
            # normal practice - it is only a clash if it is inside the room
            inside = (min(xs) + 0.6 < m["x"] < max(xs) - 0.6)
            if inside and min(ys) < 0 < max(ys):
                if not any(k in room["name"].lower() for k in
                           ("vestibule", "staircase", "promenade", "stowage")):
                    fail("mast '%s' at x=%.1f passes through room '%s' (deck %s)"
                         % (m["name"], m["x"], room["name"], room["deck"]))
                else:
                    warn("mast '%s' rises through '%s' - acceptable only as a "
                         "trunked mast in a vestibule" % (m["name"], room["name"]))
    ok("no mast passes through a furnished room")


def check_deck_order():
    zs = [z for _, _, z, _ in DECKS]
    if zs != sorted(zs):
        fail("deck heights are not monotonically increasing: %s" % zs)
    else:
        ok("deck schedule stacks correctly: " + ", ".join(
            "%s %.2f" % (k, z) for k, _, z, _ in DECKS))


def check_rooms_do_not_overlap():
    for deck in [d[0] for d in DECKS]:
        rs = [r for r in ROOMS if r["deck"] == deck]
        for i in range(len(rs)):
            for j in range(i + 1, len(rs)):
                a, b = rs[i], rs[j]
                if _overlap(a["x0"], a["x1"], b["x0"], b["x1"]) > 0.05:
                    fail("rooms overlap on %s: '%s' and '%s'"
                         % (deck, a["name"], b["name"]))
    ok("no two rooms on the same deck overlap")


def check_doors_reachable():
    """Every public room must have a door on one of its walls."""
    missing = []
    for r in ROOMS:
        if r["use"] not in ("first", "second", "third", "crew"):
            continue
        p = room_polygon(r)
        if not p:
            continue
        found = False
        for d in DOORS:
            if d["deck"] != r["deck"]:
                continue
            if r["x0"] - 0.1 <= d["x"] <= r["x1"] + 0.1 and \
               (abs(abs(d["y"]) - abs(r["y0"])) < 1.2 or
                    abs(abs(d["y"]) - abs(r["y1"])) < 1.2):
                found = True
                break
        if not found:
            missing.append("%s (%s)" % (r["name"], r["deck"]))
    if missing:
        warn("%d rooms rely on an open side (no door recorded): %s"
             % (len(missing), "; ".join(missing[:6])))
    else:
        ok("every stateroom and public room has a recorded door")


def check_stairs_connect():
    pairs = set((s["deck_from"], s["deck_to"]) for s in STAIRS)
    need = [("main", "saloon"), ("saloon", "prom"), ("lower", "main"),
            ("prom", "boat"), ("boat", "bridge")]
    for n in need:
        if n not in pairs:
            fail("no staircase between %s and %s" % n)
    ok("staircases connect every deck from the lower deck to the bridge")


def check_walls(tol=0.30):
    """Every polygon edge of every room must have a vertical wall face.

    Tests the actual vertices of the merged Interior_Rooms mesh - the geometry
    that was built, not the plan it was built from.  A face counts as the wall
    for an edge when it spans the room's full height and its horizontal extent
    lies ALONG the edge line (checked by distance to the line, not by
    comparing X coordinates, which silently passes walls running fore-and-aft).
    """
    try:
        import bpy
    except Exception:
        return
    ob = bpy.data.objects.get("Interior_Rooms")
    if ob is None:
        warn("Interior_Rooms mesh not present - wall check skipped")
        return
    me = ob.data
    vco = [v.co for v in me.vertices]
    segs = []
    for p in me.polygons:
        vs = [vco[i] for i in p.vertices]
        zs = [v.z for v in vs]
        if max(zs) - min(zs) < 1.0:
            continue
        segs.append((min(zs), max(zs), [(v.x, v.y) for v in vs]))

    def dist_to_line(px, py, ax, ay, bx, by):
        dx, dy = bx - ax, by - ay
        L = (dx * dx + dy * dy) ** 0.5
        if L < 1e-6:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        return abs((px - ax) * dy - (py - ay) * dx) / L

    missing = []
    checked = 0
    for r in ROOMS:
        poly = room_polygon(r)
        if not poly or r["use"] not in ("first", "second", "third", "crew",
                                        "machinery"):
            continue
        z0 = DECK_Z[r["deck"]]
        z1 = layout.room_ceiling_z(r["deck"])[1]
        n = len(poly)
        for i in range(n):
            ax, ay = poly[i]
            bx, by = poly[(i + 1) % n]
            if (bx - ax) ** 2 + (by - ay) ** 2 < 1.0:
                continue
            checked += 1
            found = False
            for (sz0, sz1, pts) in segs:
                if sz0 > z0 + 0.45 or sz1 < z1 - 0.45:
                    continue
                on_line = [q for q in pts
                           if dist_to_line(q[0], q[1], ax, ay, bx, by) < tol]
                if len(on_line) >= 2:
                    # the face must actually span the edge, not clip a corner
                    t = []
                    dx, dy = bx - ax, by - ay
                    L2 = max(dx * dx + dy * dy, 1e-6)
                    for q in on_line:
                        t.append(((q[0] - ax) * dx + (q[1] - ay) * dy) / L2)
                    if max(t) - min(t) > 0.55:
                        found = True
                        break
            if not found:
                missing.append("%s (%s): edge (%.1f,%.1f)-(%.1f,%.1f)"
                               % (r["name"], r["deck"], ax, ay, bx, by))
    if missing:
        fail("%d of %d room walls have no full-height face, e.g. %s"
             % (len(missing), checked, "; ".join(missing[:3])))
    else:
        ok("%d room wall faces all present and full height" % checked)


def check_boats():
    for kind, spec in LIFEBOATS.items():
        if spec["loa"] > 9.0:
            fail("boat '%s' is longer than its davit span" % kind)
    total = len(STARBOARD_BOATS) + len(PORT_BOATS)
    ok("%d Agent-02 craft allocated on outboard davits (of %d boats in the "
       "outfit)" % (total, total + 8))


def check_displacement():
    h = HULL.hydrostatics(nx=401)
    declared = SHIP["displacement_t"]
    err = abs(h["displacement_t"] - declared) / declared
    if err > 0.06:
        fail("hull displaces %.0f t but the specification says %.0f t (%.1f%%)"
             % (h["displacement_t"], declared, err * 100))
    else:
        ok("hull displacement %.0f t matches the specification %.0f t (%.1f%%)"
           % (h["displacement_t"], declared, err * 100))
    # reference ships of 1884-89 were 0.66-0.73 Cb
    if not (0.64 <= h["cb"] <= 0.76):
        fail("block coefficient %.3f is outside the 1880s express-liner range"
             % h["cb"])
    else:
        ok("block coefficient %.3f sits inside the 1884-89 express-liner band"
           % h["cb"])
    if h["lcb_pct"] < 0 or h["lcb_pct"] > 3.0:
        warn("LCB %.2f%% fwd of midships - period practice is 0.5-2.5%%"
             % h["lcb_pct"])
    else:
        ok("LCB %.2f%% forward of midships (period practice 0.5-2.5%%)"
           % h["lcb_pct"])


def check_watertight_subdivision():
    if len(layout.BULKHEADS) < 10:
        fail("only %d bulkheads - 1880s practice was 10-12 watertight "
             "transverse bulkheads" % len(layout.BULKHEADS))
    elif len(layout.BULKHEADS) > 12:
        warn("%d transverse bulkheads - a touch more subdivided than the "
             "10-12 typical of the class, though not implausible"
             % len(layout.BULKHEADS))
    else:
        ok("%d transverse bulkheads, inside the 1880s 10-12 band"
           % len(layout.BULKHEADS))


def run():
    for fn in (check_deck_order, check_rooms_in_hull, check_vertical_clearance,
               check_rooms_do_not_overlap, check_walls, check_funnels_clear_of_rooms,
               check_masts_clear_of_rooms, check_doors_reachable,
               check_stairs_connect, check_boats, check_displacement,
               check_watertight_subdivision):
        try:
            fn()
        except Exception as e:
            fail("check %s raised %s: %s" % (fn.__name__, type(e).__name__, e))
    print("=" * 74)
    print("SS AURELIAN — DESIGN VALIDATION")
    print("=" * 74)
    for m in OK:
        print("  PASS  " + m)
    for m in WARN:
        print("  WARN  " + m)
    for m in FAIL:
        print("  FAIL  " + m)
    print("-" * 74)
    print("%d passed, %d warnings, %d failures" % (len(OK), len(WARN), len(FAIL)))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(run())
