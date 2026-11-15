--!nonstrict
--[[
	BoatRig.lua -- assembles an imported boat so the moving parts really move.

	Every moving part in the Blender model was exported with its origin on its
	mechanical pivot (rowlocks for the oars, the pintle axis for the rudder and
	tiller, the shaft axis for the propeller).  This module recreates that
	relationship in Roblox with Motor6D joints, so a script can turn an oar
	about its rowlock, swing the tiller, or spin the screw, and the parts stay
	attached and welded to the hull.

	Everything except the root part is massless: the hull root carries the mass
	that Hydrodynamics works with, so adding detail never changes the handling.
]]

local BoatRig = {}

export type PartInfo = {
	name: string,
	role: string,
	origin: Vector3,
	size: Vector3,
	instance: BasePart,
}

--- Build a lookup of the boat's parts by their manifest name.
function BoatRig.collect(folder): { [string]: BasePart }
	local map = {}
	for _, d in ipairs(folder:GetDescendants()) do
		if d:IsA("BasePart") then
			map[d.Name] = d
		end
	end
	return map
end

--- Weld everything to the root except the parts that must move.
function BoatRig.weld(folder, root, movingNames)
	local welded = {}
	for _, d in ipairs(folder:GetDescendants()) do
		if d:IsA("BasePart") and d ~= root and not movingNames[d.Name] then
			d.Massless = true
			d.CanCollide = false
			d.Anchored = false
			if not d:FindFirstChild("HullWeld") then
				local w = Instance.new("WeldConstraint")
				w.Name = "HullWeld"
				w.Part0 = root
				w.Part1 = d
				w.Parent = d
			end
			welded[#welded + 1] = d
		end
	end
	return welded
end

--- Attach a part to the root with a Motor6D whose C0 places it on its pivot.
--- `pivotLocal` is the part's origin expressed in the root's local space.
function BoatRig.hinge(part, root, pivotLocal, axis)
	part.Anchored = false
	part.CanCollide = false
	part.Massless = true
	local existing = part:FindFirstChild("Pivot")
	if existing then existing:Destroy() end
	local m = Instance.new("Motor6D")
	m.Name = "Pivot"
	m.Part0 = root
	m.Part1 = part
	-- C0: where the joint sits relative to the root; C1 cancels the part's own
	-- offset so the part stays exactly in the position it was imported at.
	m.C0 = CFrame.new(pivotLocal)
	m.C1 = CFrame.new(pivotLocal) * (root.CFrame:ToObjectSpace(part.CFrame)):Inverse()
	m.Parent = part
	return m
end

--- Rig all the oars of the rowing cutter.  Each oar turns about the axis of
--- its rowlock, which is the part's own origin.
function BoatRig.rigOars(folder, root, manifest)
	local oars = {}
	for _, entry in ipairs(manifest.parts) do
		if entry.role == "moving" and entry.name:match("^Oar") then
			local part = folder:FindFirstChild(entry.name, true)
			if part and part:IsA("BasePart") then
				local pivotLocal = root.CFrame:PointToObjectSpace(part.Position)
				local m = BoatRig.hinge(part, root, pivotLocal)
				oars[#oars + 1] = { part = part, motor = m, side = part.Name:find("_S") and -1 or 1,
					index = tonumber(part.Name:match("(%d+)$")) or 1 }
			end
		end
	end
	table.sort(oars, function(a, b) return a.index < b.index end)
	return oars
end

--- Rig the steam cutter's screw and rudder.
function BoatRig.rigScrew(folder, root, manifest)
	local screw = folder:FindFirstChild("Propeller", true)
	local rudder = folder:FindFirstChild("Rudder", true)
	local out = {}
	if screw then
		local pivotLocal = root.CFrame:PointToObjectSpace(screw.Position)
		out.screw = screw
		out.screwMotor = BoatRig.hinge(screw, root, pivotLocal)
	end
	if rudder then
		local pivotLocal = root.CFrame:PointToObjectSpace(rudder.Position)
		out.rudder = rudder
		out.rudderMotor = BoatRig.hinge(rudder, root, pivotLocal)
	end
	return out
end

return BoatRig
