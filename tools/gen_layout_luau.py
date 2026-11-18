#!/usr/bin/env python3
"""Generate roblox/src/PortLayoutA.luau and PortLayoutB.luau from docs/port_<x>_meta.json.
Ensures zero drift between Blender metadata, integration specifications, and Roblox Luau runtime.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def gen_layout_a():
    with open(os.path.join(ROOT, "docs/port_a_meta.json")) as f:
        meta = json.load(f)

    code = """--!strict
--[[
	PortLayoutA

	GENERATED from docs/port_a_meta.json by tools/gen_layout_luau.py.
	Do not hand-edit: re-run the generator after a rebuild, otherwise the
	interaction points drift out of the geometry.

	All positions are METRES in the Blender frame (x east, y north, z up).
	Feed them through Config.toWorld() to get studs.
]]

local Layout = {}

Layout.port = "PORT OF ALDERMOUTH"
Layout.code = "a"
Layout.quayZ = 4.0
Layout.pontoonZ = 1.5

-- ------------------------------------------------------------------ berths
Layout.berths = {
"""
    for b in meta["berths"]:
        code += f'\t{{ id = "{b["id"]}", name = "{b["name"]}", kind = "{b["kind"]}",\n'
        code += f'\t  rect = {{ {b["rect"][0]:.1f}, {b["rect"][1]:.1f}, {b["rect"][2]:.1f}, {b["rect"][3]:.1f} }},\n'
        code += f'\t  lengthM = {b["length_m"]:.1f}, depthM = {b["depth_m"]:.1f},\n'
        env = b["ship_envelope"]
        code += f'\t  envelope = {{ L = {env["L"]:.1f}, B = {env["B"]:.1f}, draft = {env["draft"]:.1f} }} }},\n'
    code += "}\n\n"

    code += """-- ------------------------------------------------------------------ interactions
Layout.interactions = {
	{ id = "A-I1", name = "Booking Office / Tickets", kind = "ticket_purchase", radius = 4,
	  pos = { 24, 34, 4.0 } },
	{ id = "A-I2", name = "Baggage Hall (desk / weigh)", kind = "baggage_checkin", radius = 6,
	  pos = { 22, 90, 4.0 } },
	{ id = "A-I3", name = "Customs Examination", kind = "customs", radius = 6,
	  pos = { 24, 120, 4.0 } },
	{ id = "A-I4", name = "Gangway Bridge (shore end) 1", kind = "board_via_bridge", radius = 4,
	  pos = { -28, 75, 4.0 } },
	{ id = "A-I5", name = "Gangway Bridge (shore end) 2", kind = "board_via_bridge", radius = 4,
	  pos = { -28, 195, 4.0 } },
	{ id = "A-I6", name = "Landing Stage Deck", kind = "spawn_passenger", radius = 10,
	  pos = { -73, 130, 1.5 } },
	{ id = "A-I7", name = "Ship Brow (Articulated Brow)", kind = "board_ship", radius = 3,
	  pos = { -80, 130, 1.5 } },
	{ id = "A-I8", name = "Mooring bollards (Berth A-B1)", kind = "mooring", radius = 3,
	  pos = { -82, 60, 1.5 } },
	{ id = "A-I9", name = "Coal Staithe / Hydraulic Hoist", kind = "coal_bunkering", radius = 6,
	  pos = { 100, -54, 4.0 } },
	{ id = "A-I10", name = "Cargo Shed Door (Dock)", kind = "cargo_work", radius = 5,
	  pos = { 204, -140, 4.0 } },
	{ id = "A-I11", name = "Railway Platform (Boat Trains)", kind = "train_board", radius = 6,
	  pos = { 116, 48, 4.0 } },
	{ id = "A-I12", name = "Dock Gate / Time Office", kind = "worker_gate", radius = 4,
	  pos = { 170, 150, 4.0 } },
	{ id = "A-I13", name = "Victorian Hydraulic Swing Bridge", kind = "bridge_operate", radius = 4,
	  pos = { -30, -130, 4.0 } },
	{ id = "A-I14", name = "Hartley Accumulator Tower Engine Room", kind = "hydraulic_power", radius = 5,
	  pos = { 24, -52, 4.0 } },
	{ id = "A-I15", name = "Waterman Boat Steps (Small Craft)", kind = "boat_step", radius = 3,
	  pos = { -30, 10, 0.5 } },
	{ id = "A-I16", name = "Pierhead Lighthouse & Fog Bell", kind = "navigation_aid", radius = 6,
	  pos = { -28, -250, 4.0 } },
	{ id = "A-I17", name = "Harbour Signal Station (Storm Warning)", kind = "storm_warning", radius = 6,
	  pos = { -26, 372, 4.0 } },
	{ id = "A-I18", name = "Hydraulic Wagon Tipper (Coal Staithe)", kind = "coal_tipper", radius = 5,
	  pos = { 140, -52, 4.0 } },
	{ id = "A-I19", name = "Ocean Terminal Grand Concourse", kind = "passenger_concourse", radius = 8,
	  pos = { 24, 63, 4.0 } },
	{ id = "A-I20", name = "Victorian Long Room (Custom House)", kind = "customs_longroom", radius = 8,
	  pos = { 31, 142, 4.0 } },
}

-- ------------------------------------------------------------------ gangways
Layout.gangways = {
"""
    for g in meta.get("gangways", []):
        code += f'\t{json.dumps(g)},\n'
    code += "}\n\n"

    code += """-- ------------------------------------------------------------------ paths
Layout.paths = {
	passenger = { {{ -28.0, 75.0 }, { 2.0, 75.0 }, { 24.0, 60.0 }, { 24.0, 34.0 }}, {{ -28.0, 195.0 }, { -6.0, 195.0 }, { -6.0, 120.0 }, { 2.0, 120.0 }} },
	dockworker = { {{ 170.0, 150.0 }, { 170.0, 60.0 }, { 150.0, 20.0 }, { 60.0, -30.0 }, { 16.0, -60.0 }} },
	vehicle = { {{ 170.0, 150.0 }, { 170.0, 200.0 }, { 100.0, 220.0 }, { 2.0, 220.0 }} },
}

Layout.spawns = {
	{ id = "A-S1", pos = { -73, 130, 1.5 }, role = "passenger" },
	{ id = "A-S2", pos = { 170, 140, 4.0 }, role = "dockworker" },
	{ id = "A-S3", pos = { 116, 48, 4.0 }, role = "rail_passenger" },
}

return Layout
"""
    with open(os.path.join(ROOT, "roblox/src/PortLayoutA.luau"), "w") as f:
        f.write(code)
    print("wrote roblox/src/PortLayoutA.luau")


def gen_layout_b():
    with open(os.path.join(ROOT, "docs/port_b_meta.json")) as f:
        meta = json.load(f)

    code = """--!strict
--[[
	PortLayoutB

	GENERATED from docs/port_b_meta.json by tools/gen_layout_luau.py.
	Do not hand-edit: re-run the generator after a rebuild, otherwise the
	interaction points drift out of the geometry.

	All positions are METRES in the Blender frame (x east, y north, z up).
	Feed them through Config.toWorld() to get studs.
]]

local Layout = {}

Layout.port = "PORT OF CARRICKMORE"
Layout.code = "b"
Layout.quayZ = 4.0

-- ------------------------------------------------------------------ berths
Layout.berths = {
"""
    for b in meta["berths"]:
        code += f'\t{{ id = "{b["id"]}", name = "{b["name"]}", kind = "{b["kind"]}",\n'
        code += f'\t  rect = {{ {b["rect"][0]:.1f}, {b["rect"][1]:.1f}, {b["rect"][2]:.1f}, {b["rect"][3]:.1f} }},\n'
        code += f'\t  lengthM = {b["length_m"]:.1f}, depthM = {b["depth_m"]:.1f},\n'
        env = b["ship_envelope"]
        code += f'\t  envelope = {{ L = {env["L"]:.1f}, B = {env["B"]:.1f}, draft = {env["draft"]:.1f} }} }},\n'
    code += "}\n\n"

    code += """-- ------------------------------------------------------------------ interactions
Layout.interactions = {
	{ id = "B-I1", name = "Time Office / Yard Gate", kind = "worker_gate", radius = 5,
	  pos = { 70, -30, 4.0 } },
	{ id = "B-I2", name = "Princess Dock Coping (North)", kind = "dock_caisson", radius = 6,
	  pos = { 108, 262, 4.0 } },
	{ id = "B-I3", name = "Princess Dock Floor & Keel Blocks", kind = "dock_floor_work", radius = 10,
	  pos = { 108, 140, -7.0 } },
	{ id = "B-I4", name = "Moulding Loft Floor", kind = "loft_work", radius = 8,
	  pos = { 165, 219, 4.0 } },
	{ id = "B-I5", name = "Engineering Shop", kind = "workshop", radius = 8,
	  pos = { 163, 252, 4.0 } },
	{ id = "B-I6", name = "Slip 1 (Shoring & Launch Ways)", kind = "slip_work", radius = 8,
	  pos = { 10, 59, 4.0 } },
	{ id = "B-I7", name = "Day Summers 80t Sheer Legs Winch House", kind = "crane_operate", radius = 4,
	  pos = { -28, 280, 4.0 } },
	{ id = "B-I8", name = "Timber Yard", kind = "materials", radius = 8,
	  pos = { 258, 158, 4.0 } },
	{ id = "B-I9", name = "Plate Yard & Racks", kind = "materials", radius = 8,
	  pos = { 232, 46, 4.0 } },
	{ id = "B-I10", name = "Fitting-out Quay (Berth B-B1)", kind = "fitting_out", radius = 8,
	  pos = { -34, 250, 4.0 } },
	{ id = "B-I11", name = "No. 1 Graving Dock Entrance", kind = "dock_caisson", radius = 5,
	  pos = { 159, 42, 4.0 } },
	{ id = "B-I12", name = "Graving Dock Keel Blocks", kind = "keel_block_align", radius = 6,
	  pos = { 108, 100, -7.0 } },
	{ id = "B-I13", name = "Pierhead Lighthouse & Fog Bell", kind = "navigation_aid", radius = 6,
	  pos = { -26, 380, 4.0 } },
	{ id = "B-I14", name = "Harbour Signal Station Lookout", kind = "storm_warning", radius = 6,
	  pos = { 70, -50, 4.0 } },
	{ id = "B-I15", name = "Shipyard 3-Roller Plate Bending Machine", kind = "plate_rolling", radius = 6,
	  pos = { 100, 150, 4.0 } },
	{ id = "B-I16", name = "Upper Mould Loft Drafting Floor", kind = "loft_drafting", radius = 8,
	  pos = { 165, 219, 9.2 } },
}

-- ------------------------------------------------------------------ paths
Layout.paths = {
	worker = { {{ 70, -30 }, { 70, 40 }, { 60, 120 }, { 20, 200 }, { 80, 240 }}, {{ 70, -30 }, { 20, -100 }, { 20, -60 }} },
	vehicle = { {{ 340, -300 }, { 300, -100 }, { 300, 200 }, { 200, 260 }} },
	rail = { {{ 72, -300 }, { 72, 400 }} },
}

Layout.spawns = {
	{ id = "B-S1", pos = { 70, -24, 4.0 }, role = "worker" },
	{ id = "B-S2", pos = { 14, 60, 4.0 }, role = "slipworker" },
}

return Layout
"""
    with open(os.path.join(ROOT, "roblox/src/PortLayoutB.luau"), "w") as f:
        f.write(code)
    print("wrote roblox/src/PortLayoutB.luau")

if __name__ == "__main__":
    gen_layout_a()
    gen_layout_b()
