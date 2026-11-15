--!strict
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

-- ------------------------------------------------------------------ berths
Layout.berths = {
	{ id = "A-B1", name = "Trafalgar Landing Stage, West Face", kind = "passenger",
	  rect = { -106.0, 24.0, -80.0, 236.0 },
	  lengthM = 204.0, depthM = 11.0,
	  envelope = { L = 180.0, B = 20.0, draft = 9.0 } },
	{ id = "A-B2", name = "Trafalgar Landing Stage, East Berth (tender/steamer)", kind = "passenger",
	  rect = { -62.0, 42.0, -42.0, 152.0 },
	  lengthM = 110.0, depthM = 6.5,
	  envelope = { L = 100.0, B = 14.0, draft = 5.0 } },
	{ id = "A-B3", name = "Trafalgar Dock, North Quay (cargo)", kind = "cargo",
	  rect = { 68.0, -60.0, 200.0, -84.0 },
	  lengthM = 132.0, depthM = 9.0,
	  envelope = { L = 130.0, B = 18.0, draft = 8.0 } },
	{ id = "A-B4", name = "Trafalgar Dock, East Quay (cargo)", kind = "cargo",
	  rect = { 178.0, -194.0, 200.0, -70.0 },
	  lengthM = 124.0, depthM = 9.0,
	  envelope = { L = 116.0, B = 17.0, draft = 8.0 } },
}

-- ------------------------------------------------------------------ interactions
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
	  pos = { -73, 130, 4.0 } },
	{ id = "A-I7", name = "Ship Brow", kind = "board_ship", radius = 3,
	  pos = { -80, 130, 4.0 } },
	{ id = "A-I8", name = "Mooring bollards (berth 1)", kind = "mooring", radius = 3,
	  pos = { -82, 60, 4.0 } },
	{ id = "A-I9", name = "Coal Staithe / Hoist", kind = "coal_bunkering", radius = 6,
	  pos = { 100, -54, 4.0 } },
	{ id = "A-I10", name = "Cargo Shed Door (dock)", kind = "cargo_work", radius = 5,
	  pos = { 204, -140, 4.0 } },
	{ id = "A-I11", name = "Railway Platform", kind = "train_board", radius = 6,
	  pos = { 116, 48, 4.0 } },
	{ id = "A-I12", name = "Dock Gate / Time Office", kind = "worker_gate", radius = 4,
	  pos = { 170, 150, 4.0 } },
}

-- ------------------------------------------------------------------ gangways
Layout.gangways = {
	{"id":"A-G1","type":"canopied gangway bridge","y":75.0,"from":[-30.0,75.0],"to":[-66.0,75.0],"walk_width_m":3.8,"slope":"shore 4.0 m -> pontoon 1.5 m"},
	{"id":"A-G2","type":"canopied gangway bridge","y":195.0,"from":[-30.0,195.0],"to":[-66.0,195.0],"walk_width_m":3.8,"slope":"shore 4.0 m -> pontoon 1.5 m"},
	{"id":"A-G3","type":"ship brow (boarding)","at":"pontoon west face","pos":[-80.0,130.0],"length_m":9.0,"walk_width_m":1.6},
}

-- ------------------------------------------------------------------ paths
Layout.paths = {
	passenger = { {{ -28.0, 75.0 }, { 2.0, 75.0 }, { 24.0, 60.0 }, { 24.0, 34.0 }}, {{ -28.0, 195.0 }, { -6.0, 195.0 }, { -6.0, 120.0 }, { 2.0, 120.0 }} },
	dockworker = { {{ 170.0, 150.0 }, { 170.0, 60.0 }, { 150.0, 20.0 }, { 60.0, -30.0 }, { 16.0, -60.0 }} },
	vehicle = { {{ 170.0, 150.0 }, { 170.0, 200.0 }, { 100.0, 220.0 }, { 2.0, 220.0 }} },
}

Layout.spawns = {
	{ id = "A-S1", pos = { -73, 130, 4.0 }, role = "passenger" },
	{ id = "A-S2", pos = { 170, 140, 4.0 }, role = "dockworker" },
	{ id = "A-S3", pos = { 116, 48, 4.0 }, role = "rail_passenger" },
}

return Layout
