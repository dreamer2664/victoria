--!strict
-- Local-only detail/light/effects budget. Does not move ship or accept orders.
local Players=game:GetService("Players")
local RunService=game:GetService("RunService")
local ship=workspace:WaitForChild("Aurelian")
local player=Players.LocalPlayer
local M=.28
local detail={};local lamps={};local smoke={};local wake={}
local function register(o)
 if o:IsA("BasePart") and o:GetAttribute("LII_Visual") then
  local k=o:GetAttribute("LII_Kind")
  if k=="furniture" or k=="sign" then table.insert(detail,o) end
 elseif o:IsA("PointLight") and o.Name=="Incandescent" then table.insert(lamps,o) end
end
for _,o in ship:GetDescendants() do register(o) end
ship.DescendantAdded:Connect(register)
local controls=ship:WaitForChild("LII_Controls")
local function emitterAt(name,texture)
 local host=controls:WaitForChild(name);local attach=Instance.new("Attachment");attach.Name="LocalEffect";attach.Parent=host
 local e=Instance.new("ParticleEmitter");e.Name="Aurelian_Local_"..name;e.Texture=texture;e.LockedToPart=false;e.Parent=attach;return e
end
for _,name in {"Funnel_Aft","Funnel_Forward"} do
 local e=emitterAt(name,"rbxasset://textures/particles/smoke_main.dds");e.Lifetime=NumberRange.new(4.0,6.0);e.Speed=NumberRange.new(8,13);e.SpreadAngle=Vector2.new(9,9);e.Acceleration=Vector3.new(0,3,0);e.Drag=.6;e.Color=ColorSequence.new(Color3.fromRGB(55,54,50),Color3.fromRGB(150,145,130));e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,2),NumberSequenceKeypoint.new(1,16)});e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.42),NumberSequenceKeypoint.new(1,1)});table.insert(smoke,e)
end
local w=emitterAt("Wake","rbxasset://textures/particles/smoke_main.dds");w.Lifetime=NumberRange.new(2,4);w.Speed=NumberRange.new(0,1.5);w.Size=NumberSequence.new(3,14);w.Color=ColorSequence.new(Color3.fromRGB(216,230,225));w.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.58),NumberSequenceKeypoint.new(1,1)});table.insert(wake,w)
-- Compact readable instrument repeater; physical controls remain prompts.
local gui=Instance.new("ScreenGui");gui.Name="Aurelian_Instruments";gui.ResetOnSpawn=false;gui.IgnoreGuiInset=false;gui.Parent=player:WaitForChild("PlayerGui")
local frame=Instance.new("Frame");frame.Name="Panel";frame.Position=UDim2.new(0,18,1,-112);frame.Size=UDim2.fromOffset(345,94);frame.BackgroundColor3=Color3.fromRGB(24,38,45);frame.BackgroundTransparency=.10;frame.BorderColor3=Color3.fromRGB(184,151,84);frame.Visible=false;frame.Parent=gui
local label=Instance.new("TextLabel");label.Position=UDim2.fromOffset(12,6);label.Size=UDim2.new(1,-24,1,-12);label.BackgroundTransparency=1;label.Font=Enum.Font.Code;label.TextColor3=Color3.fromRGB(238,224,188);label.TextSize=14;label.TextXAlignment=Enum.TextXAlignment.Left;label.TextYAlignment=Enum.TextYAlignment.Center;label.Parent=frame
local elapsed=0
RunService.Heartbeat:Connect(function(dt)
 elapsed+=dt;if elapsed<.25 then return end;elapsed=0
 local camera=workspace.CurrentCamera;if not camera or not ship.PrimaryPart then return end
 local point=ship:GetPivot():PointToObjectSpace(camera.CFrame.Position)*M
 local aboard=math.abs(point.X)<13 and math.abs(point.Z)<88 and point.Y>-6.8 and point.Y<20
 frame.Visible=aboard
 local speed=ship:GetAttribute("SpeedKn") or 0;local rpm=ship:GetAttribute("ShaftRPM") or 0;local pressure=ship:GetAttribute("BoilerPressureBar") or 0
 label.Text=string.format("SS AURELIAN · 1889\n%-16s %5.1f kn  %5.1f rpm\nBoiler %4.1f bar   Rudder %+3.0f°\n%s",ship:GetAttribute("TelegraphOrder") or "Stop",speed,rpm,pressure,ship:GetAttribute("RudderDeg") or 0,ship:GetAttribute("MooringsClear") and "UNDER WAY / MOORINGS CLEAR" or "MADE FAST · SHIP GANGWAYS BEFORE CASTING OFF")
 local cp=camera.CFrame.Position;local pivot=ship:GetPivot()
 for _,o in detail do if o.Parent then
  local pos=pivot:PointToObjectSpace(o.Position)*M
  -- Same/adjacent deck and local detail only; walls/hull are never hidden.
  -- Bounds, not centroid alone: a long furnished compartment must not
  -- disappear while the camera is still beside one end of its mesh chunk.
  local distance=math.max(0,(o.Position-cp).Magnitude-o.Size.Magnitude*.5)
  local levelDistance=math.max(0,math.abs(point.Y-pos.Y)-o.Size.Y*M*.5)
  o.LocalTransparencyModifier=(levelDistance>3.6 or distance>105) and 1 or 0
 end end
 local generator=ship:GetAttribute("GeneratorOn")==true;local near={}
 for _,l in lamps do if l.Parent and l.Parent:IsA("BasePart") then
  local distance=(l.Parent.Position-cp).Magnitude;l.Enabled=false
  if generator and distance<58 then table.insert(near,{light=l,distance=distance}) end
 end end
 table.sort(near,function(a,b) return a.distance<b.distance end)
 local budget=math.clamp(tonumber(ship:GetAttribute("LocalLightBudget")) or 12,4,24)
 for i=1,math.min(#near,budget) do near[i].light.Enabled=true end
 local intensity=ship:GetAttribute("SmokeIntensity") or 0
 for _,e in smoke do e.Rate=2+intensity*20;e.Enabled=(e.Parent.WorldPosition-cp).Magnitude<1600 end
 for _,e in wake do e.Enabled=math.abs(speed)>1.4;e.Rate=math.min(24,math.abs(speed)*1.2) end
end)
ship:GetAttributeChangedSignal("WhistlePulse"):Connect(function()
 for _,e in smoke do e:Emit(10) end
 local id=ship:GetAttribute("WhistleSoundId")
 if typeof(id)=="string" and id:match("^rbxassetid://%d+$") then
  local h=controls:FindFirstChild("Whistle");if h then local s=h:FindFirstChild("AuthorisedWhistle") or Instance.new("Sound");s.Name="AuthorisedWhistle";s.SoundId=id;s.Volume=.65;s.RollOffMaxDistance=450;s.Parent=h;s:Play() end
 end
end)
