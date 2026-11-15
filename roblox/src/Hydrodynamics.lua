--!nonstrict
--[[
	Hydrodynamics.lua -- the shared floating/steering model for both boats.

	This is not a "hover at Y" cheat: the hull carries a set of buoyancy
	probes (one VectorForce each, applied at their real positions), so the boat
	floats at the draft published in interfaces/boats_spec.json, heels to a
	load, and pitches into a seaway.  Thrust is applied at the propeller/rudder
	position, lateral resistance is anisotropic (a hull resists sideways
	motion much more than forward motion), and yaw is resisted by a torque
	proportional to the angular velocity -- which is what gives both boats
	their heavy, unhurried turn.

	All numbers are in studs and Roblox mass units; the conversion from the
	metric design values happens in Config/BuildBoat.
]]

local WaterSurface = require(script.Parent.WaterSurface)

local Hydrodynamics = {}
Hydrodynamics.__index = Hydrodynamics

local G = 196.2

--- probe layout along the hull: fraction of length from bow, half-beam fraction
local PROBES = {
	{ 0.86, 0.0 }, { 0.62, 0.55 }, { 0.62, -0.55 },
	{ 0.30, 0.60 }, { 0.30, -0.60 }, { 0.08, 0.0 },
}

function Hydrodynamics.new(root, opts)
	local self = setmetatable({}, Hydrodynamics)
	self.root = root
	self.length = opts.length
	self.beam = opts.beam
	self.draft = opts.draft
	self.mass = opts.mass
	self.maxThrust = opts.maxThrust
	self.reverseFraction = opts.reverseFraction or 0.45
	self.steerRate = math.rad(opts.steerRateDeg or 15)

	self.throttle = 0          -- -1 .. 1 (commanded)
	self.helm = 0              -- -1 .. 1 (rudder / differential oars)
	self.yawRate = 0
	self.heading = 0
	self.speed = 0

	self.probes = {}
	for i, p in ipairs(PROBES) do
		local att = Instance.new("Attachment")
		att.Name = string.format("Buoy%d", i)
		att.Position = Vector3.new(p[1] * self.length, 0, p[2] * self.beam * 0.5)
		att.Parent = root
		local vf = Instance.new("VectorForce")
		vf.Name = "Buoyancy"
		vf.Attachment0 = att
		vf.ApplyAtCenterOfMass = false
		vf.RelativeTo = Enum.ActuatorRelativeTo.World
		vf.Force = Vector3.zero
		vf.Parent = att
		self.probes[i] = { att = att, force = vf, frac = p[1] }
	end

	-- thrust applied at the stern, below the waterline
	local thrustAtt = Instance.new("Attachment")
	thrustAtt.Name = "ThrustPoint"
	thrustAtt.Position = Vector3.new(-0.42 * self.length, -self.draft * 0.7, 0)
	thrustAtt.Parent = root
	local thrust = Instance.new("VectorForce")
	thrust.Name = "Thrust"
	thrust.Attachment0 = thrustAtt
	thrust.RelativeTo = Enum.ActuatorRelativeTo.World
	thrust.Force = Vector3.zero
	thrust.Parent = thrustAtt
	self.thrust = thrust
	self.thrustAtt = thrustAtt

	-- yaw torque
	local torque = Instance.new("Torque")
	torque.Name = "YawTorque"
	torque.RelativeTo = Enum.ActuatorRelativeTo.World
	torque.Torque = Vector3.zero
	torque.Parent = root
	self.torque = torque

	self.clock = 0
	return self
end

--- Unit forward vector of the hull in world space.
function Hydrodynamics:forward()
	local look = self.root.CFrame.LookVector
	return Vector3.new(look.X, 0, look.Z).Unit
end

function Hydrodynamics:update(dt)
	self.clock = self.clock + dt
	local cf = self.root.CFrame
	local vel = self.root.AssemblyLinearVelocity
	local pos = cf.Position

	local fwd = self:forward()
	local right = Vector3.new(fwd.Z, 0, -fwd.X)

	self.speed = vel:Dot(fwd)

	-- ---------- buoyancy ----------
	local totalWeight = self.mass * G
	local perProbe = totalWeight / #self.probes
	local waterY = WaterSurface.heightAt(pos)
	local submergedAny = false

	for _, probe in ipairs(self.probes) do
		local wp = probe.att.WorldPosition
		local surface = waterY + WaterSurface.waveAt(wp, 0.14)
		local depth = surface - wp.Y + self.draft * 0.5
		if depth > 0 then
			submergedAny = true
			local submergedFrac = math.clamp(depth / (self.draft * 1.15), 0, 1.25)
			-- spring: displaced water weight + vertical damping
			local f = perProbe * submergedFrac * 1.15
			local vdamp = (vel.Y - (probe.att.CFrame:VectorToWorldSpace(Vector3.yAxis)).Y * 0) * 0.35
			f = f - vdamp * perProbe * 0.06
			probe.force.Force = Vector3.new(0, math.max(0, f), 0)
		else
			probe.force.Force = Vector3.zero
		end
	end

	if not submergedAny then
		-- aeroplane mode: no drive while out of the water
		self.thrust.Force = Vector3.zero
		self.torque.Torque = Vector3.zero
		return
	end

	-- ---------- propulsion ----------
	local thrustMagnitude = self.throttle * self.maxThrust
	if self.throttle < 0 then
		thrustMagnitude = self.throttle * self.maxThrust * self.reverseFraction
	end
	-- thrust falls away as the hull approaches hull speed
	local speedFactor = math.clamp(1 - math.abs(self.speed) / (self.length * 1.35), 0.15, 1)
	self.thrust.Force = fwd * thrustMagnitude * speedFactor

	-- ---------- anisotropic hull resistance ----------
	local vLong = fwd * vel:Dot(fwd)
	local vLat = right * vel:Dot(right)
	local dragLong = -vLong * math.abs(vLong) * 0.09 * self.mass * 0.02
	local dragLat = -vLat * math.abs(vLat) * 0.85 * self.mass * 0.02
	local dragForce = dragLong + dragLat - Vector3.new(0, 0, 0)
	if dragForce.Magnitude > 0 then
		-- fold drag into the stern probe so it acts below the waterline
		self.thrust.Force = self.thrust.Force + dragForce
	end

	-- ---------- steering ----------
	-- a rudder (or a stronger bank of oars) turns the boat in proportion to
	-- the water flowing past it: no way on, no steering.
	local authority = math.clamp(math.abs(self.speed) / (self.length * 0.55), 0, 1)
	local targetYaw = self.helm * self.steerRate * authority * (self.speed >= 0 and 1 or -1)
	local angVel = self.root.AssemblyAngularVelocity
	local yawNow = angVel.Y
	-- proportional + damping torque
	local torqueY = (targetYaw - yawNow) * self.mass * 12
	self.torque.Torque = Vector3.new(0, torqueY, 0)
end

function Hydrodynamics:setThrottle(t)
	self.throttle = math.clamp(t, -1, 1)
end

function Hydrodynamics:setHelm(h)
	self.helm = math.clamp(h, -1, 1)
end

function Hydrodynamics:knots()
	return math.abs(self.speed) * 0.28 * 1.94384
end

return Hydrodynamics
