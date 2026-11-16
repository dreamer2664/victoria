--!nonstrict
--[[
	SteamCutter.lua -- server controller for the 25 ft steam cutter.

	Behaviour modelled on a real coal-fired launch plant:

	  * ENGINE START is not instant: the fire is lit, the boiler raises steam
	    (a pressure ramp), and only then does the screw turn.  Starting from
	    cold takes several seconds and is accompanied by smoke and a steam
	    jet from the safety valve.
	  * THROTTLE is the regulator opening: the screw's rpm follows the
	    throttle with inertia, and thrust follows rpm.
	  * REVERSE uses the Stephenson link: throttle below zero swings the
	    reversing lever and the screw turns the other way at reduced power.
	  * STOP shuts the regulator, the screw idles down and the fire is drawn.
	  * STEERING turns the rudder; the tiller is animated to match, and the
	    boat only answers the helm when there is water flowing past the rudder.

	Controls arrive from BoatClient through the shared "BoatControl" remote.
]]

local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Config = require(script.Parent.Config)
local Effects = require(script.Parent.Effects)
local Hydrodynamics = require(script.Parent.Hydrodynamics)
local WaterSurface = require(script.Parent.WaterSurface)
local BoatRig = require(script.Parent.BoatRig)

local SteamCutter = {}
SteamCutter.__index = SteamCutter

local STATE = { OFF = "off", RAISING = "raising", RUNNING = "running", STOPPING = "stopping" }

function SteamCutter.new(model, manifest)
	local self = setmetatable({}, SteamCutter)
	self.model = model
	self.manifest = manifest
	self.cfg = Config.BOATS.steam_cutter_1888
	self.state = STATE.OFF
	self.pressure = 0            -- 0..1
	self.throttle = 0
	self.helm = 0
	self.rpm = 0
	self.startTimer = 0
	self.driver = nil

	self.root = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart")
	assert(self.root, "steam cutter model needs a PrimaryPart")

	local rig = BoatRig.rigScrew(model, self.root, manifest)
	self.screw = rig.screw
	self.screwMotor = rig.screwMotor
	self.rudder = rig.rudder
	self.rudderMotor = rig.rudderMotor
	self.screwBase = self.screwMotor and self.screwMotor.C0 or CFrame.new()
	self.rudderBase = self.rudderMotor and self.rudderMotor.C0 or CFrame.new()
	self.screwAngle = 0
	self.rudderAngle = 0

	self.hydro = Hydrodynamics.new(self.root, {
		length = self.cfg.loa_m / Config.M_PER_STUD,
		beam = self.cfg.beam_m / Config.M_PER_STUD,
		draft = self.cfg.draft_m / Config.M_PER_STUD,
		mass = self.root.AssemblyMass,
		maxThrust = self.cfg.max_thrust_n * 0.06,   -- Roblox force units
		steerRateDeg = self.cfg.steer_rate_deg,
	})
	WaterSurface.ignore(model)

	-- effects
	local funnel = model:FindFirstChild("FunnelTip", true)
	if funnel then
		funnel = funnel:IsA("Attachment") and funnel or funnel:FindFirstChildWhichIsA("Attachment")
	end
	if funnel then
		self.smoke = Effects.funnelSmoke(funnel)
	else
		warn("steam cutter: no FunnelTip attachment; smoke disabled")
	end
	self.wash = nil

	self.connections = {}
	table.insert(self.connections, RunService.Heartbeat:Connect(function(dt)
		self:step(dt)
	end))

	return self
end

function SteamCutter:setDriver(player)
	self.driver = player
end

--- Handle a control message from a player.
function SteamCutter:control(player, kind, value)
	if player and self.driver and player ~= self.driver then
		return
	end
	if kind == "throttle" then
		if self.state == STATE.RUNNING or self.state == STATE.RAISING then
			self.throttle = math.clamp(value, -1, 1)
		end
	elseif kind == "helm" then
		self.helm = math.clamp(value, -1, 1)
	elseif kind == "start" then
		if self.state == STATE.OFF then
			self.state = STATE.RAISING
			self.startTimer = 0
		end
	elseif kind == "stop" then
		if self.state == STATE.RUNNING or self.state == STATE.RAISING then
			self.state = STATE.STOPPING
			self.throttle = 0
		end
	end
end

function SteamCutter:step(dt)
	WaterSurface.step(dt)

	if self.state == STATE.RAISING then
		self.startTimer = self.startTimer + dt
		self.pressure = math.clamp(self.startTimer / self.cfg.engine_start_s, 0, 1)
		if self.smoke then
			self.smoke.Rate = 6 + 18 * self.pressure
		end
		if self.startTimer >= self.cfg.engine_start_s then
			self.state = STATE.RUNNING
		end
	elseif self.state == STATE.RUNNING then
		self.pressure = math.min(1, self.pressure + dt * 0.2)
		if self.smoke then
			self.smoke.Rate = 10 + 26 * math.abs(self.throttle) * self.pressure
		end
	elseif self.state == STATE.STOPPING then
		self.pressure = math.max(0, self.pressure - dt * 0.35)
		if self.smoke then
			self.smoke.Rate = math.max(0, self.smoke.Rate - dt * 12)
		end
		if self.pressure <= 0.01 then
			self.state = STATE.OFF
			self.throttle = 0
		end
	else
		self.pressure = math.max(0, self.pressure - dt * 0.5)
		if self.smoke then self.smoke.Rate = 0 end
	end

	-- screw rpm follows the regulator with inertia
	local targetRpm = self.throttle * self.cfg.prop_max_rpm * self.pressure
	self.rpm = self.rpm + (targetRpm - self.rpm) * math.min(1, dt * 1.6)

	-- Turn the screw and the rudder through their Motor6D joints, not by
	-- writing CFrame.  BoatRig binds both parts with a Motor6D, and a part that
	-- a joint is driving cannot also be moved by hand: the two fight each other
	-- one frame apart, for as long as the boat exists.  Each joint is rebuilt
	-- from its rest pose every frame, so the angles are absolute and cannot
	-- accumulate.
	self.screwAngle = (self.screwAngle or 0) + math.rad(self.rpm * 6) * dt
	if self.screwMotor then
		self.screwMotor.C0 = self.screwBase * CFrame.Angles(0, 0, self.screwAngle)
	end
	if self.rudderMotor then
		local target = self.helm * math.rad(32)
		self.rudderAngle = (self.rudderAngle or 0)
			+ (target - (self.rudderAngle or 0)) * math.min(1, dt * 5)
		self.rudderMotor.C0 = self.rudderBase * CFrame.Angles(0, self.rudderAngle, 0)
	end

	-- the hull only answers the helm with water flowing past the rudder, and
	-- the screw's thrust is what Hydrodynamics uses
	local thrustFraction = self.rpm / self.cfg.prop_max_rpm
	self.hydro:setThrottle(thrustFraction)
	self.hydro:setHelm(self.helm)
	self.hydro:update(dt)

	if self.wash then
		self.wash.Rate = math.abs(thrustFraction) * 30
	end
end

function SteamCutter.newFromModel(model)
	local manifest = model:GetAttribute("BoatManifest")
	local m = manifest and require(ReplicatedStorage.Boats:FindFirstChild("Manifest_" .. manifest))
		or require(script.Parent.Manifest_steam_cutter_1888)
	return SteamCutter.new(model, m)
end

return SteamCutter
