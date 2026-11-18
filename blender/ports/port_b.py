"""
port_b.py -- Port B layout: Carrickmore Shipyard & Graving Docks (c. 1889).
GENERATION II — OPERATION VICTORIA (PERICLES-II)

Historical Basis:
  * Belfast River Lagan / Harland & Wolff Queen's Island shipyard c. 1889
  * The Alexandra Graving Dock (opened 1889, 800 ft x 80 ft, 3 working sections)
  * Hamilton Graving Dock (1867, 120 m repair dock)
  * River Lagan building slips with inclined ways running into the water
  * Day, Summers & Co. 80-ton tubular masting sheer legs at the fitting-out quay
  * Moulding loft, plate shops, engine works, boiler shop, and yard standard-gauge railway
"""
import math
from core import MeshBuilder, QUAY_Z, WATER_Z, DOCK_BED_Z
import parts as P
import bldg
import maritime
import machinery
import portsite as site

NAME = "Carrickmore"
CODE = "B"

# ------------------------------------------------------------------ boundaries
SITE = (-30.0, -300.0, 340.0, 400.0)
RIVER = (-460.0, -560.0, -30.0, 560.0)

# Three building slips cut back from river frontage
SLIPS = [(42.0, 76.0), (92.0, 126.0), (142.0, 176.0)]   # (y0, y1)
SLIP_X0, SLIP_X1 = -30.0, 66.0

# Alexandra Dock model (Princess Graving Dock) along Y
PRINCESS = (96.0, 20.0, 244.0, 24.4)      # x0, y0, length, width
NO1_DOCK = (150.0, 40.0, 120.0, 18.0)

DOCK_HOLES = [(PRINCESS[0], PRINCESS[1], PRINCESS[0] + PRINCESS[3],
               PRINCESS[1] + PRINCESS[2]),
              (NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
               NO1_DOCK[1] + NO1_DOCK[2])]
WATER_HOLES = [(SLIP_X0, a, SLIP_X1, b) for a, b in SLIPS] + DOCK_HOLES

LINER_L = 166.0
LINER_B = 18.0
LINER_DRAFT = 6.5


# ------------------------------------------------------------------ build
def build(R, coll, audit):
    # ================================================== prototypes
    R.define("B_quay24", _quay_module())

    # Graving docks
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

    # Building slips
    mb = MeshBuilder()
    maritime.slipway(mb, 0.0, 0.0, 34.0, 96.0, top_z=QUAY_Z, end_z=-6.0)
    R.define("B_slip", mb)

    # Day Summers 80-ton tubular masting sheer legs
    mb = MeshBuilder()
    machinery.day_summers_sheer_legs(mb, 0.0, 0.0, z=0.0, height=28.0, spread=12.0, overhang=9.0)
    R.define("B_sheerlegs80", mb)

    # Dray cart
    mb = MeshBuilder()
    machinery.dray_cart(mb, 0, 0, z=0.0)
    R.define("B_dray_cart", mb)

    # Pierhead lighthouse
    mb = MeshBuilder()
    bldg.pierhead_lighthouse(mb, 0, 0, 0.0, h_tower=14.0)
    R.define("B_lighthouse", mb, bevel=0.02)

    # Harbour signal station
    mb = MeshBuilder()
    bldg.harbour_signal_station(mb, 0, 0, 0.0)
    R.define("B_signal_station", mb, bevel=0.02)

    # Shipyard 3-roller plate bending machine
    mb = MeshBuilder()
    machinery.plate_bending_rolls(mb, 0, 0, z=0.0)
    R.define("B_plate_rolls", mb, bevel=0.02)

    # Clydesdale draught horse
    mb = MeshBuilder()
    machinery.draught_horse(mb, 0, 0, 0.0)
    R.define("B_draught_horse", mb)

    # Buildings
    mb = MeshBuilder(); bldg.moulding_loft(mb, 0, 0, 50, 18); R.define("B_moulding_loft", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 46, 24, chimney_h=22.0); R.define("B_engine_shop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 44, 22, chimney_h=18.0); R.define("B_boiler_shop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.pump_house(mb, 0, 0, 16, 12, chimney_h=26.0); R.define("B_pump_house", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 30, 18, sawtooth=True, crane_gantry=False, chimney_h=14.0); R.define("B_sawmill", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.time_office(mb, 0, 0, 11, 7); R.define("B_time_office", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 34, 20, floors=3, wall="brick_soot", hoist_side="S", hoist_bays=(1,)); R.define("B_store", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 46, 14, floors=3, ground_h=3.9, h_floor=3.3, wall="brick_soot", bays=2.9); R.define("B_terrace", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 16, 12, floors=2, ground_h=3.9, h_floor=3.1, bays=3.2, shopfront=True, wall="brick_soot"); R.define("B_pub", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 22, 46, h_eave=6.4, wall="brick_soot", open_side="W", bay=5.2); R.define("B_fitting_shed", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 38, 20, sawtooth=False, chimney_h=16.0); R.define("B_plateshop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.engineering_shop(mb, 0, 0, 34, 18, sawtooth=True, crane_gantry=False, chimney_h=0.0); R.define("B_joinershop", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 40, 16, floors=3, wall="sandstone", bays=3.4, shopfront=False); R.define("B_offices", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 30, 18, floors=3, wall="brick_buff", hoist_side="S", hoist_bays=(1,)); R.define("B_store2", mb, bevel=0.02)
    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 40, 18, h_eave=5.8, wall="brick_soot", open_side="S", bay=5.0); R.define("B_paintshop", mb, bevel=0.02)

    # Plant
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

    mb = MeshBuilder()
    mb.add_box(-10, -0.30, -0.1, 10, 0.30, 3.6, "brick_soot")
    mb.add_box(-10, -0.44, 3.6, 10, 0.44, 3.85, "granite")
    R.define("B_wall", mb)

    mb = MeshBuilder()
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
    site.water(mb, [(NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
                     NO1_DOCK[1] + NO1_DOCK[2] - 1.6)], z=0.0, step=12.0)
    site.water(mb, [RIVER], z=0.0)
    R.define("B_ground", mb)
    R.place("B_ground", 0, 0, 0.0)

    # ================================================== quay walls
    # River frontage either side of and between slips (water is West, land is East)
    edges = [(-300.0, SLIPS[0][0]), (SLIPS[0][1], SLIPS[1][0]),
             (SLIPS[1][1], SLIPS[2][0]), (SLIPS[2][1], 400.0)]
    for a, b in edges:
        _run_frontage(R, -30.0, a, b, rz=-90.0)

    # Enclose the three building slipways with masonry retaining walls
    for a, b in SLIPS:
        _run_slip_x(R, a, -30.0, 66.0, rz=180.0)      # South side wall (faces +Y into slip)
        _run_slip_x(R, b, -30.0, 66.0, rz=0.0)        # North side wall (faces -Y into slip)
        _run_frontage(R, 66.0, a, b, rz=-90.0)       # Slip head wall (faces -X into slip)

    # ================================================== slips
    for a, b in SLIPS:
        R.place("B_slip", SLIP_X0, b, 0.0, -90.0)

    # ================================================== graving docks + caissons
    R.place("B_princess_dock", 0, 0, 0.0)
    R.place("B_no1_dock", 0, 0, 0.0)
    R.place("B_caisson", PRINCESS[0], PRINCESS[1] + PRINCESS[2] - 1.6, QUAY_Z)
    R.place("B_caisson", PRINCESS[0], PRINCESS[1] + PRINCESS[2] * 0.66, QUAY_Z)
    R.place("B_caisson_s", NO1_DOCK[0], NO1_DOCK[1] + NO1_DOCK[2] - 1.6, QUAY_Z)

    # ================================================== heavy lift: 80-ton sheer legs
    # Pinned at fitting-out quay edge at x = -20.0, y = 280.0, overhang 9m over river
    R.place("B_sheerlegs80", -20.0, 280.0, QUAY_Z)

    # ================================================== buildings
    R.place("B_pump_house",    72, 250, QUAY_Z)
    R.place("B_moulding_loft", 140, 210, QUAY_Z)
    R.place("B_engine_shop",   140, 240, QUAY_Z)
    R.place("B_boiler_shop",   196, 240, QUAY_Z)
    R.place("B_sawmill",       210, 170, QUAY_Z)
    R.place("B_store",         250, 120, QUAY_Z)
    R.place("B_fitting_shed",  250,  60, QUAY_Z)
    R.place("B_time_office",    70, -30, QUAY_Z)
    R.place("B_terrace",        20, -110, QUAY_Z)
    R.place("B_terrace",        70, -110, QUAY_Z)
    R.place("B_terrace",       120, -110, QUAY_Z)
    R.place("B_pub",            24, -90, QUAY_Z)
    R.place("B_store",          20, -60, QUAY_Z)
    R.place("B_plateshop",     140, 280, QUAY_Z)
    R.place("B_joinershop",    190, 280, QUAY_Z)
    R.place("B_offices",       240, 200, QUAY_Z)
    R.place("B_store2",        250, 150, QUAY_Z)
    R.place("B_paintshop",     120, -20, QUAY_Z)
    R.place("B_store2",         20, -20, QUAY_Z)
    R.place("B_terrace",       170, -110, QUAY_Z)
    R.place("B_terrace",       220, -110, QUAY_Z)
    R.place("B_terrace",       270, -110, QUAY_Z)

    # ================================================== plant placement
    for y in (0, 30):
        R.place("B_crane", -18, y, QUAY_Z, 90.0)
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

    # Dray carts and draught horses
    R.place("B_dray_cart", 40.0, -10.0, QUAY_Z, 20.0)
    R.place("B_draught_horse", 43.5, -9.0, QUAY_Z, 20.0)
    R.place("B_dray_cart", 160.0, 180.0, QUAY_Z, -80.0)
    R.place("B_draught_horse", 160.0, 176.0, QUAY_Z, -80.0)
    R.place("B_dray_cart", 24.0, 260.0, QUAY_Z, 45.0)
    R.place("B_draught_horse", 26.5, 262.5, QUAY_Z, 45.0)

    # Platers' yard heavy 3-roller plate bending machines
    R.place("B_plate_rolls", 100.0, 150.0, QUAY_Z, 0.0)
    R.place("B_plate_rolls", 160.0, 160.0, QUAY_Z, 90.0)

    # Pierhead lighthouse and harbour signal station
    R.place("B_lighthouse", -26.0, 380.0, QUAY_Z)
    R.place("B_signal_station", 70.0, -50.0, QUAY_Z)

    # Boundary walls
    for x in range(0, 331, 20):
        R.place("B_wall", x, 396, QUAY_Z)
    for x in range(0, 331, 20):
        R.place("B_wall", x, -296, QUAY_Z)
    for y in range(-280, 396, 20):
        R.place("B_wall", 336, y, QUAY_Z, 90)

    # ================================================== furniture
    for y in range(-290, 396, 16):
        if any(a - 2 < y < b + 2 for a, b in SLIPS):
            continue
        R.place("B_bollard", -27.5, y, QUAY_Z)
    for x in range(100, 320, 16):
        R.place("B_bollard", x, -52.0, QUAY_Z)
    for y in range(-40, 380, 44):
        R.place("B_capstan", -20.0, y, QUAY_Z)

    for y in range(-260, 380, 32):
        R.place("B_lamp", 12.0, y, QUAY_Z)
    for y in range(-260, 380, 48):
        R.place("B_pole", 82.0, y, QUAY_Z)

    _railway(R)
    _signs(R)
    _life(R)

    meta = {
        "port": NAME, "code": CODE,
        "site": SITE, "water": {"river": RIVER,
                                "slip_basins": [(SLIP_X0, a, SLIP_X1, b) for a, b in SLIPS]},
        "quay_z": QUAY_Z,
        "graving_docks": [
            {"id": "B-GD1", "name": "The Princess Graving Dock",
             "built": "1885-1889", "length_m": 243.8, "width_m": 24.4,
             "entrance_depth_m": 11.0, "sections": 3,
             "rect": [PRINCESS[0], PRINCESS[1], PRINCESS[0] + PRINCESS[3],
                      PRINCESS[1] + PRINCESS[2]],
             "basis": "Alexandra Graving Dock, Belfast (1885-89)"},
            {"id": "B-GD2", "name": "No. 1 Graving Dock",
             "built": "1867", "length_m": 120.0, "width_m": 18.0,
             "entrance_depth_m": 8.0, "sections": 1,
             "rect": [NO1_DOCK[0], NO1_DOCK[1], NO1_DOCK[0] + NO1_DOCK[3],
                      NO1_DOCK[1] + NO1_DOCK[2]],
             "basis": "Hamilton Dock, Belfast (1864-67)"},
        ],
        "slips": [
            {"id": "B-S%d" % (i + 1), "y0": a, "y1": b, "width_m": b - a,
             "rect": [SLIP_X0, a, SLIP_X1, b],
             "length_m": SLIP_X1 - SLIP_X0, "gradient": "2.6 deg",
             "basis": "Ocean Steamships (1891)"}
            for i, (a, b) in enumerate(SLIPS)
        ],
        "berths": [
            {"id": "B-B1", "name": "Fitting-out quay, river frontage (Day Summers 80t sheer legs)",
             "rect": (-58.0, 186.0, -30.0, 396.0), "length_m": 210.0, "depth_m": 10.0,
             "ship_envelope": {"L": LINER_L, "B": LINER_B, "draft": LINER_DRAFT},
             "mooring": "bollards 16 m centres + capstans", "kind": "fitting_out"},
            {"id": "B-B2", "name": "Service quay south of the slips",
             "rect": (-58.0, -280.0, -30.0, 40.0), "length_m": 320.0, "depth_m": 9.0,
             "ship_envelope": {"L": 140.0, "B": 18.0, "draft": 8.0},
             "mooring": "bollards", "kind": "repair"},
            {"id": "B-B3", "name": "Princess Graving Dock",
             "rect": (PRINCESS[0], PRINCESS[1], PRINCESS[0] + PRINCESS[3],
                      PRINCESS[1] + PRINCESS[2]),
             "length_m": 243.8, "depth_m": 11.0,
             "ship_envelope": {"L": LINER_L, "B": LINER_B, "draft": LINER_DRAFT},
             "mooring": "docked on keel blocks", "kind": "dry_dock"},
        ],
    }
    return meta


# ------------------------------------------------------------------ helpers
def _quay_module():
    mb = MeshBuilder()
    maritime.quay_wall(mb, "X", 0.0, -12.0, 12.0, +1)
    return mb


def _run_frontage(R, fixed_x, y0, y1, rz=-90.0):
    L = 24.0
    n = max(1, int(round(abs(y1 - y0) / L)))
    step = (y1 - y0) / n
    for i in range(n):
        ym = y0 + step * (i + 0.5)
        R.place("B_quay24", fixed_x, ym, QUAY_Z, rz)


def _run_slip_x(R, fixed_y, x0, x1, rz=0.0):
    L = 24.0
    n = max(1, int(round(abs(x1 - x0) / L)))
    step = (x1 - x0) / n
    for i in range(n):
        xm = x0 + step * (i + 0.5)
        R.place("B_quay24", xm, fixed_y, QUAY_Z, rz)


def _railway(R):
    """Standard-gauge dock railway routed safely inland and along quays (no open water crossings)."""
    mb = MeshBuilder()
    # Main North-South spine line inland of slipway heads (x = 72.0, clears SLIP_X1 = 66.0)
    machinery.rail_track(mb, 72.0, -280.0, 72.0, 396.0, z=QUAY_Z)

    # Frontage lines north of slips (fitting-out quay): y = 186.0 to 396.0
    for x in (-22.0, -16.0):
        machinery.rail_track(mb, x, 186.0, x, 396.0, z=QUAY_Z)

    # Frontage lines south of slips (service quay): y = -290.0 to 32.0
    for x in (-22.0, -16.0):
        machinery.rail_track(mb, x, -290.0, x, 32.0, z=QUAY_Z)

    # Workshop and dock siding branches (all inland of slipways)
    machinery.rail_track(mb, 72.0, 210.0, 140.0, 210.0, z=QUAY_Z)
    machinery.rail_track(mb, 72.0, 250.0, 190.0, 250.0, z=QUAY_Z)
    machinery.rail_track(mb, 140.0, 250.0, 140.0, 300.0, z=QUAY_Z)
    machinery.rail_track(mb, 72.0, -60.0, 300.0, -60.0, z=QUAY_Z)
    machinery.rail_track(mb, 230.0, -60.0, 230.0, 120.0, z=QUAY_Z)

    R.define("B_rail", mb)
    R.place("B_rail", 0, 0, 0.0)

    for x, y in ((72, 236), (100, 250), (150, -60)):
        R.place("B_loco", x, y, QUAY_Z, 0)
    for i in range(6):
        R.place("B_wagon", 74 + i * 5.6, 253.0, QUAY_Z)


def _signs(R):
    mb = MeshBuilder()
    mp = P.wmap("X", 208.0, +1)
    bldg.sign_board(mb, mp, 25.0, 8.4, 12.0, 1.9, "sign_merrion")
    mp = P.wmap("X", 240.0, +1)
    bldg.sign_board(mb, mp, 23.0, 7.2, 5.6, 0.85, "sign_engine_shop")
    mp = P.wmap("X", 228.0, +1)
    bldg.sign_board(mb, mp, 25.0, 11.0, 3.8, 0.85, "sign_moulding_loft")
    mp = P.wmap("X", 188.0, +1)
    bldg.sign_board(mb, mp, 15.0, 6.6, 5.0, 0.80, "sign_sawmill")
    mp = P.wmap("X", 250.0, +1)
    bldg.sign_board(mb, mp, 8.0, 6.4, 5.4, 0.80, "sign_pump_house")
    mp = P.wmap("X", -23.0, +1)
    bldg.sign_board(mb, mp, 5.5, 5.4, 3.6, 0.85, "sign_time_office")
    R.define("B_signs", mb)
    R.place("B_signs", 0, 0, QUAY_Z)


def _surface_bands():
    return [
        (-30, -300, 66, 400, "setts"),
        (66, -300, 340, 260, "yard"),
        (66, 260, 340, 340, "flags"),
        (66, 340, 340, 400, "yard"),
    ]


def _life(R):
    """Ironworkers, carters and shipyard loose material."""
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
        "B_sleepers": lambda mb: L.sleeper_stack(mb, 0, 0, 0),
        "B_rails":    lambda mb: L.rail_stack(mb, 0, 0, 0),
        "B_drums":    lambda mb: L.oil_drums(mb, 0, 0, 0, seed=9),
        "B_puddle":   lambda mb: L.puddle(mb, 0, 0, 0, w=11.0, d=5.5),
    }
    for n, fn in protos.items():
        mb = MeshBuilder(); fn(mb); R.define(n, mb)

    for y in (72, 88, 100, 121, 148, 170, 210, 250, 300, -40, -120, -210):
        R.place("B_man", -8, y, QUAY_Z, (y * 13) % 360)
    for y in (96, 158, 232):
        R.place("B_men", 4, y, QUAY_Z, (y * 7) % 360)
    for x, y in ((80, 40), (96, -60), (120, 120), (150, 200), (200, 300), (250, 60)):
        R.place("B_man", x, y, QUAY_Z, (x * 3) % 360)
    for x, y, rz in ((30, 60, 90), (40, 140, 95), (90, 210, 20), (170, 320, 10), (240, 120, 200)):
        R.place("B_dray", x, y, QUAY_Z, rz)
    for x, y, rz in ((-10, 130, 90), (20, 190, 95), (70, -30, 20), (110, 250, 15)):
        R.place("B_cart", x, y, QUAY_Z, rz)
    for x, y, rz in ((252, 140, 0), (270, 140, 0)):
        R.place("B_planks", x, y, QUAY_Z, rz)
    for y in (200, 240, 280, 320, 360, -80, -140, -200):
        R.place("B_rope", -28, y, QUAY_Z)
    for x, y in ((100, 300), (220, 320)):
        R.place("B_coal", x, y, QUAY_Z)
    for x, y in ((234, 180), (234, 192)):
        R.place("B_sleepers", x, y, QUAY_Z, 0)
    for x, y in ((226, 180), (226, 192)):
        R.place("B_rails", x, y, QUAY_Z, 0)
    for x, y in ((150, 270), (190, 270)):
        R.place("B_drums", x, y, QUAY_Z)
    for x, y, rz in ((10, 20, 15), (100, 100, -25), (200, 220, 35)):
        R.place("B_puddle", x, y, QUAY_Z, rz)
