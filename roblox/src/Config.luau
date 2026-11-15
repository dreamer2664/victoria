--!strict
--[[
	Config.luau -- Operation Victoria / Port Construction

	THE SCALE RULE. The Blender source is modelled natively in metres. Roblox works
	in studs. The project-wide conversion is:

	    1 stud = 0.28 m       ->      1 m = 3.571428... studs

	Every number in the layout data modules is in METRES. Convert exactly once, here,
	and never scatter the constant through gameplay code.
]]

local Config = {}

-- metres -> studs
Config.STUDS_PER_METRE = 1 / 0.28 -- 3.5714285714...

-- The height datum: Blender z = 0 is mean water level; the quay coping is at +4 m.
Config.WATER_Z_M = 0.0
Config.QUAY_Z_M = 4.0

-- Where each port is placed in the world. Two ports, kept far enough apart that
-- neither can see the other's boundary. Units: studs.
Config.PORTS = {
	A = {
		name = "Port of Aldermouth",
		kind = "passenger",
		originStuds = Vector3.new(0, 0, 0),
	},
	B = {
		name = "Port of Carrickmore",
		kind = "industrial",
		originStuds = Vector3.new(20000, 0, 0),
	},
}

function Config.mToStuds(metres: number): number
	return metres * Config.STUDS_PER_METRE
end

function Config.studsToM(studs: number): number
	return studs * 0.28
end

--- Convert a Blender metric point to a world-space position for a port.
-- Blender is Z-up right-handed; Roblox is Y-up left-handed with -Z forward.
-- The conversion baked into the GLB export is Y-up already, so we only translate.
function Config.toWorld(portCode: string, x: number, y: number, z: number): Vector3
	local p = Config.PORTS[portCode]
	assert(p, "unknown port " .. tostring(portCode))
	local s = Config.STUDS_PER_METRE
	return p.originStuds + Vector3.new(x * s, z * s, -y * s)
end

--- Berth clearance rule used throughout the design: a ship of the given envelope
-- must have at least this much clear water around it in plan.
Config.BERTH_CLEARANCE_M = 4.0

return Config
