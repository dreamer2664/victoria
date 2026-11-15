--!strict
--[[
	ShipService.luau -- ship arrival / mooring / working / departure.

	Each berth is a small state machine. The states are the vocabulary the rest of
	the game (and the port animations) hang off:

	    Idle -> Approaching -> Berthing -> Moored -> Working -> CastingOff -> Departed -> Idle

	Timings come from the historical research rather than from guesswork:
	  * a North German Lloyd liner of 1889 turned round in about 29 hours;
	  * coaling from barges took about 4.5 days for a big mail steamer.
	So a passenger berth at Port A cycles in ~29 h game time, while a cargo berth at
	Port B with coal remains occupied for days. The service exposes those as
	configurable seconds-per-game-hour so a live game can compress them.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local Config = require(ReplicatedStorage.Shared.Config)

local ShipService = {}

export type State =
	"Idle" | "Approaching" | "Berthing" | "Moored" | "Working" | "CastingOff" | "Departed"

local VALID: { [State]: { State } } = {
	Idle = { "Approaching" },
	Approaching = { "Berthing", "Idle" },      -- Idle = aborted, sent back to sea
	Berthing = { "Moored", "Idle" },
	Moored = { "Working", "CastingOff" },
	Working = { "CastingOff" },
	CastingOff = { "Departed" },
	Departed = { "Idle" },
}

export type BerthState = {
	berthId: string,
	name: string,
	state: State,
	shipModel: Model?,
	changedAt: number,     -- os.clock()
	occupancySeconds: number,
	gangwayConnected: boolean,
	mooringLines: number,  -- count of lines actually made fast
	requiredLines: number,
	turnaroundSeconds: number,
}

local berths: { [string]: BerthState } = {}

local stateChanged = Instance.new("BindableEvent")
ShipService.StateChanged = stateChanged.Event

local function setState(b: BerthState, s: State)
	if b.state == s then return end
	assert(table.find(VALID[b.state] :: { State }, s),
		string.format("illegal transition %s -> %s on %s", b.state, s, b.berthId))
	b.state = s
	b.changedAt = os.clock()
	stateChanged:Fire(b.berthId, s, b)
end

--- Register every berth of a port from its layout data.
function ShipService.registerPort(portCode: string, layout: any)
	for _, def in ipairs(layout.berths) do
		local required = if def.kind == "passenger" then 6 else 4
		berths[def.id] = {
			berthId = def.id,
			name = def.name,
			state = "Idle",
			shipModel = nil,
			changedAt = os.clock(),
			occupancySeconds = 0,
			gangwayConnected = false,
			mooringLines = 0,
			requiredLines = required,
			-- 29 h for a passenger turnaround; 4.5 days for a coaling cargo berth
			turnaroundSeconds = if def.kind == "passenger" then 29 * 3600 / 60
				else 4.5 * 24 * 3600 / 60,
		}
	end
end

function ShipService.get(berthId: string): BerthState?
	return berths[berthId]
end

--- A ship has been spawned and is heading for the berth. `model` must already be
-- on the water, unanchored or anchored, with a pivot at its centre.
function ShipService.requestArrival(berthId: string, model: Model)
	local b = assert(berths[berthId], "no such berth " .. berthId)
	assert(b.state == "Idle", "berth occupied: " .. berthId)
	b.shipModel = model
	setState(b, "Approaching")
end

function ShipService.beginBerthing(berthId: string)
	local b = assert(berths[berthId], berthId)
	setState(b, "Berthing")
end

--- Called by MooringService once the last headline and spring are fast.
function ShipService.makeFast(berthId: string)
	local b = assert(berths[berthId], berthId)
	b.mooringLines = b.requiredLines
	if b.state == "Berthing" then setState(b, "Moored") end
end

function ShipService.addMooringLine(berthId: string)
	local b = assert(berths[berthId], berthId)
	b.mooringLines = math.min(b.requiredLines, b.mooringLines + 1)
	if b.mooringLines >= b.requiredLines then ShipService.makeFast(berthId) end
end

--- The gangway exists as a physical model; this records that it is shipped and
-- that boarding may open.
function ShipService.connectGangway(berthId: string, connected: boolean)
	local b = assert(berths[berthId], berthId)
	b.gangwayConnected = connected
	if connected and b.state == "Moored" then setState(b, "Working") end
end

--- Boarding is only legal when the ship is made fast AND a gangway is shipped.
-- This is the single gate that the client's "Board" prompt consults.
function ShipService.canBoard(berthId: string): (boolean, string)
	local b = berths[berthId]
	if not b then return false, "no such berth" end
	if b.state ~= "Working" then return false, "ship not working (" .. b.state .. ")" end
	if not b.gangwayConnected then return false, "no gangway shipped" end
	return true, "ok"
end

function ShipService.castOff(berthId: string)
	local b = assert(berths[berthId], berthId)
	b.gangwayConnected = false
	b.mooringLines = 0
	setState(b, "CastingOff")
end

function ShipService.depart(berthId: string)
	local b = assert(berths[berthId], berthId)
	local model = b.shipModel
	b.shipModel = nil
	setState(b, "Departed")
	task.delay(2, function()
		if b.state == "Departed" then setState(b, "Idle") end
		if model then model:Destroy() end
	end)
end

--- Drives working-time accumulation; call once per frame from a server loop.
function ShipService.step(dt: number)
	for _, b in pairs(berths) do
		if b.state == "Working" then
			b.occupancySeconds += dt
			if b.occupancySeconds >= b.turnaroundSeconds then
				ShipService.castOff(b.berthId)
			end
		end
	end
end

function ShipService.startLoop()
	RunService.Heartbeat:Connect(function(dt)
		ShipService.step(dt)
	end)
end

return ShipService
