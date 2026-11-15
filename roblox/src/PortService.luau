--!strict
--[[
	PortService.luau -- builds the interaction layer for a port from its layout data.

	Nothing here is placed by hand: every anchor position comes from PortLayoutA /
	PortLayoutB, which are themselves generated from the Blender meta JSON. Move a
	building in Blender, rebuild, re-run the generator, and the prompts follow.

	An "anchor" is an invisible Part with a ProximityPrompt. Anchors are grouped by
	interaction kind so gameplay systems can bind to them generically:

	    ticket_purchase   -> boarding flow
	    customs           -> clearance flow
	    gangway           -> boarding/disembarking
	    cargo             -> loading/unloading
	    mooring           -> lines / capstan
	    crane_operate     -> cargo handling
	    workshop / loft_work / slip_work / dock_floor_work -> job minigames
	    worker_gate       -> shift start / end
]]

local Players = game:GetService("Players")
local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(ReplicatedStorage.Shared.Config)

local PortService = {}

export type Anchor = {
	id: string,
	name: string,
	kind: string,
	part: BasePart,
	prompt: ProximityPrompt,
	pos: Vector3,        -- world studs
	radiusM: number,
}

local anchorsByPort: { [string]: { [string]: Anchor } } = {}

local PROMPT_STYLE: { [string]: { ActionText: string, ObjectText: string, Hold: number } } = {
	ticket_purchase = { ActionText = "Buy ticket", ObjectText = "Booking office", Hold = 0.4 },
	customs = { ActionText = "Present papers", ObjectText = "Customs", Hold = 1.0 },
	gangway = { ActionText = "Board", ObjectText = "Gangway", Hold = 0.6 },
	cargo = { ActionText = "Work cargo", ObjectText = "Cargo", Hold = 0.8 },
	mooring = { ActionText = "Take a turn", ObjectText = "Bollard", Hold = 0.5 },
	crane_operate = { ActionText = "Operate", ObjectText = "Crane", Hold = 1.2 },
	workshop = { ActionText = "Work", ObjectText = "Shop floor", Hold = 1.0 },
	loft_work = { ActionText = "Loft a frame", ObjectText = "Moulding loft", Hold = 1.5 },
	slip_work = { ActionText = "Shore up", ObjectText = "Building slip", Hold = 1.5 },
	dock_floor_work = { ActionText = "Dock work", ObjectText = "Dock floor", Hold = 1.5 },
	worker_gate = { ActionText = "Clock in", ObjectText = "Time office", Hold = 0.4 },
}

local function makeAnchor(parent: Instance, portCode: string, def: any): Anchor
	local radiusStuds = Config.mToStuds(def.radius or 5)

	local part = Instance.new("Part")
	part.Name = "Anchor_" .. def.id
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.Transparency = 1
	part.Size = Vector3.new(1, 1, 1)
	part.CFrame = CFrame.new(Config.toWorld(portCode, def.pos[1], def.pos[2], def.pos[3]))
	part.Parent = parent

	local style = PROMPT_STYLE[def.kind] or {
		ActionText = "Interact", ObjectText = def.name, Hold = 0.5,
	}

	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = style.ActionText
	prompt.ObjectText = def.name
	prompt.HoldDuration = style.Hold
	prompt.MaxActivationDistance = math.max(8, radiusStuds)
	prompt.RequiresLineOfSight = false
	prompt.Parent = part

	-- tag it so systems (and telemetry) can find anchors without a registry
	CollectionService:AddTag(part, "PortInteraction")
	part:SetAttribute("PortCode", portCode)
	part:SetAttribute("InteractionId", def.id)
	part:SetAttribute("InteractionKind", def.kind)

	return {
		id = def.id, name = def.name, kind = def.kind,
		part = part, prompt = prompt,
		pos = part.Position, radiusM = def.radius or 5,
	}
end

--- Build all interaction anchors for a port into `parent`.
function PortService.build(portCode: string, layout: any, parent: Instance): { [string]: Anchor }
	local folder = Instance.new("Folder")
	folder.Name = "Interactions_" .. portCode
	folder.Parent = parent

	local map: { [string]: Anchor } = {}
	for _, def in ipairs(layout.interactions) do
		map[def.id] = makeAnchor(folder, portCode, def)
	end
	anchorsByPort[portCode] = map
	return map
end

function PortService.get(portCode: string, interactionId: string): Anchor?
	local m = anchorsByPort[portCode]
	return m and m[interactionId] or nil
end

function PortService.ofKind(portCode: string, kind: string): { Anchor }
	local out = {}
	for _, a in pairs(anchorsByPort[portCode] or {}) do
		if a.kind == kind then table.insert(out, a) end
	end
	return out
end

--- Is `player` standing within the interaction's own radius? Anchors use
-- ProximityPrompt for reachability, but gameplay checks (e.g. "can I buy a
-- ticket here?") should use the designed radius, not the prompt distance.
function PortService.inRange(player: Player, anchor: Anchor): boolean
	local char = player.Character
	if not char then return false end
	local root = char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not root then return false end
	return (root.Position - anchor.pos).Magnitude <= Config.mToStuds(anchor.radiusM)
end

return PortService
