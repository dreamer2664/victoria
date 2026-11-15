--!strict
--[[
	PortServer.server.luau -- ServerScriptService entry point.

	Wiring order:
	  1. register both ports' berths with ShipService
	  2. build ProximityPrompt anchors from the generated layout modules
	  3. bind prompt handlers to the gameplay verbs
	  4. start the turnaround clock

	Place this as a Script in ServerScriptService. Modules go in ReplicatedStorage:
	  ReplicatedStorage/Shared/Config
	  ReplicatedStorage/Shared/PortLayoutA
	  ReplicatedStorage/Shared/PortLayoutB
	  ReplicatedStorage/Shared/PortService
	  ReplicatedStorage/Shared/ShipService
	  ReplicatedStorage/Shared/Mooring
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = require(Shared.Config)
local PortService = require(Shared.PortService)
local ShipService = require(Shared.ShipService)
local Mooring = require(Shared.Mooring)
local LayoutA = require(Shared.PortLayoutA)
local LayoutB = require(Shared.PortLayoutB)

local PortsFolder = Instance.new("Folder")
PortsFolder.Name = "Ports"
PortsFolder.Parent = workspace

-- ------------------------------------------------------------------ 1. berths
ShipService.registerPort("a", LayoutA)
ShipService.registerPort("b", LayoutB)

-- ------------------------------------------------------------------ 2. anchors
local anchorsA = PortService.build("a", LayoutA, PortsFolder)
local anchorsB = PortService.build("b", LayoutB, PortsFolder)

-- ------------------------------------------------------------------ player state
type PlayerState = {
	tickets: number,
	hasPapers: boolean,
	shift: string?,      -- "morning" / "afternoon" / nil
	onDuty: boolean,
}
local playerState: { [Player] : PlayerState } = {}

local function stateOf(player: Player): PlayerState
	local s = playerState[player]
	if not s then
		s = { tickets = 0, hasPapers = false, shift = nil, onDuty = false }
		playerState[player] = s
	end
	return s
end

Players.PlayerRemoving:Connect(function(p)
	playerState[p] = nil
end)

-- ------------------------------------------------------------------ 3. verbs
local function notify(player: Player, text: string)
	local gui = player:FindFirstChild("PlayerGui")
	if gui then
		local remote = gui:FindFirstChild("PortNotice") :: RemoteEvent?
		if remote then remote:FireClient(player, text) end
	end
	-- fall back to the chat so the prototype is legible without any UI
	print(string.format("[port] %s: %s", player.Name, text))
end

local handlers: { [string]: (Player, any, string) -> () } = {}

handlers.ticket_purchase = function(player, anchor, portCode)
	local s = stateOf(player)
	if not PortService.inRange(player, anchor) then
		notify(player, "You must be at the booking office window.")
		return
	end
	s.tickets += 1
	notify(player, ("Booked one passage. Tickets held: %d"):format(s.tickets))
end

handlers.customs = function(player, anchor)
	local s = stateOf(player)
	if s.tickets <= 0 then
		notify(player, "No passage booked - the officer waves you back.")
		return
	end
	s.hasPapers = true
	notify(player, "Papers stamped.")
end

handlers.gangway = function(player, anchor, portCode)
	-- the anchor carries the berth id it serves
	local berthId = anchor.part:GetAttribute("BerthId") or "A-B1"
	local s = stateOf(player)
	if s.tickets <= 0 then
		notify(player, "You have not booked a passage.")
		return
	end
	if not s.hasPapers then
		notify(player, "Customs have not cleared you.")
		return
	end
	local ok, why = ShipService.canBoard(berthId)
	if not ok then
		notify(player, "The gangway is not open: " .. why)
		return
	end
	-- teleport onto the ship's deck
	local b = ShipService.get(berthId)
	local model = b and b.shipModel
	local deck = model and model:FindFirstChild("BoardingPoint") :: BasePart?
	if deck then
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
		if root then root.CFrame = deck.CFrame + Vector3.new(0, 4, 0) end
	end
	notify(player, "Aboard. Mind the rail.")
end

handlers.mooring = function(player, anchor)
	local berthId = anchor.part:GetAttribute("BerthId")
	if not berthId then
		notify(player, "This bollard does not serve a berth.")
		return
	end
	local b = ShipService.get(berthId)
	if not b or not b.shipModel then
		notify(player, "Nothing alongside to make fast.")
		return
	end
	local bollard = anchor.part
	local lines = Mooring.DEFAULT_LINES
	local i = math.min(#lines, b.mooringLines + 1)
	local spec = lines[i]
	Mooring.makeLine(b.shipModel.PrimaryPart :: BasePart, bollard, spec)
	ShipService.addMooringLine(berthId)
	notify(player, ("%s fast. %d of %d lines."):format(spec.kind, b.mooringLines, b.requiredLines))
end

handlers.cargo = function(player, anchor)
	notify(player, "Slings away - cargo working.")
end

handlers.crane_operate = function(player, anchor)
	notify(player, "Crane under steam. Watch the load.")
end

handlers.worker_gate = function(player, anchor)
	local s = stateOf(player)
	s.onDuty = not s.onDuty
	notify(player, if s.onDuty then "Clocked in. Shift starts." else "Clocked out.")
end

for _, kind in ipairs({ "workshop", "loft_work", "slip_work", "dock_floor_work" }) do
	handlers[kind] = function(player, anchor)
		local s = stateOf(player)
		if not s.onDuty then
			notify(player, "Clock in at the time office first.")
			return
		end
		notify(player, "Working: " .. anchor.name)
	end
end

-- ------------------------------------------------------------------ prompt binding
local function bind(anchors: { [string]: any }, portCode: string)
	for _, anchor in pairs(anchors) do
		anchor.prompt.Triggered:Connect(function(player)
			local h = handlers[anchor.kind]
			if h then
				h(player, anchor, portCode)
			else
				notify(player, "Nothing to do there.")
			end
		end)
	end
end

bind(anchorsA, "a")
bind(anchorsB, "b")

-- Tag the mooring anchors with the berth they serve, so the verb knows which ship
-- it is tying up. Nearest berth by plan distance wins.
local function assignBerthToMoorings(portCode: string, layout: any)
	for _, a in pairs(PortService.ofKind(portCode, "mooring")) do
		local bestId, bestD = nil, math.huge
		for _, def in ipairs(layout.berths) do
			local r = def.rect
			local cx, cy = (r[1] + r[3]) / 2, (r[2] + r[4]) / 2
			local p = a.part.Position
			local q = Config.toWorld(portCode, cx, cy, 0)
			local d = (Vector3.new(p.X, 0, p.Z) - Vector3.new(q.X, 0, q.Z)).Magnitude
			if d < bestD then bestD, bestId = d, def.id end
		end
		if bestId then a.part:SetAttribute("BerthId", bestId) end
	end
end

assignBerthToMoorings("a", LayoutA)
assignBerthToMoorings("b", LayoutB)

-- ------------------------------------------------------------------ 4. clock
ShipService.startLoop()

print(("[port] %s and %s online: %d berths, %d interaction anchors.")
	:format(Config.PORTS.A.name, Config.PORTS.B.name,
		#LayoutA.berths + #LayoutB.berths,
		#LayoutA.interactions + #LayoutB.interactions))
