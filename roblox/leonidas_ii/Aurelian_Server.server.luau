--!strict
-- Disable the seven legacy ship controllers for THIS model. Do not run both.
local ship=workspace:WaitForChild("Aurelian")
local cfg=ship:WaitForChild("LII_Config")
require(cfg:WaitForChild("Aurelian_Runtime")).start(ship,require(cfg:WaitForChild("Aurelian_Data")))
