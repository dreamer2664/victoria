-- Headless LOGIC harness, not Roblox Studio, physics, replication or security certification.
-- Run through tools/test_leonidas_runtime.py, which injects the EXACT runtime source.
-- The fake API deliberately does not simulate welds, contacts, Humanoids or rendering.
local moduleSource=__RUNTIME_TEXT__
local Data=require("../../../roblox/leonidas_ii/Aurelian_Data")
local passed=0
local function check(name,ok,detail)
 assert(ok,"FAIL "..name.." · "..tostring(detail));passed+=1
 print("PASS "..name.." · "..tostring(detail or ""))
end
local V={};local VM={}
function V.new(x,y,z) return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},VM) end
VM.__index=function(a,k)
 if k=="Magnitude" then return math.sqrt(a.X*a.X+a.Y*a.Y+a.Z*a.Z) end
 if k=="Unit" then return a/a.Magnitude end
 if k=="Dot" then return function(a,b) return a.X*b.X+a.Y*b.Y+a.Z*b.Z end end
 if k=="Cross" then return function(a,b) return V.new(a.Y*b.Z-a.Z*b.Y,a.Z*b.X-a.X*b.Z,a.X*b.Y-a.Y*b.X) end end
end
VM.__add=function(a,b) return V.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z) end
VM.__sub=function(a,b) return V.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z) end
VM.__unm=function(a) return V.new(-a.X,-a.Y,-a.Z) end
VM.__mul=function(a,b)
 if type(a)=="number" then return V.new(a*b.X,a*b.Y,a*b.Z) end
 if type(b)=="number" then return V.new(a.X*b,a.Y*b,a.Z*b) end
 return V.new(a.X*b.X,a.Y*b.Y,a.Z*b.Z)
end
VM.__div=function(a,b) return V.new(a.X/b,a.Y/b,a.Z/b) end
local C={};local CM={};local CF={}
function C.fromMatrix(p,r,u,b) return setmetatable({p=p,r=r,u=u,b=b},CM) end
function C.new(x,y,z)
 local p=type(x)=="table" and x or V.new(x,y,z)
 return C.fromMatrix(p,V.new(1,0,0),V.new(0,1,0),V.new(0,0,1))
end
function CF:VectorToWorldSpace(v) return self.r*v.X+self.u*v.Y+self.b*v.Z end
function CF:PointToWorldSpace(v) return self.p+self:VectorToWorldSpace(v) end
function CF:PointToObjectSpace(v) local a=v-self.p;return V.new(a:Dot(self.r),a:Dot(self.u),a:Dot(self.b)) end
function CF:Inverse()
 local r=V.new(self.r.X,self.u.X,self.b.X);local u=V.new(self.r.Y,self.u.Y,self.b.Y);local b=V.new(self.r.Z,self.u.Z,self.b.Z)
 return C.fromMatrix(V.new(-self.p:Dot(self.r),-self.p:Dot(self.u),-self.p:Dot(self.b)),r,u,b)
end
function CF:ToObjectSpace(other) return self:Inverse()*other end
function CF:ToOrientation() return 0,math.atan2(self.b.X,self.b.Z),0 end -- identity / yaw-only initial datum used by this harness
CM.__index=function(a,k)
 if k=="Position" then return a.p elseif k=="LookVector" then return -a.b elseif k=="RightVector" then return a.r elseif k=="UpVector" then return a.u end
 return CF[k]
end
CM.__mul=function(a,b) return C.fromMatrix(a:PointToWorldSpace(b.p),a:VectorToWorldSpace(b.r),a:VectorToWorldSpace(b.u),a:VectorToWorldSpace(b.b)) end
function C.Angles(x,y,z)
 local sx,cx,sy,cy,sz,cz=math.sin(x),math.cos(x),math.sin(y),math.cos(y),math.sin(z),math.cos(z)
 local o=V.new();local rx=C.fromMatrix(o,V.new(1,0,0),V.new(0,cx,sx),V.new(0,-sx,cx));local ry=C.fromMatrix(o,V.new(cy,0,-sy),V.new(0,1,0),V.new(sy,0,cy));local rz=C.fromMatrix(o,V.new(cz,sz,0),V.new(-sz,cz,0),V.new(0,0,1))
 return rx*ry*rz
end
function C.lookAt(a,b,up)
 local f=(b-a).Unit;local r=f:Cross(up).Unit;return C.fromMatrix(a,r,r:Cross(f).Unit,-f)
end
C.identity=C.new()
local function signal()
 local s={callbacks={}}
 function s:Connect(fn) table.insert(self.callbacks,fn);return {Disconnect=function() end} end
 function s:Fire(...) for _,f in self.callbacks do f(...) end end
 return s
end
local API={};local IM={};local Instance={}
function Instance.new(class)
 local props={Name=class,ClassName=class,CFrame=C.identity,Health=100,FloorMaterial="Ground"}
 if class=="ProximityPrompt" then props.Triggered=signal() end
 return setmetatable({_props=props,_children={},_attributes={}},IM)
end
IM.__index=function(o,k)
 if k=="Position" then return o._props.CFrame.Position end
 return API[k] or o._props[k]
end
IM.__newindex=function(o,k,v)
 if k=="Parent" then
  local old=o._props.Parent;if old then local i=table.find(old._children,o);if i then table.remove(old._children,i) end end
  if v then table.insert(v._children,o) end
 end
 o._props[k]=v
end
function API:IsA(c) return self.ClassName==c or c=="BasePart" and (self.ClassName=="Part" or self.ClassName=="VehicleSeat" or self.ClassName=="Seat") end
function API:GetChildren() return self._children end
function API:GetDescendants()
 local all={};local function rec(o) for _,c in o._children do table.insert(all,c);rec(c) end end;rec(self);return all
end
function API:FindFirstChild(n,recursive)
 for _,c in self._children do if c.Name==n then return c end end
 if recursive then for _,c in self._children do local hit=c:FindFirstChild(n,true);if hit then return hit end end end
end
function API:FindFirstChildOfClass(n) for _,c in self._children do if c:IsA(n) then return c end end end
function API:WaitForChild(n) local x=self:FindFirstChild(n);assert(x,"Stub missing child "..n);return x end
function API:SetAttribute(k,v) self._attributes[k]=v end
function API:GetAttribute(k) return self._attributes[k] end
function API:GetPivot() return self.PrimaryPart.CFrame end
function API:Destroy() self.Parent=nil end
local heartbeat=signal();local now=0;local players={}
local Players={GetPlayers=function() return players end};local RunService={Heartbeat=heartbeat}
local world={blockRay=false,rayCalls=0}
function world:Raycast(...) self.rayCalls+=1;if self.blockRay then return {Instance={}} end;return nil end
local gameStub={GetService=function(_,name) if name=="Players" then return Players elseif name=="RunService" then return RunService else error(name) end end}
local env=setmetatable({game=gameStub,Vector3=V,CFrame=C,Instance=Instance,workspace=world,RaycastParams={new=function() return {} end},Enum={RaycastFilterType={Exclude="Exclude",Include="Include"},KeyCode={E="E",F="F",Q="Q",R="R"},Material={Air="Air"}},os={clock=function() return now end}}, {__index=getfenv()})
local loader,why=loadstring(moduleSource,"@Aurelian_Runtime_Under_Test");assert(loader,why);setfenv(loader,env);local Runtime=loader()
local ship=Instance.new("Model");ship.Name="Aurelian";ship.Parent=Instance.new("Folder")
local function part(name,parent,motor)
 local p=Instance.new("Part");p.Name=name;p.Parent=parent
 if motor then local m=Instance.new("Motor6D");m.Name="LII_Motor";m.C0=C.identity;m.Parent=p end
 return p
end
ship.PrimaryPart=part("LII_Root",ship,false)
local hosts=Instance.new("Folder");hosts.Name="LII_Controls";hosts.Parent=ship
for _,a in Data.attachments do part(a.id,hosts,false) end
for _,id in {"Helm_Port","Helm_Starboard"} do part(id,hosts,false) end
for _,m in Data.movers do part(m.name,ship,true) end
for _,d in Data.doors do part(d.name,ship,true);part("Collider_"..d.name,ship,true);part("Handle_"..d.id,hosts,false) end
local helm=Instance.new("VehicleSeat");helm.Name="LII_HelmSeat";helm.Parent=ship
local char=Instance.new("Model");local hrp=part("HumanoidRootPart",char,false);local hum=Instance.new("Humanoid");hum.Parent=char
local player={Character=char,UserId=12345}
local state=Runtime.start(ship,Data);local controls=ship:FindFirstChild("ShipControl")
local function invoke(n,...) return controls:FindFirstChild(n).OnInvoke(...) end
local function tick(seconds)
 for _=1,math.floor(seconds/.05+.5) do now+=.05;heartbeat:Fire(.05) end
end
local function trigger(n,move,advance)
 if advance~=false then now+=.30 end
 local h=hosts:FindFirstChild(n);assert(h,n)
 if move~=false then hrp.CFrame=C.new(h.Position) end
 h:FindFirstChildOfClass("ProximityPrompt").Triggered:Fire(player)
end
check("initial made-fast Stop state",state.order==5 and not state.clear and state.rpm==0)
check("ahead rejected before cast-off",invoke("OrderTelegraph","Full Ahead")==false)
check("cast-off rejected with lowered gangways",invoke("SetMooringsClear",true)==false)
check("NaN telegraph order rejected",invoke("OrderTelegraph",0/0)==false)
check("unknown telegraph order rejected",invoke("OrderTelegraph","Warp speed")==false)
trigger("Boarding_Port")
check("cast-off waits for actual gangway travel",state.gangways and invoke("SetMooringsClear",true)==false)
tick(10)
check("cast-off after shipped gangways",invoke("SetMooringsClear",true)==true)
check("ahead order after cast-off",invoke("OrderTelegraph",4)==true and state.order==9)
for _=1,4 do trigger("Regulator") end
for _=1,2 do trigger("Stoke") end
check("separate regulator and firing controls",state.regulator==1 and state.fire==1)
tick(240)
check("positive ahead RPM and target speed",state.rpm>71.5 and state.speed/.514444>19.0,state.rpm)
check("published signed RPM",ship:GetAttribute("ShaftRPM")>0)
local function p(a) return V.new(-a[2]/.28,(a[3]-6.5)/.28,-a[1]/.28) end
local worst=0
for _,m in Data.movers do
 if m.type=="conrod" then
  local a=state.angle+(m.phase or 0);local yy=(m.centre_y or 0)+m.r*math.sin(a);local sz=m.shaft_z or 3;local slider=m.slider_y or m.centre_y or 0;local zz=sz+m.r*math.cos(a);local cz=zz+math.sqrt(m.l*m.l-(slider-yy)^2)
  local frame=ship:FindFirstChild(m.name):FindFirstChild("LII_Motor").C0
  worst=math.max(worst,(frame:PointToWorldSpace(p(m.pin0))-p({m.x,yy,zz})).Magnitude,(frame:PointToWorldSpace(p(m.cross0))-p({m.x,slider,cz})).Magnitude)
 end
end
check("actual Luau conrod/valve-link endpoint transforms",worst<1e-7,worst)
check("cannot make fast underway",invoke("SetMooringsClear",false)==false)
check("rudder clamp",invoke("SetRudder",80)==true and state.requestedRudder==35)
check("NaN rudder rejected",invoke("SetRudder",0/0)==false)
check("Stop accepted",invoke("OrderTelegraph","Stop")==true)
tick(240)
check("shaft coasts close to zero",math.abs(state.rpm)<.001,state.rpm)
check("signed astern order",invoke("OrderTelegraph",-4)==true and state.order==1)
tick(180)
check("actual negative RPM and speed in astern",state.rpm< -45 and state.speed< -6,state.rpm)
invoke("OrderTelegraph",0);tick(300)
check("make fast after stopped shaft",invoke("SetMooringsClear",false)==true and not state.clear and state.regulator==0)
tick(180)
local y=ship:GetPivot().Position.Y;tick(180)
check("no cumulative made-fast height drift",math.abs(ship:GetPivot().Position.Y-y)<1e-9,y)
local old=state.generator;hrp.CFrame=C.new(100,0,0);trigger("Generator",false)
check("server prompt distance rejection",state.generator==old)
hum.Health=0;trigger("Generator");check("dead player prompt rejection",state.generator==old);hum.Health=100
trigger("Generator");local once=state.generator;trigger("Generator",true,false)
check("same-player prompt rate limit",state.generator==once and once~=old)
local d=Data.doors[1];local motor=ship:FindFirstChild(d.name):FindFirstChild("LII_Motor")
world.blockRay=true;trigger("Handle_"..d.id);tick(1)
check("door server LOS rejects intervening obstacle",motor.C0.p.Magnitude<1e-9 and world.rayCalls>0)
world.blockRay=false;trigger("Handle_"..d.id);tick(5)
check("door opens to finite commanded hinge transform",motor.C0.p.Magnitude>1 and motor.C0.p.Magnitude<1e5)
local collider=ship:FindFirstChild("Collider_"..d.name):FindFirstChild("LII_Motor")
check("door leaf and collider receive same transform",(collider.C0.p-motor.C0.p).Magnitude<1e-9)
-- The fake world does not weld hosts to the moving root. Place this host
-- explicitly for the guard test; this is a logic input, not a physics test.
local handle=hosts:FindFirstChild("Handle_"..d.id)
handle.CFrame=ship:GetPivot()*C.new(p(d.hinge)+V.new(0,1/.28,(d.width+.20)/.28))
hrp.CFrame=handle.CFrame;table.insert(players,player)
trigger("Handle_"..d.id,false);tick(1)
check("door close rejects avatar at far edge of hinge sweep",motor.C0.p.Magnitude>1)
table.clear(players)
trigger("Handle_"..d.id,false);tick(5)
check("door snaps fully shut without perpetual updates",motor.C0.p.Magnitude<1e-9)
local ok=pcall(function() Runtime.start(ship,Data) end)
check("duplicate controller rejected",not ok)
print("MOCK_RUNTIME_TESTS_COMPLETE",passed)
