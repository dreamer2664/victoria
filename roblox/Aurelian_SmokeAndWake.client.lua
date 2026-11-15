--[[
    SS AURELIAN — SMOKE, STEAM AND WAKE  (Roblox, StarterPlayerScripts)

    Effects are all driven by ship attributes, so they cost nothing when the
    ship is stopped.  The coal-smoke rate is written to the attribute
    SmokeIntensity by the ship controller from shaft RPM.

        SmokeIntensity 0    -> a wisp
        SmokeIntensity 1    -> a full black banner, as in the 1889 photographs
]]

local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local player = Players.LocalPlayer
local camera = workspace.CurrentCamera

local model = workspace:WaitForChild("Aurelian")

local function findEmitters(pattern)
	local out = {}
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("ParticleEmitter") and d.Name:match(pattern) then
			table.insert(out, d)
		end
	end
	return out
end

local smoke = findEmitters("^Funnel_Smoke")
local steam = findEmitters("^SteamPuff")
local wake  = findEmitters("^Wake")

------------------------------------------------------------------ SETUP
for _, e in ipairs(smoke) do
	e.Enabled = true
	e.Lifetime = NumberRange.new(5.5, 8.0)
	e.Speed = NumberRange.new(9, 14)
	e.SpreadAngle = Vector2.new(7, 7)
	e.Size = NumberSequence.new({
		NumberSequenceKeypoint.new(0.00, 1.4),
		NumberSequenceKeypoint.new(0.35, 5.0),
		NumberSequenceKeypoint.new(1.00, 16.0),
	})
	e.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0.00, 0.35),
		NumberSequenceKeypoint.new(0.55, 0.62),
		NumberSequenceKeypoint.new(1.00, 1.0),
	})
	e.Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0.0, Color3.fromRGB(48, 45, 42)),
		ColorSequenceKeypoint.new(0.6, Color3.fromRGB(112, 108, 102)),
		ColorSequenceKeypoint.new(1.0, Color3.fromRGB(168, 166, 160)),
	})
	e.Acceleration = Vector3.new(0, 5.5, 0)
	e.Drag = 1.6
end

for _, e in ipairs(steam) do
	e.Enabled = false
	e.Lifetime = NumberRange.new(0.6, 1.2)
	e.Size = NumberSequence.new(1.0, 4.0)
end

for _, e in ipairs(wake) do
	e.Enabled = true
	e.Lifetime = NumberRange.new(2.5, 4.0)
	e.Speed = NumberRange.new(0, 2)
	e.Size = NumberSequence.new(2.0, 9.0)
	e.Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0.0, 0.25),
		NumberSequenceKeypoint.new(1.0, 1.0),
	})
	e.Color = ColorSequence.new(Color3.fromRGB(206, 224, 226))
end

------------------------------------------------------------------ LOOP
RunService.Heartbeat:Connect(function()
	local intensity = model:GetAttribute("SmokeIntensity") or 0
	local rpm = model:GetAttribute("ShaftRPM") or 0
	local speed = math.abs(model:GetAttribute("SpeedKn") or 0)
	for _, e in ipairs(smoke) do
		e.Rate = 2 + intensity * 46
		e.Speed = NumberRange.new(8 + intensity * 8, 13 + intensity * 12)
		e.Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0.00, 0.42 - intensity * 0.10),
			NumberSequenceKeypoint.new(0.55, 0.66 - intensity * 0.12),
			NumberSequenceKeypoint.new(1.00, 1.0),
		})
	end
	for _, e in ipairs(wake) do
		e.Enabled = speed > 1.5
		e.Rate = math.clamp(speed * 1.8, 0, 55)
	end

	-- camera spray / bow wave only when close to the water and moving
	if camera then
		local dist = (camera.CFrame.Position - model.PrimaryPart.Position).Magnitude
		for _, e in ipairs(smoke) do
			e.LockedToPart = false
		end
		if dist > 1200 then
			-- far away: turn the detail emitters off, keep the funnel banner
			for _, e in ipairs(steam) do
				e.Enabled = false
			end
		end
	end
end)
