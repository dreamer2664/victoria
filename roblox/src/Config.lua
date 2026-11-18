--!nonstrict
--[[
	Config.lua -- shared constants for the OPERATION VICTORIA ship's boats.

	Scale contract (see interfaces/boats_spec.json):
		1 stud = 0.28 m  ->  3.5714 studs per metre.
	The Blender models are authored in metres; BuildBoat applies the factor
	below on import so both boats land in the world at their true size.
]]

local Config = {}

Config.STUD_PER_M = 1 / 0.28
Config.M_PER_STUD = 0.28

-- Water
Config.WATER_LEVEL_FALLBACK = 0          -- used when no Terrain/water plane is found
Config.WATER_PLANE_NAME = "WaterPlane"   -- optional flat part that defines the surface
Config.GRAVITY = 196.2                   -- studs/s^2 (Roblox default)

Config.BOATS = {
	steam_cutter_1888 = {
		id = "steam_cutter_1888",
		displayName = "25 ft Steam Cutter",
		loa_m = 7.620,
		beam_m = 2.134,
		depth_m = 1.203,
		light_kg = 3212,
		loaded_kg = 3532,
		-- them2 corrected hydro: Z=0 is the LOADED waterline, draft from hydro
		-- solver on the modelled hull (was a guessed 0.532 m).
		draft_m = 0.769,
		-- slings / davit points, metres, +X forward, +Z up (Blender frame)
		davit_points = { { 2.10, 0, 0.62 }, { -1.85, 0, 0.62 } },
		boarding = { x = 0.35, z = 0.60 },
		-- propulsion
		max_thrust_n = 2600,       -- tuned so the hull reaches ~6.5 kn
		max_speed_studs = 30,
		reverse_fraction = 0.45,
		steer_rate_deg = 16,       -- deg/s at full helm and cruise speed
		prop_max_rpm = 420,
		engine_start_s = 6.0,      -- boiler raising steam before the shaft turns
		funnel_offset_m = { 0.50, 0, 1.30 },
	},
	rowing_cutter_25ft = {
		id = "rowing_cutter_25ft",
		displayName = "25 ft Clinker Rowing Cutter",
		loa_m = 7.620,
		beam_m = 1.905,
		depth_m = 1.065,
		light_kg = 1112,
		loaded_kg = 1992,
		-- them2 corrected hydro (see steam_cutter note above)
		draft_m = 0.663,
		oars = 10,
		oar_length_m = 3.66,
		oar_stations_x_m = { 2.02, 1.18, 0.34, -0.50, -1.34 },
		max_speed_studs = 11,      -- ~3.1 m/s, a realistic pulling speed
		stroke_rate = 26,          -- strokes per minute
		steer_from_bank = 0.55,    -- how much differential rowing yaws the boat
		boarding = { x = 0.55, z = 0.52 },
		-- them2: 10 oars double-banked from mesh pivots; stations below are the
		-- rowlock stations in metres from mid-LOA (model frame +X = bow).
		oar_station_pivots_from_manifest = true,
	},
	whaler_27ft = {
		id = "whaler_27ft",
		displayName = "27 ft Double-ended Whaler",
		loa_m = 8.230,
		beam_m = 1.829,
		depth_m = 1.032,
		light_kg = 1007.5,
		loaded_kg = 1487.5,
		draft_m = 0.511,
		-- five oars single-banked, alternating sides (them2 manifest: side PLAN)
		oars = 5,
		single_banked = true,
		oar_side_plan = { "Oar_P1", "Oar_S2", "Oar_P3", "Oar_S4", "Oar_P5" },
		oar_length_m = 5.18,      -- 17 ft service oar, confirmed
		oar_stations_x_m = { 1.90, 1.10, 0.30, -0.50, -1.30 }, -- them2 single-banked P,S,P,S,P
		davit_points = { { 1.85, 0, 0.62 }, { -1.85, 0, 0.62 } },
		boarding = { x = 0.70, z = 0.59 },
		max_speed_studs = 11,
		stroke_rate = 24,
		steer_from_bank = 0.50,
		-- the rig is carried furled; the masts are 5.03 m and 3.96 m tall, so
		-- she cannot be hoisted under davits with the mainmast stepped
		masts = { main_m = 5.03, mizzen_m = 3.96 },
		mainmast_x_m = 0.658,
	},
}

-- Colours used by the procedural parts (seats, prompts) so the boats look
-- consistent whether or not the meshes are imported.
Config.COLOURS = {
	teak = Color3.fromRGB(96, 60, 34),
	paint = Color3.fromRGB(28, 30, 33),
	canvas = Color3.fromRGB(206, 199, 178),
	brass = Color3.fromRGB(178, 141, 62),
}

return Config
