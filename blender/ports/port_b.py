"""
port_b.py -- PORT OF CARRICKMORE : industrial shipbuilding, maintenance and repair port.

MODELLED ON BELFAST (Harland & Wolff / Workman Clark). Every distinctive feature below
is taken from the researched sources rather than invented:

  * THE PRINCESS GRAVING DOCK, cut 1885, opened 1889, "just over 800 feet long and
    80 feet wide ... the largest dry dock in the world at the time", "designed to be
    separated into 3 sections, using caissons to have a combination of dry and
    flooded dock space". Its caissons were built by another local shipbuilder and
    given yard numbers 53 and 54.
      -> modelled at 243.8 x 24.4 m (800 x 80 ft) with two intermediate caisson
         stops dividing it into three working sections.
  * AN OLDER GRAVING DOCK, on the model of the Hamilton Dock (1864-67) and the
    Clarendon Docks (1800 / 1826): the small 19th-century graving dock that the
    new dock was built to supplement.
  * BUILDING SLIPS on the river frontage. Ocean Steamships (1891) describes the
    yard frontage as "the launching-slips, where as many as fifteen vessels have
    been in course of construction at the same time", and a fitting-out dock cut at
    right angles to the river.
  * A MOULDING LOFT and a great glass-and-iron shed behind the slips "where all the
    iron-work for the hulls of fifteen ships has been handled at one time".
  * ENGINEERING / FORGE / BOILER shops with tall windows and saw-tooth roofs, a
    SAWMILL, and timber and plate stacks: "great stacks of timber, iron, and steel;
    a net-work of rails which connect the works with all the principal lines".
  * HIGH BRICK BOUNDARY WALLS: "the high brick walls which keep out idlers".
  * WORKER ACCESS: a time office / gatehouse controlling the yard, and terraced
    housing just outside the wall.

DELIBERATELY EXCLUDED because they post-date 1889: the Thompson Graving Dock (1911),
the Olympic/Titanic slipways as rebuilt for the Olympic class, and the Arrol gantry
(1905 onward). See HISTORICAL_EVIDENCE.md.

Coordinates: X east, Y north, Z up, metres. Water z = 0, quay top z = +4.0.
"""
import math
from core import MeshBuilder, QUAY_Z, LINER_L, LINER_B, LINER_DRAFT
import bldg, maritime, machinery, portsite as site
import parts as P

NAME = "PORT OF CARRICKMORE"
CODE = "B"

SITE = (-30.0, -300.0, 340.0, 400.0)
RIVER = (-460.0, -560.0, -30.0, 560.0)

# three building slips cut back from the river frontage
SLIPS = [(42.0, 76.0), (92.0, 126.0), (142.0, 176.0)]   # (y0, y1)
SLIP_X0, SLIP_X1 = -30.0, 66.0

# the great graving dock (Alexandra Dock model): along Y
PRINCESS = (96.0, 20.0, 244.0, 24.4)      # x0, y0, length, width
NO1_DOCK = (150.0, 40.0, 120.0, 18.0)

# The land platform must be holed out under BOTH graving docks, otherwise the
# land slab simply fills the dock volume and the dock is buried.
DOCK_HOLES = [(PRINCESS[0], PRINCESS[1], PRINCESS[0] + PRINCESS[3],
               PRINCESS[1] + PRINCESS[2]),
              (NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
               NO1_DOCK[1] + NO1_DOCK[2])]
WATER_HOLES = [(SLIP_X0, a, SLIP_X1, b) for a, b in SLIPS] + DOCK_HOLES


def build(R, coll, audit):
    # ================================================== prototypes
    R.define("B_quay24", _quay_module())

    # --- the two graving docks
    mb = MeshBuilder()
    maritime.graving_dock(mb, PRINCESS[0], PRINCESS[1], PRINCESS[2], PRINCESS[3],
                          depth=11.0, caissons=(0.34, 0.66))
    R.define("B_princess_dock", mb)
    mb = MeshBuilder()
    maritime.graving_dock(mb, NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[2], NO1_DOCK[3],
                          depth=8.0, caissons=())
    R.define("B_no1_dock", mb)
    mb = MeshBuilder(); maritime.caisson(mb, 0.0, 0.0, 24.4, 4.6); R.define("B_caisson", mb)
    mb = MeshBuilder(); maritime.caisson(mb, 0.0, 0.0, 18.0, 4.2); R.define("B_caisson_s", mb)

    # --- building slips (built along +Y then rotated -90 deg onto the frontage)
    mb = MeshBuilder()
    maritime.slipway(mb, 0.0, 0.0, 34.0, 96.0)
    R.define("B_slip", mb)

    # --- buildings
    mb = MeshBuilder(); bldg.moulding_loft(mb, 0, 0, 50, 18); R.define("B_moulding_loft", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 46, 24, chimney_h=22.0)
    R.define("B_engine_shop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 44, 22, chimney_h=18.0)
    R.define("B_boiler_shop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.pump_house(mb, 0, 0, 16, 12, chimney_h=26.0)
    R.define("B_pump_house", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 30, 18, sawtooth=True,
                                               crane_gantry=False, chimney_h=14.0)
    R.define("B_sawmill", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.time_office(mb, 0, 0, 11, 7); R.define("B_time_office", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 34, 20, floors=3, wall="brick_soot",
                                        hoist_side="S", hoist_bays=(1,))
    R.define("B_store", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 46, 14, floors=3, ground_h=3.9,
                                           h_floor=3.3, wall="brick_soot", bays=2.9)
    R.define("B_terrace", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 16, 12, floors=2, ground_h=3.9,
                                           h_floor=3.1, bays=3.2, shopfront=True,
                                           wall="brick_soot")
    R.define("B_pub", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 22, 46, h_eave=6.4, wall="brick_soot",
                                           open_side="W", bay=5.2)
    R.define("B_fitting_shed", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 38, 20, sawtooth=False,
                                               chimney_h=16.0)
    R.define("B_plateshop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 34, 18, sawtooth=True,
                                               crane_gantry=False, chimney_h=0.0)
    R.define("B_joinershop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 40, 16, floors=3, wall="sandstone",
                                           bays=3.4, shopfront=False)
    R.define("B_offices", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 30, 18, floors=3, wall="brick_buff",
                                        hoist_side="S", hoist_bays=(1,))
    R.define("B_store2", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 40, 18, h_eave=5.8, wall="brick_soot",
                                           open_side="S", bay=5.0)
    R.define("B_paintshop", mb, bevel=0.02)

    # --- plant
    mb = MeshBuilder(); machinery.titan_crane(mb, 0, 0, 0); R.define("B_titan", mb)
    mb = MeshBuilder(); machinery.sheer_legs(mb, 0, 0, 0); R.define("B_sheerlegs", mb)
    mb = MeshBuilder(); machinery.hydraulic_crane(mb, 0, 0, 0); R.define("B_crane", mb)
    mb = MeshBuilder(); machinery.steam_crane(mb, 0, 0, 0); R.define("B_steamcrane", mb)
    mb = MeshBuilder(); machinery.gas_lamp(mb, 0, 0, 0); R.define("B_lamp", mb)
    mb = MeshBuilder(); machinery.telegraph_pole(mb, 0, 0, 0); R.define("B_pole", mb)
    mb = MeshBuilder(); maritime.bollard(mb, 0, 0, 0); R.define("B_bollard", mb)
    mb = MeshBuilder(); maritime.capstan(mb, 0, 0, 0); R.define("B_capstan", mb)
    mb = MeshBuilder(); machinery.plate_stack(mb, 0, 0, 0); R.define("B_plates", mb)
    mb = MeshBuilder(); machinery.cargo_stack(mb, 0, 0, 0, seed=9); R.define("B_cargo", mb)
    mb = MeshBuilder(); machinery.wagon(mb, 0, 0, 0, kind="mineral"); R.define("B_wagon", mb)
    mb = MeshBuilder(); machinery.tank_loco(mb, 0, 0, 0); R.define("B_loco", mb)
    mb = MeshBuilder(); machinery.winch(mb, 0, 0, 0); R.define("B_winch", mb)
    mb = MeshBuilder(); machinery.fingerpost(mb, 0, 0, 0); R.define("B_fingerpost", mb)
    mb = MeshBuilder(); machinery.drain_gully(mb, 0, 0, 0); R.define("B_gully", mb)

    mb = MeshBuilder()                     # estate boundary wall
    mb.add_box(-10, -0.30, QUAY_Z - 0.1, 10, 0.30, QUAY_Z + 3.6, "brick_soot")
    mb.add_box(-10, -0.44, QUAY_Z + 3.6, 10, 0.44, QUAY_Z + 3.85, "granite")
    R.define("B_wall", mb)

    mb = MeshBuilder()                     # timber stacks
    for k in range(8):
        mb.add_box(0, 0, k * 0.26, 9.0, 2.4, k * 0.26 + 0.24, "timber")
    for k in range(5):
        mb.add_box(0.3, 2.5, k * 0.26, 8.7, 4.8, k * 0.26 + 0.24, "timber")
    R.define("B_timber", mb)

    # ================================================== land + water
    mb = MeshBuilder()
    site.add_land(mb, SITE, WATER_HOLES, top=QUAY_Z, bottom=-4.5, surf=None)
    site.land_surface_bands(mb, _surface_bands(), WATER_HOLES, top=QUAY_Z)
    site.water(mb, [(SLIP_X0, a, SLIP_X1, b) for a, b in SLIPS], z=0.0)
    # No. 1 dock is flooded with its caisson seated; the Princess dock is pumped dry
    site.water(mb, [(NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
                     NO1_DOCK[1] + NO1_DOCK[2] - 1.6)], z=0.0, step=12.0)
    site.water(mb, [RIVER], z=0.0)
    R.define("B_ground", mb)

    # ================================================== quay walls
    # river frontage either side of, and between, the slips
    edges = [(-300.0, SLIPS[0][0]), (SLIPS[0][1], SLIPS[1][0]),
             (SLIPS[1][1], SLIPS[2][0]), (SLIPS[2][1], 400.0)]
    for a, b in edges:
        _run(R, "X", -30.0, a, b, +1)
    # sides of each slip notch
    for a, b in SLIPS:
        _run(R, "Y", SLIP_X1, a, b, -1)

    # ================================================== slips
    for a, b in SLIPS:
        # prototype runs +Y from the low end; rotate -90 so it runs +X inland
        R.place("B_slip", SLIP_X0, b, 0.0, -90.0)

    # ================================================== graving docks + caissons
    R.place("B_princess_dock", 0, 0)
    R.place("B_no1_dock", 0, 0)
    # caissons seated at the dock entrances (north ends)
    R.place("B_caisson", PRINCESS[0], PRINCESS[1] + PRINCESS[2] - 1.6)
    R.place("B_caisson", PRINCESS[0], PRINCESS[1] + PRINCESS[2] * 0.66)
    R.place("B_caisson_s", NO1_DOCK[0], NO1_DOCK[1] + NO1_DOCK[2] - 1.6)

    # ================================================== buildings
    R.place("B_pump_house",    72, 250)
    R.place("B_moulding_loft", 140, 210)
    R.place("B_engine_shop",   140, 240)
    R.place("B_boiler_shop",   196, 240)
    R.place("B_sawmill",       210, 170)
    R.place("B_store",         250, 120)
    R.place("B_fitting_shed",  250, 60)
    R.place("B_time_office",    70, -30)
    R.place("B_terrace",        20, -110)
    R.place("B_terrace",        70, -110)
    R.place("B_terrace",       120, -110)
    R.place("B_pub",            24, -90)
    R.place("B_store",          20, -60)
    R.place("B_plateshop",     140, 280)
    R.place("B_joinershop",    190, 280)
    R.place("B_offices",       240, 200)
    R.place("B_store2",        250, 150)
    R.place("B_paintshop",     120, -20)
    R.place("B_store2",         20, -20)
    R.place("B_terrace",       170, -110)
    R.place("B_terrace",       220, -110)
    R.place("B_terrace",       270, -110)

    for a in [("B_plateshop", 140, 280, 178, 300), ("B_joinershop", 190, 280, 224, 298),
              ("B_offices", 240, 200, 280, 216), ("B_store2", 250, 150, 280, 168),
              ("B_paintshop", 120, -20, 160, -2), ("B_store2", 20, -20, 50, -2),
              ("B_terrace", 170, -110, 216, -96), ("B_terrace", 220, -110, 266, -96),
              ("B_terrace", 270, -110, 316, -96)]:
        audit.add(a[0], a[1], a[2], a[3], a[4])

    for a in [("B_pump_house", 72, 250, 88, 262), ("B_moulding_loft", 140, 210, 190, 228),
              ("B_engine_shop", 140, 240, 186, 264), ("B_boiler_shop", 196, 240, 240, 262),
              ("B_sawmill", 210, 170, 240, 188), ("B_store", 250, 120, 284, 140),
              ("B_fitting_shed", 250, 60, 272, 106), ("B_time_office", 70, -30, 81, -23),
              ("B_terrace", 20, -110, 66, -96), ("B_terrace", 70, -110, 116, -96),
              ("B_terrace", 120, -110, 166, -96), ("B_pub", 24, -90, 40, -78),
              ("B_store", 20, -60, 54, -40)]:
        audit.add(a[0], a[1], a[2], a[3], a[4])

    # ================================================== plant placement
    R.place("B_titan", 40, 200, QUAY_Z, 0.0)
    R.place("B_sheerlegs", 30, 20, QUAY_Z, 0.0)
    for y in (0, 30, 60):
        R.place("B_crane", 8, y, QUAY_Z, 90.0)
    for y in (190, 220, 250):
        R.place("B_steamcrane", 84, y, QUAY_Z, 180.0)
    for i in range(3):
        R.place("B_plates", 230, 20 + i * 26, QUAY_Z, 0.0)
    for x, y in ((250, 150), (268, 150), (250, 170)):
        R.place("B_timber", x, y, QUAY_Z)
    for x, y in ((10, -60), (30, -70), (200, 20), (100, 200)):
        R.place("B_cargo", x, y, QUAY_Z)
    for x, y in ((12, -20), (60, 190), (240, 200), (150, 30), (200, 120)):
        R.place("B_winch", x, y, QUAY_Z)
    for x, y in ((70, 120), (75, 160), (210, 60), (86, 300), (30, -140)):
        R.place("B_cargo", x, y, QUAY_Z)
    for x, y in ((216, 40), (232, 76), (216, 96)):
        R.place("B_plates", x, y, QUAY_Z)
    for x, y in ((286, 180), (286, 196), (60, 250)):
        R.place("B_timber", x, y, QUAY_Z)

    # ================================================== furniture
    for y in range(-290, 396, 16):
        if any(a - 2 < y < b + 2 for a, b in SLIPS):
            continue
        R.place("B_bollard", -27.5, y)
    for x in range(100, 320, 16):
        R.place("B_bollard", x, -52.0)
    for y in range(-40, 380, 44):
        R.place("B_capstan", -16.0, y)
    for y in range(-280, 390, 26):
        R.place("B_lamp", -8.0, y)
    for x in range(0, 300, 26):
        R.place("B_lamp", x, -46.0)
    for y in range(-30, 260, 34):
        R.place("B_pole", 92.0, y)
    for x, y in ((-14, 100), (86, -20), (130, 210), (24, -70)):
        R.place("B_fingerpost", x, y)
    for i in range(8):
        R.place("B_gully", -20, 10 + i * 44, QUAY_Z + 0.02)

    # ================================================== boundary wall
    for x in range(-10, 341, 20):
        R.place("B_wall", x, 400)
        R.place("B_wall", x, -300)
    for y in range(-290, 400, 20):
        R.place("B_wall", 340, y, 0, 90)

    # ================================================== railway
    _railway(R)

    # ================================================== signs
    _signs(R)

    meta = {
        "port": NAME, "code": CODE,
        "site": SITE, "water": {"river": RIVER,
                                "slip_basins": [(SLIP_X0, a, SLIP_X1, b) for a, b in SLIPS]},
        "quay_z": QUAY_Z,
        "graving_docks": [
            {"id": "B-GD1", "name": "The Princess Graving Dock",
             "built": "1885-1889", "length_m": 243.8, "width_m": 24.4,
             "entrance_depth_m": 11.0, "sections": 3,
             "caisson_stops_at": [0.34, 0.66],
             "rect": [PRINCESS[0], PRINCESS[1], PRINCESS[0] + PRINCESS[3],
                      PRINCESS[1] + PRINCESS[2]],
             "ship_envelope": {"L": LINER_L, "B": LINER_B, "draft": LINER_DRAFT},
             "basis": "Alexandra Dock, Belfast: 800 ft x 80 ft, largest dry dock in "
                      "the world when opened; arranged in 3 sections by caissons.",
             "adaptation": "Depth increased from the Alexandra's 26 ft sill to 11 m so "
                           "the specified 9 m-draft envelope can be docked on blocks."},
            {"id": "B-GD2", "name": "No. 1 Graving Dock",
             "built": "1867", "length_m": 120.0, "width_m": 18.0,
             "entrance_depth_m": 8.0, "sections": 1,
             "rect": [NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
                      NO1_DOCK[1] + NO1_DOCK[2]],
             "basis": "Hamilton Dock, Belfast (1864-67): the older graving dock on the "
                      "Co. Down side of the river, in use for repair and fitting out."},
        ],
        "slips": [
            {"id": "B-S%d" % (i + 1), "y0": a, "y1": b, "width_m": b - a,
             "rect": [SLIP_X0, a, SLIP_X1, b],
             "length_m": SLIP_X1 - SLIP_X0, "gradient": "2.6 deg",
             "basis": "Ocean Steamships (1891): the yard frontage lined with "
                      "launching slips; up to fifteen vessels building at once."}
            for i, (a, b) in enumerate(SLIPS)
        ],
        "berths": [
            {"id": "B-B1", "name": "Fitting-out quay, river frontage",
             "rect": (-58.0, 186.0, -30.0, 396.0), "length_m": 210.0, "depth_m": 10.0,
             "ship_envelope": {"L": LINER_L, "B": LINER_B, "draft": LINER_DRAFT},
             "mooring": "bollards 16 m centres + capstans", "kind": "fitting_out"},
            {"id": "B-B2", "name": "Service quay south of the slips",
             "rect": (-58.0, -280.0, -30.0, 40.0), "length_m": 320.0, "depth_m": 9.0,
             "ship_envelope": {"L": 140.0, "B": 18.0, "draft": 8.0},
             "mooring": "bollards", "kind": "repair"},
            {"id": "B-B3", "name": "No. 1 Graving Dock entrance",
             "rect": (NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
                      NO1_DOCK[1] + NO1_DOCK[2]),
             "length_m": 120.0, "depth_m": 8.0,
             "ship_envelope": {"L": 105.0, "B": 13.0, "draft": 6.5},
             "mooring": "docked on keel blocks", "kind": "dry_dock"},
        ],
        "interactions": [
            {"id": "B-I1", "name": "Time Office / Yard Gate", "pos": (70, -30),
             "type": "worker_gate", "radius": 5},
            {"id": "B-I2", "name": "Princess Dock Coping (north)", "pos": (108, 262),
             "type": "dock_caisson", "radius": 6},
            {"id": "B-I3", "name": "Princess Dock Floor", "pos": (108, 140),
             "type": "dock_floor_work", "radius": 10, "z": -11.0},
            {"id": "B-I4", "name": "Moulding Loft Floor", "pos": (165, 219),
             "type": "loft_work", "radius": 8},
            {"id": "B-I5", "name": "Engineering Shop", "pos": (163, 252),
             "type": "workshop", "radius": 8},
            {"id": "B-I6", "name": "Slip 1 (shoring / keel blocks)", "pos": (10, 59),
             "type": "slip_work", "radius": 8},
            {"id": "B-I7", "name": "Titan Crane Cab", "pos": (40, 200),
             "type": "crane_operate", "radius": 4},
            {"id": "B-I8", "name": "Timber Yard", "pos": (258, 158),
             "type": "materials", "radius": 8},
            {"id": "B-I9", "name": "Plate Yard", "pos": (232, 46),
             "type": "materials", "radius": 8},
            {"id": "B-I10", "name": "Fitting-out Quay", "pos": (-34, 250),
             "type": "fitting_out", "radius": 8},
        ],
        "paths": {
            "worker": [[(70, -30), (70, 40), (60, 120), (20, 200), (80, 240)],
                       [(70, -30), (20, -100), (20, -60)]],
            "vehicle": [[(340, -300), (300, -100), (300, 200), (200, 260)]],
            "rail": [[(-16, -280), (-16, 380)]],
        },
        "spawns": [{"id": "B-S1", "pos": (70, -24), "role": "worker"},
                   {"id": "B-S2", "pos": (14, 60), "role": "slipworker"}],
    }
    _life(R)

    return meta


# ------------------------------------------------------------------ helpers
def _quay_module():
    mb = MeshBuilder()
    maritime.quay_wall(mb, "X", 0.0, -12.0, 12.0, +1)
    return mb


def _run(R, axis, fixed, u0, u1, inward):
    L = 24.0
    n = max(1, int(round((u1 - u0) / L)))
    step = (u1 - u0) / n
    for i in range(n):
        u = u0 + step * (i + 0.5)
        if axis == "X":
            R.place("B_quay24", u, fixed, 0.0, 0.0 if inward > 0 else 180.0)
        else:
            R.place("B_quay24", fixed, u, 0.0, -90.0 if inward < 0 else 90.0)


def _railway(R):
    mb = MeshBuilder()
    # main yard line down the frontage
    for x in (-22.0, -16.0):
        machinery.rail_track(mb, x, -290.0, x, 396.0, z=QUAY_Z)
    # branches into the shops and across to the docks
    machinery.rail_track(mb, -16.0, 210.0, 140.0, 236.0, z=QUAY_Z)
    machinery.rail_track(mb, -16.0, 250.0, 190.0, 250.0, z=QUAY_Z)
    machinery.rail_track(mb, 140.0, 250.0, 140.0, 300.0, z=QUAY_Z)
    machinery.rail_track(mb, -16.0, 60.0, 90.0, 60.0, z=QUAY_Z)
    machinery.rail_track(mb, -16.0, -60.0, 300.0, -60.0, z=QUAY_Z)
    machinery.rail_track(mb, 230.0, -60.0, 230.0, 120.0, z=QUAY_Z)
    R.define("B_rail", mb)
    for x, y in ((60, 236), (100, 250), (150, 60)):
        R.place("B_loco", x, y, QUAY_Z, 0)
    for i in range(6):
        R.place("B_wagon", 74 + i * 5.6, 253.0, QUAY_Z)


def _signs(R):
    mb = MeshBuilder()
    mp = P.wmap("X", 208.0, +1)          # moulding loft south elevation
    bldg.sign_board(mb, mp, 25.0, 8.4, 12.0, 1.9, "sign_merrion")
    mp = P.wmap("X", 240.0, +1)          # engineering shop
    bldg.sign_board(mb, mp, 23.0, 7.2, 5.6, 0.85, "sign_engine_shop")
    mp = P.wmap("X", 228.0, +1)
    bldg.sign_board(mb, mp, 25.0, 11.0, 3.8, 0.85, "sign_moulding_loft")
    mp = P.wmap("X", 188.0, +1)          # sawmill
    bldg.sign_board(mb, mp, 15.0, 6.6, 5.0, 0.80, "sign_sawmill")
    mp = P.wmap("X", 250.0, +1)          # pump house
    bldg.sign_board(mb, mp, 8.0, 6.4, 5.4, 0.80, "sign_pump_house")
    mp = P.wmap("X", -23.0, +1)          # time office
    bldg.sign_board(mb, mp, 5.5, 5.4, 3.6, 0.85, "sign_time_office")
    R.define("B_signs", mb)
    R.place("B_signs", 0, 0)


# ------------------------------------------------------------------ surfaces
def _surface_bands():
    """Setts on the frontage and the slip heads, earth yards and plate roads inland.

    An ironworks yard is mud, ash, plate offcuts and spilt coal -- not paving.
    """
    return [
        (-30, -300, 66, 400, "setts"),      # river frontage, slip heads
        (66, -300, 340, 260, "yard"),       # fitting-out and plate yards
        (66, 260, 340, 340, "flags"),       # forecourt of the offices and shops
        (66, 340, 340, 400, "yard"),        # coal and scrap ground at the north
    ]


# ------------------------------------------------------------------ life
def _life(R):
    """Ironworkers, carters and the loose material of a building yard.

    Kept to where work is: the slip heads, the dock altars, the shop doors and
    the fitting-out quay. Empty ground between them is correct -- a yard full of
    evenly-spaced props looks like a showroom.
    """
    from core import QUAY_Z
    import life as L

    protos = {
        "B_man":      lambda mb: L.workman(mb, 0, 0, 0, coat="black"),
        "B_men":      lambda mb: L.workman_pair(mb, 0, 0, 0),
        "B_dray":     lambda mb: L.dray(mb, 0, 0, 0),
        "B_cart":     lambda mb: L.handcart(mb, 0, 0, 0),
        "B_planks":   lambda mb: L.plank_stack(mb, 0, 0, 0),
        "B_rope":     lambda mb: L.rope_coil(mb, 0, 0, 0),
        "B_coal":     lambda mb: L.coal_heap(mb, 0, 0, 0),
        "B_ladder":   lambda mb: L.ladder(mb, 0, 0, 0),
        "B_bales":    lambda mb: L.bale_stack(mb, 0, 0, 0, seed=11),
    }
    for n, fn in protos.items():
        mb = MeshBuilder(); fn(mb); R.define(n, mb)

    # men at the slip heads and along the frontage
    for y in (72, 88, 100, 121, 148, 170, 210, 250, 300, -40, -120, -210):
        R.place("B_man", -8, y, QUAY_Z, (y * 13) % 360)
    for y in (96, 158, 232):
        R.place("B_men", 4, y, QUAY_Z, (y * 7) % 360)
    # men on the shop floor side and in the yards
    for x, y in ((80, 40), (96, -60), (120, 120), (150, 200), (200, 300), (250, 60)):
        R.place("B_man", x, y, QUAY_Z, (x * 3) % 360)
    for x, y, rz in ((30, 60, 90), (40, 140, 95), (90, 210, 20), (170, 320, 10),
                     (240, 120, 200)):
        R.place("B_dray", x, y, QUAY_Z, rz)
    for x, y, rz in ((-10, 130, 90), (20, 190, 95), (70, -30, 20), (110, 250, 15)):
        R.place("B_cart", x, y, QUAY_Z, rz)
    # plate and timber stacks in the yards
    for x, y, rz in ((100, -180, 0), (130, -180, 0), (160, -120, 90), (90, 320, 0),
                     (210, 250, 90)):
        R.place("B_planks", x, y, QUAY_Z, rz)
    for y in (-260, -200, -150, 300, 360):
        R.place("B_rope", -22, y, QUAY_Z + 0.02)
    for x, y in ((150, -150), (180, -80), (230, 340)):
        R.place("B_coal", x, y, QUAY_Z)
    for x, y, rz in ((60, 210, 180), (120, 300, 90), (200, -200, 10)):
        R.place("B_ladder", x, y, QUAY_Z, rz)
    for x, y in ((80, 270), (140, 300), (190, 280)):
        R.place("B_bales", x, y, QUAY_Z, (x * 5) % 360)
