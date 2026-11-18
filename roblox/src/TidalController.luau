--!strict
-- TidalController.luau -- server-authoritative tide clock and harbour kinematics.
-- Install in ReplicatedStorage/Shared. The matching local visual interpolator is
-- TidalClient.client.luau. See docs/TIDAL_SIMULATION.md for the model/tag contract.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage.Shared.Config)
local TideMath = require(ReplicatedStorage.Shared.TideMath)

local TidalController = {}

local UPDATE_INTERVAL = 0.10 -- 10 Hz authoritative transform + replicated tide sample
local IMPOUNDED_DOCK_LEVEL_M = 3.2
local BASE_PIVOT_ATTRIBUTE = "VictoriaTideBasePivot"

local TAGS = {
	pontoon = "VictoriaTidalPontoon",
	span = "VictoriaTidalGangwaySpan",
	bogie = "VictoriaTidalGangwayBogie",
	water = "VictoriaTidalWaterSurface",
}

-- Port A's operational envelope is the one specified by the Gen-III handoff.
-- Port B uses the documented 3.5 m semi-diurnal range, centred on mean water.
-- The 20 minute period is a gameplay compression; set it to taste in production.
local PORT_TIDES: { [string]: TideMath.TideSpec } = {
	a = { lowM = -2.0, highM = 3.5, periodSeconds = 20 * 60 },
	b = { lowM = -1.75, highM = 1.75, periodSeconds = 20 * 60 },
}

local states: { [Instance]: any } = {}
local started = false
local epoch = 0.0
local accumulator = 0.0
local heartbeatConnection: RBXScriptConnection? = nil

local function portCodeOf(instance: Instance): string
	return string.lower(tostring(instance:GetAttribute("PortCode") or ""))
end

local function readNumber(instance: Instance, attribute: string, fallback: number): number
	local value = instance:GetAttribute(attribute)
	return if typeof(value) == "number" then value else fallback
end

local function captureBasePivot(instance: Instance): CFrame?
	if not (instance:IsA("Model") or instance:IsA("BasePart")) then
		warn("[tide] Tagged object must be a Model or BasePart: " .. instance:GetFullName())
		return nil
	end
	local saved = instance:GetAttribute(BASE_PIVOT_ATTRIBUTE)
	if typeof(saved) == "CFrame" then
		return saved
	end
	local pivot = if instance:IsA("Model") then instance:GetPivot() else instance.CFrame
	instance:SetAttribute(BASE_PIVOT_ATTRIBUTE, pivot)
	return pivot
end

local function bindInstance(instance: Instance, kind: string)
	if states[instance] then return end
	local code = portCodeOf(instance)
	if PORT_TIDES[code] == nil then
		warn(string.format("[tide] %s needs PortCode='a' or 'b'", instance:GetFullName()))
		return
	end
	local basePivot = captureBasePivot(instance)
	if basePivot == nil then return end

	local state: any = {
		instance = instance,
		kind = kind,
		portCode = code,
		basePivot = basePivot,
		baseWaterM = readNumber(instance, "WaterDatumM", 0.0),
		referenceTideM = readNumber(instance, "ReferenceTideM", 0.0),
		shoreZ_M = readNumber(instance, "ShoreZ_M", Config.QUAY_Z_M),
		deckOffsetM = readNumber(instance, "PontoonDeckOffsetM", 1.5),
		spanM = readNumber(instance, "SpanLengthM", 36.0),
		directionX = readNumber(instance, "TideDirectionX", -1.0),
		hingeX_M = readNumber(instance, "HingeX_M", -30.0),
		hingeY_M = readNumber(instance, "HingeY_M", 75.0),
		hingeZ_M = readNumber(instance, "HingeZ_M", Config.QUAY_Z_M),
	}
	states[instance] = state
end

local function unbindInstance(instance: Instance)
	states[instance] = nil
end

local function pivotOf(instance: Instance): CFrame
	return if instance:IsA("Model") then instance:GetPivot() else (instance :: BasePart).CFrame
end

local function setPivot(instance: Instance, pivot: CFrame)
	if instance:IsA("Model") then
		instance:PivotTo(pivot)
	elseif instance:IsA("BasePart") then
		instance.CFrame = pivot
	end
end

local function gangwaySpec(state: any): TideMath.GangwaySpec
	return {
		shoreZ_M = state.shoreZ_M,
		deckOffsetM = state.deckOffsetM,
		spanM = state.spanM,
		referenceTideM = state.referenceTideM,
		directionX = state.directionX,
	}
end

local function targetPivot(state: any, tideM: number): CFrame
	local base = state.basePivot :: CFrame
	local instance = state.instance :: Instance
	local kind = state.kind :: string

	if kind == "pontoon" then
		local deltaY = Config.mToStuds(tideM - state.referenceTideM)
		return CFrame.new(0, deltaY, 0) * base
	elseif kind == "water" then
		local targetM = if instance:GetAttribute("WaterKind") == "impounded"
			then readNumber(instance, "WaterLevelM", IMPOUNDED_DOCK_LEVEL_M)
			else tideM
		local deltaY = Config.mToStuds(targetM - state.baseWaterM)
		return CFrame.new(0, deltaY, 0) * base
	elseif kind == "span" then
		local spec = gangwaySpec(state)
		local targetAngle = TideMath.gangwayAngle(tideM, spec)
		local referenceAngle = TideMath.referenceAngle(spec)
		local hinge = Config.toWorld(state.portCode, state.hingeX_M, state.hingeY_M, state.hingeZ_M)
		local rotation = CFrame.new(hinge)
			* CFrame.Angles(0, 0, targetAngle - referenceAngle)
			* CFrame.new(-hinge)
		return rotation * base
	elseif kind == "bogie" then
		local spec = gangwaySpec(state)
		local slideM = TideMath.bogieSlideM(tideM, spec)
		local deltaY = Config.mToStuds(tideM - state.referenceTideM)
		local deltaX = Config.mToStuds(slideM)
		return CFrame.new(deltaX, deltaY, 0) * base
	end

	return base
end

local function applyAll(tideByPort: { [string]: number })
	for instance, state in pairs(states) do
		if instance.Parent == nil then
			states[instance] = nil
		else
			local tideM = tideByPort[state.portCode]
			if tideM ~= nil then
				setPivot(instance, targetPivot(state, tideM))
			end
		end
	end
end

local function publish(tideByPort: { [string]: number })
	Workspace:SetAttribute("VictoriaTideA_M", tideByPort.a)
	Workspace:SetAttribute("VictoriaTideB_M", tideByPort.b)
	Workspace:SetAttribute("VictoriaTideEpoch", epoch)
	Workspace:SetAttribute("VictoriaTidePeriodA_S", PORT_TIDES.a.periodSeconds)
	Workspace:SetAttribute("VictoriaTidePeriodB_S", PORT_TIDES.b.periodSeconds)
end

function TidalController.levelAt(portCode: string, elapsedSeconds: number): number
	local spec = assert(PORT_TIDES[string.lower(portCode)], "unknown port tide " .. portCode)
	return TideMath.levelAt(spec, elapsedSeconds)
end

function TidalController.start()
	if started then return end
	started = true
	epoch = Workspace:GetServerTimeNow()

	for kind, tag in pairs(TAGS) do
		local registeredKind = kind
		for _, instance in ipairs(CollectionService:GetTagged(tag)) do
			bindInstance(instance, registeredKind)
		end
		CollectionService:GetInstanceAddedSignal(tag):Connect(function(instance)
			bindInstance(instance, registeredKind)
		end)
		CollectionService:GetInstanceRemovedSignal(tag):Connect(unbindInstance)
	end

	local function tick()
		local elapsed = Workspace:GetServerTimeNow() - epoch
		local tideByPort = {
			a = TideMath.levelAt(PORT_TIDES.a, elapsed),
			b = TideMath.levelAt(PORT_TIDES.b, elapsed),
		}
		publish(tideByPort)
		applyAll(tideByPort)
	end

	tick()
	heartbeatConnection = RunService.Heartbeat:Connect(function(dt)
		accumulator += dt
		if accumulator < UPDATE_INTERVAL then return end
		accumulator %= UPDATE_INTERVAL
		tick()
	end)
	print("[tide] Macrotidal controller online; Port A and Port B surfaces registered.")
end

function TidalController.stop()
	if heartbeatConnection then
		heartbeatConnection:Disconnect()
		heartbeatConnection = nil
	end
	started = false
	states = {}
end

return TidalController
