--!nonstrict
--[[
	BoatClient.lua -- client input and the helm readout.  Put in StarterPlayerScripts.

	Controls (while your character is sitting in a boat seat):

	  W / S        throttle ahead / astern  (rowing: row / stop)
	  A / D        helm to port / starboard (rowing: pull harder that bank)
	  Shift+W      full ahead
	  E            engine start / stop      (steam cutter only)
	  R            sound the whistle         (steam cutter only)

	The two boats share the remote but send different messages, matching the
	controllers' APIs.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local player = Players.LocalPlayer
local remote = ReplicatedStorage:WaitForChild("BoatControl")

local aboardId = nil      -- boat id we are sitting in, or nil
local throttle = 0
local helm = 0
local engineOn = false

remote.OnClientEvent:Connect(function(kind, boatId)
	if kind == "aboard" then
		aboardId = boatId
	end
end)

local function send(kind, value)
	if aboardId then
		remote:FireServer(aboardId, kind, value)
	end
end

local function isSteam()
	return aboardId == "steam_cutter_1888"
end

UserInputService.InputBegan:Connect(function(input, processed)
	if processed then return end
	if input.KeyCode == Enum.KeyCode.E and isSteam() then
		engineOn = not engineOn
		send("start", engineOn and 1 or 0)
		if not engineOn then send("stop", 1) end
	elseif input.KeyCode == Enum.KeyCode.R and isSteam() then
		send("whistle", 1)
	end
end)

-- Steering and throttle are integrated per frame so keyboard input feels
-- analogue rather than snapping to full deflection.
RunService.RenderStepped:Connect(function(dt)
	if not aboardId then return end
	local up = UserInputService:IsKeyDown(Enum.KeyCode.W)
	local down = UserInputService:IsKeyDown(Enum.KeyCode.S)
	local left = UserInputService:IsKeyDown(Enum.KeyCode.A)
	local right = UserInputService:IsKeyDown(Enum.KeyCode.D)
	local boost = UserInputService:IsKeyDown(Enum.KeyCode.LeftShift)

	if isSteam() then
		local target = 0
		if up then target = boost and 1 or 0.55 end
		if down then target = boost and -0.6 or -0.3 end
		throttle = throttle + (target - throttle) * math.min(1, dt * 2.5)
		send("throttle", throttle)
	else
		-- rowing: W sets the stroke, releasing it lets the boat carry her way
		throttle = up and (boost and 1 or 0.7) or 0
	end

	local helmTarget = 0
	if left then helmTarget = -1 end
	if right then helmTarget = 1 end
	helm = helm + (helmTarget - helm) * math.min(1, dt * 4)
	send("helm", helm)

	if not isSteam() then
		send("row", up and 1 or 0)
		if up then send("power", boost and 1 or 0.7) end
	end
end)

-- simple on-screen readout
local gui = Instance.new("ScreenGui")
gui.Name = "BoatHUD"
gui.ResetOnSpawn = false
gui.Parent = player:WaitForChild("PlayerGui")
local label = Instance.new("TextLabel")
label.Size = UDim2.fromOffset(320, 28)
label.Position = UDim2.new(0, 16, 1, -60)
label.BackgroundTransparency = 0.55
label.BackgroundColor3 = Color3.new(0, 0, 0)
label.TextColor3 = Color3.new(1, 1, 1)
label.Font = Enum.Font.Code
label.TextSize = 16
label.TextXAlignment = Enum.TextXAlignment.Left
label.Text = ""
label.Parent = gui

RunService.RenderStepped:Connect(function()
	if aboardId then
		gui.Enabled = true
		local mode
		if isSteam() then
			mode = engineOn and "ENGINE RUNNING" or "ENGINE STOPPED"
		else
			mode = throttle > 0.05 and "PULLING" or "OARS TRAILED"
		end
		label.Text = string.format("%s  |  %s  |  helm %+.2f  throttle %+.2f",
			aboardId == "steam_cutter_1888" and "25ft STEAM CUTTER" or "25ft ROWING CUTTER",
			mode, helm, throttle)
	else
		gui.Enabled = false
	end
end)
