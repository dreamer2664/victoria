"""
port_a.py -- PORT OF ALDERMOUTH : major passenger & transatlantic shipping port.

MODELLED ON LIVERPOOL. The defining characteristics of Liverpool in 1889 that this
port reproduces (see HISTORICAL_EVIDENCE.md for the sourcing of each one):

  * a great tidal river frontage, with passengers embarking from a FLOATING LANDING
    STAGE reached by long canopied gangway bridges -- not from a fixed quay. This is
    the single most distinctive feature of Liverpool and it is what Ocean Steamships
    (1891) plate "Landing Stages at Liverpool" actually shows.
  * an enclosed / half-tide dock east of the frontage carrying the cargo trade,
    coal staithes and the railway goods lines.
  * a civic Custom House set back from the quay, and a hotel/office quarter of
    shipping-company offices behind the stage.
  * the dockside railway running the length of the quay, connecting the transit
    sheds and the passenger station.
  * coal bunkering performed from barges alongside, served by quay hoists.

Coordinates: X east, Y north, Z up, metres. Water surface z = 0, quay top z = +4.0.
"""
import math
from core import MeshBuilder, QUAY_Z, LINER_L, LINER_B, LINER_DRAFT
import bldg, maritime, machinery, portsite as site
import parts as P

NAME = "PORT OF ALDERMOUTH"
CODE = "A"

# ------------------------------------------------------------------ site plan
SITE = (-30.0, -300.0, 330.0, 430.0)          # land platform (x0,y0,x1,y1)
RIVER = (-460.0, -560.0, -30.0, 560.0)        # River Alde (west of the frontage)
DOCK = (-30.0, -200.0, 200.0, -60.0)          # Trafalgar Dock: half-tide basin,
                                              # open to the river on its west side
WATER_HOLES = [DOCK[:4]]

# The floating landing stage and the liner berths alongside it
STAGE = (-80.0, 30.0, -66.0, 240.0)           # pontoon x0,y0,x1,y1
BRIDGE_Y = (75.0, 195.0)
BERTH = (-106.0, 24.0, -80.0, 236.0)          # 180 m liner envelope + 4 m clearance all round


def build(R, coll, audit):
    """Define the port's modular assets, place them, and return runtime metadata."""

    # ================================================== prototypes (modular assets)
    R.define("A_quay24", _quay_module(), bevel=0.0)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 44, 46, floors=3, ground_h=5.0,
                                          h_floor=3.9, wall="stucco", bays=3.6,
                                          shopfront=False)
    R.define("A_terminal", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.custom_house(mb, 0, 0, 58, 32, storeys=3)
    R.define("A_customhouse", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 60, 26, h_eave=6.8, wall="brick_buff",
                                           open_side="S")
    R.define("A_baggage_hall", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 60, 24, h_eave=6.4, wall="brick_buff",
                                           open_side="S")
    R.define("A_transit_shed", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 34, 20, floors=4, hoist_side="S",
                                        hoist_bays=(1, 4))
    R.define("A_warehouse_4", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 32, 20, floors=3, wall="brick_buff",
                                        roof="hip", hoist_side="S", hoist_bays=(1, 3))
    R.define("A_warehouse_3", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.warehouse(mb, 0, 0, 40, 22, floors=3, hoist_side="E",
                                        hoist_bays=(2,))
    R.define("A_warehouse_wide", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.station_shed(mb, 0, 0, 72, 22, tracks=2)
    R.define("A_station", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 72, 16, floors=4, bays=3.0)
    R.define("A_office_row", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 56, 16, floors=3, bays=3.2)
    R.define("A_office_row2", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 18, 13, floors=2, ground_h=4.0,
                                           h_floor=3.2, bays=3.0, shopfront=True)
    R.define("A_shop_small", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 16, 12, floors=2, ground_h=3.9,
                                           h_floor=3.1, bays=3.4, shopfront=True,
                                           wall="brick_soot")
    R.define("A_chandlery", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 40, 20, floors=3, wall="sandstone",
                                           bays=3.4, shopfront=False)
    R.define("A_harbour_offices", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.time_office(mb, 0, 0, 10, 7)
    R.define("A_gatehouse", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 24, 118, h_eave=7.2, wall="brick_soot",
                                           open_side="W", bay=5.4)
    R.define("A_dock_shed", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 40, 26, floors=5, ground_h=5.2,
                                           h_floor=3.8, wall="sandstone", bays=3.4,
                                           shopfront=False)
    R.define("A_hotel", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.office_block(mb, 0, 0, 46, 14, floors=3, ground_h=3.9,
                                           h_floor=3.3, wall="brick_soot", bays=2.9)
    R.define("A_terrace", mb, bevel=0.02)

    mb = MeshBuilder(); bldg.transit_shed(mb, 0, 0, 20, 52, h_eave=6.0, wall="brick_soot",
                                           open_side="W", bay=5.0)
    R.define("A_goods_shed", mb, bevel=0.02)

    mb = MeshBuilder()                     # 20 m perimeter boundary wall of the estate
    mb.add_box(-10, -0.30, QUAY_Z - 0.1, 10, 0.30, QUAY_Z + 3.2, "brick_soot")
    mb.add_box(-10, -0.42, QUAY_Z + 3.2, 10, 0.42, QUAY_Z + 3.45, "granite")
    for i in range(6):
        mb.add_box(-10 + i * 3.4, -0.16, QUAY_Z + 3.0, -9.6 + i * 3.4, 0.16,
                   QUAY_Z + 3.9, "brick_soot")
    R.define("A_boundary_wall", mb, bevel=0.0)

    mb = MeshBuilder()                     # stacked imported timber
    for k in range(7):
        mb.add_box(0, 0, k * 0.26, 8.0, 2.2, k * 0.26 + 0.24, "timber")
    for k in range(4):
        mb.add_box(0.2, 2.3, k * 0.26, 7.8, 4.4, k * 0.26 + 0.24, "timber")
    R.define("A_timber", mb)

    # --- the floating landing stage and its bridges
    mb = MeshBuilder()
    maritime.pontoon(mb, STAGE[0], STAGE[1], STAGE[2], STAGE[3])
    R.define("A_landing_stage", mb, bevel=0.0)

    mb = MeshBuilder()
    maritime.gangway_bridge(mb, -30.0, 0.0, QUAY_Z, -66.0, 1.5, width=3.8)
    R.define("A_gangway_bridge", mb, bevel=0.0)

    # --- small units that are instanced many times
    mb = MeshBuilder(); maritime.bollard(mb, 0, 0, 0); R.define("A_bollard", mb)
    mb = MeshBuilder(); maritime.capstan(mb, 0, 0, 0); R.define("A_capstan", mb)
    mb = MeshBuilder(); machinery.hydraulic_crane(mb, 0, 0, 0); R.define("A_crane", mb)
    mb = MeshBuilder(); machinery.steam_crane(mb, 0, 0, 0); R.define("A_steamcrane", mb)
    mb = MeshBuilder(); machinery.coal_hoist(mb, 0, 0, 0); R.define("A_coalhoist", mb)
    mb = MeshBuilder(); machinery.coal_staithe(mb, 0, 0, 40, 9, z=0.0); R.define("A_staithe", mb)
    mb = MeshBuilder(); machinery.coal_barge(mb, 0, 0, 0); R.define("A_barge", mb)
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

    # ================================================== quay walls
    _quays(R)

    # ================================================== buildings
    R.place("A_terminal",       2,  40)
    R.place("A_baggage_hall",   2,  92)
    R.place("A_customhouse",    2, 126)
    R.place("A_transit_shed",   2, 166)
    R.place("A_warehouse_4",    2, 196)
    R.place("A_warehouse_3",   40, 196)
    R.place("A_station",       80,  36)
    R.place("A_office_row",    80,  66)
    R.place("A_office_row2",   80,  90)
    R.place("A_warehouse_wide", 80, 116)
    R.place("A_warehouse_3",  126, 116)
    R.place("A_shop_small",    80, 148)
    R.place("A_chandlery",    100, 148)
    R.place("A_harbour_offices", 126, 148)
    R.place("A_gatehouse",    170, 150)

    # --- north / inland quarter: hotel, terraces, goods sheds behind the estate wall
    R.place("A_terrace",        2, 250)
    R.place("A_terrace",       52, 250)
    R.place("A_terrace",      102, 250)
    R.place("A_hotel",        152, 250)
    R.place("A_goods_shed",   240, 230)
    R.place("A_goods_shed",   266, 230)
    R.place("A_warehouse_3",  206, 230)
    R.place("A_warehouse_4",  176, 120)
    R.place("A_hotel",        226, 116)
    R.place("A_terrace",      226, 150)
    R.place("A_terrace",      226, 168)
    R.place("A_goods_shed",   276, 120)
    R.place("A_warehouse_wide", 276, 40)
    R.place("A_warehouse_3",  276, 66)

    for a in [("A_terrace", 2, 250, 48, 264), ("A_terrace", 52, 250, 98, 264),
              ("A_terrace", 102, 250, 148, 264), ("A_hotel", 152, 250, 192, 276),
              ("A_goods_shed", 240, 230, 260, 282), ("A_goods_shed", 266, 230, 286, 282),
              ("A_warehouse_3", 206, 230, 238, 250),
              ("A_warehouse_4", 176, 120, 210, 140), ("A_hotel", 226, 116, 266, 142),
              ("A_terrace", 226, 150, 272, 164), ("A_terrace", 226, 168, 272, 182),
              ("A_goods_shed", 276, 120, 296, 172), ("A_warehouse_wide", 276, 40, 316, 62),
              ("A_warehouse_3", 276, 66, 308, 86)]:
        audit.add(a[0], a[1], a[2], a[3], a[4])

    R.place("A_boundary_wall", -10, -290)
    _boundary(R)
    _streets(R)
    R.place("A_timber", 0, -40)
    R.place("A_timber", 40, -40, 0, 90)
    R.place("A_timber", 230, -30)
    R.place("A_timber", 246, -30)
    R.place("A_timber", -6, 232, 0, 90)
    # working clutter across the open apron so it reads as a yard, not a car park
    for x, y in ((20, 10), (44, 10), (68, 10), (120, 100), (140, 60),
                 (200, 190), (170, 90), (30, 236), (250, 200)):
        R.place("A_cargo", x, y, QUAY_Z)
    for x, y in ((16, 20), (60, 190), (196, 20), (256, 24)):
        R.place("A_winch", x, y, QUAY_Z)

    R.place("A_dock_shed",    206, -192)
    R.place("A_warehouse_4",  240, -190)
    R.place("A_warehouse_3",  240, -164)
    R.place("A_warehouse_wide", 240, -136)

    for a in [("A_terminal", 2, 40, 46, 86), ("A_baggage_hall", 2, 92, 62, 118),
              ("A_customhouse", 2, 126, 60, 158), ("A_transit_shed", 2, 166, 62, 190),
              ("A_warehouse_4", 2, 196, 36, 216), ("A_warehouse_3", 40, 196, 72, 216),
              ("A_station", 80, 36, 152, 58), ("A_office_row", 80, 66, 152, 82),
              ("A_office_row2", 80, 90, 136, 106), ("A_warehouse_wide", 80, 116, 120, 138),
              ("A_warehouse_3", 126, 116, 158, 136), ("A_shop_small", 80, 148, 98, 161),
              ("A_chandlery", 100, 148, 116, 160), ("A_harbour_offices", 126, 148, 166, 168),
              ("A_dock_shed", 206, -192, 230, -74), ("A_warehouse_4", 240, -190, 274, -170)]:
        audit.add(a[0], a[1], a[2], a[3], a[4])

    # ================================================== the landing stage
    R.place("A_landing_stage", 0, 0)
    for by in BRIDGE_Y:
        R.place("A_gangway_bridge", 0, by)
    # shore end abutments for the bridges
    mb = MeshBuilder()
    for by in BRIDGE_Y:
        mb.add_box(-31.2, by - 3.0, 2.2, -29.4, by + 3.0, QUAY_Z, "granite")
        mb.add_box(-30.2, by - 3.2, QUAY_Z, -26.0, by + 3.2, QUAY_Z + 0.12, "plank")
    R.define("A_bridge_abutment", mb)
    for by in BRIDGE_Y:
        R.place("A_bridge_abutment", 0, 0)

    # ================================================== quay furniture
    _furniture(R)

    # ================================================== railway
    _railway(R)

    # ================================================== signs
    _signs(R)

    # ================================================== life
    _life(R)

    # ================================================== metadata for Roblox / docs
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
        "interactions": [
            {"id": "A-I1", "name": "Booking Office / Tickets", "pos": (24, 34),
             "type": "ticket_purchase", "radius": 4},
            {"id": "A-I2", "name": "Baggage Hall (desk / weigh)", "pos": (22, 90),
             "type": "baggage_checkin", "radius": 6},
            {"id": "A-I3", "name": "Customs Examination", "pos": (24, 120),
             "type": "customs", "radius": 6},
            {"id": "A-I4", "name": "Gangway Bridge (shore end) 1", "pos": (-28, 75),
             "type": "board_via_bridge", "radius": 4},
            {"id": "A-I5", "name": "Gangway Bridge (shore end) 2", "pos": (-28, 195),
             "type": "board_via_bridge", "radius": 4},
            {"id": "A-I6", "name": "Landing Stage Deck", "pos": (-73, 130),
             "type": "spawn_passenger", "radius": 10},
            {"id": "A-I7", "name": "Ship Brow", "pos": (-80, 130),
             "type": "board_ship", "radius": 3},
            {"id": "A-I8", "name": "Mooring bollards (berth 1)", "pos": (-82, 60),
             "type": "mooring", "radius": 3},
            {"id": "A-I9", "name": "Coal Staithe / Hoist", "pos": (100, -54),
             "type": "coal_bunkering", "radius": 6},
            {"id": "A-I10", "name": "Cargo Shed Door (dock)", "pos": (204, -140),
             "type": "cargo_work", "radius": 5},
            {"id": "A-I11", "name": "Railway Platform", "pos": (116, 48),
             "type": "train_board", "radius": 6},
            {"id": "A-I12", "name": "Dock Gate / Time Office", "pos": (170, 150),
             "type": "worker_gate", "radius": 4},
        ],
        "paths": {
            "passenger": [[(-28.0, 75.0), (2.0, 75.0), (24.0, 60.0), (24.0, 34.0)],
                          [(-28.0, 195.0), (-6.0, 195.0), (-6.0, 120.0), (2.0, 120.0)]],
            "dockworker": [[(170.0, 150.0), (170.0, 60.0), (150.0, 20.0),
                            (60.0, -30.0), (16.0, -60.0)]],
            "vehicle": [[(170.0, 150.0), (170.0, 200.0), (100.0, 220.0), (2.0, 220.0)]],
        },
        "spawns": [{"id": "A-S1", "pos": (-73, 130), "role": "passenger"},
                   {"id": "A-S2", "pos": (170, 140), "role": "dockworker"},
                   {"id": "A-S3", "pos": (116, 48), "role": "rail_passenger"}],
    }
    return meta


# ------------------------------------------------------------------ helpers
def _quay_module():
    """A 24 m modular length of masonry quay, instanced along every water edge."""
    mb = MeshBuilder()
    maritime.quay_wall(mb, "X", 0.0, -12.0, 12.0, +1)
    return mb


def _quays(R):
    """Lay the modular quay runs around the river frontage and Trafalgar Dock."""
    # river frontage, north of the dock entrance  (y from -60 to 380)
    _run(R, "X", -30.0, -60.0, 380.0, +1)
    # river frontage, south of the dock entrance (y -260 .. -200)
    _run(R, "X", -30.0, -260.0, -200.0, +1)
    # dock north quay  (y = -60), x from -30 to 200
    _run(R, "X", -60.0, -30.0, 200.0, -1)
    # dock south quay  (y = -200)
    _run(R, "X", -200.0, -30.0, 200.0, +1)
    # dock east quay   (x = 200), y from -200 to -60
    _run(R, "Y", 200.0, -200.0, -60.0, -1)


def _run(R, axis, fixed, u0, u1, inward):
    """Place 24 m quay modules end to end along a straight edge."""
    L = 24.0
    n = max(1, int(round((u1 - u0) / L)))
    step = (u1 - u0) / n
    for i in range(n):
        u = u0 + step * (i + 0.5)
        if axis == "X":
            R.place("A_quay24", u - 0.0, fixed, 0.0, 0.0)
        else:
            R.place("A_quay24", fixed, u, 0.0, 90.0)


def _furniture(R):
    # bollards along the river frontage and the dock edges
    for y in range(-56, 376, 16):
        R.place("A_bollard", -27.5, y)
    for y in range(-196, -61, 16):
        R.place("A_bollard", 203.0, y)
        R.place("A_bollard", 57.0, y)
    for x in range(-26, 196, 16):
        R.place("A_bollard", x, -57.5)
        R.place("A_bollard", x, -202.5)

    # pontoon edge bollards (berth 1)
    for y in range(36, 236, 20):
        R.place("A_bollard", -78.5, y)

    # capstans and winches on the quay
    for y in range(-40, 360, 48):
        R.place("A_capstan", -14.0, y)
        R.place("A_winch", -22.0, y + 8)

    # hydraulic cranes along the river quay, spaced as working berths
    for y in range(-30, 370, 40):
        R.place("A_crane", -24.0, y, QUAY_Z, 90.0)
    # steam cranes + coal hoists on the dock quays
    for x in range(-20, 180, 34):
        R.place("A_coalhoist", x, -62.0, QUAY_Z - 0.9)
    for y in range(-190, -70, 30):
        R.place("A_steamcrane", 196.0, y, QUAY_Z, 180.0)

    # coal staithe along the dock north quay
    R.place("A_staithe", 70.0, -56.0, QUAY_Z)

    # gas lamps along the quay and streets
    for y in range(-50, 370, 26):
        R.place("A_lamp", -8.0, y)
    for x in range(0, 200, 26):
        R.place("A_lamp", x, -46.0)
    for y in range(20, 220, 24):
        R.place("A_lamp", 74.0, y)
    for y in range(20, 220, 24):
        R.place("A_lamp", 160.0, y)

    # telegraph poles + overhead lines
    for y in range(-20, 360, 40):
        R.place("A_pole", 68.0, y)
    for x in range(0, 170, 40):
        R.place("A_pole", x, -40.0)

    for x, y in ((-16, 70), (-16, 210), (66, 40), (196, -70), (74, 190)):
        R.place("A_fingerpost", x, y)

    # cargo on the quays and in the sheds
    for x, y in ((150, -70), (120, -80), (34, 186), (66, 130), (196, -100)):
        R.place("A_cargo", x, y, QUAY_Z)
    for i in range(6):
        R.place("A_gully", -20 + i * 2, 30 + i * 55, QUAY_Z + 0.02)


def _railway(R):
    """The dockside railway: tracks are built as one-off geometry (they are long,
    low-poly ribbons) rather than instanced modules."""
    mb = MeshBuilder()
    # three tracks along the river quay
    for i, x in enumerate((-22.0, -16.0, -10.0)):
        machinery.rail_track(mb, x, -250.0, x, 372.0, z=QUAY_Z)
    # branch east into the station throat
    machinery.rail_track(mb, -16.0, 44.0, 80.0, 44.0, z=QUAY_Z)
    machinery.rail_track(mb, -16.0, 52.0, 80.0, 52.0, z=QUAY_Z)
    # tracks through the station shed (into the far end)
    for y in (42.0, 52.0):
        machinery.rail_track(mb, 152.0, y, 200.0, y, z=QUAY_Z)
    # goods lines down to the dock quays
    machinery.rail_track(mb, -10.0, -60.0, -10.0, -200.0, z=QUAY_Z)
    machinery.rail_track(mb, -10.0, -60.0, 190.0, -64.0, z=QUAY_Z)
    machinery.rail_track(mb, 60.0, -64.0, 60.0, -200.0, z=QUAY_Z)
    # rail along the coal staithe
    machinery.rail_track(mb, 70.0, -52.0, 110.0, -52.0, z=QUAY_Z + 3.0)
    R.define("A_rail", mb)

    for x, y, rz in ((120, 44, 0), (86, 43, 0), (60, 52, 180), (150, 52, 0)):
        R.place("A_loco", x, y, QUAY_Z, rz)
    for i in range(7):
        R.place("A_wagon", 84 + i * 6.0, 47.6, QUAY_Z)
    for i in range(5):
        R.place("A_van", 40 + i * 6.0, -66.0, QUAY_Z, 90)
    for i in range(4):
        R.place("A_wagon", 74 + i * 5.6, -52.0, QUAY_Z + 3.0)
    R.place("A_bufferstop", -24.0, -246.0, QUAY_Z)
    R.place("A_bufferstop", -18.0, -246.0, QUAY_Z)
    R.place("A_bufferstop", -12.0, -246.0, QUAY_Z)


def _signs(R):
    """Painted signage, fixed to the buildings that carry it."""
    mb = MeshBuilder()
    mp = P.wmap("X", 40.0, +1)          # terminal's south elevation at y = 40
    bldg.sign_board(mb, mp, 24.0, 12.6, 7.5, 1.55, "sign_ravenna_line")
    mp2 = P.wmap("X", 40.0, +1)
    bldg.sign_board(mb, mp2, 24.0, 9.4, 6.4, 1.45, "sign_albion_line")
    # Custom House portico
    mp3 = P.wmap("X", 124.0, +1)
    bldg.sign_board(mb, mp3, 31.0, 11.0, 5.0, 0.85, "sign_custom_house")
    # Harbour Board over the gatehouse
    mp4 = P.wmap("X", 148.0, +1)
    bldg.sign_board(mb, mp4, 8.0, 5.6, 5.2, 1.30, "sign_harbour_board")
    # baggage hall
    mp5 = P.wmap("X", 92.0, +1)
    bldg.sign_board(mb, mp5, 30.0, 5.4, 4.2, 0.80, "sign_no1_shed")
    R.define("A_signs", mb)
    R.place("A_signs", 0, 0)


def _boundary(R):
    """Estate boundary wall: keeps the public out and the working dock a working dock."""
    L = 20.0
    for x in range(-10, 331, 20):                      # north edge
        R.place("A_boundary_wall", x, 430)
    for x in range(-10, 331, 20):                      # south edge
        R.place("A_boundary_wall", x, -300)
    for y in range(-290, 430, 20):                     # east edge
        R.place("A_boundary_wall", 330, y, 0, 90)


def _streets(R):
    """Kerbed granite pavements and drainage channels give the estate a real street
    layout instead of a paved apron."""
    mb = MeshBuilder()
    Z = QUAY_Z

    def pavement(x0, y0, x1, y1):
        mb.add_box(x0, y0, Z, x1, y1, Z + 0.16, "granite", top="granite")
        # kerb edge + channel along the road side
        mb.add_box(x0, y0 - 0.30, Z - 0.02, x1, y0, Z + 0.18, "granite")

    # front of the river frontage buildings
    pavement(0.0, 34.0, 62.0, 38.5)
    pavement(78.0, 30.0, 154.0, 34.5)
    pavement(0.0, 220.0, 200.0, 224.0)
    # Trafalgar Street, running north between the two building rows
    pavement(72.0, 20.0, 76.0, 224.0)
    pavement(154.0, 30.0, 158.0, 224.0)
    # dock road along the north quay of Trafalgar Dock
    pavement(-10.0, -56.0, 200.0, -52.0)
    # east quay pavement
    pavement(224.0, -196.0, 228.0, -70.0)
    # inland street north of the passenger group
    pavement(0.0, 244.0, 200.0, 248.0)
    R.define("A_streets", mb)
    R.place("A_streets", 0, 0)


# ------------------------------------------------------------------ surfaces
def _surface_bands():
    """The estate is not one material.

    The frontage is granite setts because it carries iron-shod wheels and
    railway metals; the yards behind are compacted earth and gravel; the
    forecourts of the public buildings are big stone flags. A single uniform
    apron across 790 x 1120 m is the biggest give-away in a port model.
    """
    B = []
    # frontage: setts along the whole waterfront
    B.append((-30, -300, 0, 430, "setts"))
    # north-east yard
    B.append((0, 190, 330, 430, "yard"))
    # terminal forecourt + station approach + custom house court (flags)
    B.append((0, 20, 72, 124, "flags"))
    B.append((0, 124, 66, 162, "flags"))
    B.append((72, 124, 330, 190, "yard"))
    # working yard between the forecourts and the north-east yard
    B.append((72, 20, 330, 124, "yard"))
    # south yard down to Trafalgar Dock coping
    B.append((0, -60, 330, 20, "yard"))
    B.append((0, -300, 330, -60, "yard"))
    return B


# ------------------------------------------------------------------ life
def _life(R):
    """People, drays, handcarts and loose cargo.

    Placement is not random scatter: men stand where work happens (at the
    gangway, at the shed doors, at the crane feet), carts stand where they would
    be loaded, and rope sits at the bollards because that is where it is used.
    """
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

    # --- men along the working quay and at the public buildings
    for x, y, rz in ((4, 40, 90), (7, 96, 80), (2, 150, 100), (10, 200, 70),
                     (26, 58, 200), (34, 74, 180), (52, 30, 160), (64, 118, 210),
                     (96, 60, 250), (120, 60, 280), (150, 100, 300), (44, 190, 120),
                     (86, 200, 200), (200, 90, 20), (240, 130, 40)):
        R.place("A_man", x, y, QUAY_Z, rz)
    for x, y, rz in ((12, 88, 100), (30, 44, 190), (100, 130, 250)):
        R.place("A_men", x, y, QUAY_Z, rz)
    # --- carts where goods are handled
    for x, y, rz in ((14, 110, 90), (20, 176, 95), (48, 140, 88), (206, 120, 20),
                     (246, 200, 15), (100, 30, 180)):
        R.place("A_dray", x, y, QUAY_Z, rz)
    for x, y, rz in ((-6, 60, 90), (0, 132, 92), (56, 170, 100), (208, 100, 20),
                     (30, 210, 120), (110, 128, 250)):
        R.place("A_handcart", x, y, QUAY_Z, rz)
    # --- loose cargo at the shed doors and on the apron
    for x, y in ((-4, 84), (-2, 168), (44, 128), (58, 196), (208, 148), (252, 168),
                 (14, 186), (120, 140)):
        R.place("A_sacks", x, y, QUAY_Z, (x * 7) % 360)
    for x, y in ((-8, 100), (40, 150), (204, 166), (250, 214), (64, 132)):
        R.place("A_barrels", x, y, QUAY_Z, (y * 5) % 360)
    for x, y in ((-22, 52), (-22, 96), (-22, 140), (-22, 196), (-22, 240),
                 (66, 40), (66, 180), (66, 300)):
        R.place("A_rope", x, y, QUAY_Z + 0.02)
    for x, y, rz in ((8, 152, 0), (48, 162, 0), (210, 160, 90), (244, 236, 90)):
        R.place("A_planks", x, y, QUAY_Z, rz)
    for x, y in ((16, 146), (52, 124), (212, 110), (238, 246)):
        R.place("A_bales", x, y, QUAY_Z, (x * 3) % 360)
    for x, y, rz in ((2, 118, 20), (46, 240, 120), (206, 190, 10), (256, 130, 200)):
        R.place("A_ladder", x, y, QUAY_Z, rz)
    # --- permanent-way material and standing water along the running lines
    for x, y, rz in ((-10, 24, 0), (-10, 186, 0), (46, 8, 90), (188, 16, 0)):
        R.place("A_sleepers", x, y, QUAY_Z, rz)
    for x, y, rz in ((-12, 300, 0), (30, -240, 90), (150, 240, 0)):
        R.place("A_rails", x, y, QUAY_Z, rz)
    for x, y in ((6, 132), (52, 168), (204, 124), (250, 200)):
        R.place("A_drums", x, y, QUAY_Z, (x * 3) % 360)
    for x, y, rz in ((-8, 150, 4), (24, -120, -3), (70, 60, 6), (120, 200, -5),
                     (200, 60, 3), (60, 300, -7), (16, -250, 5), (170, -180, -4)):
        R.place("A_puddle", x, y, QUAY_Z, rz)
    # --- coal on the staithe
    for x, y in ((70, -60), (96, -66), (150, -62)):
        R.place("A_coalheap", x, y, QUAY_Z)
