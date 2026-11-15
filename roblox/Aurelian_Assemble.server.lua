--[[
    SS AURELIAN — MODULE ASSEMBLY AND TAGGING  (Roblox)

    Run ONCE in Studio after importing the seven FBX modules.  It:

      1. collects every imported MeshPart into one Model named "Aurelian";
      2. verifies the scale (1 stud = 0.28 m) by measuring the hull against
         the published 592.9-stud overall length and correcting if the
         importer applied its own scale;
      3. sets the origin so the model's PrimaryPart sits amidships, on the
         waterline, on the centreline — the same frame the Blender file uses;
      4. tags every deck and interior part with its location, so door,
         lighting and boarding scripts can find what they need;
      5. builds the attribute defaults the other scripts expect.

    This is the bridge between the Blender export and the runtime scripts.
]]

local Workspace = game:GetService("Workspace")
local CollectionService = game:GetService("CollectionService")

local METRES_PER_STUD = 0.28
local LOA_STUDS = 166.0 / METRES_PER_STUD     -- 592.86
local BEAM_STUDS = 18.4 / METRES_PER_STUD     -- 65.71

------------------------------------------------------------------ 1. COLLECT
local model = Workspace:FindFirstChild("Aurelian")
if not model then
	model = Instance.new("Model")
	model.Name = "Aurelian"
	model.Parent = Workspace
end

-- The Roblox 3D importer parents meshes to a Folder/Model per import.  Pull
-- every MeshPart whose name we recognise into the ship model.
local PREFIXES = {
	"Hull", "Keel", "Rudder", "Boot_Top", "Bulwarks", "Anchors", "SaloonHouse",
	"DeckHouse", "Decks_", "BoatDeck", "Bridge", "Promenade_Rails", "Funnels",
	"Masts", "Rigging", "NavLights", "Boats_", "DeckMachinery", "Cargo",
	"Boiler_", "Engine_", "Crankshaft", "Propeller", "Steering_", "Thrust_",
	"Interior_", "Dining_", "Library", "Smoking_", "Music_", "Grand_",
	"Staterooms", "Third_Class", "Galley", "Officers_", "Wheelhouse_",
	"Lavatories", "Corridor_", "Scuppers", "Stair_", "Ceil_", "Carpet_",
	"Dado_", "Panel_", "Cornice_", "Chair", "Table", "Settee", "Bed",
	"Washstand", "Wardrobe", "Bookcase", "Column", "Lamp", "Door_", "Skylight",
}

local function looksLikeShipPart(name)
	for _, p in ipairs(PREFIXES) do
		if string.sub(name, 1, #p) == p then
			return true
		end
	end
	return false
end

local moved = 0
for _, d in ipairs(Workspace:GetDescendants()) do
	if d:IsA("BasePart") and looksLikeShipPart(d.Name)
		and d:IsDescendantOf(Workspace) and not d:IsDescendantOf(model) then
		d.Parent = model
		moved = moved + 1
	end
end
print(("[Aurelian] assembled %d parts into the ship model"):format(moved))

------------------------------------------------------------------ 2. SCALE
local function measure()
	local lo, hi = Vector3.new(1e9, 1e9, 1e9), Vector3.new(-1e9, -1e9, -1e9)
	local n = 0
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("BasePart") then
			local p = d.Position
			lo = Vector3.new(math.min(lo.X, p.X), math.min(lo.Y, p.Y),
				math.min(lo.Z, p.Z))
			hi = Vector3.new(math.max(hi.X, p.X), math.max(hi.Y, p.Y),
				math.max(hi.Z, p.Z))
			n = n + 1
		end
	end
	return lo, hi, n
end

local lo, hi, count = measure()
local longest = math.max(hi.X - lo.X, hi.Z - lo.Z)
print(("[Aurelian] measured length %.1f studs (expected %.1f), %d parts")
	:format(longest, LOA_STUDS, count))

if longest > 1 and math.abs(longest - LOA_STUDS) > LOA_STUDS * 0.08 then
	local factor = LOA_STUDS / longest
	warn(("[Aurelian] scale is off by %.3f - rescaling the model"):format(factor))
	model:PivotTo(model:GetPivot() * CFrame.new(Vector3.zero)
		* CFrame.Angles(0, 0, 0))
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Size = d.Size * factor
			local rel = (d.Position - lo) * factor
			d.Position = lo + rel
		end
	end
else
	print("[Aurelian] scale verified at 1 stud = 0.28 m")
end

------------------------------------------------------------------ 3. ORIGIN
-- A small invisible part at amidships/waterline becomes the PrimaryPart and
-- the model's pivot; the ship controller drives this part.
local root = model:FindFirstChild("ShipRoot")
if not root then
	root = Instance.new("Part")
	root.Name = "ShipRoot"
	root.Size = Vector3.new(2, 2, 2)
	root.Transparency = 1
	root.CanCollide = false
	root.Anchored = true
	root.Parent = model
end
lo, hi = measure()
root.Position = Vector3.new((lo.X + hi.X) / 2, 0, (lo.Z + hi.Z) / 2)
model.PrimaryPart = root
model:PivotTo(CFrame.new(root.Position))

------------------------------------------------------------------ 4. TAGS
local TAGS = {
	{ tag = "Deck", pattern = "^Decks_" },
	{ tag = "Deck", pattern = "^BoatDeck" },
	{ tag = "Deck", pattern = "^Bridge_Deck" },
	{ tag = "Interior", pattern = "^Interior_" },
	{ tag = "Machinery", pattern = "^Boiler_" },
	{ tag = "Machinery", pattern = "^Engine_" },
	{ tag = "Machinery", pattern = "^Propeller" },
	{ tag = "Door", pattern = "^Door_" },
	{ tag = "Lamp", pattern = "^Interior_Lamp" },
	{ tag = "Boat", pattern = "^Lifeboat" },
	{ tag = "Boat", pattern = "^Agent02_" },
}
local tagged = 0
for _, d in ipairs(model:GetDescendants()) do
	if not d:IsA("BasePart") then
		continue
	end
	for _, t in ipairs(TAGS) do
		if string.match(d.Name, t.pattern) then
			CollectionService:AddTag(d, t.tag)
			tagged = tagged + 1
			break
		end
	end
	-- every ship part should be anchored: this is a moving model driven by
	-- its pivot, not a physics assembly
	d.Anchored = true
	d.CanCollide = true
end
print(("[Aurelian] %d parts tagged"):format(tagged))

------------------------------------------------------------------ 5. ATTRS
for k, v in pairs({
	Throttle = 0, ShaftRPM = 0, ShaftAngle = 0, SpeedKn = 0, Heading = 0,
	RudderAngle = 0, Telegraph = "Finished with Engines", BoilerPressure = 0,
	EngineIHP = 0, SmokeIntensity = 0, MooringsClear = false,
	LightsOut = false, EngineRunning = false,
}) do
	if model:GetAttribute(k) == nil then
		model:SetAttribute(k, v)
	end
end

print("[Aurelian] ready. Scale 1 stud = 0.28 m; LOA 592.9 studs; beam 65.7 studs.")
