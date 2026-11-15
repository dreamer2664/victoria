--!strict
--[[
	PortClient.client.luau -- HUD and local feedback.

	Deliberately minimal: the port is meant to be read from the world, so the client
	only shows what the world cannot tell you -- your tickets, your clearance state,
	your shift, and which berths have a ship working. Put this as a LocalScript in
	StarterPlayerScripts.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = require(Shared.Config)
local ShipService = require(Shared.ShipService)

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

-- ------------------------------------------------------------------ notice channel
local noticeRemote = Instance.new("RemoteEvent")
noticeRemote.Name = "PortNotice"
noticeRemote.Parent = playerGui
    -- note: in a real place this lives in ReplicatedStorage and the server fires it;
    -- see docs/ROBLOX_SETUP.md, which ships the matching server-side remote.

-- ------------------------------------------------------------------ HUD
local screen = Instance.new("ScreenGui")
screen.Name = "PortHUD"
screen.ResetOnSpawn = false
screen.IgnoreGuiInset = true
screen.Parent = playerGui

local panel = Instance.new("Frame")
panel.AnchorPoint = Vector2.new(0, 0)
panel.Position = UDim2.new(0, 18, 0, 18)
panel.Size = UDim2.new(0, 290, 0, 118)
panel.BackgroundColor3 = Color3.fromRGB(24, 26, 24)
panel.BackgroundTransparency = 0.18
panel.BorderSizePixel = 0
panel.Parent = screen

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 4)
corner.Parent = panel

local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(150, 130, 92)
stroke.Thickness = 1
stroke.Transparency = 0.45
stroke.Parent = panel

local title = Instance.new("TextLabel")
title.BackgroundTransparency = 1
title.Position = UDim2.new(0, 12, 0, 8)
title.Size = UDim2.new(1, -24, 0, 20)
title.Font = Enum.Font.Garamond
title.TextSize = 15
title.TextXAlignment = Enum.TextXAlignment.Left
title.TextColor3 = Color3.fromRGB(226, 214, 184)
title.Text = "ALDERMOUTH  ·  HARBOUR BOARD"
title.Parent = panel

local body = Instance.new("TextLabel")
body.BackgroundTransparency = 1
body.Position = UDim2.new(0, 12, 0, 32)
body.Size = UDim2.new(1, -24, 1, -40)
body.Font = Enum.Font.Code
body.TextSize = 13
body.TextXAlignment = Enum.TextXAlignment.Left
body.TextYAlignment = Enum.TextYAlignment.Top
body.TextColor3 = Color3.fromRGB(196, 196, 188)
body.Text = ""
body.Parent = panel

-- ------------------------------------------------------------------ notices
local noticeQueue: { string } = {}
local noticeLabel = Instance.new("TextLabel")
noticeLabel.AnchorPoint = Vector2.new(0.5, 1)
noticeLabel.Position = UDim2.new(0.5, 0, 1, -70)
noticeLabel.Size = UDim2.new(0, 620, 0, 30)
noticeLabel.BackgroundTransparency = 1
noticeLabel.Font = Enum.Font.Garamond
noticeLabel.TextSize = 20
noticeLabel.TextColor3 = Color3.fromRGB(238, 230, 206)
noticeLabel.TextStrokeTransparency = 0.35
noticeLabel.Text = ""
noticeLabel.Parent = screen

noticeRemote.OnClientEvent:Connect(function(text: string)
	table.insert(noticeQueue, text)
end)

task.spawn(function()
	while true do
		if #noticeQueue > 0 then
			noticeLabel.Text = table.remove(noticeQueue, 1)
			task.wait(2.4)
			noticeLabel.Text = ""
			task.wait(0.2)
		else
			task.wait(0.2)
		end
	end
end)

-- ------------------------------------------------------------------ live panel
local function nearestPortCode(): string
	local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not root then return "a" end
	local best, bestD = "a", math.huge
	for code, p in pairs(Config.PORTS) do
		local d = (root.Position - p.originStuds).Magnitude
		if d < bestD then bestD, best = d, code end
	end
	return best
end

RunService.RenderStepped:Connect(function()
	local code = nearestPortCode()
	local berthIds = if code == "a"
		then { "A-B1", "A-B2", "A-B3", "A-B4" }
		else { "B-B1", "B-B2", "B-B3" }

	local lines = { "BERTHS" }
	for _, id in ipairs(berthIds) do
		local b = ShipService.get(id)
		if b then
			table.insert(lines, string.format("  %-6s %-12s %s", id, b.state,
				if b.gangwayConnected then "gangway out" else ""))
		end
	end
	body.Text = table.concat(lines, "\n")
end)
