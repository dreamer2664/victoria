--!nonstrict
--[[
	Whaler.lua -- server controller for the 27 ft double-ended clinker whaler.

	The whaler is a pulling boat, so she shares the stroke engine in
	RowingCutter, but she is not a smaller rowing cutter and must not be driven
	as one.  What is different, and why this module exists at all:

	  * FIVE oars, SINGLE banked -- three to port, two to starboard, the
	    Admiralty arrangement for the 27 ft whaler.  There is no second bank, so
	    there is nothing to pull against: steering is done by the stroke oar and
	    the bow oar holding water on one side, which swings the stern round.
	    RowingCutter takes that branch when the config says `single_banked`.

	  * NO TRANSOM.  She is a double-ender: the after oar is worked right aft in
	    the boat where a transom boat would have a tiller and a rudder, and the
	    rudder in the model is a small steering oar, not a hung blade.  Nothing
	    in the control scheme may assume a transom to push against.

	  * A CENTREBOARD, drawn up.  It lives in its trunk and is welded in the
	    drawn-up pose -- a whaler under oars or towing a line does not want it
	    down, and a board that swung when the boat rolled would look wrong.

	  * SHE CARRIES HER RIG FURLED.  Mainmast 5.03 m, mizzen 3.96 m: stepped,
	    she is far too tall to hoist under a davit, so the sticks are stowed
	    and the boat is a pulling boat in play.  See
	    boats/docs/CONSTRUCTION_C_whaler.md.

	Everything else -- buoyancy probes, hull drag, stroke cycle, spray -- comes
	from the shared model, so the three boats behave consistently.
]]

local RowingCutter = require(script.Parent.RowingCutter)

local Whaler = {}
Whaler.__index = Whaler
setmetatable(Whaler, { __index = RowingCutter })

--- Build the controller.  `manifest` is Manifest_whaler_27ft.
function Whaler.new(model, manifest)
	local self = RowingCutter.new(model, manifest, "whaler_27ft")
	setmetatable(self, Whaler)

	self.singleBanked = true
	self.centreboard = model:FindFirstChild("Centreboard", true)
	return self
end

--- The whaler has no engine: "start" means "ship oars and give way".
--- Both go through the shared control path so the client HUD agrees with the
--- controller about what the boat is doing.
function Whaler:start()
	self:control(nil, "row", true)
	self:control(nil, "power", math.max(self.power, 0.35))
end

--- Crew away: oars trailed flat, as a boat lying at a boom would have them.
function Whaler:stop()
	self:control(nil, "row", false)
end

return Whaler
