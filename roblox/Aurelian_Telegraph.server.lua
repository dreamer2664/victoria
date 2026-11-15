--[[
    SS AURELIAN — ENGINE ORDER TELEGRAPH + HELM  (Roblox)

    Put this inside the Wheelhouse model.  It builds a working 1889-style
    engine room telegraph (a dial with the order ring and the reply ring),
    the helm wheel, and the whistle pull.

    Controls (touch/mouse/ProximityPrompt, no keyboard required so it works on
    phones and consoles):
        * ProximityPrompt on the telegraph body: advance one order (Ahead side)
        * ProximityPrompt on the telegraph base: advance one order (Astern)
        * Click the wheel rim: turn to port / starboard
        * ProximityPrompt on the whistle: sound the whistle
]]

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")

local wheelhouse = script.Parent
local ship = wheelhouse:FindFirstAncestorOfClass("Model")
	or wheelhouse.Parent

local function shipAttribute(name, default)
	return ship:GetAttribute(name) or default
end

------------------------------------------------------------------ TELEGRAPH
local ORDERS = {
	"Full Astern", "Half Astern", "Slow Astern", "Dead Slow Astern",
	"Stand By", "Dead Slow Ahead", "Slow Ahead", "Half Ahead",
	"Three-Quarter", "Full Ahead",
}
local ORDER_THROTTLE = {
	["Full Astern"] = -0.80, ["Half Astern"] = -0.50, ["Slow Astern"] = -0.25,
	["Dead Slow Astern"] = -0.10, ["Stand By"] = 0.0,
	["Dead Slow Ahead"] = 0.10, ["Slow Ahead"] = 0.25, ["Half Ahead"] = 0.50,
	["Three-Quarter"] = 0.75, ["Full Ahead"] = 1.0,
}

local telegraphModel = wheelhouse:FindFirstChild("EngineTelegraph")
if not telegraphModel then
	warn("Aurelian: no EngineTelegraph model under Wheelhouse")
	return
end

local needle = telegraphModel:FindFirstChild("OrderNeedle", true)
local index = 5   -- Stand By

local controlFolder = ship:FindFirstChild("ShipControl")
local function callShip(name, ...)
	local f = controlFolder and controlFolder:FindFirstChild(name)
	if f and f:IsA("BindableFunction") then
		return f:Invoke(...)
	end
end

local function applyOrder()
	local order = ORDERS[index]
	if needle then
		local targetDeg = -90 + (index - 1) * 20
		TweenService:Create(needle, TweenInfo.new(0.7, Enum.EasingStyle.Sine),
			{ Orientation = Vector3.new(0, targetDeg, 0) }):Play()
	end
	local prompt = telegraphModel:FindFirstChildOfClass("ProximityPrompt")
	if prompt then
		prompt.ObjectText = "Telegraph: " .. order
	end
	callShip("OrderTelegraph", order)
	print("[Aurelian] telegraph order:", order)
end

local stepAhead = Instance.new("ProximityPrompt")
stepAhead.ActionText = "Ahead"
stepAhead.ObjectText = "Engine Order Telegraph"
stepAhead.HoldDuration = 0
stepAhead.MaxActivationDistance = 8
stepAhead.RequiresLineOfSight = false
stepAhead.Parent = telegraphModel

local stepAstern = Instance.new("ProximityPrompt")
stepAstern.ActionText = "Astern"
stepAstern.ObjectText = "Engine Order Telegraph"
stepAstern.HoldDuration = 0
stepAstern.MaxActivationDistance = 8
stepAstern.RequiresLineOfSight = false
stepAstern.Parent = telegraphModel

stepAhead.Triggered:Connect(function()
	index = math.min(#ORDERS, index + 1)
	applyOrder()
end)
stepAstern.Triggered:Connect(function()
	index = math.max(1, index - 1)
	applyOrder()
end)

------------------------------------------------------------------ HELM
local helm = wheelhouse:FindFirstChild("HelmWheel", true)
if helm then
	local rudder = 0
	local function apply()
		callShip("SetRudder", rudder)
		helm:PivotTo(helm:GetPivot() * CFrame.Angles(0, 0, 0))
		helm.Orientation = Vector3.new(helm.Orientation.X,
			helm.Orientation.Y, math.clamp(rudder * 4.0, -160, 160))
	end
	local portPrompt = Instance.new("ProximityPrompt")
	portPrompt.ActionText = "Port"
	portPrompt.ObjectText = "Helm"
	portPrompt.MaxActivationDistance = 8
	portPrompt.RequiresLineOfSight = false
	portPrompt.Parent = helm
	local stbdPrompt = portPrompt:Clone()
	stbdPrompt.ActionText = "Starboard"
	stbdPrompt.Parent = helm
	portPrompt.Triggered:Connect(function()
		rudder = math.clamp(rudder - 5, -35, 35); apply()
	end)
	stbdPrompt.Triggered:Connect(function()
		rudder = math.clamp(rudder + 5, -35, 35); apply()
	end)
	-- re-centre when the player walks away
	helm.AncestryChanged:Connect(function()
		rudder = 0; apply()
	end)
end

------------------------------------------------------------------ WHISTLE
local whistle = wheelhouse:FindFirstChild("Whistle", true)
if whistle then
	local bell = whistle:FindFirstChildWhichIsA("Sound")
		or Instance.new("Sound")
	bell.Name = "Whistle"
	bell.SoundId = "rbxassetid://9114307222"     -- replace with your own chime
	bell.Volume = 1
	bell.Parent = whistle
	local prompt = Instance.new("ProximityPrompt")
	prompt.ActionText = "Sound Whistle"
	prompt.ObjectText = "Ship's Whistle"
	prompt.MaxActivationDistance = 10
	prompt.Parent = whistle
	prompt.Triggered:Connect(function()
		bell:Play()
		-- steam puff from each funnel
		for _, funnel in ipairs(ship:GetChildren()) do
			if funnel.Name:match("Funnel") and funnel:IsA("Model") then
				local puff = funnel:FindFirstChild("SteamPuff", true)
				if puff and puff:IsA("ParticleEmitter") then
					puff:Emit(45)
				end
			end
		end
	end)
end
