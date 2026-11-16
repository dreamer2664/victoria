--!nonstrict
--[[
	RowingCutter.lua -- server controller for the 25 ft clinker rowing cutter.

	The boat is pulled, not driven.  Ten oars are double-banked (two men to a
	thwart, one oar each -- the Service arrangement described in the 1905
	establishment tables).  Each oar is animated through a real stroke:

	    catch  -- blades turned square, oars swung forward
	    drive  -- blades buried, body swing, boat accelerates
	    finish -- blades released at the end of the stroke
	    recover-- blades feathered flat and swung forward again

	The boat has no rudder that matters at pulling speed, so she is STEERED BY
	ROWING: pulling harder on one bank than the other yaws her.  That is the
	control scheme -- the left/right input biases the stroke power between the
	port and starboard banks, exactly as a coxswain would call it.

	Momentum is real: the hull is heavy, so she carries her way between
	strokes and takes several lengths to answer the oars.
]]

local RunService = game:GetService("RunService")

local Config = require(script.Parent.Config)
local Effects = require(script.Parent.Effects)
local Hydrodynamics = require(script.Parent.Hydrodynamics)
local WaterSurface = require(script.Parent.WaterSurface)
local BoatRig = require(script.Parent.BoatRig)

local RowingCutter = {}
RowingCutter.__index = RowingCutter

local PHASE = { CATCH = "catch", DRIVE = "drive", FINISH = "finish", RECOVER = "recover" }

--- `cfgId` selects the boat's own numbers from Config.BOATS.  Without it the
--- module used the rowing cutter's dimensions for every boat that shares this
--- stroke engine, which meant the 27 ft whaler was driven as a 25 ft cutter:
--- wrong length (so wrong hull speed and wrong probe spread), wrong mass, wrong
--- steering authority.
function RowingCutter.new(model, manifest, cfgId)
	local self = setmetatable({}, RowingCutter)
	self.model = model
	self.manifest = manifest
	local id = cfgId or model:GetAttribute("BoatId") or "rowing_cutter_25ft"
	self.cfg = Config.BOATS[id] or Config.BOATS.rowing_cutter_25ft
	self.singleBanked = self.cfg.single_banked == true

	self.root = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart")
	assert(self.root, "rowing cutter model needs a PrimaryPart")

	self.oars = BoatRig.rigOars(model, self.root, manifest)
	self.oarCount = #self.oars

	self.rowing = false
	self.power = 0             -- 0..1 effort
	self.helm = 0              -- -1..1 differential between banks
	self.phase = PHASE.RECOVER
	self.strokeT = 0
	self.strokeRate = 0.9      -- strokes per second at full effort
	self.crewAboard = 0

	self.hydro = Hydrodynamics.new(self.root, {
		length = self.cfg.loa_m / Config.M_PER_STUD,
		beam = self.cfg.beam_m / Config.M_PER_STUD,
		draft = self.cfg.draft_m / Config.M_PER_STUD,
		mass = self.root.AssemblyMass,
		maxThrust = 900 * 0.06,
		steerRateDeg = 9,
	})
	WaterSurface.ignore(model)

	-- spray at the bow once the boat has way on
	local bow = Instance.new("Attachment")
	bow.Name = "BowSpray"
	bow.Position = Vector3.new(self.cfg.loa_m * 0.42 * Config.STUD_PER_M, 0, 0)
	bow.Parent = self.root
	self.spray = Effects.bowSpray(bow)

	self.connections = {}
	table.insert(self.connections, RunService.Heartbeat:Connect(function(dt)
		self:step(dt)
	end))
	return self
end

function RowingCutter:control(player, kind, value)
	if kind == "row" then
		self.rowing = value and true or false
		self.power = self.rowing and (self.power > 0 and self.power or 0.7) or 0
	elseif kind == "power" then
		self.power = math.clamp(value, 0, 1)
	elseif kind == "helm" then
		self.helm = math.clamp(value, -1, 1)
	end
end

--- Animate one oar for the current stroke phase.
--- The oar's local +X runs outboard along the loom, so:
---   swing  = rotation about the boat's vertical axis (the stroke arc)
---   feather= rotation about the oar's own axis (blade flat/square)
function RowingCutter:poseOar(oar, swing, feather)
	if not oar.motor then return end
	-- rebuild the joint transform: swing about Y, feather about X
	oar.motor.Transform = CFrame.Angles(0, swing * oar.side, 0)
		* CFrame.Angles(feather, 0, 0)
end

--- The oar furthest aft on the boat -- the one a single-banked crew steers
--- with.  Positions are in the root's local space, where the bow is -Z.
function RowingCutter:aftmostOar()
	local best, bestZ = nil, -math.huge
	for _, oar in ipairs(self.oars) do
		local z = self.root.CFrame:PointToObjectSpace(oar.part.Position).Z
		if z > bestZ then best, bestZ = oar, z end
	end
	return best
end

function RowingCutter:step(dt)
	WaterSurface.step(dt)

	local rate = self.cfg.stroke_rate / 60 * (0.55 + 0.45 * self.power)
	if self.rowing and self.power > 0.02 then
		self.strokeT = self.strokeT + dt * rate
		if self.strokeT >= 1 then
			self.strokeT = self.strokeT - 1
			self.phase = PHASE.CATCH
		elseif self.strokeT < 0.18 then
			self.phase = PHASE.CATCH
		elseif self.strokeT < 0.62 then
			self.phase = PHASE.DRIVE
		elseif self.strokeT < 0.70 then
			self.phase = PHASE.FINISH
		else
			self.phase = PHASE.RECOVER
		end
	end

	-- oar angles for the phase (radians)
	local swing, feather
	local t = self.strokeT
	if self.phase == PHASE.CATCH then
		swing = math.rad(38) * (1 - t / 0.18)
		feather = 0
	elseif self.phase == PHASE.DRIVE then
		local f = (t - 0.18) / 0.44
		swing = math.rad(38) * (1 - f) - math.rad(34) * f
		feather = 0
	elseif self.phase == PHASE.FINISH then
		swing = math.rad(-34)
		feather = math.rad(80) * ((t - 0.62) / 0.08)
	else
		local f = (t - 0.70) / 0.30
		swing = math.rad(-34) + math.rad(72) * f
		feather = math.rad(80)
	end
	if not self.rowing or self.power <= 0.02 then
		swing = math.rad(8)   -- oars trailed, blades flat
		feather = math.rad(80)
	end

	for _, oar in ipairs(self.oars) do
		self:poseOar(oar, swing, feather)
	end

	-- thrust: only during the drive, scaled by the bank balance
	local driving = (self.phase == PHASE.DRIVE) and 1.0 or 0.0
	local push = self.power * driving
	if self.singleBanked then
		-- A single-banked boat (the whaler: three oars to port, two to
		-- starboard) cannot steer by pulling one bank harder -- there is no
		-- second bank to pull against.  She is steered from aft: the bow oar
		-- and the stroke oar hold water on one side, which swings the stern.
		self.hydro:setThrottle(push)
		self.sternOar = self.sternOar or self:aftmostOar()
		if self.sternOar then
			self:poseOar(self.sternOar, swing - self.helm * math.rad(22), feather)
		end
		self.hydro:setHelm(self.helm * 0.92)
	else
		-- differential: the bank the coxswain calls for pulls harder
		local portBias = math.clamp(1 + self.helm * self.cfg.steer_from_bank, 0.2, 1.6)
		local stbdBias = math.clamp(1 - self.helm * self.cfg.steer_from_bank, 0.2, 1.6)
		local meanBias = (portBias + stbdBias) * 0.5
		self.hydro:setThrottle(push * meanBias)
		self.hydro:setHelm(self.helm * 0.6 + (portBias - stbdBias) * 0.3)
	end
	self.hydro:update(dt)

	if self.spray then
		self.spray.Rate = math.clamp(math.abs(self.hydro.speed) * 2.2, 0, 26)
	end
end

function RowingCutter:knots()
	return self.hydro:knots()
end

return RowingCutter
