--[[
    SS AURELIAN — MACHINERY ANIMATION  (Roblox)

    Place inside the Machinery model.  Drives the moving components exported
    from Blender as separate objects:

        Crankshaft            rotate about its own long axis (X, fore-aft)
        Engine_HP_Rod         piston rod: reciprocating along its axis
        Engine_IP_Rod         "
        Engine_LP_Rod         "
        Propeller_Shaft       rotate about X
        Propeller             rotate about X (3-blade, or 4 in the build)
        Furnace_Glow*         flicker (fire bars)

    Everything is driven from the ship model's ShaftRPM / ShaftAngle
    attributes, so it always agrees with the ship's actual speed - the engine
    can never turn the propeller faster than the ship is doing.

    Stroke and crank throw come from shipdesign/spec.py:
        3 cylinders 0.965 / 1.575 / 2.565 m bore, 1.295 m stroke
        62 rpm at 14 000 IHP
]]

local RunService = game:GetService("RunService")

local machinery = script.Parent
local ship = machinery:FindFirstAncestorOfClass("Model") or machinery.Parent

local STROKE_STUDS = 1.295 / 0.28
local CRANK_R_STUDS = (1.295 / 2) / 0.28      -- crank radius = half stroke

local function find(pattern)
	local found = {}
	for _, d in ipairs(machinery:GetDescendants()) do
		if d:IsA("BasePart") and d.Name:match(pattern) then
			table.insert(found, d)
		end
	end
	return found
end

local crank = machinery:FindFirstChild("Crankshaft", true)
local shaft = machinery:FindFirstChild("Propeller_Shaft", true)
local prop  = machinery:FindFirstChild("Propeller", true)
local rods = {
	{ part = find("^Engine_HP_Rod"), phase = 0.0 },
	{ part = find("^Engine_IP_Rod"), phase = 2.0944 },
	{ part = find("^Engine_LP_Rod"), phase = 4.1888 },
}
local fires = find("^Furnace_Glow")

-- Keep the originals so we can offset from them every frame.
local baseCFrame = {}
for _, entry in ipairs(rods) do
	for _, p in ipairs(entry.part) do
		baseCFrame[p] = p.CFrame
	end
end

local function rotAboutAxis(part, axisLocal, degrees)
	part.CFrame = part.CFrame * CFrame.fromAxisAngle(axisLocal, math.rad(degrees))
end

local accumulator = 0.0
RunService.Heartbeat:Connect(function(dt)
	local rpm = ship:GetAttribute("ShaftRPM") or 0
	local angle = ship:GetAttribute("ShaftAngle") or 0

	-- ---- propeller + shaft: rigid rotation about the fore-aft axis -------
	local dAngle = rpm * 6.0 * dt
	if prop then
		prop.CFrame = prop.CFrame * CFrame.fromAxisAngle(Vector3.new(1, 0, 0),
			math.rad(dAngle))
	end
	if shaft then
		shaft.CFrame = shaft.CFrame * CFrame.fromAxisAngle(Vector3.new(1, 0, 0),
			math.rad(dAngle))
	end
	if crank then
		crank.CFrame = crank.CFrame * CFrame.fromAxisAngle(Vector3.new(1, 0, 0),
			math.rad(dAngle))
	end

	-- ---- piston rods: simple harmonic motion, 120 deg out of phase ------
	local theta = math.rad(angle)
	for _, entry in ipairs(rods) do
		local a = theta + entry.phase
		-- exact slider-crank displacement, normalised to crank radius
		local throwRatio = 1.0 / 3.4        -- connecting rod length / crank r
		local s = math.cos(a) + math.sqrt(
			math.max(0, throwRatio ^ 2 - math.sin(a) ^ 2)) - throwRatio
		local offset = Vector3.new(0, CRANK_R_STUDS * s, 0)
		for _, p in ipairs(entry.part) do
			local base = baseCFrame[p]
			p.CFrame = base + offset
		end
	end

	-- ---- furnace flicker ------------------------------------------------
	accumulator = accumulator + dt
	if accumulator > 0.08 and #fires > 0 then
		accumulator = 0
		for _, f in ipairs(fires) do
			local t = f:FindFirstChildWhichIsA("PointLight")
			if t then
				t.Brightness = 1.4 + math.random() * 1.6
			end
			f.Color = Color3.fromRGB(255, 120 + math.random(60), 40)
		end
	end

	-- ---- boiler-room sound ---------------------------------------------
	local hum = machinery:FindFirstChild("EngineHum", true)
	if hum and hum:IsA("Sound") then
		if rpm > 1 and not hum.IsPlaying then
			hum:Play()
		elseif rpm <= 1 and hum.IsPlaying then
			hum:Stop()
		end
		if hum.IsPlaying then
			hum.PlaybackSpeed = 0.55 + math.min(rpm / 62, 1) * 0.9
		end
	end
end)
