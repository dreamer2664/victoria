--!strict
-- TidalClient.client.luau -- smooth, local interpolation of server tide targets.
-- Place in StarterPlayer/StarterPlayerScripts. Server-side collision and tide state
-- remain authoritative in TidalController; this script only smooths replicated visuals.

local CollectionService = game:GetService("CollectionService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage.Shared.Config)
local TideMath = require(ReplicatedStorage.Shared.TideMath)

local TAGS = {
	pontoon = "VictoriaTidalPontoon",
	span = "VictoriaTidalGangwaySpan",
	bogie = "VictoriaTidalGangwayBogie",
	water = "VictoriaTidalWaterSurface",
}

local SPECS: { [string]: TideMath.TideSpec } = {
	a = { lowM = -2.0, highM = 3.5, periodSeconds = 20 * 60 },
	b = { lowM = -1.75, highM = 1.75, periodSeconds = 20 * 60 },
}

local BASE_PIVOT_ATTRIBUTE = "VictoriaTideBasePivot"
local IMPOUNDED_DOCK_LEVEL_M = 3.2
local SMOOTHING_RATE = 14.0
local states: { [Instance]: any } = {}

local function readNumber(instance: Instance, attribute: string, fallback: number): number
	local value = instance:GetAttribute(attribute)
	return if typeof(value) == "number" then value else fallback
end

local function currentPivot(instance: Instance): CFrame
	return if instance:IsA("Model") then instance:GetPivot() else (instance :: BasePart).CFrame
end

local function setPivot(instance: Instance, pivot: CFrame)
	if instance:IsA("Model") then
		instance:PivotTo(pivot)
	elseif instance:IsA("BasePart") then
		instance.CFrame = pivot
	end
end

local function bind(instance: Instance, kind: string)
	if states[instance] then return end
	local code = string.lower(tostring(instance:GetAttribute("PortCode") or ""))
	if SPECS[code] == nil then return end

	local function finishBinding()
		if instance.Parent == nil or states[instance] then return end
		local base = instance:GetAttribute(BASE_PIVOT_ATTRIBUTE)
		if typeof(base) ~= "CFrame" then
			warn("[tide-client] Missing server-set base pivot on " .. instance:GetFullName())
			return
		end
		states[instance] = {
			instance = instance,
			kind = kind,
			portCode = code,
			basePivot = base,
			currentPivot = currentPivot(instance),
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
	end

	if typeof(instance:GetAttribute(BASE_PIVOT_ATTRIBUTE)) == "CFrame" then
		finishBinding()
	else
		-- The server captures and replicates the immutable mean-tide transform.
		-- Give that attribute a short window to arrive before trying to interpolate.
		task.spawn(function()
			for _ = 1, 50 do
				if instance.Parent == nil or states[instance] then return end
				if typeof(instance:GetAttribute(BASE_PIVOT_ATTRIBUTE)) == "CFrame" then
					finishBinding()
					return
				end
				task.wait(0.1)
			end
			warn("[tide-client] Timed out waiting for base pivot: " .. instance:GetFullName())
		end)
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
	if state.kind == "pontoon" then
		return CFrame.new(0, Config.mToStuds(tideM - state.referenceTideM), 0) * base
	elseif state.kind == "water" then
		local targetM = if instance:GetAttribute("WaterKind") == "impounded"
			then readNumber(instance, "WaterLevelM", IMPOUNDED_DOCK_LEVEL_M)
			else tideM
		return CFrame.new(0, Config.mToStuds(targetM - state.baseWaterM), 0) * base
	elseif state.kind == "span" then
		local spec = gangwaySpec(state)
		local angle = TideMath.gangwayAngle(tideM, spec)
		local baseAngle = TideMath.referenceAngle(spec)
		local hinge = Config.toWorld(state.portCode, state.hingeX_M, state.hingeY_M, state.hingeZ_M)
		local rotation = CFrame.new(hinge)
			* CFrame.Angles(0, 0, angle - baseAngle)
			* CFrame.new(-hinge)
		return rotation * base
	elseif state.kind == "bogie" then
		local spec = gangwaySpec(state)
		local slideM = TideMath.bogieSlideM(tideM, spec)
		return CFrame.new(
			Config.mToStuds(slideM),
			Config.mToStuds(tideM - state.referenceTideM),
			0
		) * base
	end
	return base
end

for kind, tag in pairs(TAGS) do
	local registeredKind = kind
	for _, instance in ipairs(CollectionService:GetTagged(tag)) do
		bind(instance, registeredKind)
	end
	CollectionService:GetInstanceAddedSignal(tag):Connect(function(instance)
		bind(instance, registeredKind)
	end)
	CollectionService:GetInstanceRemovedSignal(tag):Connect(function(instance)
		states[instance] = nil
	end)
end

RunService.RenderStepped:Connect(function(dt)
	local epoch = Workspace:GetAttribute("VictoriaTideEpoch")
	if typeof(epoch) ~= "number" then return end
	local elapsed = Workspace:GetServerTimeNow() - epoch
	local alpha = 1 - math.exp(-SMOOTHING_RATE * dt)

	for instance, state in pairs(states) do
		if instance.Parent == nil then
			states[instance] = nil
		else
			local tideM = TideMath.levelAt(SPECS[state.portCode], elapsed)
			local goal = targetPivot(state, tideM)
			state.currentPivot = (state.currentPivot :: CFrame):Lerp(goal, alpha)
			setPivot(instance, state.currentPivot)
		end
	end
end)
