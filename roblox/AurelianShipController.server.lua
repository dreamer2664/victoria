--[[
    SS AURELIAN — SHIP CONTROLLER  (Roblox / ServerScriptService)

    Master state machine for the ship.  Every other script reads or writes the
    Attributes on this model, so propulsion, telegraph, helm, lighting and
    docking all stay in step without a spaghetti of RemoteEvents.

    CONFIG is calibrated from the Blender machinery module:
        propeller pitch 6.90 m, engine 62 rpm at 14 000 IHP, service 19.3 kn
    At 1 stud = 0.28 m the hull is 592.9 studs long, 65.7 studs abeam.

    Place this script inside a Model named "Aurelian" in Workspace.
    Set the model's PrimaryPart to a small invisible part at the ship's centre.
]]

local Ship = script.Parent
local RunService = game:GetService("RunService")

------------------------------------------------------------------ CONFIG
local CONFIG = {
	METRES_PER_STUD   = 0.28,
	LOA_M             = 166.0,
	BEAM_M            = 18.4,
	DRAFT_M           = 6.50,
	-- propulsion
	PROP_PITCH_M      = 6.90,
	PROP_RPM_MAX      = 62.0,
	PROP_DIA_M        = 5.30,
	ENGINE_IHP        = 14000,
	SPEED_SERVICE_KN  = 19.3,
	SPEED_MAX_KN      = 20.2,
	-- hydrodynamics (calibrated so 62 rpm gives 19.3 kn)
	HULL_RESISTANCE   = 0.00068,
	-- helm
	RUDDER_MAX_DEG    = 35.0,
	TURN_RATE_DEG_S   = 0.62,
	RUDDER_RATE_DEG_S = 9.0,
	-- sea keeping
	PITCH_MAX_DEG     = 1.9,
	ROLL_MAX_DEG      = 3.4,
	HEAVE_M           = 0.42,
}

local STUDS = 1 / CONFIG.METRES_PER_STUD

------------------------------------------------------------------ STATE
local State = {
	throttle      = 0.0,   -- 0..1 ordered from the telegraph
	shaftRPM      = 0.0,   -- actual, lags the order
	shaftAngle    = 0.0,
	speedKn       = 0.0,
	headingDeg    = 0.0,
	rudderDeg     = 0.0,
	rudderOrder   = 0.0,
	engineTelegraph = "Finished with Engines",
	booster       = false,
	mooringsClear = true,
}

local SHIP_ATTRS = {
	Throttle = 0, ShaftRPM = 0, SpeedKn = 0, Heading = 0,
	RudderAngle = 0, Telegraph = "Finished with Engines",
	BoilerPressure = 0, EngineIHP = 0, SmokeIntensity = 0,
	MooringsClear = true, EngineRunning = false,
}

local function initAttributes()
	for k, v in pairs(SHIP_ATTRS) do
		Ship:SetAttribute(k, v)
	end
end

------------------------------------------------------------------ TELEGRAPH
-- Engine order telegraph: 9 positions each way, as on an 1889 bridge.
local TELEGRAPH_STEPS = {
	{ name = "Full Ahead",      throttle = 1.00 },
	{ name = "Three-Quarter",   throttle = 0.75 },
	{ name = "Half Ahead",      throttle = 0.50 },
	{ name = "Slow Ahead",      throttle = 0.25 },
	{ name = "Dead Slow Ahead", throttle = 0.10 },
	{ name = "Stand By",        throttle = 0.00 },
	{ name = "Dead Slow Astern",throttle = -0.10 },
	{ name = "Slow Astern",     throttle = -0.25 },
	{ name = "Half Astern",     throttle = -0.50 },
	{ name = "Full Astern",     throttle = -0.80 },
}

local TELEGRAPH_INDEX = {}
for i, s in ipairs(TELEGRAPH_STEPS) do
	TELEGRAPH_INDEX[s.name] = i
end

function State:orderTelegraph(replyName)
	local i = TELEGRAPH_INDEX[replyName]
	if not i then
		warn("Aurelian: unknown telegraph order " .. tostring(replyName))
		return
	end
	if not State.mooringsClear and TELEGRAPH_STEPS[i].throttle > 0.15 then
		State.engineTelegraph = "Moorings held - cast off first"
		Ship:SetAttribute("Telegraph", State.engineTelegraph)
		return
	end
	State.engineTelegraph = replyName
	State.throttle = TELEGRAPH_STEPS[i].throttle
	Ship:SetAttribute("Telegraph", replyName)
	Ship:SetAttribute("Throttle", State.throttle)
	Ship:SetAttribute("EngineRunning", math.abs(State.throttle) > 0.001)
end

------------------------------------------------------------------ MAIN LOOP
local function step(dt, t)
	-- ---- shaft speed: engine lag ~ 12 s, matches reciprocating plant ------
	local targetRPM = State.throttle * CONFIG.PROP_RPM_MAX
	local lag = (math.abs(targetRPM) > math.abs(State.shaftRPM)) and 0.10 or 0.16
	State.shaftRPM = State.shaftRPM + (targetRPM - State.shaftRPM) * math.min(1, dt / 12.0) * (lag / 0.10)
	if math.abs(State.shaftRPM) < 0.15 then State.shaftRPM = 0 end

	-- ---- speed from propeller law ---------------------------------------
	-- advance per rev (slip 12% at service speed, more when accelerating)
	local advanceKn = (State.shaftRPM * CONFIG.PROP_PITCH_M * 60.0) / 1852.0
	local slip = 0.12 + 0.10 * (1.0 - math.min(1.0, math.abs(State.shaftRPM) / CONFIG.PROP_RPM_MAX))
	local targetKn = advanceKn * (1.0 - slip)
	State.speedKn = State.speedKn + (targetKn - State.speedKn) * math.min(1, dt / 26.0)

	-- ---- helm ------------------------------------------------------------
	local dR = State.rudderOrder - State.rudderDeg
	local maxStep = CONFIG.RUDDER_RATE_DEG_S * dt
	State.rudderDeg = State.rudderDeg + math.clamp(dR, -maxStep, maxStep)

	-- turn rate scales with speed and rudder angle (induced-flow model)
	local speedFactor = math.clamp(math.abs(State.speedKn) / CONFIG.SPEED_SERVICE_KN, 0, 1.35)
	local turn = (State.rudderDeg / CONFIG.RUDDER_MAX_DEG) * CONFIG.TURN_RATE_DEG_S * speedFactor
	State.headingDeg = (State.headingDeg + turn * dt
		* (State.speedKn >= 0 and 1 or -1)) % 360

	-- ---- publish ---------------------------------------------------------
	Ship:SetAttribute("ShaftRPM", math.abs(State.shaftRPM))
	Ship:SetAttribute("SpeedKn", State.speedKn)
	Ship:SetAttribute("Heading", State.headingDeg)
	Ship:SetAttribute("RudderAngle", State.rudderDeg)
	Ship:SetAttribute("EngineIHP", math.floor(
		CONFIG.ENGINE_IHP * math.abs(State.shaftRPM) / CONFIG.PROP_RPM_MAX + 0.5))
	Ship:SetAttribute("BoilerPressure", math.floor(11.0 *
		math.clamp(0.25 + 0.75 * math.abs(State.shaftRPM) / CONFIG.PROP_RPM_MAX, 0, 1) * 10) / 10)
	Ship:SetAttribute("SmokeIntensity",
		math.clamp(math.abs(State.shaftRPM) / CONFIG.PROP_RPM_MAX * 1.15, 0, 1))
	Ship:SetAttribute("MooringsClear", State.mooringsClear)

	-- ---- move the ship in world space ------------------------------------
	local root = Ship.PrimaryPart
	if root then
		local hdg = math.radians(State.headingDeg)
		local vStuds = State.speedKn * 1852.0 / 3600.0 * STUDS
		local dir = Vector3.new(math.sin(hdg), 0, -math.cos(hdg))
		local target = root.Position + dir * vStuds * dt
		-- idle motion: pitch/roll/heave from the sea state, mast height
		local heave = math.sin(t * 0.55) * CONFIG.HEAVE_M * STUDS * 0.30
		local pitch = math.radians(math.sin(t * 0.47 + 0.6) * CONFIG.PITCH_MAX_DEG * speedFactor)
		local roll  = math.radians(math.sin(t * 0.39 + 1.9) * CONFIG.ROLL_MAX_DEG)
		target = target + Vector3.new(0, heave, 0)
		local cf = CFrame.new(target) * CFrame.Angles(pitch, hdg, roll)
		root.CFrame = root.CFrame:Lerp(cf, math.min(1, dt * 8.0))
		State.shaftAngle = (State.shaftAngle + State.shaftRPM * 6.0 * dt) % 360
		Ship:SetAttribute("ShaftAngle", State.shaftAngle)
	end
end

------------------------------------------------------------------ PUBLIC API
Ship:SetAttribute("AurelianReady", false)
initAttributes()

-- Expose control functions as attributes-driven BindableEvents so other
-- scripts never need to call into this module directly.
local bindables = Instance.new("Folder")
bindables.Name = "ShipControl"
bindables.Parent = Ship
local function bindable(name)
	local b = Instance.new("BindableFunction")
	b.Name = name
	b.Parent = bindables
	return b
end
bindable("OrderTelegraph").OnInvoke = function(name)
	State:orderTelegraph(name)
end
bindable("SetRudder").OnInvoke = function(deg)
	State.rudderOrder = math.clamp(deg, -CONFIG.RUDDER_MAX_DEG, CONFIG.RUDDER_MAX_DEG)
end
bindable("CenterRudder").OnInvoke = function()
	State.rudderOrder = 0
end
bindable("SetMooringsClear").OnInvoke = function(v)
	State.mooringsClear = v and true or false
end

local acc = 0
RunService.Heartbeat:Connect(function(dt)
	acc = acc + dt
	-- fixed 30 Hz physics step so behaviour is frame-rate independent
	while acc > 1.0 / 30.0 do
		step(1.0 / 30.0, os.clock())
		acc = acc - 1.0 / 30.0
	end
end)

Ship:SetAttribute("AurelianReady", true)
print(("[Aurelian] ship controller online: %.1f m LOA, %.1f studs"):format(
	CONFIG.LOA_M, CONFIG.LOA_M * STUDS))
