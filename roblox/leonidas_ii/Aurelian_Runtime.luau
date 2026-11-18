--!strict
-- SS Aurelian / LEONIDAS-II. Server authoritative kinematic ship simulation.
-- Fictional 1889 plant; not a naval/pressure-vessel simulator.
-- No arbitrary remote command endpoint, no audio asset IDs, no math.radians.
local RunService=game:GetService("RunService")
local Players=game:GetService("Players")
local Runtime={}
local M=.28
local function v(a) return Vector3.new(a[1],a[2],a[3]) end
local function p(a) return Vector3.new(-a[2]/M,(a[3]-6.5)/M,-a[1]/M) end
local function pivotDelta(point,rotation) return CFrame.new(point)*rotation*CFrame.new(-point) end
local function rodFrame(a,b) return CFrame.lookAt((a+b)*.5,b,Vector3.new(0,0,-1)) end
local function approach(a,b,dt,tau) return a+(b-a)*(1-math.exp(-dt/tau)) end
local ORDERS={"Full Astern","Half Astern","Slow Astern","Dead Slow Astern","Stop","Dead Slow Ahead","Slow Ahead","Half Ahead","Full Ahead"}
local FRACTIONS={-.65,-.45,-.25,-.10,0,.15,.35,.65,1}
local function match(part,name) return part.Name==name or part.Name:sub(1,#name+1)==name.."_" end

function Runtime.start(ship,Data)
 assert(ship and ship:IsA("Model") and ship.PrimaryPart,"Install the imported Aurelian model first")
 assert(not ship:GetAttribute("LII_Running"),"Aurelian already has a controller")
 ship:SetAttribute("LII_Running",true)
 local origin=ship:GetPivot();local base={};local visuals={}
 for _,o in ship:GetDescendants() do
  if o:IsA("BasePart") then base[o]=origin:ToObjectSpace(o.CFrame);if o:GetAttribute("LII_Visual") then table.insert(visuals,o) end end
 end
 local bindings={}
 for _,m in Data.movers do
  local parts={}
  for _,o in ship:GetDescendants() do if o:IsA("BasePart") and (match(o,m.name) or o.Name=="Collider_"..m.name) then table.insert(parts,o) end end
  assert(#parts>0,"Missing animated export: "..m.name)
  local b={data=m,parts=parts}
  if m.type=="conrod" then b.oldFrame=rodFrame(p(m.pin0),p(m.cross0)) end
  table.insert(bindings,b)
 end
 local doors={}
 for _,d in Data.doors do
  local parts={}
  for _,o in ship:GetDescendants() do if o:IsA("BasePart") and (match(o,d.name) or o.Name=="Collider_"..d.name) then table.insert(parts,o) end end
  assert(#parts>0,"Missing interactive door: "..d.name)
  table.insert(doors,{data=d,parts=parts,open=false,alpha=0})
 end
 local state={order=5,regulator=0,fire=.55,pressure=8,rpm=0,angle=0,speed=0,rudder=0,requestedRudder=0,clear=false,generator=true,gangways=false,gangle=math.atan(1.7/5),whistle=0}
 local function publish()
  ship:SetAttribute("TelegraphOrder",ORDERS[state.order]);ship:SetAttribute("BoilerPressureBar",state.pressure);ship:SetAttribute("ShaftRPM",state.rpm);ship:SetAttribute("ShaftAngle",math.deg(state.angle)%360);ship:SetAttribute("SpeedKn",state.speed/.514444);ship:SetAttribute("RudderDeg",state.rudder);ship:SetAttribute("Regulator",state.regulator);ship:SetAttribute("FireRate",state.fire);ship:SetAttribute("MooringsClear",state.clear);ship:SetAttribute("GangwaysStowed",state.gangways);ship:SetAttribute("GeneratorOn",state.generator);ship:SetAttribute("SmokeIntensity",state.fire*.35+math.abs(state.rpm)/72*.65)
 end
 publish()
 local function setOrder(value)
  local n=nil
  if typeof(value)=="number" and value==value and math.abs(value)<1e9 then n=math.clamp(math.floor(value)+5,1,9)
  elseif typeof(value)=="string" then
   for i,s in ORDERS do if s==value then n=i;break end end
   if value=="Stand By" then n=5 end
   if value=="Three-Quarter" then n=8 end
  end
  if not n then return false,"Unknown order" end
  if not state.clear and n~=5 then return false,"Moorings / gangways interlock" end
  state.order=n;publish();return true
 end
 local function clearMoorings(clear)
  if math.abs(state.speed)>.2 or math.abs(state.rpm)>2 then return false,"Stop ship and shaft before mooring changes" end
  if clear and (not state.gangways or state.gangle<math.rad(85)) then return false,"Wait until both gangways are fully shipped" end
  state.clear=clear==true
  if not state.clear then state.order=5;state.regulator=0 end
  publish();return true
 end
 local api=ship:FindFirstChild("ShipControl") or Instance.new("Folder");api.Name="ShipControl";api.Parent=ship
 local function bind(name,fn) local old=api:FindFirstChild(name);if old then old:Destroy() end;local b=Instance.new("BindableFunction");b.Name=name;b.OnInvoke=fn;b.Parent=api end
 bind("OrderTelegraph",setOrder)
 bind("SetRudder",function(deg) if typeof(deg)~="number" or deg~=deg then return false end;state.requestedRudder=math.clamp(deg,-35,35);return true end)
 bind("SetMooringsClear",clearMoorings)
 bind("GetSpeed",function() return state.speed/.514444 end)
 -- Prompt events are checked server-side for distance, liveness and rate.
 local last={}
 local function permit(player,host,ignoredDoorParts)
  local char=player.Character;local hrp=char and char:FindFirstChild("HumanoidRootPart");local hum=char and char:FindFirstChildOfClass("Humanoid")
  if not(hrp and hum and hum.Health>0) then return false end
  if (hrp.Position-host.Position).Magnitude>13 then return false end
  -- Door handles sit on the leaf centre plane. Ignore that same leaf and
  -- its moving proxy, NOT the intervening room walls, for a server-side
  -- sight test from either side. Built-in LOS alone would hit the separate
  -- collider before reaching the invisible handle host.
  if ignoredDoorParts then
   local ignore={char,host};for _,part in ignoredDoorParts do table.insert(ignore,part) end
   local rp=RaycastParams.new();rp.FilterType=Enum.RaycastFilterType.Exclude;rp.FilterDescendantsInstances=ignore;rp.RespectCanCollide=true
   if workspace:Raycast(hrp.Position,host.Position-hrp.Position,rp) then return false end
  end
  local key=tostring(player.UserId)..host.Name;local now=os.clock()
  if now-(last[key] or -10)<.28 then return false end;last[key]=now;return true
 end
 local function prompt(host,action,object,callback,key,ignoredDoorParts)
  local q=Instance.new("ProximityPrompt");q.ActionText=action;q.ObjectText=object;q.MaxActivationDistance=8.5;q.RequiresLineOfSight=ignoredDoorParts==nil;q.HoldDuration=.15;q.KeyboardKeyCode=key or Enum.KeyCode.E;q.Parent=host
  q.Triggered:Connect(function(player) if permit(player,host,ignoredDoorParts) then callback(player,q) end end)
  return q
 end
 local hosts=ship:WaitForChild("LII_Controls")
 local function host(name) local h=hosts:FindFirstChild(name);assert(h and h:IsA("BasePart"),"Missing control locator "..name);return h end
 prompt(host("Telegraph_Ahead"),"Order ahead", "Engine order telegraph",function(_,q)
  local ok,why=setOrder(math.min(9,state.order+1)-5);q.ObjectText=ok and ORDERS[state.order] or why
 end)
 prompt(host("Telegraph_Astern"),"Order astern / stop","Engine order telegraph",function(_,q)
  local ok,why=setOrder(math.max(1,state.order-1)-5);q.ObjectText=ok and ORDERS[state.order] or why
 end,Enum.KeyCode.F)
 prompt(host("Regulator"),"Adjust regulator","Engine-room regulator",function(_,q)
  state.regulator=(math.floor(state.regulator*4+.5)+1)%5/4;q.ObjectText=string.format("Regulator %.0f%%",state.regulator*100);publish()
 end)
 prompt(host("Stoke"),"Set firing rate","Stokehold",function(_,q)
  if state.fire<.7 then state.fire=.80 elseif state.fire<.9 then state.fire=1 else state.fire=.40 end
  q.ObjectText=string.format("Fire %.0f%% / %.1f bar",state.fire*100,state.pressure);publish()
 end)
 prompt(host("Generator"),"Switch lighting dynamo","Electrical switchboard",function(_,q)
  state.generator=not state.generator;q.ObjectText=state.generator and "Dynamo connected" or "Dynamo disconnected";publish()
 end)
 prompt(host("CastOff"),"Cast off / make fast","Mooring interlock",function(_,q)
  local ok,why=clearMoorings(not state.clear);q.ObjectText=ok and (state.clear and "Moorings clear" or "Made fast") or why
 end)
 for _,id in {"Boarding_Port","Boarding_Starboard"} do
  prompt(host(id),"Ship / lower gangways","Boarding gangway",function(_,q)
   if state.clear or math.abs(state.speed)>.2 then q.ObjectText="Make fast before lowering";return end
   state.gangways=not state.gangways;q.ObjectText=state.gangways and "Gangways being shipped" or "Gangways being lowered";publish()
  end)
 end
 prompt(host("Whistle"),"Steam whistle","Whistle pull",function()
  if state.pressure>2 then state.whistle+=1;ship:SetAttribute("WhistlePulse",state.whistle);state.pressure=math.max(0,state.pressure-.05) end
 end)
 local seat=ship:FindFirstChild("LII_HelmSeat",true)
 if seat and seat:IsA("VehicleSeat") then
  prompt(host("Helm"),"Take helm","Ship's wheel",function(player)
   local hum=player.Character and player.Character:FindFirstChildOfClass("Humanoid");if hum and not seat.Occupant then seat:Sit(hum) end
  end)
 end
 -- A local port/starboard fallback is available on touch/gamepad prompts.
 prompt(host("Helm_Port"),"Port five degrees","Helm",function() state.requestedRudder=math.clamp(state.requestedRudder-5,-35,35) end,Enum.KeyCode.Q)
 prompt(host("Helm_Starboard"),"Starboard five degrees","Helm",function() state.requestedRudder=math.clamp(state.requestedRudder+5,-35,35) end,Enum.KeyCode.R)
 for _,d in doors do
  local h=host("Handle_"..d.data.id)
  prompt(h,"Open / close",d.data.watertight and "Dogged watertight door" or "Cabin / compartment door",function()
   if d.open then
    -- Conservative hinge-sweep cylinder, including an avatar margin.
    -- A sphere centred on the hinge missed the far edge of wider leaves.
    local hinge=p(d.data.hinge);local radius=(d.data.width+.35)/M
    for _,pl in Players:GetPlayers() do
     local hrp=pl.Character and pl.Character:FindFirstChild("HumanoidRootPart")
     if hrp then
      local q=ship:GetPivot():PointToObjectSpace(hrp.Position)-hinge
      if q.Y>-.5/M and q.Y<(d.data.height+.5)/M and q.X*q.X+q.Z*q.Z<radius*radius then return end
     end
    end
   end
   d.open=not d.open
  end,nil,d.parts)
 end
 local planar=Vector3.new(origin.Position.X,origin.Position.Y,origin.Position.Z);local _,yaw,_=origin:ToOrientation();local clock=0;local pub=0
 local ray=RaycastParams.new();ray.FilterType=Enum.RaycastFilterType.Include;ray.FilterDescendantsInstances={ship};ray.RespectCanCollide=true
 local function carry(oldCF,newCF)
  local delta=newCF*oldCF:Inverse()
  for _,player in Players:GetPlayers() do
   local char=player.Character;local hum=char and char:FindFirstChildOfClass("Humanoid");local hrp=char and char:FindFirstChild("HumanoidRootPart")
   if hum and hrp and hum.Health>0 and not hum.Sit and hum.FloorMaterial~=Enum.Material.Air then
    local hit=workspace:Raycast(hrp.Position,Vector3.new(0,-7,0),ray)
    if hit and hit.Instance:GetAttribute("LII_Collider") then hrp.CFrame=delta*hrp.CFrame end
   end
  end
 end
 local connection;local accumulated=0
 connection=RunService.Heartbeat:Connect(function(frameDt)
  if not ship.Parent then connection:Disconnect();return end
  accumulated+=frameDt;if accumulated<.05 then return end
  local dt=math.min(accumulated,.1);accumulated=0;clock+=dt
  local demand=math.abs(state.rpm)/72*1.75+(state.generator and .06 or 0)
  state.pressure=math.clamp(state.pressure+(state.fire*2.5-demand-(state.pressure-1)*.06)*dt,.1,11)
  local live=math.clamp((state.pressure-2)/9,0,1)
  local target=state.clear and FRACTIONS[state.order]*72*state.regulator*live or 0
  state.rpm=approach(state.rpm,target,dt,8.5);state.angle=(state.angle+state.rpm*math.pi/30*dt)%(math.pi*2)
  local advance=state.rpm*9.4/60*.88;state.speed=approach(state.speed,advance,dt,19)
  if not state.clear then state.speed=approach(state.speed,0,dt,.7) end
  if seat and seat.Occupant then state.requestedRudder=seat.SteerFloat*35 end
  state.rudder=approach(state.rudder,state.requestedRudder,dt,2.3)
  yaw-=math.rad(state.rudder)*state.speed/166*.58*dt
  local horizontal=CFrame.Angles(0,yaw,0).LookVector;planar+=horizontal*(state.speed/M*dt)
  -- Absolute water datum: wave displacement is never added to previous Y.
  local heave=state.clear and (.045*math.sin(clock*.51)+.018*math.sin(clock*.83)) or 0
  local roll=state.clear and math.rad(.10)*math.sin(clock*.42) or 0
  local pitch=state.clear and math.rad(.06)*math.sin(clock*.56) or 0
  local newCF=CFrame.new(planar.X,origin.Position.Y+heave/M,planar.Z)*CFrame.Angles(0,yaw,0)*CFrame.Angles(pitch,0,roll)
  local oldCF=ship:GetPivot();carry(oldCF,newCF);ship.PrimaryPart.CFrame=newCF
  local wantedGangway=state.gangways and math.rad(88) or math.atan(1.7/5);state.gangle=approach(state.gangle,wantedGangway,dt,1.1)
  for _,b in bindings do
   local m=b.data;local delta=CFrame.identity
   if m.type=="shaft" then delta=pivotDelta(p(m.origin),CFrame.Angles(0,0,state.angle))
   elseif m.type=="piston" then
    local a=state.angle+(m.phase or 0);local yy=(m.centre_y or 0)+m.r*math.sin(a);local slider=m.slider_y or m.centre_y or 0;local zz=(m.shaft_z or 3)+m.r*math.cos(a)+math.sqrt(math.max(0,m.l*m.l-(slider-yy)^2));delta=CFrame.new(0,(zz-m.cross_z0)/M,0)
   elseif m.type=="conrod" then
    local a=state.angle+(m.phase or 0);local yy=(m.centre_y or 0)+m.r*math.sin(a);local sz=m.shaft_z or 3;local slider=m.slider_y or m.centre_y or 0;local zz=sz+m.r*math.cos(a);local cz=zz+math.sqrt(math.max(0,m.l*m.l-(slider-yy)^2));local pin=p({m.x,yy,zz});local cross=p({m.x,slider,cz});delta=rodFrame(pin,cross)*b.oldFrame:Inverse()
   elseif m.type=="rudder" then delta=pivotDelta(p(m.origin),CFrame.Angles(0,math.rad(state.rudder),0))
   elseif m.type=="helm" then delta=pivotDelta(p(m.origin),CFrame.Angles(0,0,math.rad(-state.rudder*4)))
   elseif m.type=="gangway" then delta=pivotDelta(p(m.origin),CFrame.Angles(0,0,-m.side*state.gangle)) end
   for _,part in b.parts do if part.Parent then local motor=part:FindFirstChild("LII_Motor");if motor and motor:IsA("Motor6D") then motor.C0=delta*base[part] end end end
  end
  for _,d in doors do
   local targetAlpha=d.open and 1 or 0;local alpha=approach(d.alpha,targetAlpha,dt,.30)
   if math.abs(alpha-targetAlpha)<.0001 then alpha=targetAlpha end
   -- Closed/stationary doors do not generate 392 redundant motor updates
   -- every heartbeat. Only actively easing leaves/colliders are written.
   if alpha~=d.alpha then
    d.alpha=alpha
    local delta=pivotDelta(p(d.data.hinge),CFrame.Angles(0,math.rad(d.data.angle_deg)*alpha,0))
    for _,part in d.parts do if part.Parent then local motor=part:FindFirstChild("LII_Motor");if motor and motor:IsA("Motor6D") then motor.C0=delta*base[part] end end end
   end
  end
  pub+=dt;if pub>.15 then pub=0;publish() end
 end)
 -- No copyrighted/unverified whistle/bell sound is silently attached. Supply
 -- ship attributes WhistleSoundId/BellSoundId with authorised uploaded audio.
 return state
end
return Runtime
