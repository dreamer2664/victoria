--!strict
-- Explicit Studio-side smoke test, NOT run/certified by the build agent.
-- Edit/Play command bar: require(workspace.Aurelian_Package.Aurelian_StudioAcceptance)(workspace.Aurelian)
-- Then perform the manual route / motion / multiplayer sheet in docs.
return function(ship)
 assert(ship and ship:IsA("Model") and ship.PrimaryPart,"Install Aurelian first")
 local data=require(ship:WaitForChild("LII_Config"):WaitForChild("Aurelian_Data"))
 local rows={};local function test(name,ok,detail) table.insert(rows,{name=name,pass=ok,detail=detail});print((ok and "PASS " or "FAIL ")..name.." · "..tostring(detail)) end
 test("Waterline root / metres per stud",ship.PrimaryPart.Name=="LII_Root" and ship:GetAttribute("M_Per_Stud")==.28,ship:GetPivot())
 local visuals,proxies,motors,unbound,lo,hi=0,0,0,0,Vector3.new(math.huge,math.huge,math.huge),Vector3.new(-math.huge,-math.huge,-math.huge)
 local forbidden={}
 for _,o in ship:GetDescendants() do
  if o:IsA("BasePart") then
   if o:GetAttribute("LII_Visual") then visuals+=1;if o.CanCollide then table.insert(forbidden,o.Name) end end
   if o:GetAttribute("LII_Collider") then proxies+=1 end
   if o:FindFirstChild("LII_Motor") then motors+=1 end
   if o~=ship.PrimaryPart and not o:FindFirstChild("LII_Weld") and not o:FindFirstChild("LII_Motor") then unbound+=1 end
   if o.Name:sub(1,14)=="Hull_Shell_New" then
    for x=-1,1,2 do for y=-1,1,2 do for z=-1,1,2 do
     local a=ship:GetPivot():PointToObjectSpace(o.CFrame:PointToWorldSpace(o.Size*Vector3.new(x,y,z)*.5))
     lo=Vector3.new(math.min(lo.X,a.X),math.min(lo.Y,a.Y),math.min(lo.Z,a.Z));hi=Vector3.new(math.max(hi.X,a.X),math.max(hi.Y,a.Y),math.max(hi.Z,a.Z))
    end end end
   end
  end
 end
 local loa=(hi.Z-lo.Z)*.28;local beam=(hi.X-lo.X)*.28
 test("Imported shell LOA",math.abs(loa-166)<.12,loa.." m")
 test("Imported shell beam",math.abs(beam-18.4)<.12,beam.." m including plating")
 test("All visual detail noncolliding",#forbidden==0,table.concat(forbidden,", "))
 test("Every passive part welded / animated motor bound",unbound==0,unbound)
 test("Only the root anchored",(function() for _,o in ship:GetDescendants() do if o:IsA("BasePart") and o~=ship.PrimaryPart and o.Anchored then return false end end;return ship.PrimaryPart.Anchored end)(),"anchored kinematic root / welded assembly")
 test("Visual node count",visuals==data.expected_visual_nodes,visuals.." / "..data.expected_visual_nodes)
 test("Collisions generated",proxies>=#data.proxies,proxies)
 test("Door and machinery motors",motors>=#data.doors*2+#data.movers,motors)
 for _,d in data.doors do
  local leaf=ship:FindFirstChild(d.name,true);local proxy=ship:FindFirstChild("Collider_"..d.name,true)
  test("Door "..d.id,leaf~=nil and proxy~=nil and proxy:FindFirstChild("LII_Motor")~=nil,d.width.." m clear opening")
 end
 print("UNVERIFIED UNTIL YOU PLAYTEST: prompt distance/line of sight; full route into every major room; avatar size; stairs/landings; gangway to real quay; reversing crank/shaft/propeller; rudder/helm; seated/standing passengers; two clients; streaming, network ownership and frame times.")
 return rows
end
