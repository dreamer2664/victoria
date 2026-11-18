--!strict
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
	{ id = "B-B1", name = "Fitting-out quay, river frontage (Day Summers 80t sheer legs)", kind = "fitting_out",
	  rect = { -58.0, 186.0, -30.0, 396.0 },
	  lengthM = 210.0, depthM = 10.0,
	  envelope = { L = 166.0, B = 18.0, draft = 6.5 } },
	{ id = "B-B2", name = "Service quay south of the slips", kind = "repair",
	  rect = { -58.0, -280.0, -30.0, 40.0 },
	  lengthM = 320.0, depthM = 9.0,
	  envelope = { L = 140.0, B = 18.0, draft = 8.0 } },
	{ id = "B-B3", name = "Princess Graving Dock", kind = "dry_dock",
	  rect = { 96.0, 20.0, 120.4, 264.0 },
	  lengthM = 243.8, depthM = 11.0,
	  envelope = { L = 166.0, B = 18.0, draft = 6.5 } },
}

-- ------------------------------------------------------------------ interactions
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
