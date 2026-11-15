--!nonstrict
--[[
	BuildBoat.lua -- Studio assembly tool (run once from the command bar or a
	plugin).  It takes the imported meshes for one boat and produces a
	driveable model:

	    BuildBoat.assemble("steam_cutter_1888", importedFolder)

	What it does, in order:
	  1. scales the meshes to the 1 stud = 0.28 m contract;
	  2. rotates them so the bow points -Z (Roblox forward) -- the Blender
	     export is Y-up with the bow on +X, so this is a 90 deg turn about Y;
	  3. picks the hull mesh as the PrimaryPart and gives it a mass equal to
	     the published loaded displacement, so the buoyancy probes float her
	     at the designed draught;
	  4. welds every part to the hull and re-creates the moving parts' pivots;
	  5. tags the model with BoatId so BoatService finds and drives it;
	  6. places the model in Workspace.Boats.

	The scale and mass come from interfaces/boats_spec.json, which is the
	single source of truth shared with the ship agent.
]]

local Workspace = game:GetService("Workspace")

local Config = require(script.Parent.Config)
local BoatRig = require(script.Parent.BoatRig)

local BuildBoat = {}

local MANIFEST_MODULES = {
	steam_cutter_1888 = "Manifest_steam_cutter_1888",
	rowing_cutter_25ft = "Manifest_rowing_cutter_25ft",
}

--- The imported meshes come in metres (1 GLB unit = 1 m); Roblox imports them
--- as 1 unit = 1 stud, so everything must be scaled by STUD_PER_M.
function BuildBoat.scaleAll(folder, factor)
	for _, d in ipairs(folder:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Size = d.Size * factor
			d.CFrame = CFrame.new(d.Position * factor) * (d.CFrame - d.Position)
		end
	end
end

function BuildBoat.assemble(boatId, importedFolder, opts)
	opts = opts or {}
	local cfg = Config.BOATS[boatId]
	assert(cfg, "unknown boat id " .. tostring(boatId))

	local manifestName = MANIFEST_MODULES[boatId]
	local manifest = require(script.Parent[manifestName])

	local model = Instance.new("Model")
	model.Name = cfg.displayName:gsub("%s", "_")
	model:SetAttribute("BoatId", boatId)

	-- move the meshes into the model
	for _, d in ipairs(importedFolder:GetChildren()) do
		d.Parent = model
	end

	local folder = model
	BuildBoat.scaleAll(folder, Config.STUD_PER_M)

	-- Blender +X (bow) -> Roblox -Z
	local pivot = folder:GetPivot()
	folder:PivotTo(pivot * CFrame.Angles(0, math.rad(90), 0))

	-- the hull mesh carries the mass
	local hull = folder:FindFirstChild("Planking_Carvel", true)
		or folder:FindFirstChild("Planking_Clinker", true)
		or folder:FindFirstChildWhichIsA("BasePart")
	assert(hull, "no hull mesh found in the imported folder")
	model.PrimaryPart = hull
	hull.Anchored = false
	hull.CanCollide = true

	local totalMass = cfg.loaded_kg          -- kg == Roblox mass units here
	local volume = hull.Size.X * hull.Size.Y * hull.Size.Z
	hull.CustomPhysicalProperties = PhysicalProperties.new(
		math.max(totalMass / math.max(volume, 1), 0.05), 0.3, 0.2, 1, 1)

	-- weld everything else to the hull
	local moving = { Propeller = true, Rudder = true }
	for _, p in ipairs(manifest.parts) do
		if p.role == "moving" then moving[p.name] = true end
	end
	BoatRig.weld(folder, hull, moving)

	-- cockpit floor for the crew, and a seat is added by BoatService
	hull:SetAttribute("DraftStuds", cfg.draft_m * Config.STUD_PER_M)

	-- parent into the world
	local boats = Workspace:FindFirstChild("Boats")
	if not boats then
		boats = Instance.new("Folder")
		boats.Name = "Boats"
		boats.Parent = Workspace
	end
	model.Parent = boats

	if not opts.noDock then
		model:PivotTo(CFrame.new(opts.position or Vector3.new(0, 6, 0)))
	end
	print(string.format("[BuildBoat] %s assembled: %d parts, hull %.2f x %.2f x %.2f studs",
		boatId, #model:GetChildren(), hull.Size.X, hull.Size.Y, hull.Size.Z))
	return model
end

--- Convenience: assemble both boats side by side for a quick test scene.
function BuildBoat.assembleDemo(folders)
	local a = BuildBoat.assemble("steam_cutter_1888", folders.steam,
		{ position = Vector3.new(-12, 2, 0) })
	local b = BuildBoat.assemble("rowing_cutter_25ft", folders.rowing,
		{ position = Vector3.new(12, 2, 0) })
	return a, b
end

return BuildBoat
