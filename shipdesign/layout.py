"""Deck-by-deck layout of SS Aurelian (1889).

This module is the single source of truth for the internal arrangement.  It is
consumed by:
    shipdesign.drawings   -> deck plan drawings
    blender/build_interiors -> 3D rooms, corridors, stairs, doors

Reasoning behind the stacking (documented in research/HISTORICAL_EVIDENCE.md):
    * White Star Teutonic / Majestic (1889) placed the first-class public
      rooms on the two decks immediately below the boat deck, with the
      library directly over the main saloon and a ground-glass table in the
      library floor lighting the saloon below (Ocean Magazine, Sept 1889).
    * Second class was a separate department aft, with its own dining saloon
      and its own small smoking room one deck above it.
    * Third class was split fore and aft, berthed in large rooms on the lower
      (orlop) deck and the 'tween decks, as on Umbria/Etruria.
    * Machinery amidships-aft: boiler rooms forward of the engine room, coal
      bunkers outboard of both, shafts in a watertight alley to the stern.

Coordinate convention: x forward (+), y to port (+), z up from base line.
Room rectangles are (x0, x1, y0, y1) in metres; y0/y1 are the bulwark-side
limits of the room, corridors are carved separately.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# DECK SCHEDULE  (z = top of deck plating at side, amidships)
# ---------------------------------------------------------------------------
DECKS = [
    # key       name                              z      hull extent
    ("bottom", "Inner Bottom / Tank Top",       1.30, (-76.0, 70.0)),
    ("lower",  "Lower (Orlop) Deck",            5.20, (-79.5, 76.0)),
    ("main",   "Main Deck",                     8.80, (-81.5, 79.5)),
    ("saloon", "Saloon Deck",                  11.80, (-60.0, 54.0)),
    ("prom",   "Promenade Deck",               14.40, (-78.0, 46.0)),
    ("boat",   "Boat Deck",                    17.20, (-14.0, 41.0)),
    ("bridge", "Bridge Deck",                  18.60, (30.0, 41.0)),
]
DECK_Z = {k: z for k, _, z, _ in DECKS}
DECK_EXT = {k: e for k, _, _, e in DECKS}
DECK_NAME = {k: n for k, n, _, _ in DECKS}

# sheer at side, amidships / at stem / at stern
SHEER_MID, SHEER_BOW, SHEER_STERN = 8.80, 11.40, 10.60

# superstructure side plating runs from main deck up to promenade deck
SUPERSTRUCTURE_EXT = (-78.0, 46.0)

# ---------------------------------------------------------------------------
# WATERTIGHT SUBDIVISION  (bulkhead x positions, from collision bulkhead aft)
# ---------------------------------------------------------------------------
BULKHEADS = [70.0, 58.0, 46.0, 34.0, 30.0, 18.0, 6.0, -6.0, -18.0, -27.0,
             -40.0, -52.0, -64.0, -74.0]

# ---------------------------------------------------------------------------
# ROOMS  (deck, x0, x1, y_min, y_max, name, class/use)
# y values are the inner faces.  Side corridors are defined implicitly by
# leaving 1.15 m between the room wall and the ship's side/bulwark.
# ---------------------------------------------------------------------------
Y_HALF_MAX = 9.20          # half beam
CORRIDOR_W = 1.15

ROOMS = []


def room(deck, x0, x1, y0, y1, name, use="", note=""):
    ROOMS.append(dict(deck=deck, x0=x0, x1=x1, y0=y0, y1=y1,
                      name=name, use=use, note=note))


# ============================ LOWER DECK 5.20 ==============================
room("lower", 58.0, 74.0, -8.0, 8.0, "Third Class — forward berths (men)", "third",
     "open berthing, 96 berths in three tiers")
room("lower", 46.0, 58.0, -8.0, 8.0, "Third Class — forward berths (women)", "third")
room("lower", 34.0, 46.0, -8.0, 8.0, "Third Class mess / washroom", "third")
room("lower", 18.0, 34.0, -8.2, 8.2, "No. 1 Hold (forward)", "cargo")
room("lower", 6.0, 18.0, -8.2, 8.2, "Crew — petty officers", "crew")
room("lower", -6.0, 6.0, -8.2, 8.2, "No. 2 Hold (midship) / store", "cargo")
room("lower", -18.0, -6.0, -4.2, 4.2, "Engine room casing & stores", "machinery")
room("lower", -40.0, -27.0, -8.2, 8.2, "Stokers' & trimmers' quarters", "crew")
room("lower", -52.0, -40.0, -8.2, 8.2, "No. 3 Hold (after)", "cargo")
room("lower", -64.0, -52.0, -8.2, 8.2, "Third Class — after berths", "third")
room("lower", -74.0, -64.0, -8.0, 8.0, "Third Class — after berths", "third",
     "100 berths, families")

# ============================= MAIN DECK 8.80 ==============================
room("main", 62.0, 78.0, -7.4, 7.4, "Forecastle — seamen's quarters", "crew",
     "14 seamen, boatswain's locker, paint store")
room("main", 48.0, 62.0, -8.0, 8.0, "No. 1 Hatch & winch", "cargo")
room("main", 30.0, 48.0, -8.4, 8.4, "Third Class berths (forward)", "third")
room("main", 12.0, 30.0, -8.6, 8.6, "First Class staterooms (forward)", "first",
     "34 staterooms, 46 berths")
room("main", -2.0, 12.0, -6.0, 6.0, "Entrance Hall (main staircase)", "first")
room("main", -24.0, -2.0, -8.6, 8.6, "First Class staterooms (midship)", "first",
     "40 staterooms, 58 berths")
room("main", -46.0, -24.0, -8.4, 8.4, "Third Class dining saloon", "third",
     "620 seats at long tables")
room("main", -58.0, -46.0, -8.4, 8.4, "No. 3 Hatch & winch", "cargo")
room("main", -78.0, -58.0, -7.6, 7.6, "Poop — Third Class berths (aft)", "third")

# ============================ SALOON DECK 11.80 ============================
room("saloon", 44.0, 56.0, -7.2, 7.2, "First Class staterooms (fwd)", "first")
room("saloon", 33.0, 36.5, -4.0, 4.0, "Funnel casing & uptakes (fwd)", "machinery")
room("saloon", 11.0, 27.0, -5.2, 5.2, "First Class music room", "first",
     "also used as a writing room by day")
room("saloon", 1.5, 6.5, -4.0, 4.0, "Funnel casing & uptakes (aft)", "machinery")
room("saloon", -9.0, 1.0, -5.4, 5.4, "Entrance Hall & Grand Staircase", "first",
     "three flights, dome above")
room("saloon", -44.0, -9.5, -7.4, 7.4, "First Class Dining Saloon", "first",
     "228 seats; central well covered by the library floor above")
room("saloon", -58.0, -45.5, -7.6, 7.6, "Galley, pantry & bakery", "crew")
room("saloon", -74.0, -58.0, -6.4, 6.4, "Second Class dining saloon", "second",
     "aft deckhouse, 132 seats")

# =========================== PROMENADE DECK 14.40 ==========================
room("prom", 38.0, 50.0, -7.0, 7.0, "First Class staterooms (promenade)", "first")
room("prom", 33.0, 36.5, -4.0, 4.0, "Funnel casing (fwd) & fidley", "machinery")
room("prom", 11.0, 27.0, -5.2, 5.2, "First Class Library", "first",
     "between the funnels; ground-glass centre table lights the saloon below")
room("prom", 1.5, 6.5, -4.0, 4.0, "Funnel casing (aft) & fidley", "machinery")
room("prom", -9.0, 1.0, -5.0, 5.0, "Staircase landing, vestibule & bar", "first",
     "mainmast trunk rises on the bulkhead at the after end")
room("prom", -24.0, -9.5, -7.2, 7.2, "First Class Smoking Saloon", "first",
     "panelled, leather settees, coal fire")
room("prom", -38.0, -24.0, -7.0, 7.0, "Barber, lavatories, bathrooms", "first")
room("prom", -49.0, -47.0, -6.0, 6.0, "Second Class smoking & library", "second")
room("prom", -70.0, -50.0, -5.0, 5.0, "Second Class promenade / boat stowage", "second",
     "mizzenmast trunk at its after end")

# ============================= BOAT DECK 16.60 =============================
room("boat", 12.0, 20.0, -5.6, 5.6, "Officers' quarters & captain's cabin", "crew")
room("boat", 20.5, 24.0, -4.4, 4.4, "Chart house & wireless-room store", "crew")
room("boat", -12.0, -6.5, -4.0, 4.0, "Engine skylight & fidley", "machinery")
room("boat", -14.0, -13.0, -3.0, 3.0, "Boat stowage", "machinery")

# ============================== BRIDGE 17.80 ===============================
room("bridge", 34.5, 40.5, -5.2, 5.2, "Wheelhouse", "crew",
     "teak, brass fittings, forward end of the bridge deck")

# ---------------------------------------------------------------------------
# STAIRCASES  (deck, name, x centre, y centre, width, run)
# ---------------------------------------------------------------------------
STAIRS = [
    dict(deck_from="main", deck_to="saloon", x=-1.0, y=0.0, w=6.4, run=9.0,
         name="Grand Staircase, main flight"),
    dict(deck_from="saloon", deck_to="prom", x=2.5, y=0.0, w=6.4, run=8.4,
         name="Grand Staircase, upper flight"),
    dict(deck_from="lower", deck_to="main", x=37.0, y=6.4, w=2.2, run=7.0,
         name="Third class stair, forward"),
    dict(deck_from="lower", deck_to="main", x=-60.0, y=5.8, w=2.2, run=7.0,
         name="Third class stair, aft"),
    dict(deck_from="main", deck_to="saloon", x=-50.0, y=6.2, w=1.6, run=6.4,
         name="Service stair, galley"),
    dict(deck_from="saloon", deck_to="prom", x=-36.0, y=6.4, w=1.4, run=6.0,
         name="Service stair, smoking room"),
    dict(deck_from="main", deck_to="saloon", x=-66.0, y=5.6, w=1.6, run=6.4,
         name="Second class stair"),
    dict(deck_from="prom", deck_to="boat", x=20.0, y=4.6, w=1.3, run=6.0,
         name="Officers' ladder"),
    dict(deck_from="boat", deck_to="bridge", x=36.0, y=4.2, w=1.3, run=5.4,
         name="Bridge ladder"),
]

# ---------------------------------------------------------------------------
# DOORS (bulkhead openings) — (deck, x, y, width, type)
# ---------------------------------------------------------------------------
DOORS = []
def door(deck, x, y, w=0.86, kind="cabin"):
    DOORS.append(dict(deck=deck, x=x, y=y, w=w, kind=kind))

# first class cabins open onto the side corridors
for x in (13.0, 16.0, 19.0, 22.0, 25.0, 28.0):
    door("main", x, 8.62, 0.86)
    door("main", x, -8.62, 0.86)
for x in (-4.0, -7.0, -10.0, -13.0, -16.0, -19.0, -22.0):
    door("main", x, 8.62, 0.86)
    door("main", x, -8.62, 0.86)
# public room entries
door("saloon", 6.0, 5.42, 1.6, "double")
door("saloon", 2.0, -5.42, 1.6, "double")
door("saloon", -30.0, 7.42, 1.2, "double")
door("prom", 10.0, 5.22, 1.4, "double")
door("prom", -12.0, 7.22, 1.4, "double")
door("prom", 2.0, -5.02, 1.4, "double")

# ---------------------------------------------------------------------------
# CORRIDOR CENTRELINES (used to place wall gaps and lighting)
# ---------------------------------------------------------------------------
CORRIDORS = dict(
    main=[dict(x0=6.0, x1=30.0, y=8.05), dict(x0=6.0, x1=30.0, y=-8.05),
          dict(x0=-24.0, x1=-2.0, y=8.05), dict(x0=-24.0, x1=-2.0, y=-8.05)],
    saloon=[dict(x0=-46.0, x1=-2.0, y=7.85), dict(x0=-46.0, x1=-2.0, y=-7.85)],
    prom=[dict(x0=-44.0, x1=30.0, y=7.65), dict(x0=-44.0, x1=30.0, y=-7.65)],
)


def _hull():
    """Import the hull lazily (layout <-> hull import order)."""
    from .hull import HULL
    return HULL


def hull_half_beam(x, z):
    """Local half breadth of the shell at (x, z)."""
    return _hull().half_beam_at(x, z)


def room_ceiling_z(deck):
    """Heights of the space a deck's rooms sit in.

    Each deck's rooms occupy the space between that deck and the one above,
    or - for the topmost decks - a normal storey above.  Above the hull the
    side of the ship is the deckhouse wall, so the room must be clipped to
    the HULL only where the hull actually exists at that height.
    """
    keys = [d[0] for d in DECKS]
    z = DECK_Z[deck]
    i = keys.index(deck)
    if i + 1 < len(keys):
        return z, DECK_Z[keys[i + 1]] - 0.08
    return z, z + 2.45


def hull_side_halfbeam(x, z):
    """Half beam of whatever forms the side of the ship at (x, z).

    Inside the hull envelope: the shell.  Above the sheer strake: the
    superstructure side (the deckhouse wall), which is what a room on the
    promenade deck actually abuts.
    """
    b = hull_half_beam(x, z)
    if b > 0.6:
        return b
    zdeck = _hull().deck_z(x)
    b = hull_half_beam(x, zdeck - 0.05)
    if b > 0.6:
        # superstructure side: a straight continuation with a small tumblehome
        return max(b - 0.42 - 0.05 * (z - zdeck), 0.6)
    return b


def room_polygon(r, inset=0.10):
    """Clip a room rectangle to the ship's side at its deck height."""
    z = DECK_Z[r["deck"]]
    x0, x1, y0, y1 = r["x0"], r["x1"], r["y0"], r["y1"]
    # clip the y range to the narrowest half-breadth in the x span
    ymax = min(hull_side_halfbeam(x, z) for x in
               [x0, (x0 + x1) / 2, x1]) - inset
    if ymax < 0.25:
        return []
    y1 = min(y1, ymax)
    y0 = max(y0, -ymax)
    if y1 - y0 < 0.3:
        return []
    # also trim the x range where the ship is too narrow for the room width
    need = max(abs(y0), abs(y1))
    xs = [x for x in [x0 + i * (x1 - x0) / 60.0 for i in range(61)]
          if hull_side_halfbeam(x, z) - inset >= need - 1e-6]
    if not xs:
        return []
    x0c, x1c = min(xs), max(xs)
    if x1c - x0c < 0.4:
        return []
    return [(x0c, y1), (x1c, y1), (x1c, y0), (x0c, y0)]


def rooms_on(deck):
    return [r for r in ROOMS if r["deck"] == deck]


def room_at(deck, x, y):
    for r in rooms_on(deck):
        if r["x0"] <= x <= r["x1"] and r["y0"] <= y <= r["y1"]:
            return r
    return None


def summary():
    import collections
    c = collections.Counter()
    for r in ROOMS:
        c[r["deck"]] += 1
    return dict(c)


if __name__ == "__main__":
    print(summary())
    for r in ROOMS:
        print("%-7s %7.1f %7.1f  %-38s %s" % (r["deck"], r["x0"], r["x1"],
                                              r["name"], r["use"]))
