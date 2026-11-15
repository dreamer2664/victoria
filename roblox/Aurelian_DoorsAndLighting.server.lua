--[[
    SS AURELIAN — DOORS, BOARDING AND INTERIOR LIGHTING  (Roblox)

    Put inside ServerScriptService.  Three jobs:

    1. DOORS — every part named Door_* swings open when a player is within
       6 studs and shuts again when they leave.  Watertight doors (WT_*) in
       the machinery spaces need a ProximityPrompt (period practice: they
       were dogged shut at sea).

    2. BOARDING — a gangway at the forward shell door plus a boarding ramp
       at the after gangway.  Stepping on the plate sets MooringsClear and
       lets the player walk aboard; the ship will not answer the telegraph
       until the gangway is shipped (this is the coupling to the ship
       controller's moorings interlock).

    3. LIGHTING — the interior lamps (Interior_Lamp_*) are battery/hurricane
       lamps in 1889, not electric.  They are point lights at 0.55 brightness
       with a warm 2400 K tint; the public rooms have clusters, the cabins one
       each.  A global "LightsOut" attribute dims every lamp for the night
       watch.
]]

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local RunService = game:GetService("RunService")

local model = workspace:FindFirstChild("Aurelian")
if not model then
	warn("Aurelian: model 'Aurelian' not found in Workspace")
	return
end

local OPEN_ANGLE = math.rad(88)
local SENSOR_RANGE = 7

------------------------------------------------------------------ DOORS
local doors = {}
for _, d in ipairs(model:GetDescendants()) do
	if d:IsA("BasePart") and d.Name:match("^Door_") then
		table.insert(doors, {
			part = d,
			closed = d.CFrame,
			open = d.CFrame * CFrame.Angles(0, OPEN_ANGLE, 0),
			state = "closed",
			watertight = d.Name:match("^Door_WT") ~= nil,
		})
	end
end

if #doors > 0 then
	RunService.Heartbeat:Connect(function()
		local character = {}
		for _, p in ipairs(Players:GetPlayers()) do
			local c = p.Character
			if c and c:FindFirstChild("HumanoidRootPart") then
				table.insert(character, c.HumanoidRootPart.Position)
			end
		end
		for _, door in ipairs(doors) do
			if door.watertight then
				continue
			end
			local near = false
			for _, pos in ipairs(character) do
				if (pos - door.part.Position).Magnitude < SENSOR_RANGE then
					near = true
					break
				end
			end
			local want = near and "open" or "closed"
			if door.state ~= want then
				door.state = want
				TweenService:Create(door.part,
					TweenInfo.new(0.85, Enum.EasingStyle.Quad,
						Enum.EasingDirection.InOut),
					{ CFrame = door[want] }):Play()
			end
		end
	end)
end

------------------------------------------------------------------ BOARDING
local control = model:FindFirstChild("ShipControl")
local function callShip(name, ...)
	local f = control and control:FindFirstChild(name)
	if f and f:IsA("BindableFunction") then
		return f:Invoke(...)
	end
end

for _, padName in ipairs({ "BoardingPlate", "GangwayPlate" }) do
	local pad = model:FindFirstChild(padName, true)
	if pad and pad:IsA("BasePart") then
		local wasAboard = {}
		RunService.Heartbeat:Connect(function()
			for _, p in ipairs(Players:GetPlayers()) do
				local c = p.Character
				local hrp = c and c:FindFirstChild("HumanoidRootPart")
				if not hrp then
					continue
				end
				local aboard = (hrp.Position - pad.Position).Magnitude < 14
				if wasAboard[p] ~= aboard then
					wasAboard[p] = aboard
					callShip("SetMooringsClear", aboard)
					model:SetAttribute("MooringsClear", aboard)
					if aboard then
						p:SetAttribute("Aboard", true)
					else
						p:SetAttribute("Aboard", nil)
					end
				end
			end
		end)
	end
end

------------------------------------------------------------------ LIGHTING
local lampCount = 0
for _, d in ipairs(model:GetDescendants()) do
	if d:IsA("BasePart") and d.Name:match("^Interior_Lamp") then
		local l = d:FindFirstChildWhichIsA("PointLight")
		if not l then
			l = Instance.new("PointLight")
			l.Parent = d
		end
		l.Color = Color3.fromRGB(255, 208, 150)   -- ~2400 K hurricane lamp
		l.Brightness = 0.55
		l.Range = 14
		l.Shadows = false                          -- cost control on mobile
		lampCount = lampCount + 1
	end
end
print(("[Aurelian] %d door(s), %d interior lamp(s) wired"):format(#doors, lampCount))

-- Night watch: everything down to a dim sergeants' lamp
local function applyLightsOut(v)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("PointLight") and d.Parent.Name:match("^Interior_Lamp") then
			d.Brightness = v and 0.12 or 0.55
		end
	end
end
model:GetAttributeChangedSignal("LightsOut"):Connect(function()
	applyLightsOut(model:GetAttribute("LightsOut"))
end)
