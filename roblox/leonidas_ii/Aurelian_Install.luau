--!strict
-- Run in Studio EDIT mode from the command bar after importing the provided
-- GLB, with the package Model also imported:
-- require(workspace.Aurelian_Package.Aurelian_Install)(workspace.Aurelian, CFrame.new(0,0,0))
-- The returned assembly uses a waterline pivot, not a part-centre estimate.
-- Fails closed on missing calibration markers or required animated meshes.
local M=.28
local function p(a) return Vector3.new(-a[2]/M,(a[3]-6.5)/M,-a[1]/M) end
local function boxSize(a) return Vector3.new(a[2]/M,a[3]/M,a[1]/M) end
local function find(ship,name) local o=ship:FindFirstChild(name,true);assert(o and o:IsA("BasePart"),"Missing imported object "..name);return o end
local function marker(ship,name) return find(ship,"CAL_"..name).Position end
local function native(parent,name,size,cf,collide)
 local part=Instance.new("Part");part.Name=name;part.Size=size;part.CFrame=cf;part.Anchored=true;part.Transparency=1;part.CanCollide=collide==true;part.CanTouch=false;part.CanQuery=collide==true;part.CastShadow=false;part.TopSurface=Enum.SurfaceType.Smooth;part.BottomSurface=Enum.SurfaceType.Smooth;part.Parent=parent;return part
end
local function matches(name,prefix) return name==prefix or name:sub(1,#prefix+1)==prefix.."_" end
return function(ship,spawnCF)
 assert(not game:GetService("RunService"):IsRunning(),"Install only in Studio EDIT mode, then save the place")
 assert(ship and ship:IsA("Model"),"Pass the imported GLB model; do not run against ports/boats")
 assert(not ship:GetAttribute("LII_Installed"),"Already installed; undo/delete this instance before reinstalling")
 local existing=workspace:FindFirstChild("Aurelian");assert(not existing or existing==ship,"A different Aurelian model already exists; use an empty test place")
 local package=script.Parent;local Data=require(package:WaitForChild("Aurelian_Data"));spawnCF=spawnCF or CFrame.identity
 local imports={}
 if not ship:FindFirstChild("CAL_Origin") then
  for _,child in ship:GetChildren() do if child:IsA("Model") and child:FindFirstChild("CAL_Origin",true) then table.insert(imports,child) end end
 end
 if #imports==0 then imports={ship} end
 for _,model in imports do
  local O,F,P,U=marker(model,"Origin"),marker(model,"Forward"),marker(model,"Port"),marker(model,"Up")
  local length=(F-O).Magnitude;assert(length>.01,"Invalid forward calibration in "..model.Name)
  model:ScaleTo(model:GetScale()*(10/M)/length)
  O=marker(model,"Origin");F=marker(model,"Forward");P=marker(model,"Port");U=marker(model,"Up")
  local forward=(F-O).Unit;local right=(O-P).Unit;local up=(U-O).Unit
  assert(math.abs(forward:Dot(right))<.001 and math.abs(up:Dot(right))<.001 and right:Cross(up):Dot(-forward)>.999,"Nonorthogonal / mirrored import calibration")
  local basis=CFrame.fromMatrix(O,right,up,-forward)
  model:PivotTo(spawnCF*basis:Inverse()*model:GetPivot())
 end
 -- Use named mesh-node centroids against the exported BOUNDS, not the source
 -- origin of a single part. Some importers centre vertices automatically.
 local visualCount=0
 for _,o in ship:GetDescendants() do if o:IsA("BasePart") then
  if o.Name:sub(1,4)=="CAL_" then continue end
  o.Anchored=true;o.CanCollide=false;o.CanTouch=false;o.CanQuery=false;o.Massless=true;o:SetAttribute("LII_Visual",true);visualCount+=1
 end end
 assert(visualCount==Data.expected_visual_nodes,string.format("Visual nodes missing/merged/duplicated: %d imported, %d required",visualCount,Data.expected_visual_nodes))
 for _,m in Data.movers do
  local count=0
  for _,o in ship:GetDescendants() do if o:IsA("BasePart") and matches(o.Name,m.name) then count+=1 end end
  assert(count>0,"Required moving mesh missing / renamed by importer: "..m.name)
 end
 for _,d in Data.doors do find(ship,d.name) end
 local markerPart=find(ship,"CAL_Origin")
 assert((spawnCF:PointToObjectSpace(markerPart.Position)).Magnitude<.05,"Waterline datum normalisation failed")
 assert(math.abs((marker(ship,"Forward")-marker(ship,"Origin")).Magnitude-10/M)<.02,"Scale correction failed")
 for _,o in ship:GetDescendants() do if o:IsA("BasePart") and o.Name:sub(1,4)=="CAL_" then o:Destroy() end end
 ship.Name="Aurelian"
 local root=native(ship,"LII_Root",Vector3.new(.25,.25,.25),spawnCF,false);ship.PrimaryPart=root
 local collisions=Instance.new("Folder");collisions.Name="LII_Collision";collisions.Parent=ship
 local dynamic=Instance.new("Folder");dynamic.Name="LII_DynamicCollision";dynamic.Parent=ship
 local controls=Instance.new("Folder");controls.Name="LII_Controls";controls.Parent=ship
 for i,c in Data.proxies do
  local rotation=CFrame.Angles(0,c.yaw or 0,0)*CFrame.Angles(-(c.pitch or 0),0,0)
  local part=native(collisions,string.format("C_%04d_%s",i,c.tag or ""),boxSize(c.size),spawnCF*CFrame.new(p(c.position))*rotation,true)
  part:SetAttribute("LII_Collider",true);part:SetAttribute("LII_Tag",c.tag or "");part.CustomPhysicalProperties=PhysicalProperties.new(.7,.8,0,1,1)
 end
 for _,d in Data.doors do
  local centre={d.hinge[1]+d.width*.5*math.cos(d.yaw),d.hinge[2]+d.width*.5*math.sin(d.yaw),d.hinge[3]+d.height*.5}
  local cf=spawnCF*CFrame.new(p(centre))*CFrame.Angles(0,d.yaw,0)
  local part=native(dynamic,"Collider_"..d.name,Vector3.new(.065/M,d.height/M,d.width/M),cf,true);part:SetAttribute("LII_Collider",true)
 end
 for _,m in Data.movers do if m.type=="gangway" then
  local centre={m.origin[1],m.origin[2]+m.side*2.5,m.origin[3]};local part=native(dynamic,"Collider_"..m.name,Vector3.new(5/M,.15/M,1.5/M),spawnCF*CFrame.new(p(centre)),true);part:SetAttribute("LII_Collider",true)
 end end
 -- Source-native collider dimensions map +X to -Z, +Y to -X, +Z to +Y.
 -- Gangway width is longitudinal; exported source deck is 1.5m x 5.0m.
 local function control(id,pos)
  return native(controls,id,Vector3.new(.18,.18,.18),spawnCF*CFrame.new(p(pos)),false)
 end
 for _,a in Data.attachments do control(a.id,a.position) end
 control("Helm_Port",{38.0,1.1,21.0});control("Helm_Starboard",{38.0,-1.1,21.0})
 for _,d in Data.doors do
  local pos={d.hinge[1]+d.width*.55*math.cos(d.yaw),d.hinge[2]+d.width*.55*math.sin(d.yaw),d.hinge[3]+1.0};control("Handle_"..d.id,pos)
 end
 local seat=Instance.new("VehicleSeat");seat.Name="LII_HelmSeat";seat.Size=Vector3.new(1.8,.35,1.8);seat.CFrame=spawnCF*CFrame.new(p({37.4,0,20.50}));seat.Anchored=true;seat.Transparency=1;seat.CanCollide=false;seat.CanTouch=true;seat.CanQuery=false;seat.HeadsUpDisplay=false;seat.MaxSpeed=0;seat.Torque=0;seat.TurnSpeed=0;seat.Parent=ship
 local seatsFolder=Instance.new("Folder");seatsFolder.Name="LII_Seats";seatsFolder.Parent=ship
 for i,s in Data.seats do
  local a=Instance.new("Seat");a.Name=string.format("Seat_%03d",i);a.Size=Vector3.new(.42/M,.10/M,.40/M);a.CFrame=spawnCF*CFrame.new(p(s.position))*CFrame.Angles(0,s.yaw-math.pi/2,0);a.Anchored=true;a.Transparency=1;a.CanCollide=false;a.CanQuery=false;a.CanTouch=true;a.Parent=seatsFolder
 end
 local lamps=Instance.new("Folder");lamps.Name="LII_Lamps";lamps.Parent=ship
 for i,l in Data.lights do
  local h=native(lamps,"Lamp_"..i,Vector3.new(.08,.08,.08),spawnCF*CFrame.new(p(l.position)),false);local li=Instance.new("PointLight");li.Name="Incandescent";li.Color=Color3.fromRGB(255,215,163);li.Range=l.range_m/M;li.Brightness=l.brightness;li.Shadows=false;li.Enabled=false;li.Parent=h
 end
 local config=Instance.new("Folder");config.Name="LII_Config";config.Parent=ship
 for _,name in {"Aurelian_Data","Aurelian_Runtime"} do local c=package:FindFirstChild(name):Clone();c.Parent=config end
 -- Assign culling/inspection metadata by longest export-node prefix.
 local nodes=Data.nodes;table.sort(nodes,function(a,b) return #a.name>#b.name end)
 local assigned=0;local seen={}
 for _,o in ship:GetDescendants() do if o:IsA("BasePart") and o:GetAttribute("LII_Visual") then
  for _,n in nodes do if matches(o.Name,n.name) then
   o:SetAttribute("LII_Kind",n.kind or "");o:SetAttribute("LII_Room",n.room or "");o:SetAttribute("LII_Deck",n.deck or "");o:SetAttribute("LII_Node",n.name)
   seen[n.name]=(seen[n.name] or 0)+1;assigned+=1;break
  end end
 end end
 assert(assigned==visualCount,"Importer renamed visual nodes; do not install an unmatched mesh hierarchy")
 for _,n in nodes do assert(seen[n.name]==1,"Missing or duplicate regional mesh node: "..n.name) end
 -- One anchored waterline root, welded passive parts. Only root CFrame and
 -- the few Motor6D C0 values are replicated, not thousands of part CFrames.
 for _,part in ship:GetDescendants() do if part:IsA("BasePart") and part~=root then
  local animated=false
  for _,m in Data.movers do if matches(part.Name,m.name) or part.Name=="Collider_"..m.name then animated=true;break end end
  if not animated then for _,d in Data.doors do if matches(part.Name,d.name) or part.Name=="Collider_"..d.name then animated=true;break end end end
  if animated then
   local motor=Instance.new("Motor6D");motor.Name="LII_Motor";motor.Part0=root;motor.Part1=part;motor.C0=root.CFrame:ToObjectSpace(part.CFrame);motor.C1=CFrame.identity;motor.Parent=part
  else
   local weld=Instance.new("WeldConstraint");weld.Name="LII_Weld";weld.Part0=root;weld.Part1=part;weld.Parent=part
  end
  part.Massless=true;part.Anchored=false
 end end
 local server=package:WaitForChild("Aurelian_Server"):Clone();server.Disabled=false;server.Parent=game:GetService("ServerScriptService")
 local client=package:WaitForChild("Aurelian_Client"):Clone();client.Disabled=false;client.Parent=game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")
 ship:SetAttribute("LII_Installed",true);ship:SetAttribute("MooringsClear",false);ship:SetAttribute("GangwaysStowed",false);ship:SetAttribute("VesselClass","1889 Atlantic express liner");ship:SetAttribute("LOA_M",166);ship:SetAttribute("Beam_M",18.4);ship:SetAttribute("Draft_M",6.5);ship:SetAttribute("M_Per_Stud",M);ship:SetAttribute("LII_VisualParts",visualCount);ship:SetAttribute("LII_ProxyParts",#Data.proxies)
 print(string.format("Aurelian installed: %d visual parts, %d metadata matches, %d native proxies. LIVE STUDIO ACCEPTANCE STILL REQUIRED.",visualCount,assigned,#Data.proxies))
 print("Recommended place settings: StreamingEnabled, MinRadius 64, TargetRadius 128. Installer does not alter global port/lighting/streaming settings.")
 return ship
end
