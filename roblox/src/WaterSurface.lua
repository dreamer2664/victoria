--!nonstrict
--[[
	WaterSurface.lua -- finds the water height under a point.

	Three sources, in order:
	  1. a flat Part named Config.WATER_PLANE_NAME (cheap and exact);
	  2. a downward raycast that accepts Terrain Water;
	  3. Config.WATER_LEVEL_FALLBACK.

	Also provides the small wave field used by the buoyancy model, so both
	boats bob in a believable way without any physics cheats.
]]

local Workspace = game:GetService("Workspace")

local Config = require(script.Parent.Config)

local WaterSurface = {}

local rayParams = RaycastParams.new()
rayParams.FilterType = Enum.RaycastFilterType.Exclude
rayParams.IgnoreWater = false
local ignoreList = {}

local waveClockValue = 0
local function waveClock()
	return waveClockValue
end

--- Register an instance the water tests must ignore (the boat itself).
function WaterSurface.ignore(instance)
	ignoreList[#ignoreList + 1] = instance
	rayParams.FilterDescendantsInstances = ignoreList
end

function WaterSurface.setIgnoreList(list)
	ignoreList = list
	rayParams.FilterDescendantsInstances = ignoreList
end

function WaterSurface.step(dt)
	waveClockValue = waveClockValue + dt
end

--- Height of the water surface directly under `position` (world space).
function WaterSurface.heightAt(position)
	local plane = Workspace:FindFirstChild(Config.WATER_PLANE_NAME, true)
	if plane and plane:IsA("BasePart") then
		return plane.Position.Y
	end

	local origin = Vector3.new(position.X, position.Y + 400, position.Z)
	local result = Workspace:Raycast(origin, Vector3.new(0, -1200, 0), rayParams)
	if result then
		if result.Material == Enum.Material.Water then
			return result.Position.Y
		end
		-- walk down through anything solid to see whether water lies below
		local again = Workspace:Raycast(result.Position - Vector3.new(0, 1, 0),
			Vector3.new(0, -400, 0), rayParams)
		while again do
			if again.Material == Enum.Material.Water then
				return again.Position.Y
			end
			again = Workspace:Raycast(again.Position - Vector3.new(0, 1, 0),
				Vector3.new(0, -400, 0), rayParams)
		end
		return result.Position.Y
	end
	return Config.WATER_LEVEL_FALLBACK
end

--- Small sum-of-sines wave height at a world position, in studs.
function WaterSurface.waveAt(position, amplitude)
	local t = waveClock()
	local a = amplitude or 0.18
	local x, z = position.X * 0.06, position.Z * 0.05
	return a * (math.sin(t * 1.1 + x) * 0.6 + math.sin(t * 0.71 + z * 1.3) * 0.4)
end

--- Surface normal-ish tilt to give the hull a gentle roll in a seaway.
function WaterSurface.slopeAt(position)
	local t = waveClock()
	return math.sin(t * 0.9 + position.X * 0.07) * 0.7, math.cos(t * 0.63 + position.Z * 0.05) * 0.5
end

return WaterSurface
