"""
port_a.py -- Port A layout: Aldermouth Liner Terminal & Trafalgar Dock (c. 1889).
GENERATION II — OPERATION VICTORIA (PERICLES-II)

Historical Basis:
  * Mersey Docks & Harbour Board deep-water ocean liner passenger terminal
  * Prince's Landing Stage floating pontoon & canopied articulated gangway bridges
  * Non-tidal impounded commercial basin (Trafalgar Dock) entered via lock
  * Jesse Hartley hydraulic accumulator tower & Armstrong hydraulic portal cranes
  * Hydraulic wrought-iron swing bridge crossing lock entrance
"""
import math
from core import MeshBuilder, QUAY_Z, WATER_Z, DOCK_BED_Z
import parts as P
import bldg
import maritime
import machinery
import portsite as site

NAME = "Aldermouth"
CODE = "A"

# ------------------------------------------------------------------ boundaries
SITE = (-30.0, -260.0, 300.0, 400.0)
RIVER = (-460.0, -560.0, -30.0, 560.0)
DOCK = (-30.0, -200.0, 200.0, -60.0)
WATER_HOLES = [DOCK]

# The Prince's Landing Stage (Liverpool model): floating pontoon in the river
STAGE = (-84.0, 36.0, -66.0, 240.0)
BRIDGE_Y = [75.0, 195.0]

LINER_L = 166.0
LINER_B = 18.0
LINER_DRAFT = 6.5
BERTH = (-84.0, 36.0, -66.0, 240.0)


# ------------------------------------------------------------------ build
def build(R, coll, audit):
    # ================================================== prototypes
    R.define("A_quay24", _quay_module())

    # Hydraulic swing bridge over lock entrance
    mb = MeshBuilder()
    maritime.swing_bridge(mb, -30.0, -130.0, z_quay=QUAY_Z, length=32.0, width=6.5, angle_deg=0.0)
    R.define("A_swing_bridge", mb, bevel=0.0)

    # Hartley hydraulic accumulator tower
    mb = MeshBuilder()
    bldg.accumulator_tower(mb, 0, 0, 10.0, 10.0, h_tower=26.0, wall="brick_red", trim="sandstone")
    R.define("A_accumulator_tower", mb, bevel=0.02)

    # Armstrong hydraulic portal crane
    mb = MeshBuilder()
    machinery.armstrong_portal_crane(mb, 0, 0, z=0.0)
    R.define("A_portal_crane", mb)

    # Dray cart
    mb = MeshBuilder()
    machinery.dray_cart(mb, 0, 0, z=0.0)
    R.define("A_dray_cart", mb)

    # Buildings
    mb = MeshBuilder()
    bldg.custom_house(mb, 0, 0, 58, 32, storeys=3, wall="sandstone")
    R.define("A_customhouse", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.warehouse(mb, 0, 0, 44, 46, floors=4, ground_h=4.6, h_floor=3.6,
                   wall="brick_buff", trim="sandstone", roof="hip", pitch=32,
                   hoist_side="W", hoist_bays=(1, 3))
    R.define("A_terminal", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.transit_shed(mb, 0, 0, 60, 26, h_eave=7.0, wall="brick_buff", open_side="S")
    R.define("A_baggage_hall", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.transit_shed(mb, 0, 0, 60, 24, h_eave=6.4, wall="brick_buff", open_side="S")
    R.define("A_transit_shed", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.warehouse(mb, 0, 0, 34, 20, floors=4, hoist_side="S", hoist_bays=(1, 4))
    R.define("A_warehouse_4", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.warehouse(mb, 0, 0, 32, 20, floors=3, wall="brick_buff", roof="hip",
                   hoist_side="S", hoist_bays=(1, 3))
    R.define("A_warehouse_3", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.warehouse(mb, 0, 0, 40, 22, floors=3, hoist_side="E", hoist_bays=(2,))
    R.define("A_warehouse_wide", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.station_shed(mb, 0, 0, 72, 22, tracks=2)
    R.define("A_station", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 72, 16, floors=4, bays=3.0)
    R.define("A_office_row", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 56, 16, floors=3, bays=3.2)
    R.define("A_office_row2", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 18, 13, floors=2, ground_h=4.0, h_floor=3.2, bays=3.0, shopfront=True)
    R.define("A_shop_small", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 16, 12, floors=2, ground_h=3.9, h_floor=3.1, bays=3.4, shopfront=True, wall="brick_soot")
    R.define("A_chandlery", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 40, 20, floors=3, wall="sandstone", bays=3.4, shopfront=False)
    R.define("A_harbour_offices", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.time_office(mb, 0, 0, 10, 7)
    R.define("A_gatehouse", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.transit_shed(mb, 0, 0, 24, 118, h_eave=7.2, wall="brick_soot", open_side="W", bay=5.4)
    R.define("A_dock_shed", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 40, 26, floors=5, ground_h=5.2, h_floor=3.8, wall="sandstone", bays=3.4, shopfront=False)
    R.define("A_hotel", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.office_block(mb, 0, 0, 46, 14, floors=3, ground_h=3.9, h_floor=3.3, wall="brick_soot", bays=2.9)
    R.define("A_terrace", mb, bevel=0.02)

    mb = MeshBuilder()
    bldg.transit_shed(mb, 0, 0, 20, 52, h_eave=6.0, wall="brick_soot", open_side="W", bay=5.0)
    R.define("A_goods_shed", mb, bevel=0.02)

    # Boundary wall defined at base z = 0.0
    mb = MeshBuilder()
    mb.add_box(-10, -0.30, -0.1, 10, 0.30, 3.2, "brick_soot")
    mb.add_box(-10, -0.42, 3.2, 10, 0.42, 3.45, "granite")
    for i in range(6):
        mb.add_box(-10 + i * 3.4, -0.16, 3.0, -9.6 + i * 3.4, 0.16, 3.9, "brick_soot")
    R.define("A_boundary_wall", mb, bevel=0.0)

    # Stacked timber
    mb = MeshBuilder()
    for k in range(7):
        mb.add_box(0, 0, k * 0.26, 8.0, 2.2, k * 0.26 + 0.24, "timber")
    for k in range(4):
        mb.add_box(0.2, 2.3, k * 0.26, 7.8, 4.4, k * 0.26 + 0.24, "timber")
    R.define("A_timber", mb)

    # Floating landing stage and bridges
    mb = MeshBuilder()
    maritime.pontoon(mb, STAGE[0], STAGE[1], STAGE[2], STAGE[3])
    R.define("A_landing_stage", mb, bevel=0.0)

    mb = MeshBuilder()
    maritime.gangway_bridge(mb, -30.0, 0.0, QUAY_Z, -66.0, 1.5, width=3.8)
    R.define("A_gangway_bridge", mb, bevel=0.0)

    # Small craft boat landing steps
    mb = MeshBuilder()
    maritime.boat_steps(mb, "Y", -30.0, 50.0, 56.0, inward=+1, z_quay=QUAY_Z, z_water=WATER_Z)
    R.define("A_boat_steps", mb)

    # Dockside equipment
    mb = MeshBuilder(); maritime.bollard(mb, 0, 0, 0); R.define("A_bollard", mb)
    mb = MeshBuilder(); maritime.capstan(mb, 0, 0, 0); R.define("A_capstan", mb)
    mb = MeshBuilder(); machinery.hydraulic_crane(mb, 0, 0, 0); R.define("A_crane", mb)
    mb = MeshBuilder(); machinery.steam_crane(mb, 0, 0, 0); R.define("A_steamcrane", mb)
    mb = MeshBuilder(); machinery.coal_hoist(mb, 0, 0, 0); R.define("A_coalhoist", mb)
    mb = MeshBuilder(); machinery.coal_staithe(mb, 0, 0, 40, 9, z=0.0); R.define("A_staithe", mb)
    mb = MeshBuilder(); machinery.wagon(mb, 0, 0, 0, kind="mineral"); R.define("A_wagon", mb)
    mb = MeshBuilder(); machinery.wagon(mb, 0, 0, 0, kind="van"); R.define("A_van", mb)
    mb = MeshBuilder(); machinery.tank_loco(mb, 0, 0, 0); R.define("A_loco", mb)
    mb = MeshBuilder(); machinery.gas_lamp(mb, 0, 0, 0); R.define("A_lamp", mb)
    mb = MeshBuilder(); machinery.telegraph_pole(mb, 0, 0, 0); R.define("A_pole", mb)
    mb = MeshBuilder(); machinery.fingerpost(mb, 0, 0, 0); R.define("A_fingerpost", mb)
    mb = MeshBuilder(); machinery.winch(mb, 0, 0, 0); R.define("A_winch", mb)
    mb = MeshBuilder(); machinery.gangway(mb, 0, 0, 0, -2.5, 9.0); R.define("A_gangway", mb)
    mb = MeshBuilder(); machinery.drain_gully(mb, 0, 0, 0); R.define("A_gully", mb)
    mb = MeshBuilder(); machinery.cargo_stack(mb, 0, 0, 0, seed=3); R.define("A_cargo", mb)
    mb = MeshBuilder(); machinery.buffer_stop(mb, 0, 0, 0); R.define("A_bufferstop", mb)

    # ================================================== land + water
    mb = MeshBuilder()
    site.add_land(mb, SITE, WATER_HOLES, top=QUAY_Z, bottom=-4.0, surf=None)
    site.land_surface_bands(mb, _surface_bands(), WATER_HOLES, top=QUAY_Z)
    site.water(mb, [DOCK], z=0.0)
    site.water(mb, [RIVER], z=0.0)
    R.define("A_ground", mb)
    R.place("A_ground", 0, 0, 0.0)

    # ================================================== quay walls
    _quays(R)

    # ================================================== hydraulic infrastructure
    R.place("A_swing_bridge", 0, 0, 0.0)
    R.place("A_accumulator_tower", 24, -52, QUAY_Z)
    R.place("A_boat_steps", 0, 0, 0.0)

    # ================================================== buildings
    R.place("A_terminal",       2,  40, QUAY_Z)
    R.place("A_baggage_hall",   2,  92, QUAY_Z)
    R.place("A_customhouse",    2, 126, QUAY_Z)
    R.place("A_transit_shed",   2, 166, QUAY_Z)
    R.place("A_warehouse_4",    2, 196, QUAY_Z)
    R.place("A_warehouse_3",   40, 196, QUAY_Z)
    R.place("A_station",       80,  36, QUAY_Z)
    R.place("A_office_row",    80,  66, QUAY_Z)
    R.place("A_office_row2",   80,  90, QUAY_Z)
    R.place("A_warehouse_wide", 80, 116, QUAY_Z)
    R.place("A_warehouse_3",   126, 116, QUAY_Z)
    R.place("A_shop_small",    80, 148, QUAY_Z)
    R.place("A_chandlery",    100, 148, QUAY_Z)
    R.place("A_harbour_offices", 126, 148, QUAY_Z)
    R.place("A_gatehouse",    170, 148, QUAY_Z)

    R.place("A_hotel",        152, 250, QUAY_Z)
    R.place("A_terrace",        2, 250, QUAY_Z)
    R.place("A_terrace",       52, 250, QUAY_Z)
    R.place("A_terrace",      102, 250, QUAY_Z)
    R.place("A_goods_shed",   240, 230, QUAY_Z)
    R.place("A_goods_shed",   266, 230, QUAY_Z)
    R.place("A_warehouse_3",  206, 230, QUAY_Z)

    R.place("A_warehouse_4",  176, 120, QUAY_Z)
    R.place("A_hotel",        226, 116, QUAY_Z)
    R.place("A_terrace",      226, 150, QUAY_Z)
    R.place("A_terrace",      226, 168, QUAY_Z)
    R.place("A_goods_shed",   276, 120, QUAY_Z)
    R.place("A_warehouse_wide", 276, 40, QUAY_Z)
    R.place("A_warehouse_3",  276, 66, QUAY_Z)

    R.place("A_dock_shed",    206, -192, QUAY_Z)
    R.place("A_warehouse_4",  240, -190, QUAY_Z)
    R.place("A_warehouse_3",  240, -164, QUAY_Z)
    R.place("A_warehouse_wide", 240, -136, QUAY_Z)

    _boundary(R)
    _streets(R)

    # Port dressing
    R.place("A_timber", 0, -40, QUAY_Z)
    R.place("A_timber", 40, -40, QUAY_Z, 90)
    R.place("A_timber", 230, -30, QUAY_Z)
    R.place("A_timber", 246, -30, QUAY_Z)
    R.place("A_timber", -6, 232, QUAY_Z, 90)

    for x, y in ((20, 10), (44, 10), (68, 10), (120, 100), (140, 60),
                 (200, 190), (170, 90), (30, 236), (250, 200)):
        R.place("A_cargo", x, y, QUAY_Z)
    for x, y in ((16, 20), (60, 190), (196, 20), (256, 24)):
        R.place("A_winch", x, y, QUAY_Z)

    # Dray carts
    R.place("A_dray_cart", 14.0, 30.0, QUAY_Z, 15.0)
    R.place("A_dray_cart", 48.0, 110.0, QUAY_Z, -40.0)
    R.place("A_dray_cart", 110.0, 130.0, QUAY_Z, 90.0)

    # Landing stage and bridges
    R.place("A_landing_stage", 0, 0, 0.0)
    for by in BRIDGE_Y:
        R.place("A_gangway_bridge", 0, by, 0.0)

    # Bridge abutments
    mb = MeshBuilder()
    for by in BRIDGE_Y:
        mb.add_box(-31.2, by - 3.0, 2.2, -29.4, by + 3.0, QUAY_Z, "granite")
        mb.add_box(-30.2, by - 3.2, QUAY_Z, -26.0, by + 3.2, QUAY_Z + 0.12, "plank")
    R.define("A_bridge_abutment", mb)
    for by in BRIDGE_Y:
        R.place("A_bridge_abutment", 0, 0, 0.0)

    _furniture(R)
    _railway(R)
    _signs(R)
    _life(R)

    meta = {
        "port": NAME, "code": CODE,
        "site": SITE, "water": {"river": RIVER, "dock": DOCK},
        "quay_z": QUAY_Z,
        "berths": [
            {"id": "A-B1", "name": "Trafalgar Landing Stage, West Face",
             "rect": BERTH, "length_m": 204.0, "depth_m": 11.0,
             "ship_envelope": {"L": LINER_L, "B": LINER_B, "draft": LINER_DRAFT},
             "mooring": "bollards on pontoon edge, 20 m centres; 2 headlines, 4 springs",
             "gangway_from": "pontoon deck", "kind": "passenger"},
            {"id": "A-B2", "name": "Trafalgar Landing Stage, East Berth (tender/steamer)",
             "rect": (-62.0, 42.0, -42.0, 152.0), "length_m": 110.0, "depth_m": 6.5,
             "ship_envelope": {"L": 100.0, "B": 14.0, "draft": 5.0},
             "mooring": "bollards on pontoon edge", "gangway_from": "pontoon deck",
             "kind": "passenger"},
            {"id": "A-B3", "name": "Trafalgar Dock, North Quay (cargo)",
             "rect": (68.0, -60.0, 200.0, -84.0), "length_m": 132.0, "depth_m": 9.0,
             "ship_envelope": {"L": 130.0, "B": 18.0, "draft": 8.0},
             "mooring": "bollards + capstans", "gangway_from": "quay", "kind": "cargo"},
            {"id": "A-B4", "name": "Trafalgar Dock, East Quay (cargo)",
             "rect": (178.0, -194.0, 200.0, -70.0), "length_m": 124.0, "depth_m": 9.0,
             "ship_envelope": {"L": 116.0, "B": 17.0, "draft": 8.0},
             "mooring": "bollards", "gangway_from": "quay", "kind": "cargo"},
        ],
        "gangways": [
            {"id": "A-G1", "type": "canopied gangway bridge", "y": BRIDGE_Y[0],
             "from": (-30.0, BRIDGE_Y[0]), "to": (-66.0, BRIDGE_Y[0]),
             "walk_width_m": 3.8, "slope": "shore 4.0 m -> pontoon 1.5 m"},
            {"id": "A-G2", "type": "canopied gangway bridge", "y": BRIDGE_Y[1],
             "from": (-30.0, BRIDGE_Y[1]), "to": (-66.0, BRIDGE_Y[1]),
             "walk_width_m": 3.8, "slope": "shore 4.0 m -> pontoon 1.5 m"},
            {"id": "A-G3", "type": "ship brow (boarding)", "at": "pontoon west face",
             "pos": (-80.0, 130.0), "length_m": 9.0, "walk_width_m": 1.6},
        ],
    }
    return meta


# ------------------------------------------------------------------ helpers
def _quay_module():
    mb = MeshBuilder()
    maritime.quay_wall(mb, "X", 0.0, -12.0, 12.0, +1)
    return mb


def _quays(R):
    """Place modular quays facing correctly outward toward water."""
    # River frontage, north of dock entrance: x = -30.0, y from -60 to 380 (water at -X, land at +X)
    _run_frontage(R, -30.0, -60.0, 380.0, rz=-90.0)
    # River frontage, south of dock entrance: x = -30.0, y from -260 to -200 (water at -X, land at +X)
    _run_frontage(R, -30.0, -260.0, -200.0, rz=-90.0)
    # Trafalgar Dock North Quay: y = -60.0, x from -30 to 200 (water at -Y, land at +Y)
    _run_dock_x(R, -60.0, -30.0, 200.0, rz=0.0)
    # Trafalgar Dock South Quay: y = -200.0, x from -30 to 200 (water at +Y, land at -Y)
    _run_dock_x(R, -200.0, -30.0, 200.0, rz=180.0)
    # Trafalgar Dock East Quay: x = 200.0, y from -200 to -60 (water at -X, land at +X)
    _run_frontage(R, 200.0, -200.0, -60.0, rz=-90.0)


def _run_frontage(R, fixed_x, y0, y1, rz=-90.0):
    L = 24.0
    n = max(1, int(round(abs(y1 - y0) / L)))
    step = (y1 - y0) / n
    for i in range(n):
        ym = y0 + step * (i + 0.5)
        R.place("A_quay24", fixed_x, ym, QUAY_Z, rz)


def _run_dock_x(R, fixed_y, x0, x1, rz=0.0):
    L = 24.0
    n = max(1, int(round(abs(x1 - x0) / L)))
    step = (x1 - x0) / n
    for i in range(n):
        xm = x0 + step * (i + 0.5)
        R.place("A_quay24", xm, fixed_y, QUAY_Z, rz)


def _furniture(R):
    for y in range(-56, 376, 16):
        R.place("A_bollard", -27.5, y, QUAY_Z)
    for y in range(-196, -61, 16):
        R.place("A_bollard", 197.5, y, QUAY_Z)
    for x in range(-26, 196, 16):
        R.place("A_bollard", x, -62.5, QUAY_Z)
        R.place("A_bollard", x, -197.5, QUAY_Z)

    for y in range(36, 236, 20):
        R.place("A_bollard", -83.5, y, 1.42)

    for y in range(-40, 360, 48):
        R.place("A_capstan", -14.0, y, QUAY_Z)
        R.place("A_winch", -22.0, y + 8, QUAY_Z)

    # Armstrong hydraulic portal cranes along river frontage (straddling railway)
    for y in range(-20, 360, 48):
        R.place("A_portal_crane", -20.0, y, QUAY_Z)

    for x in range(-10, 180, 38):
        R.place("A_coalhoist", x, -64.0, QUAY_Z)
    for y in range(-190, -70, 36):
        R.place("A_steamcrane", 192.0, y, QUAY_Z, 180.0)

    mb = MeshBuilder()
    machinery.coal_staithe(mb, 70, -58, 40, 9, z=0.0)
    R.define("A_staithe_run", mb)
    R.place("A_staithe_run", 0, 0, QUAY_Z)

    for y in range(-240, 380, 24):
        R.place("A_lamp", -8.0, y, QUAY_Z)
    for y in range(-240, 380, 36):
        R.place("A_pole", 72.0, y, QUAY_Z)


def _railway(R):
    """Dockside railway permanent way routed strictly on land and across swing bridge."""
    mb = MeshBuilder()
    # Three lines along River Quay (North of lock): y = -50 to y = 372
    for x in (-22.0, -16.0, -10.0):
        machinery.rail_track(mb, x, -50.0, x, 372.0, z=QUAY_Z)
    # South of lock: y = -250 to y = -210 with buffer stops
    for x in (-22.0, -16.0, -10.0):
        machinery.rail_track(mb, x, -250.0, x, -210.0, z=QUAY_Z)

    # Track across swing bridge connecting North and South quays across lock entrance
    machinery.rail_track(mb, -22.0, -146.0, -22.0, -114.0, z=QUAY_Z)
    machinery.rail_track(mb, -22.0, -210.0, -22.0, -146.0, z=QUAY_Z)
    machinery.rail_track(mb, -22.0, -114.0, -22.0, -50.0, z=QUAY_Z)

    # Station throat branches
    machinery.rail_track(mb, -16.0, 44.0, 80.0, 44.0, z=QUAY_Z)
    machinery.rail_track(mb, -16.0, 52.0, 80.0, 52.0, z=QUAY_Z)
    for y in (42.0, 52.0):
        machinery.rail_track(mb, 152.0, y, 200.0, y, z=QUAY_Z)

    # Trafalgar Dock quayside lines (North Quay, East Quay, South Quay - strictly on land)
    machinery.rail_track(mb, -10.0, -52.0, 188.0, -52.0, z=QUAY_Z)
    machinery.rail_track(mb, 188.0, -52.0, 188.0, -208.0, z=QUAY_Z)
    machinery.rail_track(mb, -10.0, -208.0, 188.0, -208.0, z=QUAY_Z)

    # High-level coal line
    machinery.rail_track(mb, 70.0, -52.0, 110.0, -52.0, z=QUAY_Z + 3.0)

    R.define("A_rail", mb)
    R.place("A_rail", 0, 0, 0.0)

    for x, y, rz in ((120, 44, 0), (86, 43, 0), (60, 52, 180), (150, 52, 0)):
        R.place("A_loco", x, y, QUAY_Z, rz)
    for i in range(7):
        R.place("A_wagon", 84 + i * 6.0, 47.6, QUAY_Z)
    for i in range(5):
        R.place("A_van", 40 + i * 6.0, -52.0, QUAY_Z, 90)
    for i in range(4):
        R.place("A_wagon", 74 + i * 5.6, -52.0, QUAY_Z + 3.0)
    R.place("A_bufferstop", -22.0, -210.0, QUAY_Z)
    R.place("A_bufferstop", -16.0, -210.0, QUAY_Z)
    R.place("A_bufferstop", -10.0, -210.0, QUAY_Z)


def _signs(R):
    """Painted signage fixed cleanly to building entablatures without window overlap."""
    mb = MeshBuilder()
    mp = P.wmap("X", 40.0, +1)
    bldg.sign_board(mb, mp, 12.0, 3.8, 6.8, 1.1, "sign_ravenna_line")
    bldg.sign_board(mb, mp, 34.0, 3.8, 6.8, 1.1, "sign_albion_line")

    mp2 = P.wmap("X", 148.0, +1)
    bldg.sign_board(mb, mp2, 146.0, 4.2, 5.2, 1.1, "sign_harbour_board")

    mp3 = P.wmap("X", 92.0, +1)
    bldg.sign_board(mb, mp3, 32.0, 4.2, 5.4, 0.9, "sign_no1_shed")

    R.define("A_signs", mb)
    R.place("A_signs", 0, 0, QUAY_Z)


def _boundary(R):
    L = 20.0
    for x in range(-10, 331, 20):
        R.place("A_boundary_wall", x, 430, QUAY_Z)
    for x in range(-10, 331, 20):
        R.place("A_boundary_wall", x, -300, QUAY_Z)
    for y in range(-290, 430, 20):
        R.place("A_boundary_wall", 330, y, QUAY_Z, 90)


def _streets(R):
    mb = MeshBuilder()
    Z = QUAY_Z

    def pavement(x0, y0, x1, y1):
        mb.add_box(x0, y0, Z, x1, y1, Z + 0.16, "granite", top="flags")

    pavement(-14, 28, -6, 240)
    pavement(48, 28, 56, 240)
    pavement(74, 28, 78, 240)
    pavement(160, 28, 168, 240)
    pavement(-6, 28, 48, 38)
    pavement(-6, 218, 168, 226)
    pavement(-6, 86, 48, 92)
    pavement(-6, 118, 48, 126)
    pavement(-6, 158, 48, 166)
    pavement(78, 58, 160, 66)
    pavement(78, 82, 160, 90)
    pavement(78, 106, 160, 116)
    pavement(78, 138, 160, 148)

    for y in range(40, 220, 24):
        machinery.drain_gully(mb, -14.2, y, Z)
        machinery.drain_gully(mb, 47.8, y, Z)
        machinery.drain_gully(mb, 74.2, y, Z)
        machinery.drain_gully(mb, 159.8, y, Z)

    R.define("A_streets", mb)
    R.place("A_streets", 0, 0, 0.0)


def _surface_bands():
    return [
        (-30, -260,  70, 400, "setts"),
        ( 70, -260, 200, 400, "setts"),
        (200, -260, 300, 400, "puddle"),
    ]


def _life(R):
    """People, drays, handcarts and loose cargo."""
    from core import QUAY_Z
    import life as L

    prototypes = {
        "A_man":       lambda mb: L.workman(mb, 0, 0, 0),
        "A_men":       lambda mb: L.workman_pair(mb, 0, 0, 0),
        "A_dray":      lambda mb: L.dray(mb, 0, 0, 0),
        "A_handcart":  lambda mb: L.handcart(mb, 0, 0, 0),
        "A_sacks":     lambda mb: L.sack_pile(mb, 0, 0, 0, seed=5),
        "A_barrels":   lambda mb: L.barrel_group(mb, 0, 0, 0, seed=3),
        "A_rope":      lambda mb: L.rope_coil(mb, 0, 0, 0),
        "A_planks":    lambda mb: L.plank_stack(mb, 0, 0, 0),
        "A_bales":     lambda mb: L.bale_stack(mb, 0, 0, 0, seed=7),
        "A_ladder":    lambda mb: L.ladder(mb, 0, 0, 0),
        "A_coalheap":  lambda mb: L.coal_heap(mb, 0, 0, 0),
        "A_sleepers":  lambda mb: L.sleeper_stack(mb, 0, 0, 0),
        "A_rails":     lambda mb: L.rail_stack(mb, 0, 0, 0),
        "A_drums":     lambda mb: L.oil_drums(mb, 0, 0, 0, seed=4),
        "A_puddle":    lambda mb: L.puddle(mb, 0, 0, 0, w=9.0, d=4.5),
    }
    for name, fn in prototypes.items():
        mb = MeshBuilder(); fn(mb); R.define(name, mb)

    for x, y, rz in ((4, 40, 90), (7, 96, 80), (2, 150, 100), (10, 200, 70),
                     (26, 58, 200), (34, 74, 180), (52, 30, 160), (64, 118, 210),
                     (96, 60, 250), (120, 60, 280), (150, 100, 300), (44, 190, 120),
                     (86, 200, 200), (200, 90, 20), (240, 130, 40)):
        R.place("A_man", x, y, QUAY_Z, rz)
    for x, y, rz in ((12, 88, 100), (30, 44, 190), (100, 130, 250)):
        R.place("A_men", x, y, QUAY_Z, rz)
    for x, y, rz in ((14, 110, 90), (20, 176, 95), (48, 140, 88), (206, 120, 20),
                     (246, 200, 15), (100, 30, 180)):
        R.place("A_dray", x, y, QUAY_Z, rz)
    for x, y, rz in ((-20, 80, 90), (-18, 160, 85), (28, 44, 180), (130, 48, 270),
                     (210, -100, 10), (240, -180, 180)):
        R.place("A_handcart", x, y, QUAY_Z, rz)
    for x, y in ((18, 100), (38, 172), (210, 140), (248, 180)):
        R.place("A_sacks", x, y, QUAY_Z)
    for x, y in ((22, 120), (54, 180), (212, 160), (244, 160)):
        R.place("A_barrels", x, y, QUAY_Z)
    for x, y in ((-28, 60), (-28, 120), (-28, 180), (-28, 240), (-28, 300),
                 (198, -80), (198, -140), (198, -180)):
        R.place("A_rope", x, y, QUAY_Z)
    for x, y, rz in ((236, -24, 0), (252, -24, 0), (244, -14, 90)):
        R.place("A_planks", x, y, QUAY_Z, rz)
    for x, y in ((16, 140), (46, 110), (214, 100), (252, 130)):
        R.place("A_bales", x, y, QUAY_Z)
    for x, y in ((100, -48), (140, -48)):
        R.place("A_coalheap", x, y, QUAY_Z)
    for x, y, rz in ((194, 30, 0), (194, 20, 0)):
        R.place("A_sleepers", x, y, QUAY_Z, rz)
    for x, y, rz in ((186, 30, 0), (186, 20, 0)):
        R.place("A_rails", x, y, QUAY_Z, rz)
    for x, y in ((16, -20), (30, -20)):
        R.place("A_drums", x, y, QUAY_Z)
    for x, y, rz in ((-2, 130, 20), (40, 130, -10), (120, 200, 30), (240, 100, -20)):
        R.place("A_puddle", x, y, QUAY_Z, rz)
