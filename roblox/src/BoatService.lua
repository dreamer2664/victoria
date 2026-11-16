--!nonstrict
--[[
	BoatService.lua -- server entry point.  Put this in ServerScriptService.

	Responsibilities:
	  * find both boats in Workspace.Boats and start the right controller;
	  * create the control remote and route messages to the boat the player is
	    in;
	  * build the boarding seats and docking points from the published spec
	    (interfaces/boats_spec.json), so a player can step aboard and take
	    the helm;
	  * hand out the "driver" role on a first-come basis and release it when
	    the player leaves the seat.

	Both boats can be driven at the same time by different players.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local Config = require(script.Parent.Config)
local SteamCutter = require(script.Parent.SteamCutter)
local RowingCutter = require(script.Parent.RowingCutter)

local remote = ReplicatedStorage:FindFirstChild("BoatControl")
if not remote then
	remote = Instance.new("RemoteEvent")
	remote.Name = "BoatControl"
	remote.Parent = ReplicatedStorage
end

local boats = {}          -- model -> controller
local playerBoat = {}     -- player -> model

local function manifestFor(model)
	local id = model:GetAttribute("BoatId")
	if id == "steam_cutter_1888" then
		return require(script.Parent.Manifest_steam_cutter_1888)
	elseif id == "rowing_cutter_25ft" then
		return require(script.Parent.Manifest_rowing_cutter_25ft)
	elseif id == "whaler_27ft" then
		return require(script.Parent.Manifest_whaler_27ft)
	end
	return nil
end

local function addSeat(model, cf, name)
	local seat = Instance.new("Seat")
	seat.Name = name
	seat.Size = Vector3.new(1.6, 0.4, 1.6)
	seat.TopSurface = Enum.SurfaceType.Smooth
	seat.BottomSurface = Enum.SurfaceType.Smooth
	seat.Transparency = 1
	seat.CanCollide = false
	seat.Anchored = false
	seat.Massless = true
	seat.CFrame = cf
	seat.Parent = model
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = model.PrimaryPart
	weld.Part1 = seat
	weld.Parent = seat
	seat:SetAttribute("IsBoatSeat", true)
	return seat
end

local function addDockPoint(model, cf)
	local marker = Instance.new("Part")
	marker.Name = "DockPoint"
	marker.Size = Vector3.new(1, 1, 1)
	marker.Transparency = 1
	marker.CanCollide = false
	marker.Anchored = false
	marker.Massless = true
	marker.CFrame = cf
	marker.Parent = model
	local weld = Instance.new("WeldConstraint")
	weld.Part0 = model.PrimaryPart
	weld.Part1 = marker
	weld.Parent = marker
	return marker
end

local function startBoat(model)
	if boats[model] then return boats[model] end
	local manifest = manifestFor(model)
	if not manifest then
		warn("BoatService: unknown boat id", model:GetAttribute("BoatId"))
		return nil
	end
	local id = model:GetAttribute("BoatId")
	local ctrl
	if id == "steam_cutter_1888" then
		ctrl = SteamCutter.new(model, manifest)
	else
		ctrl = RowingCutter.new(model, manifest)
	end
	boats[model] = ctrl

	local cfg = Config.BOATS[id]
	-- seats and docking points from the published interface
	local boardingStuds = cfg.boarding.x * Config.STUD_PER_M
	local base = model.PrimaryPart.CFrame
	addSeat(model, base * CFrame.new(-boardingStuds * 0.15, 0.6, 0), "HelmSeat")
	addSeat(model, base * CFrame.new(-boardingStuds * 0.45, 0.6, 0.5), "PassengerSeat_A")
	addSeat(model, base * CFrame.new(-boardingStuds * 0.45, 0.6, -0.5), "PassengerSeat_B")
	addDockPoint(model, base * CFrame.new(cfg.loa_m * Config.STUD_PER_M * 0.5, 0, 0))

	return ctrl
end

local function onSeatOccupant(seat, model)
	seat:GetPropertyChangedSignal("Occupant"):Connect(function()
		local humanoidSeat = seat.Occupant
		local player = humanoidSeat and Players:GetPlayerFromCharacter(humanoidSeat.Parent)
		if player then
			if not playerBoat[player] then
				playerBoat[player] = model
				local ctrl = boats[model]
				if ctrl and ctrl.setDriver then ctrl:setDriver(player) end
				remote:FireClient(player, "aboard", model:GetAttribute("BoatId"))
			end
		else
			for p, m in pairs(playerBoat) do
				if m == model then
					local ctrl = boats[m]
					if ctrl and ctrl.setDriver then ctrl:setDriver(nil) end
					playerBoat[p] = nil
				end
			end
		end
	end)
end

local function hookSeats(model)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("Seat") and d:GetAttribute("IsBoatSeat") then
			onSeatOccupant(d, model)
		end
	end
end

remote.OnServerEvent:Connect(function(player, boatId, kind, value)
	local model
	for m in pairs(boats) do
		if m:GetAttribute("BoatId") == boatId then
			model = m
			break
		end
	end
	if not model then return end
	if playerBoat[player] ~= model then return end
	local ctrl = boats[model]
	if ctrl and ctrl.control then
		ctrl:control(player, kind, value)
	end
end)

local function watchBoat(model)
	if model:GetAttribute("BoatId") and not boats[model] then
		startBoat(model)
		hookSeats(model)
	end
end

local boatFolder = Workspace:WaitForChild("Boats", 30)
if boatFolder then
	for _, m in ipairs(boatFolder:GetChildren()) do
		if m:IsA("Model") then watchBoat(m) end
	end
	boatFolder.ChildAdded:Connect(function(m)
		if m:IsA("Model") then
			task.wait(0.2)
			watchBoat(m)
		end
	end)
else
	warn("BoatService: no Workspace.Boats folder; nothing to drive")
end

Players.PlayerRemoving:Connect(function(player)
	playerBoat[player] = nil
end)

print("[OPERATION VICTORIA] BoatService running")
