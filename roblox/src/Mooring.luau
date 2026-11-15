--!strict
--[[
	Mooring.luau -- lines and gangways between a ship and the quay.

	Mooring is the part of port work that is easiest to fake and most worth getting
	right, because it is what the whole berth design exists to permit. A ship is held
	by headline, sternline and springs; the model here makes the player take each
	line to an actual bollard, and refuses to let the ship be "moored" until the
	required number of lines is fast.

	Nothing is attached to a moving ship with a rigid weld: lines are RopeConstraints
	from a bollard to a ship-side cleat, which keeps them visually correct while the
	ship settles against the quay.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)

local Mooring = {}

export type LineKind = "headline" | "sternline" | "spring" | "breastline"

--- Where a line goes, as a fraction along the ship's length (0 = stern, 1 = bow)
-- and which side of the quay it is made fast to.
export type LineSpec = {
	kind: LineKind,
	shipFraction: number,   -- 0..1 along the hull
	quayOffsetM: number,    -- metres from the berth centreline, +ve = toward the ship
}

-- A liner is held by head, stern, two springs and breast lines; four lines is the
-- minimum the service will accept before allowing "Moored".
Mooring.DEFAULT_LINES = {
	{ kind = "headline", shipFraction = 0.97, quayOffsetM = 6 },
	{ kind = "headline", shipFraction = 0.93, quayOffsetM = 10 },
	{ kind = "sternline", shipFraction = 0.03, quayOffsetM = 6 },
	{ kind = "sternline", shipFraction = 0.07, quayOffsetM = 10 },
	{ kind = "spring", shipFraction = 0.62, quayOffsetM = 6 },
	{ kind = "spring", shipFraction = 0.38, quayOffsetM = 6 },
} :: { LineSpec }

local LINE_COLOURS: { [LineKind]: Color3 } = {
	headline = Color3.fromRGB(196, 176, 128),
	sternline = Color3.fromRGB(196, 176, 128),
	spring = Color3.fromRGB(176, 150, 104),
	breastline = Color3.fromRGB(210, 190, 150),
}

local function makeRope(a: BasePart, b: BasePart, kind: LineKind): RopeConstraint
	local rope = Instance.new("RopeConstraint")
	rope.Attachment0 = a:FindFirstChildOfClass("Attachment")
	rope.Attachment1 = b:FindFirstChildOfClass("Attachment")
	rope.Length = (a.Position - b.Position).Magnitude / Config.STUDS_PER_METRE
	rope.Thickness = 0.35
	rope.Color = LINE_COLOURS[kind]
	rope.Visible = true
	rope.Name = "Line_" .. kind
	return rope
end

local function cleatAt(part: BasePart, localOffset: Vector3): Attachment
	local att = Instance.new("Attachment")
	att.Position = localOffset
	att.Name = "Cleat"
	att.Parent = part
	return att
end

--- Ship a gangway between a quay anchor and a ship's rail.
-- The gangway is a real, walkable model: a Part with a deck you can stand on and
-- invisible railings, tilted to the freeboard of the ship.
function Mooring.shipGangway(
	quayPart: BasePart,
	shipPart: BasePart,
	widthStuds: number,
	deckThickness: number
): Model
	local from = quayPart.Position
	local to = shipPart.Position
	local delta = to - from
	local flat = Vector3.new(delta.X, 0, delta.Z)
	local length = flat.Magnitude

	local gangway = Instance.new("Model")
	gangway.Name = "Gangway"

	local deck = Instance.new("Part")
	deck.Name = "Deck"
	deck.Anchored = true
	deck.Size = Vector3.new(length, deckThickness, widthStuds)
	deck.Material = Enum.Material.WoodPlanks
	deck.Color = Color3.fromRGB(96, 78, 56)
	deck.CFrame = CFrame.lookAt(from:Lerp(to, 0.5), to) * CFrame.Angles(0, 0, 0)
	-- tilt so the deck follows the ship's freeboard
	local rise = to.Y - from.Y
	deck.CFrame = CFrame.lookAt(from:Lerp(to, 0.5), to) * CFrame.Angles(0, 0, math.atan2(rise, length))
	deck.Parent = gangway

	-- rails: two boxes that read as the enclosed Victorian gangway screen
	for _, side in ipairs({ -1, 1 }) do
		local rail = Instance.new("Part")
		rail.Name = "Screen"
		rail.Anchored = true
		rail.CanCollide = true
		rail.Transparency = 0.35
		rail.Size = Vector3.new(length, Config.mToStuds(1.1), 0.2)
		rail.CFrame = deck.CFrame
			* CFrame.new(0, Config.mToStuds(0.55), side * (widthStuds / 2 - 0.1))
		rail.Material = Enum.Material.Metal
		rail.Color = Color3.fromRGB(64, 82, 68)
		rail.Parent = gangway
	end

	gangway.PrimaryPart = deck
	return gangway
end

--- Take a line from a ship cleat to a quay bollard.
function Mooring.makeLine(shipPart: BasePart, bollard: BasePart, spec: LineSpec): RopeConstraint
	local cleat = cleatAt(shipPart, Vector3.new(0, 0, 0))
	local bollardAtt = bollard:FindFirstChildOfClass("Attachment")
		or cleatAt(bollard, Vector3.new(0, 1, 0))
	local rope = makeRope(cleat.Parent :: BasePart, bollardAtt.Parent :: BasePart, spec.kind)
	rope.Parent = shipPart
	return rope
end

--- Where along a hull of `lengthM` a given line should be made fast, in studs
-- from the ship's centre, along its local Z (bow = +Z by project convention).
function Mooring.lineOffsetStuds(lengthM: number, spec: LineSpec): number
	return Config.mToStuds(lengthM) * (spec.shipFraction - 0.5)
end

return Mooring
